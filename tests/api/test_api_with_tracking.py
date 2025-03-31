#!/usr/bin/env python3
"""
Test script to verify API functionality with token tracking
"""

import os
import sys
import logging
import json
import requests
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_tracking_test")

# Add the parent directory to the path to import agents modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

# Ensure test_storage directory exists
os.makedirs("test_storage", exist_ok=True)

def start_api_server():
    """Start the API server in the background"""
    import subprocess
    import time
    
    logger.info("Starting API server...")
    
    # Start the server in the background
    server_process = subprocess.Popen(
        ["python3", "run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(5)
    
    logger.info("API server started")
    return server_process

def test_api_endpoint():
    """Test the API endpoint with token tracking"""
    
    api_url = "http://localhost:8000/api/v1/content"
    
    # Test data
    test_data = {
        "topic": "productivity tips for remote work",
        "content_type": "blog post",
        "tone": "informative",
        "word_count": 200  # Keep it short for quick testing
    }
    
    try:
        # Send the request
        logger.info(f"Sending request to {api_url} with data: {test_data}")
        response = requests.post(api_url, json=test_data)
        
        # Check response
        if response.status_code == 200:
            initial_response = response.json()
            workflow_id = initial_response["workflow_id"]
            logger.info(f"Content creation started with workflow ID: {workflow_id}")
            
            # Wait for workflow to complete
            max_retries = 20  # Maximum number of retries
            retry_interval = 10  # Seconds between retries
            
            workflow_status_url = f"http://localhost:8000/api/v1/workflows/{workflow_id}"
            
            for attempt in range(max_retries):
                logger.info(f"Checking workflow status (attempt {attempt+1}/{max_retries})...")
                
                status_response = requests.get(workflow_status_url)
                if status_response.status_code == 200:
                    workflow_data = status_response.json()
                    
                    if workflow_data["status"] == "completed":
                        logger.info("Workflow completed successfully")
                        
                        # Save the complete response data
                        timestamp = os.path.basename(__file__).replace('.py', '')
                        
                        # Ensure test_storage directory exists
                        os.makedirs("test_storage", exist_ok=True)
                        
                        api_result_file = f"test_storage/api_response_{timestamp}.json"
                        
                        with open(api_result_file, "w") as f:
                            json.dump(workflow_data, f, indent=2)
                        logger.info(f"API response saved to {api_result_file}")
                        
                        # If token usage is included, save it separately
                        if "token_usage" in workflow_data:
                            token_usage_file = f"test_storage/api_token_usage_{timestamp}.json"
                            with open(token_usage_file, "w") as f:
                                json.dump(workflow_data["token_usage"], f, indent=2)
                            logger.info(f"Token usage saved to {token_usage_file}")
                            
                            # Save content output for easier review
                            if "steps" in workflow_data and "content" in workflow_data["steps"]:
                                content_file = f"test_storage/api_content_{timestamp}.md"
                                with open(content_file, "w") as f:
                                    f.write(workflow_data["steps"]["content"]["output"])
                                logger.info(f"Content output saved to {content_file}")
                        
                            logger.info("Token tracking data is included in the response")
                            return True, workflow_data
                        else:
                            logger.error("Token tracking data is not included in the response")
                            return False, workflow_data
                    elif workflow_data["status"] == "failed":
                        logger.error(f"Workflow failed: {workflow_data.get('error', 'No error message')}")
                        return False, workflow_data
                    
                    else:
                        logger.info(f"Workflow status: {workflow_data['status']}")
                        time.sleep(retry_interval)
                else:
                    logger.error(f"Error checking workflow status: {status_response.status_code}")
                    time.sleep(retry_interval)
            
            logger.error(f"Workflow did not complete within the timeout period")
            return False, {"error": "Workflow timeout"}
        else:
            error_file = f"test_storage/api_error_{timestamp}.txt"
            with open(error_file, "w") as f:
                f.write(f"Status code: {response.status_code}\n\n")
                f.write(f"Response: {response.text}")
            logger.error(f"API request failed with status code {response.status_code}")
            logger.error(f"Error details saved to {error_file}")
            return False, None
    
    except Exception as e:
        logger.error(f"Error testing API endpoint: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(error_trace)
        
        # Save error details
        error_file = f"test_storage/api_exception_{timestamp}.txt"
        with open(error_file, "w") as f:
            f.write(f"Exception: {str(e)}\n\n")
            f.write(error_trace)
        logger.error(f"Exception details saved to {error_file}")
        
        return False, None

def main():
    """Main function to run the API test with token tracking"""
    import datetime
    
    logger.info("Starting API tracking test")
    timestamp = os.path.basename(__file__).replace('.py', '')
    
    # Start API server
    server_process = start_api_server()
    
    try:
        # Test API endpoint
        success, response_data = test_api_endpoint()
        
        # Create summary report
        summary = {
            "timestamp": str(datetime.datetime.now()),
            "success": success,
            "has_token_tracking": success and response_data and "token_usage" in response_data
        }
        
        if success and response_data and "token_usage" in response_data:
            # Check if the token usage data is in the expected format
            if "usage" in response_data["token_usage"] and "total" in response_data["token_usage"]["usage"]:
                total_usage = response_data["token_usage"]["usage"]["total"]
                
                summary["total_tokens"] = (
                    total_usage["input_tokens"] + 
                    total_usage["output_tokens"]
                )
                summary["total_cost"] = total_usage["cost"]
            else:
                # Handle alternative format if needed
                logger.warning("Token usage data is in an unexpected format")
                summary["token_usage_format"] = "unexpected"
        
        # Save summary report
        summary_file = f"test_storage/api_test_summary_{timestamp}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Test summary saved to {summary_file}")
        
        # Print results
        if success and "has_token_tracking" in summary and summary["has_token_tracking"]:
            logger.info("API tracking test completed successfully")
            print("\n===== API TRACKING TEST =====")
            print("SUCCESS: API endpoint works with token tracking enabled")
            if "total_tokens" in summary:
                print(f"Total tokens: {summary['total_tokens']:,}")
                print(f"Total cost: ${summary['total_cost']:.4f}")
            print("=============================\n")
            return 0
        else:
            logger.error("API tracking test failed")
            print("\n===== API TRACKING TEST =====")
            print("FAILED: API endpoint does not work with token tracking")
            print("=============================\n")
            return 1
    
    finally:
        # Stop API server
        if server_process:
            logger.info("Stopping API server...")
            server_process.terminate()
            stdout, stderr = server_process.communicate()
            
            # Save server logs
            logs_file = f"test_storage/api_server_logs_{timestamp}.txt"
            with open(logs_file, "w") as f:
                f.write("=== STDOUT ===\n")
                f.write(stdout.decode() if stdout else "No output\n")
                f.write("\n=== STDERR ===\n")
                f.write(stderr.decode() if stderr else "No errors\n")
            
            if stdout:
                logger.info(f"Server stdout: {stdout.decode()}")
            if stderr:
                logger.error(f"Server stderr: {stderr.decode()}")
            logger.info(f"Server logs saved to {logs_file}")
            logger.info("API server stopped")

if __name__ == "__main__":
    sys.exit(main()) 