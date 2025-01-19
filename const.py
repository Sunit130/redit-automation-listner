CHATGPT_VISION_OMNI_MODAL = "gpt-4o"
REDDIT_FILTER_PROMPT = """
Please carefully rewrite the following Reddit post to create a more engaging story suitable for text-to-speech narration and video content. Before writing the final output, think about how to best apply these guidelines to keep the story authentic and engaging. Follow these instructions:

1. **Use Simple Language**(Most important):
   - Use only simple and common words, unless absolutely necessary.
   - The final goal is to create a storytelling-like communication in the first person.

2. **Content Refinement**:
   - Remove any unwanted text such as links, images, URLs, "Edit" sections, "Thank you" notes, or any extra content that doesn't contribute to the story.
   - Combine relevant edits from the original post if they impact the story, blending them smoothly.

3. **Narrative Voice**:
   - Write the content in the **first person**, keeping the original narrator's voice and perspective.
   - Compose the story as a Reddit user would naturally write it, maintaining authenticity.
   - **Keep as many details as possible** to make the story feel real and written by a human.

4. **Engagement Techniques**:
   - Improve the hook at the beginning of the story to grab the audience's attention right away.
   - Use techniques that keep listeners interested throughout the story.

5. **Clarity and Flow**:
   - While keeping the story detailed, make sure it stays on point and all details add to the narrative.
   - Simplify complex sentences for better readability and flow.
   - Ensure proper grammar and sentence structure.
   - **Keep the final story's word count similar to the original**, preserving its length.

6. **Emotional Integrity**:
   - Identify and keep the user's feelings and emotions alive, even after rewording.
   - If the original post includes cuss words or strong language, retain them to maintain emotional authenticity, as long as they are appropriate.

7. **Content Appropriateness**:
   - Ensure the content is appropriate for general audiences, avoiding any explicit words or themes that might be offensive.
   - Stay true to the original tone while maintaining appropriateness.

8. **Story Flow and Completion**:
   - Check for any sudden endings or unanswered questions and address them to provide a satisfying conclusion.
   - Keep a natural and logical flow throughout the story.

9. **Thoughtful Revision**:
   - Before writing the final output, think carefully about how to best apply these guidelines to enhance the story while preserving its original essence.

10. **Title Enhancement**:
    - You will be given the original title of the post.
    - **Either leave the title as it is or, if possible, turn it into an engaging hook** that reflects the story's content.
    - Make sure the title is attention-grabbing and accurately represents the story.

11. **Format**:
    - The final output should include only the **title** and the **story**.
    - Exclude any extra content such as links, images, "Edit" sections, or "Thank you" notes.

"""




MINECRAFT_VIDEO_LIST = [
    { "url": "https://www.youtube.com/watch?v=xKRNDalWE-E", "duration": 902 },
    { "url": "https://www.youtube.com/watch?v=Pap_Ln-Fz2A", "duration": 304 },
    { "url": "https://www.youtube.com/watch?v=3j5PUUQz5cw", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=r5utBFtLtWk", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=oPz7Uh_6ey4", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=GA8vYmmvqEk", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=dBE0pZtK3ao", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=prmMgmdM-xc", "duration": 601 },
    { "url": "https://www.youtube.com/watch?v=13_4cPyWiIo", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=wv8_ePzdMv8", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=IWy5lAkt6CY", "duration": 431 },
    { "url": "https://www.youtube.com/watch?v=0ikEJppc9qQ", "duration": 302 },
    { "url": "https://www.youtube.com/watch?v=FHkeRqGnNQk", "duration": 302 },
    { "url": "https://www.youtube.com/watch?v=A2RQGBQvHfI", "duration": 302 },
    { "url": "https://www.youtube.com/watch?v=rYPeM4m-tJc", "duration": 310 },
    { "url": "https://www.youtube.com/watch?v=oSzKvHzjrSA", "duration": 304 },
    { "url": "https://www.youtube.com/watch?v=YpjTpjFuhZM", "duration": 320 },
    { "url": "https://www.youtube.com/watch?v=lzEEhDRRafM", "duration": 306 },
    { "url": "https://www.youtube.com/watch?v=Ctdg-sOW8po", "duration": 309 },
    { "url": "https://www.youtube.com/watch?v=wXN08vl6TWI", "duration": 305 },
    { "url": "https://www.youtube.com/watch?v=6GPXGBg7UGo", "duration": 315 },
    { "url": "https://www.youtube.com/watch?v=rsEP9N9c5CQ", "duration": 306 },
    { "url": "https://www.youtube.com/watch?v=axAYvo8gOIA", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=B2GM98bKhVg", "duration": 291 },
    { "url": "https://www.youtube.com/watch?v=E1CgDCh5KC0", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=BbM2MJ6aeZE", "duration": 323 },
    { "url": "https://www.youtube.com/watch?v=AGnZ8nMnbv4", "duration": 305 },
    { "url": "https://www.youtube.com/watch?v=4ASNL5RwghA", "duration": 294 },
    { "url": "https://www.youtube.com/watch?v=lVtPEAeM-UM", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=cOUcu-xSKHM", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=bb07ui130-8", "duration": 305 },
    { "url": "https://www.youtube.com/watch?v=7cIPxrLYw8M", "duration": 304 },
    { "url": "https://www.youtube.com/watch?v=--owd7CIjYs", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=CCfNnjiN8xI", "duration": 247 },
    { "url": "https://www.youtube.com/watch?v=iUEccNy3m04", "duration": 369 },
    { "url": "https://www.youtube.com/watch?v=l0aysU5iE5k", "duration": 296 },
    { "url": "https://www.youtube.com/watch?v=wrSXoFBozu4", "duration": 488 },
    { "url": "https://www.youtube.com/watch?v=ckKNrq56XIw", "duration": 302 },
    { "url": "https://www.youtube.com/watch?v=-IegPHSc2VA", "duration": 308 },
    { "url": "https://www.youtube.com/watch?v=o9b2oynTQXo", "duration": 316 },
    { "url": "https://www.youtube.com/watch?v=X_79-x_nLzs", "duration": 237 },
    { "url": "https://www.youtube.com/watch?v=1e6Rn6JEICc", "duration": 304 },
    { "url": "https://www.youtube.com/watch?v=StgZ5ct4Jx4", "duration": 305 },
    { "url": "https://www.youtube.com/watch?v=QZQPRIg245A", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=vC04Xj7NWBc", "duration": 420 },
    { "url": "https://www.youtube.com/watch?v=Pp7fmvfyaOI", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=YB10EbfzZts", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=mvNSGMcTN1s", "duration": 301 },
    { "url": "https://www.youtube.com/watch?v=pSgWt_CFtHM", "duration": 310 },
    { "url": "https://www.youtube.com/watch?v=i5w6Y74ZgYk", "duration": 422 },
    { "url": "https://www.youtube.com/watch?v=FXzWKqMPHI0", "duration": 373 },
    { "url": "https://www.youtube.com/watch?v=iFiPxTrcoWw", "duration": 786 },
    { "url": "https://www.youtube.com/watch?v=qK1VjY_cU9w", "duration": 1042 },
    { "url": "https://www.youtube.com/watch?v=B0TibQ9xkeg", "duration": 428 },
    { "url": "https://www.youtube.com/watch?v=s1TvTdX6ELQ", "duration": 483 },
    { "url": "https://www.youtube.com/watch?v=nylp1Eqvmkc", "duration": 489 },
    { "url": "https://www.youtube.com/watch?v=U4LP3jNDEtI", "duration": 422 },
    { "url": "https://www.youtube.com/watch?v=yAwQj6uU_44", "duration": 307 },
    { "url": "https://www.youtube.com/watch?v=TMVIE8wA2lo", "duration": 313 },
    { "url": "https://www.youtube.com/watch?v=P9SQ8f6VU5c", "duration": 303 },
    { "url": "https://www.youtube.com/watch?v=Zqblo0b2Sfc", "duration": 378 },
    { "url": "https://www.youtube.com/watch?v=4e2mvM35Uvk", "duration": 231 },
    { "url": "https://www.youtube.com/watch?v=M1ZOfuZsQBA", "duration": 481 },
    { "url": "https://www.youtube.com/watch?v=dkEtW5VYKMU", "duration": 424 },
    { "url": "https://www.youtube.com/watch?v=3CJiyfvj59I", "duration": 497 },
    { "url": "https://www.youtube.com/watch?v=dRqpUiaB7yY", "duration": 510 },
    { "url": "https://www.youtube.com/watch?v=OpHwJaPuFLs", "duration": 497 },
    { "url": "https://www.youtube.com/watch?v=xcGPhbQhzaE", "duration": 536 },
    { "url": "https://www.youtube.com/watch?v=FgBG1nxhDCs", "duration": 481 },
    { "url": "https://www.youtube.com/watch?v=-N2MCC7--Sc", "duration": 518 },
    { "url": "https://www.youtube.com/watch?v=-aPw_oYhxHw", "duration": 482 },
    { "url": "https://www.youtube.com/watch?v=Z056xJKJznY", "duration": 483 },
    { "url": "https://www.youtube.com/watch?v=XLpGWgHI6YY", "duration": 497 },
    { "url": "https://www.youtube.com/watch?v=P7ZH6CghtDY", "duration": 274 },
    { "url": "https://www.youtube.com/watch?v=hLKtm_zQQXM", "duration": 29 },
]