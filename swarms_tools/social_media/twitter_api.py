import os
from typing import Callable
import tweepy
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class TwitterBot:
    """Twitter Bot to auto-respond to DMs and mentions."""

    def __init__(self, response_callback: Callable[[str], str]):
        try:
            # Load credentials from environment variables
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv(
                "TWITTER_ACCESS_TOKEN_SECRET"
            )

            if not all(
                [
                    api_key,
                    api_secret,
                    access_token,
                    access_token_secret,
                ]
            ):
                raise ValueError("Missing Twitter API credentials")

            # Authenticate and initialize Tweepy clients
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True,
            )
            auth = tweepy.OAuth1UserHandler(
                api_key, api_secret, access_token, access_token_secret
            )
            self.api = tweepy.API(auth)

            # Verify credentials
            self.me = self.client.get_me().data
            logger.info(
                f"Twitter Bot initialized for user @{self.me.username}"
            )

            self.response_callback = response_callback
            self.processed_ids = set()

        except Exception as e:
            logger.error(
                f"Failed to initialize Twitter Bot: {str(e)}"
            )
            raise

    def auto_respond_mentions(self):
        """Fetch and respond to mentions."""
        try:
            mentions = self.client.get_users_mentions(
                self.me.id,
                tweet_fields=["created_at"],
                max_results=100,
            )
            if not mentions.data:
                logger.info("No new mentions to process.")
                return

            for mention in mentions.data:
                if mention.id in self.processed_ids:
                    continue

                logger.info(
                    f"Processing mention {mention.id}: {mention.text}"
                )
                response = self.response_callback(mention.text)
                if response:
                    self.client.create_tweet(
                        text=response, in_reply_to_tweet_id=mention.id
                    )
                    logger.info(f"Replied to mention {mention.id}.")
                    self.processed_ids.add(mention.id)

        except Exception as e:
            logger.error(
                f"Error while responding to mentions: {str(e)}"
            )

    def auto_respond_dms(self):
        """Fetch and respond to DMs."""
        try:
            logger.warning(
                "DM functionality is limited by API access level. Upgrade required."
            )

            # If access is granted, implement DM handling logic for v2 or elevated v1.1
            # Example for v1.1 (requires elevated access)
            messages = self.api.get_direct_messages()
            for message in messages:
                message_id = message.id
                if message_id in self.processed_ids:
                    continue

                text = message.message_create["message_data"]["text"]
                sender_id = message.message_create["sender_id"]

                logger.info(
                    f"Processing DM {message_id} from {sender_id}: {text}"
                )
                response = self.response_callback(text)
                if response:
                    self.api.send_direct_message(sender_id, response)
                    logger.info(f"Replied to DM {message_id}.")
                    self.processed_ids.add(message_id)

        except Exception as e:
            logger.error(f"Error while responding to DMs: {str(e)}")

    def run(self):
        """Run the bot to handle mentions and DMs."""
        logger.info("Starting Twitter Bot...")
        self.auto_respond_mentions()
        self.auto_respond_dms()


# if __name__ == "__main__":

#     def generate_response(message: str) -> str:
#         """Simple response generator."""
#         return f"Thank you for your message! You said: {message}"

#     bot = TwitterBot(response_callback=generate_response)
#     bot.run()
