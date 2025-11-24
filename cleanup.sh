#!/bin/bash

# Cleanup script - removes all deployed resources
# WARNING: This will delete Lambda functions, ECR repositories, and IAM roles

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}========================================${NC}"
echo -e "${RED}MCP Serverless AI Agent System Cleanup${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}WARNING: This will delete all deployed resources!${NC}"
echo -e "${YELLOW}Press Ctrl+C to cancel, or Enter to continue...${NC}"
read

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${YELLOW}AWS Region: ${AWS_REGION}${NC}"
echo ""

# Function to delete Lambda function
delete_lambda() {
    local function_name=$1
    
    echo -e "${YELLOW}Deleting Lambda function: ${function_name}${NC}"
    
    if aws lambda get-function --function-name ${function_name} --region ${AWS_REGION} 2>/dev/null; then
        # Delete function URL config
        aws lambda delete-function-url-config \
            --function-name ${function_name} \
            --region ${AWS_REGION} 2>/dev/null || true
        
        # Delete function
        aws lambda delete-function \
            --function-name ${function_name} \
            --region ${AWS_REGION}
        
        echo -e "${GREEN}✓ Deleted function: ${function_name}${NC}"
    else
        echo -e "${YELLOW}Function ${function_name} not found${NC}"
    fi
}

# Function to delete IAM role
delete_iam_role() {
    local role_name=$1
    
    echo -e "${YELLOW}Deleting IAM role: ${role_name}${NC}"
    
    if aws iam get-role --role-name ${role_name} 2>/dev/null; then
        # Detach managed policies
        aws iam list-attached-role-policies --role-name ${role_name} \
            --query 'AttachedPolicies[].PolicyArn' --output text | \
            xargs -n1 aws iam detach-role-policy --role-name ${role_name} --policy-arn 2>/dev/null || true
        
        # Delete inline policies
        aws iam list-role-policies --role-name ${role_name} \
            --query 'PolicyNames' --output text | \
            xargs -n1 aws iam delete-role-policy --role-name ${role_name} --policy-name 2>/dev/null || true
        
        # Delete role
        aws iam delete-role --role-name ${role_name}
        
        echo -e "${GREEN}✓ Deleted role: ${role_name}${NC}"
    else
        echo -e "${YELLOW}Role ${role_name} not found${NC}"
    fi
}

# Function to delete ECR repository
delete_ecr_repo() {
    local repo_name=$1
    
    echo -e "${YELLOW}Deleting ECR repository: ${repo_name}${NC}"
    
    if aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} 2>/dev/null; then
        aws ecr delete-repository \
            --repository-name ${repo_name} \
            --force \
            --region ${AWS_REGION}
        
        echo -e "${GREEN}✓ Deleted repository: ${repo_name}${NC}"
    else
        echo -e "${YELLOW}Repository ${repo_name} not found${NC}"
    fi
}

# Delete Lambda functions
echo -e "${GREEN}Deleting Lambda functions...${NC}"
delete_lambda "mcp-query-server"
delete_lambda "mcp-evaluation-server"
delete_lambda "mcp-github-server"

echo ""

# Delete IAM roles
echo -e "${GREEN}Deleting IAM roles...${NC}"
delete_iam_role "mcp-query-server-role"
delete_iam_role "mcp-evaluation-server-role"
delete_iam_role "mcp-github-server-role"

echo ""

# Delete ECR repositories
echo -e "${GREEN}Deleting ECR repositories...${NC}"
delete_ecr_repo "mcp-query-server"
delete_ecr_repo "mcp-evaluation-server"
delete_ecr_repo "mcp-github-server"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}All resources have been deleted.${NC}"
echo ""
