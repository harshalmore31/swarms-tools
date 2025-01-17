import os
import time

from dotenv import load_dotenv
from loguru import logger
from swarm_models import OpenAIChat
from swarms import Agent

from swarms_tools.social_media.twitter_api import TwitterBot

load_dotenv()


def init_medical_coder() -> Agent:
    """Initialize the medical coding agent."""
    model = OpenAIChat(
        model_name="gpt-4",
        max_tokens=3000,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    return Agent(
        agent_name="Medical Coder",
        system_prompt="""
        You are a highly experienced and certified medical coder with extensive knowledge of ICD-10 coding guidelines, clinical documentation standards, and compliance regulations. Your responsibility is to ensure precise, compliant, and well-documented coding for all clinical cases.

        ### Primary Responsibilities:
        1. **Review Clinical Documentation**: Analyze all available clinical records, including specialist inputs, physician notes, lab results, imaging reports, and discharge summaries.
        2. **Assign Accurate ICD-10 Codes**: Identify and assign appropriate codes for primary diagnoses, secondary conditions, symptoms, and complications.
        3. **Ensure Coding Compliance**: Follow the latest ICD-10-CM/PCS coding guidelines, payer-specific requirements, and organizational policies.
        4. **Document Code Justification**: Provide clear, evidence-based rationale for each assigned code.

        ### Output Requirements:
        Provide a concise, Twitter-friendly response that includes:
        1. The most relevant ICD-10 codes
        2. Brief descriptions
        3. Key supporting evidence
        
        Keep responses under 280 characters when possible, split into threads if needed.
        """,
        llm=model,
        max_loops=1,
        dynamic_temperature_enabled=True,
    )


class MedicalCodingBot:
    """Twitter bot that provides medical coding assistance."""

    def __init__(self):
        self.medical_coder = init_medical_coder()
        self.twitter_bot = TwitterBot(
            response_callback=self.generate_response
        )
        logger.info("Medical Coding Bot initialized")

    def generate_response(self, message: str) -> str:
        """Generate a medical coding response."""
        try:
            # Remove mentions from the message to focus on the medical query
            clean_message = self.clean_message(message)

            # Get response from medical coder
            response = self.medical_coder.run(clean_message)

            # Ensure response fits Twitter's character limit
            return self.format_response(response)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def clean_message(self, message: str) -> str:
        """Remove Twitter mentions and clean up the message."""
        # Remove mentions (starting with @)
        words = message.split()
        clean_words = [
            word for word in words if not word.startswith("@")
        ]
        return " ".join(clean_words).strip()

    def format_response(self, response: str) -> str:
        """Format the response to fit Twitter's character limit."""
        if len(response) <= 280:
            return response

        # Split into multiple tweets if needed
        # For now, just truncate to fit
        return response[:277] + "..."

    def run(self, check_interval: int = 60):
        """Run the bot continuously."""
        logger.info("Starting Medical Coding Bot")

        while True:
            try:
                # Handle mentions
                self.twitter_bot.handle_mentions()

                # Handle DMs
                self.twitter_bot.handle_dms()

                # Wait before next check
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in bot loop: {str(e)}")
                time.sleep(check_interval)


if __name__ == "__main__":
    # Initialize and run the bot
    medical_bot = MedicalCodingBot()
    medical_bot.run()
