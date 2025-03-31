#!/bin/bash
# Test script for the Content Creation API

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Content Creation API${NC}"
echo -e "${YELLOW}=========================${NC}"

# Start the API server if it's not already running
if ! pgrep -f "python api.py" > /dev/null; then
    echo -e "${YELLOW}Starting API server...${NC}"
    python api.py &
    API_PID=$!
    echo -e "${GREEN}API server started with PID: $API_PID${NC}"
    # Wait for server to start
    sleep 5
fi

# Create a new content workflow
echo -e "\n${YELLOW}Creating new content workflow...${NC}"
CREATE_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "topic": "desk organization tips",
        "content_type": "blog post",
        "tone": "helpful",
        "word_count": 500,
        "brand_voice": {
            "tone": "Friendly but professional",
            "style": "Direct and practical",
            "sentence_structure": "Mix of short and long sentences with active voice",
            "language": "Accessible to general audience",
            "taboo_words": ["obviously", "simply", "just", "clearly"],
            "persuasion": "Focus on benefits rather than features",
            "format": "Use headers and bullet points for scannability"
        }
    }' \
    http://localhost:8000/api/v1/content)

echo -e "${GREEN}Response: $CREATE_RESPONSE${NC}"

# Extract workflow ID
WORKFLOW_ID=$(echo $CREATE_RESPONSE | grep -o '"workflow_id":"[^"]*' | sed 's/"workflow_id":"//')

if [ -z "$WORKFLOW_ID" ]; then
    echo -e "${RED}Failed to extract workflow ID${NC}"
    exit 1
fi

echo -e "${GREEN}Workflow ID: $WORKFLOW_ID${NC}"

# Monitor workflow status
echo -e "\n${YELLOW}Monitoring workflow status...${NC}"
STATUS="pending"

while [ "$STATUS" == "pending" ] || [ "$STATUS" == "running" ]; do
    RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/workflows/$WORKFLOW_ID)
    STATUS=$(echo $RESPONSE | grep -o '"status":"[^"]*' | sed 's/"status":"//')
    echo -e "${YELLOW}Current status: $STATUS${NC}"
    
    if [ "$STATUS" != "pending" ] && [ "$STATUS" != "running" ]; then
        break
    fi
    
    echo -e "${YELLOW}Waiting 10 seconds...${NC}"
    sleep 10
done

# Get final results
echo -e "\n${YELLOW}Final workflow results:${NC}"
FINAL_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/workflows/$WORKFLOW_ID)
echo $FINAL_RESPONSE | python -m json.tool

# Save the result to a file
echo $FINAL_RESPONSE | python -m json.tool > "api_test_result_$WORKFLOW_ID.json"
echo -e "${GREEN}Results saved to api_test_result_$WORKFLOW_ID.json${NC}"

# Clean up
if [ ! -z "$API_PID" ]; then
    echo -e "\n${YELLOW}Stopping API server...${NC}"
    kill $API_PID
    echo -e "${GREEN}API server stopped${NC}"
fi

echo -e "\n${GREEN}Test completed${NC}" 