#!/bin/bash
# Test script for demonstrating the approval workflow

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Create directory for approval requests if it doesn't exist
mkdir -p ./approval_requests

# Function to press any key to continue
press_any_key() {
    echo ""
    echo -e "${YELLOW}Press any key to continue...${NC}"
    read -n 1 -s
    echo ""
}

clear
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Approval Workflow Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}This script will walk through the entire approval workflow:${NC}"
echo "1. Running the agent with a goal that requires approval"
echo "2. Viewing pending approval requests"
echo "3. Examining a specific approval request"
echo "4. Approving the request"
echo "5. Running the agent again to process the approved request"
echo ""
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Step 1: Running the agent with a goal that requires approval${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Command:${NC} python planner_agent_with_approval.py --goal \"Create PR with custom prompt\" --debug"
echo ""
echo -e "${YELLOW}Press any key to execute...${NC}"
read -n 1 -s
echo ""

# Step 1: Run the agent that will create an approval request
python planner_agent_with_approval.py --goal "Create PR with custom prompt" --debug

# Step 2: Extract the request ID from the output
REQUEST_ID=$(ls ./approval_requests | grep -m 1 "req_" | sed 's/\.json$//')

if [ -z "$REQUEST_ID" ]; then
    echo -e "${RED}Error: No approval request was created.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Request ID: ${REQUEST_ID}${NC}"
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Step 2: View pending approval requests${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Command:${NC} python approve_action.py --list"
echo ""
echo -e "${YELLOW}Press any key to execute...${NC}"
read -n 1 -s
echo ""

# List pending approval requests
python approve_action.py --list
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Step 3: Examine the specific request${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Command:${NC} python approve_action.py --show ${REQUEST_ID}"
echo ""
echo -e "${YELLOW}Press any key to execute...${NC}"
read -n 1 -s
echo ""

# Show the request details
python approve_action.py --show ${REQUEST_ID}
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Step 4: Approve the request${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Command:${NC} python approve_action.py --approve ${REQUEST_ID} --notes \"Approved for testing\""
echo ""
echo -e "${YELLOW}Press any key to execute...${NC}"
read -n 1 -s
echo ""

# Approve the request
python approve_action.py --approve ${REQUEST_ID} --notes "Approved for testing"
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Step 5: Run the agent again to process approved request${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Command:${NC} python planner_agent_with_approval.py --goal \"Get last 3 conversations\" --debug"
echo ""
echo -e "${YELLOW}Note:${NC} In a real scenario, this would create a GitHub PR"
echo -e "${YELLOW}      In our test environment, it will show an error since"
echo -e "${YELLOW}      we don't have valid GitHub credentials configured."
echo ""
echo -e "${YELLOW}Press any key to execute...${NC}"
read -n 1 -s
echo ""

# Run the agent again, which should process the approved request
python planner_agent_with_approval.py --goal "Get last 3 conversations" --debug
press_any_key

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Approval Workflow Test Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "This test demonstrated the complete approval workflow:"
echo "1. ✓ Agent created an approval request"
echo "2. ✓ Listed pending approval requests"
echo "3. ✓ Examined the request details"
echo "4. ✓ Approved the request"
echo "5. ✓ Agent processed the approved request"
echo ""
echo "You can now use these components in your own application:"
echo "- planner_agent_with_approval.py: Agent that requires approval for critical actions"
echo "- approve_action.py: Command-line tool for managing approvals"
echo "- approval_store.py: File-based storage for approval requests"
echo ""
