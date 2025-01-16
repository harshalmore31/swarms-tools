import os
import subprocess
import sys
from typing import Any, Dict, List

try:
    import tweepy
except ImportError as error:
    print(f"Tweepy not found {error} Installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "tweepy"]
    )
    print("Tweepy has been installed.")
    import tweepy

from loguru import logger


def authenticate_twitter_api() -> tweepy.API:
    """
    Authenticates and returns the Tweepy API object.

    Returns:
        tweepy.API: Authenticated Twitter API object.
    """
    try:
        API_KEY = os.getenv("TWITTER_API_KEY")
        API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
        ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
        ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

        if not all(
            [
                API_KEY,
                API_SECRET_KEY,
                ACCESS_TOKEN,
                ACCESS_TOKEN_SECRET,
            ]
        ):
            raise ValueError(
                "Missing one or more Twitter API keys in .env file"
            )

        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        logger.info("Successfully authenticated with Twitter API")
        return api
    except Exception as e:
        logger.error(f"Failed to authenticate Twitter API: {e}")
        raise


def fetch_all_dms(
    api: tweepy.API, count: int = 20
) -> List[Dict[str, Any]]:
    """
    Fetches all Direct Messages (DMs) from the authenticated user's inbox.

    Args:
        api (tweepy.API): Authenticated Twitter API object.
        count (int): Number of messages to fetch.

    Returns:
        List[Dict[str, Any]]: A list of messages with sender and message content.
    """
    try:
        messages = api.list_direct_messages(count=count)
        logger.info(f"Fetched {len(messages)} direct messages")
        return [
            {
                "message_id": message.id,
                "sender_id": message.message_create["sender_id"],
                "text": message.message_create["message_data"][
                    "text"
                ],
            }
            for message in messages
        ]
    except Exception as e:
        logger.error(f"Failed to fetch direct messages: {e}")
        return [{"error": str(e)}]


def auto_reply_to_dms(
    api: tweepy.API, reply_text: str, limit: int = 10
):
    """
    Automatically replies to DMs with a predefined message.

    Args:
        api (tweepy.API): Authenticated Twitter API object.
        reply_text (str): The text to reply with.
        limit (int): Number of DMs to process for replies.

    Returns:
        List[Dict[str, Any]]: A list of replies sent with their statuses.
    """
    try:
        messages = fetch_all_dms(api, count=limit)
        replies = []

        for message in messages:
            sender_id = message.get("sender_id")
            message_id = message.get("message_id")
            text = message.get("text")

            if (
                sender_id
                and sender_id != api.verify_credentials().id_str
            ):  # Avoid replying to self
                try:
                    api.send_direct_message(
                        recipient_id=sender_id, text=reply_text
                    )
                    logger.info(
                        f"Replied to DM from {sender_id}: {text}"
                    )
                    replies.append(
                        {
                            "message_id": message_id,
                            "sender_id": sender_id,
                            "status": "success",
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to reply to DM from {sender_id}: {e}"
                    )
                    replies.append(
                        {
                            "message_id": message_id,
                            "sender_id": sender_id,
                            "status": "error",
                            "error": str(e),
                        }
                    )

        return replies
    except Exception as e:
        logger.error(f"Failed to auto-reply to DMs: {e}")
        return [{"error": str(e)}]


# # Example Execution
# if __name__ == "__main__":
#     logger.add("twitter_api.log", rotation="500 MB", level="INFO")

#     try:
#         # Authenticate with Twitter API
#         api = authenticate_twitter_api()

#         # Fetch all DMs
#         dms = fetch_all_dms(api, count=5)
#         print("Fetched DMs:", dms)

#         # Auto-reply to DMs
#         auto_replies = auto_reply_to_dms(api, reply_text="Thank you for reaching out! We'll get back to you soon.", limit=5)
#         print("Auto Replies Sent:", auto_replies)

#     except Exception as e:
#         logger.error(f"Error in Twitter API tool: {e}")
