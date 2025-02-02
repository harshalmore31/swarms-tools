import os
import time

from swarm_models import OpenAIChat
from swarms import Agent
from dotenv import load_dotenv

from swarms_tools.social_media.twitter_tool import TwitterTool

load_dotenv()

model_name = "gpt-4o"

model = OpenAIChat(
    model_name=model_name,
    max_tokens=3000,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


treatment_agent = Agent(
    agent_name="Medical Treatment Expert",
    system_prompt="""
    You are a highly experienced medical doctor with expertise in evidence-based treatments, pharmaceuticals, and clinical therapeutics. Your primary focus is to provide comprehensive, safe, and effective treatment plans for patients. You do not offer official diagnoses or medical advice; rather, you provide educational information. Always advise users to consult a healthcare professional for personalized guidance.

    ### Primary Responsibilities:
    1. **Focus on Treatments**: Recommend the most appropriate treatments (medications, therapies, procedures) based on standard clinical guidelines and the latest medical evidence.
    2. **Detail Therapeutic Approaches**: Explain how each treatment works, typical usage, dosage ranges (if relevant), expected outcomes, and any potential side effects or contraindications.
    3. **Integrate Holistic Care**: When appropriate, discuss lifestyle modifications, rehabilitation, adjunct therapies, or preventive measures that support overall well-being.
    4. **Provide Clear Explanations**: Use lay-friendly language whenever possible, but maintain clinical accuracy and detail.

    ### Formatting and Clarity:
    - Present treatment recommendations in a structured, easy-to-follow manner.
    - Where applicable, cite brief references to reputable guidelines or organizations (e.g., WHO, CDC, NICE, etc.).
    - Include any necessary cautionary notes about drug interactions, special populations (e.g., pregnant women, children, elderly), and the importance of personalized medical care.

    ### Important Disclaimer:
    - Your responses are for general educational purposes only and do not replace professional medical consultation.
    - Always advise the user to consult a qualified healthcare provider for personalized treatment.
    """,
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)


# Define your options with the necessary credentials
options = {
    "id": "mcsswarm",
    "name": "mcsswarm",
    "description": "An example Twitter Plugin for testing.",
    "credentials": {
        "apiKey": os.getenv("TWITTER_API_KEY"),
        "apiSecretKey": os.getenv("TWITTER_API_SECRET_KEY"),
        "accessToken": os.getenv("TWITTER_ACCESS_TOKEN"),
        "accessTokenSecret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    },
}

# Initialize the TwitterTool with your options
twitter_plugin = TwitterTool(options)

# Assuming `twitter_plugin` and `medical_coder` are already initialized
post_tweet = twitter_plugin.get_function("post_tweet")

# Set to track posted tweets and avoid duplicates
posted_tweets = set()


def post_unique_tweet():
    """
    Generate and post a unique tweet. Skip duplicates.
    """
    tweet_prompt = (
        "Craft a concise and engaging tweet about a specific disease and various treatment options for that disease using traditional medicine without invasive measures."
        "Be very direct and to the point, but also engaging and interesting. Aim to provide maximum value "
        "Focus on one disease and its corresponding treatment per tweet."
        "Keep it informative, yet brief and captivating."
    )

    # Generate a new tweet text
    tweet_text = treatment_agent.run(tweet_prompt)

    # Check for duplicates
    if tweet_text in posted_tweets:
        print("Duplicate tweet detected. Skipping...")
        return

    # Post the tweet
    try:
        post_tweet(tweet_text)
        print(f"Posted tweet: {tweet_text}")
        # Add the tweet to the set of posted tweets
        posted_tweets.add(tweet_text)
    except Exception as e:
        print(f"Error posting tweet: {e}")


# Loop to post tweets every 10 seconds
def start_tweet_loop(interval: int = 10):
    """
    Continuously post tweets every `interval` seconds.

    Args:
        interval (int): Time in seconds between tweets.
    """
    print("Starting tweet loop...")
    while True:
        post_unique_tweet()
        time.sleep(interval)


# Start the loop
start_tweet_loop(200)
