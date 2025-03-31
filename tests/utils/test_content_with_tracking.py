#!/usr/bin/env python3
"""
Test script to run the content pipeline with token tracking
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("content_tracking_test")

# Add the parent directory to the path to import agents modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the content pipeline
from agents.content.pipeline import run_content_pipeline

# Load environment variables
load_dotenv()

# Ensure test_storage directory exists
os.makedirs("test_storage", exist_ok=True)

def main():
    """Main function to run the content pipeline with token tracking"""
    
    # Simple brand voice configuration for testing
    brand_voice = {
        "tone": "Conversational and helpful",
        "style": "Informative but easy to understand",
        "sentence_structure": "Mix of short and medium sentences for readability",
        "language": "Accessible to general audience with minimal jargon",
        "taboo_words": ["obviously", "simply", "just", "clearly", "very"],
        "persuasion": "Use examples and evidence rather than hyperbole",
        "format": "Clear structure with headings and short paragraphs"
    }
    
    # Run the content pipeline with a simple test topic
    logger.info("Running content pipeline with token tracking")
    
    try:
        # Choose a simple topic that won't be too expensive to process
        topic = "home office organization tips"
        word_count = 300
        
        # Run the pipeline with token tracking and save results to test_storage
        timestamp = os.path.basename(__file__).replace('.py', '')
        results_file = f"test_storage/content_results_{timestamp}.json"
        token_usage_file = f"test_storage/token_usage_{timestamp}.json"
        
        results = run_content_pipeline(
            topic=topic,
            brand_voice=brand_voice,
            word_count=word_count,
            save_results=False  # We'll save results manually to the test_storage directory
        )
        
        # Save results to test_storage directory
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Content results saved to {results_file}")
        
        # Save token usage report separately
        with open(token_usage_file, "w") as f:
            json.dump(results["token_usage"], f, indent=2)
        logger.info(f"Token usage saved to {token_usage_file}")
        
        # Save just the content output for easier review
        content_file = f"test_storage/content_output_{timestamp}.md"
        with open(content_file, "w") as f:
            f.write(results["steps"]["content"]["output"])
        logger.info(f"Content output saved to {content_file}")
        
        logger.info(f"Content pipeline completed for topic: {topic}")
        
        # Print a summary
        print("\n===== CONTENT PIPELINE TEST RESULTS =====")
        print(f"Topic: {topic}")
        print(f"Word count: {word_count}")
        print(f"Total tokens: {results['token_usage']['usage']['total']['input_tokens'] + results['token_usage']['usage']['total']['output_tokens']:,}")
        print(f"Total cost: ${results['token_usage']['usage']['total']['cost']:.4f}")
        print("Results saved to:", results_file)
        print("Token usage saved to:", token_usage_file)
        print("Content output saved to:", content_file)
        print("==========================================\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error running content pipeline: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main()) 