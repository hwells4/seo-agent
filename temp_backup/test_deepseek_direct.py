#!/usr/bin/env python3
"""
Direct test for DeepSeek API using their recommended approach
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get the API key from environment
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

if not deepseek_api_key:
    print("ERROR: DEEPSEEK_API_KEY not found in environment variables")
    exit(1)

print(f"Using DeepSeek API key: {deepseek_api_key}")

try:
    # Initialize client with DeepSeek's recommended approach
    client = OpenAI(
        api_key=deepseek_api_key, 
        base_url="https://api.deepseek.com"
    )

    # Make a simple request
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Create a content brief for a blog post about 'desk organization tips'"},
        ],
        stream=False
    )

    # Print the response
    print("\nDeepSeek Response:")
    print(response.choices[0].message.content)
    print("\nTest successful!")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\nCheck if your API key is correctly formatted and valid.")
    print("Also check if the base_url 'https://api.deepseek.com' is correct.") 