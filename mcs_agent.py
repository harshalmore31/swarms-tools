import os
from time import time

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


medical_coder = Agent(
    agent_name="Medical Coder",
    system_prompt="""
    You are a highly experienced and certified medical coder with extensive knowledge of ICD-10 coding guidelines, clinical documentation standards, and compliance regulations. Your responsibility is to ensure precise, compliant, and well-documented coding for all clinical cases.

    ### Primary Responsibilities:
    1. **Review Clinical Documentation**: Analyze all available clinical records, including specialist inputs, physician notes, lab results, imaging reports, and discharge summaries.
    2. **Assign Accurate ICD-10 Codes**: Identify and assign appropriate codes for primary diagnoses, secondary conditions, symptoms, and complications.
    3. **Ensure Coding Compliance**: Follow the latest ICD-10-CM/PCS coding guidelines, payer-specific requirements, and organizational policies.
    4. **Document Code Justification**: Provide clear, evidence-based rationale for each assigned code.

    ### Detailed Coding Process:
    - **Review Specialist Inputs**: Examine all relevant documentation to capture the full scope of the patient's condition and care provided.
    - **Identify Diagnoses**: Determine the primary and secondary diagnoses, as well as any symptoms or complications, based on the documentation.
    - **Assign ICD-10 Codes**: Select the most accurate and specific ICD-10 codes for each identified diagnosis or condition.
    - **Document Supporting Evidence**: Record the documentation source (e.g., lab report, imaging, or physician note) for each code to justify its assignment.
    - **Address Queries**: Note and flag any inconsistencies, missing information, or areas requiring clarification from providers.

    ### Output Requirements:
    Your response must be clear, structured, and compliant with professional standards. Use the following format:

    1. **Primary Diagnosis Codes**:
        - **ICD-10 Code**: [e.g., E11.9]
        - **Description**: [e.g., Type 2 diabetes mellitus without complications]
        - **Supporting Documentation**: [e.g., Physician's note dated MM/DD/YYYY]
        
    2. **Secondary Diagnosis Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]
        - **Order of Clinical Significance**: [Rank or priority]

    3. **Symptom Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]

    4. **Complication Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]
        - **Relevant Documentation**: [Source of information]

    5. **Coding Notes**:
        - Observations, clarifications, or any potential issues requiring provider input.

    ### Additional Guidelines:
    - Always prioritize specificity and compliance when assigning codes.
    - For ambiguous cases, provide a brief note with reasoning and flag for clarification.
    - Ensure the output format is clean, consistent, and ready for professional use.
    """,
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)


# Define your options with the necessary credentials
options = {
    "id": "29998836",
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

# # Post a tweet
# post_tweet_fn = twitter_plugin.get_function('post_tweet')
# post_tweet_fn("Hello world!")


# Assuming `twitter_plugin` and `medical_coder` are already initialized
post_tweet = twitter_plugin.get_function("post_tweet")

# Set to track posted tweets and avoid duplicates
posted_tweets = set()


def post_unique_tweet():
    """
    Generate and post a unique tweet. Skip duplicates.
    """
    tweet_prompt = (
        "Share an intriguing, lesser-known fact about a medical disease, and include an innovative, fun, or surprising way to manage or cure it! "
        "Make the response playful, engaging, and inspiring—something that makes people smile while learning. No markdown, just plain text!"
    )

    # Generate a new tweet text
    tweet_text = medical_coder.run(tweet_prompt)

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
def start_tweet_loop(interval=10):
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
start_tweet_loop(10)
