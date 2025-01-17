import os
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Optional, Union

import tweepy
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class TwitterAction(Enum):
    """Enum for Twitter actions."""

    REPLY = "reply"
    DM = "dm"
    RESPOND = "respond"


class TwitterAPI:
    """A simplified Twitter API wrapper for responding to DMs and mentions."""

    def __init__(self):
        """Initialize Twitter API with credentials from environment variables."""
        try:
            # Log environment variable presence (not their values)
            logger.debug("Checking Twitter API credentials...")
            credentials = {
                "API_KEY": bool(os.getenv("TWITTER_API_KEY")),
                "API_SECRET": bool(os.getenv("TWITTER_API_SECRET")),
                "ACCESS_TOKEN": bool(
                    os.getenv("TWITTER_ACCESS_TOKEN")
                ),
                "ACCESS_TOKEN_SECRET": bool(
                    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                ),
            }
            logger.debug(f"Credentials present: {credentials}")

            if not all(credentials.values()):
                missing = [k for k, v in credentials.items() if not v]
                raise ValueError(f"Missing credentials: {missing}")

            self.client = tweepy.Client(
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv(
                    "TWITTER_ACCESS_TOKEN_SECRET"
                ),
                wait_on_rate_limit=True,
            )

            auth = tweepy.OAuth1UserHandler(
                os.getenv("TWITTER_API_KEY"),
                os.getenv("TWITTER_API_SECRET"),
                os.getenv("TWITTER_ACCESS_TOKEN"),
                os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            )
            self.api = tweepy.API(auth)

            # Verify credentials
            self.api.verify_credentials()
            self.me = self.client.get_me()
            if not self.me:
                raise tweepy.TweepyException(
                    "Failed to get user details"
                )

            logger.info(
                f"Twitter API initialized successfully for user @{self.me.data.username}"
            )

        except Exception as e:
            logger.error(
                f"Failed to initialize Twitter API: {str(e)}",
                exc_info=True,
            )
            raise

    def reply_to_tweet(self, tweet_id: str, message: str) -> bool:
        """Reply to a specific tweet."""
        try:
            self.client.create_tweet(
                text=message, in_reply_to_tweet_id=tweet_id
            )
            logger.info(f"Successfully replied to tweet {tweet_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to reply to tweet {tweet_id}: {str(e)}"
            )
            return False

    def send_dm(self, user_id: str, message: str) -> bool:
        """Send a direct message to a user."""
        try:
            self.api.send_direct_message(user_id, message)
            logger.info(f"Successfully sent DM to user {user_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to send DM to user {user_id}: {str(e)}"
            )
            return False

    def get_mentions(self) -> Optional[Dict]:
        """Get recent mentions of the authenticated user."""
        try:
            logger.info("Attempting to fetch recent mentions")

            mentions = self.client.get_users_mentions(
                self.me.data.id,
                tweet_fields=["created_at", "text", "author_id"],
                expansions=["author_id"],
                max_results=100,
            )

            if mentions.data:
                logger.info(f"Found {len(mentions.data)} mentions")
                for mention in mentions.data:
                    logger.debug(
                        f"Mention ID: {mention.id}, "
                        f"Text: {mention.text}, "
                        f"Created at: {mention.created_at}"
                    )
                return mentions.data
            else:
                logger.info("No mentions found")
                return None

        except Exception as e:
            logger.error(
                f"Failed to get mentions: {str(e)}", exc_info=True
            )
            return None

    def get_dms(self) -> Optional[Dict]:
        """Get recent direct messages."""
        try:
            messages = self.api.get_direct_messages()
            return messages

        except Exception as e:
            logger.error(f"Failed to get DMs: {str(e)}")
            return None


class TwitterBot:
    """A simplified Twitter bot that responds to mentions and DMs."""

    def __init__(self, response_callback: Callable[[str], str]):
        try:
            self.api = TwitterAPI()
            self.response_callback = response_callback
            self.last_mention_time = datetime.now()
            self.processed_dms = set()
            logger.info("TwitterBot initialized successfully")
        except Exception as e:
            logger.error(
                f"Failed to initialize TwitterBot: {str(e)}",
                exc_info=True,
            )
            raise

    def handle_mentions(self) -> None:
        """Process and respond to new mentions."""
        try:
            logger.info("Checking for new mentions")
            mentions = self.api.get_mentions()

            if not mentions:
                logger.debug("No mentions to process")
                return

            for mention in mentions:
                try:
                    # Skip if we've already processed this mention
                    if (
                        hasattr(mention, "id")
                        and str(mention.id) in self.processed_dms
                    ):
                        logger.debug(
                            f"Skipping already processed mention {mention.id}"
                        )
                        continue

                    mention_time = mention.created_at
                    logger.debug(
                        f"Processing mention {mention.id} from {mention_time}"
                    )

                    if mention_time > self.last_mention_time:
                        logger.info(
                            f"New mention found: {mention.id}"
                        )
                        logger.debug(f"Mention text: {mention.text}")

                        response = self.response_callback(
                            mention.text
                        )
                        logger.debug(
                            f"Generated response: {response}"
                        )

                        if response:
                            success = self.api.reply_to_tweet(
                                mention.id, response
                            )
                            if success:
                                logger.info(
                                    f"Successfully replied to mention {mention.id}"
                                )
                                self.last_mention_time = mention_time
                                self.processed_dms.add(
                                    str(mention.id)
                                )
                            else:
                                logger.error(
                                    f"Failed to reply to mention {mention.id}"
                                )
                        else:
                            logger.warning(
                                f"Empty response generated for mention {mention.id}"
                            )

                except Exception as e:
                    logger.error(
                        f"Error processing mention {mention.id}: {str(e)}",
                        exc_info=True,
                    )

        except Exception:
            logger.error("Error in handle_mentions", exc_info=True)

    def handle_dms(self) -> None:
        """Process and respond to new DMs."""
        messages = self.api.get_dms()
        if not messages:
            return

        for message in messages:
            message_id = message.id
            if message_id not in self.processed_dms:
                text = message.message_create["message_data"]["text"]
                sender_id = message.message_create["sender_id"]
                response = self.response_callback(text)
                self.api.send_dm(sender_id, response)
                self.processed_dms.add(message_id)


def twitter_agent(
    action: Union[str, TwitterAction],
    message: str,
    target_id: str,
    **kwargs,
) -> bool:
    """Simple wrapper function for Twitter actions."""
    try:
        logger.info(f"Attempting to perform Twitter action: {action}")
        if isinstance(action, str):
            logger.info(
                f"Converting action string to TwitterAction: {action}"
            )
            action = TwitterAction(action)

        api = TwitterAPI()
        logger.info("TwitterAPI instance created successfully")

        if action == TwitterAction.REPLY:
            logger.info(
                f"Sending reply to tweet with ID: {target_id}"
            )
            return api.reply_to_tweet(target_id, message)
        elif action == TwitterAction.DM:
            logger.info(f"Sending DM to user with ID: {target_id}")
            return api.send_dm(target_id, message)
        else:
            logger.error(f"Unknown action: {action}")
            return False

    except Exception as e:
        logger.error(f"Error in twitter_agent wrapper: {str(e)}")
        return False
