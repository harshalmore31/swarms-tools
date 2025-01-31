import os
from typing import List
import requests


def search_exa_ai(
    query: str = "Latest developments in LLM capabilities",
    num_results: int = 10,
    auto_prompt: bool = True,
    include_domains: List[str] = ["arxiv.org", "paperswithcode.com"],
    exclude_domains: List[str] = [],
    category: str = "research paper",
) -> str:
    url = "https://api.exa.ai/search"
    payload = {
        "query": query,
        "useAutoprompt": auto_prompt,
        "type": "auto",
        "category": category,
        "numResults": num_results,
        "includeDomains": include_domains,
        "excludeDomains": exclude_domains,
    }
    headers = {
        "x-api-key": os.getenv("EXA_API_KEY"),
        "Content-Type": "application/json",
    }

    try:
        response = requests.request(
            "POST", url, json=payload, headers=headers
        )
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return "Failed to retrieve results due to an HTTP error."
    except Exception as err:
        print(f'Other error occurred: {err}')
        return "Failed to retrieve results due to an error."


# # Example usage
# query = "Latest developments in LLM capabilities"
# print(search_exa_ai(query))
