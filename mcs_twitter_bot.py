import os
import time
from dotenv import load_dotenv
from loguru import logger
import tweepy
from swarm_models import OpenAIChat
from swarms import Agent
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Verify environment variables are present
required_vars = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
    "OPENAI_API_KEY",
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f"Missing required environment variables: {missing_vars}"
    )

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    "medical_coding_bot.log",
    rotation="1 day",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
logger.add(
    lambda msg: print(msg), level="INFO"
)  # Also log to console


class MedicalCodingBot:
    def __init__(self):
        """Initialize the bot with Twitter and OpenAI credentials."""
        try:
            logger.debug("Initializing Twitter client...")
            # Initialize Twitter client
            self.client = tweepy.Client(
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv(
                    "TWITTER_ACCESS_TOKEN_SECRET"
                ),
                wait_on_rate_limit=True,
            )

            # Test Twitter authentication
            logger.debug("Testing Twitter authentication...")
            self.me = self.client.get_me()
            if not self.me or not self.me.data:
                raise ValueError("Failed to get Twitter user details")
            logger.info(
                f"Twitter initialized for @{self.me.data.username}"
            )

            # Initialize OpenAI
            logger.debug("Initializing OpenAI...")
            self.model = OpenAIChat(
                model_name="gpt-4",
                max_tokens=3000,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

            # Test OpenAI
            logger.debug("Testing OpenAI connection...")
            test_message = HumanMessage(content="Test message")
            test_response = self.model.invoke([test_message])
            if not test_response:
                raise ValueError("Failed to get response from OpenAI")
            logger.debug("OpenAI test successful")

            # Initialize Medical Coder
            logger.debug("Initializing Medical Coder agent...")
            self.medical_coder = Agent(
                agent_name="Medical Coder",
                system_prompt="""You are a medical coding expert. When asked about medical conditions, provide:
                1. The most relevant ICD-10 code
                2. A brief description (1-2 sentences)
                Keep total response under 280 characters.""",
                llm=self.model,
                max_loops=1,
            )

            self.last_mention_time = None
            logger.info("Medical Coding Bot initialized successfully")

        except Exception:
            logger.error("Initialization failed", exc_info=True)
            raise

    def clean_message(self, text: str) -> str:
        """Remove mentions and clean the message."""
        words = text.split()
        clean_words = [
            word for word in words if not word.startswith("@")
        ]
        return " ".join(clean_words).strip()

    def check_mentions(self):
        """Check and respond to mentions."""
        try:
            logger.info("Checking mentions...")
            mentions = self.client.get_users_mentions(
                self.me.data.id,
                tweet_fields=["created_at", "text"],
                max_results=10,
            )

            if not mentions.data:
                logger.debug("No mentions found")
                return

            logger.info(f"Found {len(mentions.data)} mentions")
            for mention in mentions.data:
                try:
                    # Skip if we've already processed this mention
                    if (
                        self.last_mention_time
                        and mention.created_at
                        <= self.last_mention_time
                    ):
                        logger.debug(
                            f"Skipping already processed mention {mention.id}"
                        )
                        continue

                    logger.info(
                        f"Processing mention {mention.id}: {mention.text}"
                    )

                    # Clean the message
                    clean_text = self.clean_message(mention.text)
                    logger.debug(f"Cleaned text: {clean_text}")

                    if not clean_text:
                        logger.debug(
                            "Skipping empty message after cleaning"
                        )
                        continue

                    # Generate response
                    logger.debug("Generating response...")
                    response = self.medical_coder.run(clean_text)
                    logger.debug(f"Generated response: {response}")

                    if not response:
                        logger.warning(
                            "Empty response from medical coder"
                        )
                        continue

                    # Ensure response isn't too long
                    if len(response) > 280:
                        response = response[:277] + "..."

                    # Reply to tweet
                    logger.debug(f"Sending reply to {mention.id}")
                    self.client.create_tweet(
                        text=response, in_reply_to_tweet_id=mention.id
                    )
                    logger.info(
                        f"Successfully replied to mention {mention.id}"
                    )

                    self.last_mention_time = mention.created_at

                except Exception:
                    logger.error(
                        f"Error processing mention {mention.id}",
                        exc_info=True,
                    )
                    continue

        except Exception:
            logger.error("Error checking mentions", exc_info=True)

    def run(self):
        """Run the bot continuously."""
        logger.info("Starting bot...")
        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"Starting iteration {iteration}")
                self.check_mentions()
                logger.info(
                    f"Completed iteration {iteration}, sleeping for 60 seconds"
                )
                time.sleep(60)  # Check every minute
            except Exception:
                logger.error(
                    f"Error in iteration {iteration}", exc_info=True
                )
                time.sleep(60)  # Wait before retrying


if __name__ == "__main__":
    try:
        logger.info("Starting Medical Coding Bot")
        bot = MedicalCodingBot()
        bot.run()
    except Exception:
        logger.critical("Fatal error occurred", exc_info=True)
        raise
