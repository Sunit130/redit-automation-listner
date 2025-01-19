import os
import asyncio
from time import sleep
import json
import aiohttp
import asyncio
import logging
import useful.logs
from concurrent.futures import ThreadPoolExecutor
from const import CHATGPT_VISION_OMNI_MODAL, REDDIT_FILTER_PROMPT


JSON_FIELDS = {
    "message": "message",
    "time": "created",
    "log_level": "levelname",
    "process": "process",
    "thread": "thread",
    "traceback": "exc_text",
    "__htime": "asctime",
    'pathname': 'pathname',
    'lineno': 'lineno',
    'funcName': 'funcName',
    'stack_info': 'stack_info'
}

# always extra fields for all Log events
ALWAYS_EXTRA = {
    "source": "python",
    "traceback": None,
    "trace_id": None,
    "request_id": None,
    "params": None,
    "state": None
}

EXEMPT_PATHS = [
        '/health/',
    ]

useful.logs.setup(log_level="INFO", json_fields=JSON_FIELDS, always_extra=ALWAYS_EXTRA)
LOGGER = logging.getLogger(__name__)



class LLM:

    GPT_MAX_RETRIES = 5

    def __init__(self, raw_prompts):
        self.raw_prompts = raw_prompts

    @staticmethod
    def get_gpt_payload(user_prompt):
        """
        Constructs a GPT API payload for image-based input.

        Parameters:
            user_prompt (list): List of messages for GPT to analyze.

        Returns:
            dict: The constructed GPT API payload.

        """

        return {
            "model": CHATGPT_VISION_OMNI_MODAL,
            "messages": [
                {'role': 'system', 'content': REDDIT_FILTER_PROMPT},
                {'role': 'user', 'content': [{"type": "text", "text": user_prompt}]}
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                "name": "revised_story",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                    "title": {
                        "type": "string",
                        "description": "An engaging and catchy title for the revised story."
                    },
                    "story": {
                        "type": "string",
                        "description": "The revised story based on the given prompt."
                    },
                    "character": {
                        "type": "string",
                        "description": "Gender of the character based on the narrator of the story. Default is male",
                        "enum": [
                        "male",
                        "female"
                        ]
                    }
                    },
                    "required": [
                    "title",
                    "story",
                    "character"
                    ],
                    "additionalProperties": False
                }
                }
            },
            "temperature": 1.00,
            "max_tokens": 10000,
        }



    async def get_model_scores(self, category, index, session, gpt_payload, raw_prompt):
        """
        Asynchronously performs the get_model_scores processing by calling the GPT API.
        """

        LOGGER.info(f"Started processing llm score", extra={'params': {'category': category, 'prompt_index': index}})
        api_url = os.environ.get("OPEN_API_URL")
        api_key = os.environ.get("OPEN_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        retry_count = 1
        max_retries = self.GPT_MAX_RETRIES

        print("GPT : PAYLOAD : ", gpt_payload)

        while retry_count <= max_retries:
            try:
                LOGGER.info(f"Hitting GPT API | retry_count - {retry_count}", extra={
                    'params': {'category': category, 'retry_count': retry_count,
                               'prompt_index': index}})
                async with session.post(api_url, headers=headers, json=gpt_payload) as response:
                    result = await response.json()
                    response.raise_for_status()
                    if result:
                        content = json.loads(result['choices'][0]['message']['content'])
                        print("content : ", content)
                        title = content.get("title", "")
                        story = content.get("story", "")
                        character = content.get("character", "")
                        return {**raw_prompt, "revised_title": title, "revised_content": story, 'revised_content_length': len(story), 'character': character,}

            except Exception as e:
                warn_msg = f"Failed GPT ({category} - {index}) retry_count - {retry_count}"
                LOGGER.warning(warn_msg,
                               extra={"params": {'error': str(e)}, 'category': category,
                                      'retry_count': retry_count, 'prompt_index': index})
                if retry_count < max_retries:
                    retry_count = retry_count + 1
                    sleep(1)
                else:
                    error_msg = f"Max retries reached for GPT ({category} - {index}). Returning failure status."
                    LOGGER.error(error_msg,
                                 extra={"params": {'error': str(e)}, 'category': category,
                                        'retry_count': retry_count, 'prompt_index': index})
                    return {**raw_prompt, "revised_content": ""}


    async def make_llm_scoring(self):

        async with aiohttp.ClientSession() as session:
            # Asynchronously execute LLM tasks for all prompts
            tasks = []

            for i, raw_prompt in enumerate(self.raw_prompts):
                # prompt = f"{raw_prompt.get("title", "")} | {raw_prompt.get("content", "")}"
                prompt = f'Title : {raw_prompt.get("title", "")} \n\n Story : \n{raw_prompt.get("content", "")}'
                payload = self.get_gpt_payload(prompt)
                task = self.get_model_scores("redit", i, session, payload, raw_prompt)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

            # separate analysis for desktop and mobile to then store in excel
            return results



    async def run_automation(self):
        with ThreadPoolExecutor() as executor:
            llm_scoring_future = asyncio.create_task(self.make_llm_scoring())
            [ llm_review ] = await asyncio.gather(llm_scoring_future)
            print("llm_review : ", llm_review)
            return llm_review
