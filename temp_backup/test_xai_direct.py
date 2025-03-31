#!/usr/bin/env python3
"""
Direct test for xAI/Grok API using OpenAI's client
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get the API key from environment
xai_api_key = os.getenv("XAI_API_KEY")

if not xai_api_key:
    print("ERROR: XAI_API_KEY not found in environment variables")
    exit(1)

print(f"Using xAI API key: {xai_api_key}")

try:
    # Initialize client with corrected base URL
    client = OpenAI(
        api_key=xai_api_key, 
        base_url="https://api.x.ai/v1"
    )

    # Make a simple request
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": "You are a helpful assistant with access to real-time internet information."},
            {"role": "user", "content": "What are the current trends in desk organization for 2024? Include statistics and recent products if available."},
        ],
        stream=False
    )

    # Print the response
    print("\nxAI/Grok Response:")
    print(response.choices[0].message.content)
    print("\nTest successful!")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nCheck if your API key is correctly formatted and valid.")
    print("Also check if the base_url 'https://api.x.ai/v1' is correct.") 