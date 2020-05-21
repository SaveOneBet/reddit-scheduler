import os
import time
import logging

from datetime import datetime, timedelta
import gspread
from dotenv import load_dotenv, find_dotenv
import praw

load_dotenv(find_dotenv(), override=True)
gc = gspread.service_account(filename="gsheet_credentials.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sh = gc.open_by_key('1XQyZJEqIxTm3dk7JGJd5Zprkd_XfQJXOFjwTOGtx2B4')
worksheet = sh.sheet1

connection = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent=os.getenv("REDDIT_USER_AGENT"),
            username=os.getenv("REDDIT_USERNAME")
        )

interval = int(os.getenv("INTERVAL"))
DEBUG = os.getenv("DEBUG") == "1"


def main():
    while True:
        post_records = worksheet.get_all_records()
        current_time = datetime.utcnow() + timedelta(hours=2)
        logger.info(f"{len(post_records)} posts found at {current_time}")
        for idx, post in enumerate(post_records, start=2):
            msg = post["message"]
            time_str = post["time"]
            done = post["done"]
            date_time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            if not done:
                now_time_cet = datetime.utcnow() + timedelta(hours=2)
                if date_time_obj < now_time_cet:
                    logger.info("this should be posted")
                    try:
                        my_subreddit = connection.subreddit("sportsbook")
                        regex_title = f"Pick of the Day - {now_time_cet.month}/{now_time_cet.day-1}"
                        for submission in my_subreddit.hot(limit=30):
                            if regex_title in submission.title:
                                post_reddit = connection.submission(id=submission.id)
                                post_reddit.reply(body=msg)

                                worksheet.update_cell(idx, 3, 1)
                    except Exception as e:
                        logger.warning(f"exception during post! {e}")

        time.sleep(interval)


if __name__ == '__main__':
    main()
