#!/usr/bin/env python3
"""
Run the SEO Agent API server
"""

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    uvicorn.run("api.base:app", host="0.0.0.0", port=8000, reload=True) 