#!/bin/bash

# Local testing script for MCP servers
# Tests each Lambda function locally before deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MCP Servers Local Testing${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Test MCP Server 1 - Query Conversations
echo -e "${YELLOW}Testing MCP Server 1 - Query Conversations${NC}"
echo "-------------------------------------------"
cd mcp_query_server
python3 lambda_function.py
cd ..
echo ""

# Test MCP Server 2 - Evaluation (requires AWS credentials and Bedrock access)
echo -e "${YELLOW}Testing MCP Server 2 - Evaluation${NC}"
echo "-------------------------------------------"
if [ -n "$AWS_REGION" ] && [ -n "$BEDROCK_MODEL_ID" ]; then
    cd mcp_evaluation_server
    python3 lambda_function.py
    cd ..
else
    echo -e "${YELLOW}Note: This requires AWS credentials and Bedrock access${NC}"
    echo -e "${YELLOW}Skipping Bedrock test (AWS credentials not found)${NC}"
fi
echo ""

# Test MCP Server 3 - GitHub PR (requires GitHub token)
echo -e "${YELLOW}Testing MCP Server 3 - GitHub PR${NC}"
echo "-------------------------------------------"
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_REPO" ]; then
    cd mcp_github_server
    python3 lambda_function.py
    cd ..
else
    echo -e "${YELLOW}Note: This requires GITHUB_TOKEN environment variable${NC}"
    echo -e "${YELLOW}Skipping GitHub test (GitHub credentials not found)${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Local Testing Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Configure .env file with your credentials"
echo "2. Run ./deploy.sh to deploy to AWS"
echo "3. Test deployed functions with curl"
echo "4. Run planner agent: cd planner_agent && python planner_agent.py"
echo ""
