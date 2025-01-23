import praw
import gspread
import asyncio
import os

from post_sheet import PostsSpreadSheet
from priority_queue import PriorityQueue
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

from manual_flow.llm import LLM
from dotenv import load_dotenv

load_dotenv()


class Redit:

    REDIT_CLIENT_ID = os.getenv('REDIT_CLIENT_ID')
    REDIT_SECRET_ID = os.getenv('REDIT_SECRET_ID')
    REDIT_USER_AGENT = os.getenv('REDIT_USER_AGENT')
    SUBREDDITS = [
        'nosleep',              # horror stories
        'AmItheAsshole',        # am i the a** hole
        'tifu',                 # Today I F***ed Up – funny/awkward stories
        'relationships',        # personal advice stories
        'confession',           # honest and raw stories
        # # TODO : 'AskReddit',   # just question and comments will answer
        'ProRevenge',           # revenge stories
        'MaliciousCompliance',  # satisfying compliance stories          
    ]


    def __init__(self):
        self.reddit = praw.Reddit(
            client_id = self.REDIT_CLIENT_ID,
            client_secret = self.REDIT_SECRET_ID,
            user_agent = self.REDIT_USER_AGENT
        )


    def sort_posts(self, posts):
        return sorted(posts, key=lambda x: x['normalized_score'], reverse=True)


    def fetch_top_posts(self, posts_per_subreddit=10, time_filter='week'):
        all_posts = []
        
        for subreddit_name in self.SUBREDDITS:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            for post in subreddit.top(limit=posts_per_subreddit, time_filter=time_filter):
                post_age_seconds = (datetime.utcnow() - datetime.utcfromtimestamp(post.created_utc)).total_seconds()
                upvotes = post.score  # Upvotes or total score
                comments = post.num_comments  # Number of comments
                
                # Normalize by dividing the score by the post age and the number of comments
                normalized_score = (upvotes / (post_age_seconds + 1)) * (comments + 1)  # Adding +1 to avoid division by zero
            
                content = post.selftext if post.selftext else '[Link]' if post.url else '[Media]'
                post_date = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')  # Convert timestamp to date

                if(len(content) > 700):
                    all_posts.append({
                        'id': post.id,
                        'post_date': post_date,
                        'post_subreddit': subreddit_name,
                        'progress': 'SCRIPT_READY',
                        'title': post.title,
                        'score': post.score,
                        'normalized_score': normalized_score,
                        'content': content,
                        'content_length': len(content),
                        'post_link': post.url,

                    })

            print("Got latest post for : ", subreddit)
        

        sorted_posts = self.sort_posts(all_posts)
        return sorted_posts
    


def process():

    POST_PER_SUBREDIT = 10
    # # Fetch, sort, and upload posts
    posts = Redit().fetch_top_posts(posts_per_subreddit = POST_PER_SUBREDIT)
    print("Completed the redit fetching process")

    posts = asyncio.run(LLM(posts).run_automation())
    print("Completed the redit revision process")

    sheet_name = 'Redit Posts'
    PostsSpreadSheet(sheet_name).add_to_google_sheets(posts)
    print("Complete adding posts to excel")




def main():
    process()


if __name__=="__main__":
    main()