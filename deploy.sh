#!/bin/bash

# Deploy all MCP servers to AWS Lambda
# This script builds Docker images, pushes to ECR, and creates/updates Lambda functions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MCP Serverless AI Agent System Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Load environment variables
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Check required variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: AWS_ACCOUNT_ID not set in .env${NC}"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    AWS_REGION="us-east-1"
    echo -e "${YELLOW}Using default AWS_REGION: us-east-1${NC}"
fi

# ECR repository base URL
ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo -e "${YELLOW}AWS Account: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${YELLOW}AWS Region: ${AWS_REGION}${NC}"
echo ""

# Authenticate with ECR
echo -e "${YELLOW}Authenticating with ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_BASE}

# Function to create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    echo -e "${YELLOW}Checking ECR repository: ${repo_name}${NC}"
    
    if ! aws ecr describe-repositories --repository-names ${repo_name} --region ${AWS_REGION} 2>/dev/null; then
        echo -e "${YELLOW}Creating ECR repository: ${repo_name}${NC}"
        aws ecr create-repository \
            --repository-name ${repo_name} \
            --region ${AWS_REGION} \
            --image-scanning-configuration scanOnPush=true
    else
        echo -e "${GREEN}✓ Repository ${repo_name} already exists${NC}"
    fi
}

# Function to build and push Docker image
build_and_push() {
    local service_dir=$1
    local repo_name=$2
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Building ${repo_name}${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    cd ${service_dir}
    
    # Build image
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t ${repo_name}:latest .
    
    # Tag for ECR
    docker tag ${repo_name}:latest ${ECR_BASE}/${repo_name}:latest
    
    # Push to ECR
    echo -e "${YELLOW}Pushing to ECR...${NC}"
    docker push ${ECR_BASE}/${repo_name}:latest
    
    echo -e "${GREEN}✓ ${repo_name} built and pushed${NC}"
    
    cd ..
}

# Function to create or update Lambda function
deploy_lambda() {
    local function_name=$1
    local repo_name=$2
    local env_vars=$3
    
    echo ""
    echo -e "${YELLOW}Deploying Lambda function: ${function_name}${NC}"
    
    # Check if function exists
    if aws lambda get-function --function-name ${function_name} --region ${AWS_REGION} 2>/dev/null; then
        echo -e "${YELLOW}Updating existing function...${NC}"
        aws lambda update-function-code \
            --function-name ${function_name} \
            --image-uri ${ECR_BASE}/${repo_name}:latest \
            --region ${AWS_REGION}
        
        # Update environment variables if provided
        if [ ! -z "$env_vars" ]; then
            aws lambda update-function-configuration \
                --function-name ${function_name} \
                --environment "Variables={${env_vars}}" \
                --region ${AWS_REGION}
        fi
    else
        echo -e "${YELLOW}Creating new function...${NC}"
        
        # Create IAM role if it doesn't exist
        local role_name="${function_name}-role"
        if ! aws iam get-role --role-name ${role_name} 2>/dev/null; then
            echo -e "${YELLOW}Creating IAM role: ${role_name}${NC}"
            
            # Create trust policy
            cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
            
            aws iam create-role \
                --role-name ${role_name} \
                --assume-role-policy-document file:///tmp/trust-policy.json
            
            # Attach basic execution policy
            aws iam attach-role-policy \
                --role-name ${role_name} \
                --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
            
            # For evaluation server, add Bedrock permissions
            if [[ ${function_name} == *"evaluation"* ]]; then
                cat > /tmp/bedrock-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
EOF
                aws iam put-role-policy \
                    --role-name ${role_name} \
                    --policy-name bedrock-policy \
                    --policy-document file:///tmp/bedrock-policy.json
            fi
            
            # Wait for role to be available
            echo -e "${YELLOW}Waiting for IAM role to be ready...${NC}"
            sleep 10
        fi
        
        # Get role ARN
        local role_arn=$(aws iam get-role --role-name ${role_name} --query 'Role.Arn' --output text)
        
        # Create function
        local create_cmd="aws lambda create-function \
            --function-name ${function_name} \
            --package-type Image \
            --code ImageUri=${ECR_BASE}/${repo_name}:latest \
            --role ${role_arn} \
            --timeout 30 \
            --memory-size 512 \
            --architectures arm64 \
            --region ${AWS_REGION}"
        
        if [ ! -z "$env_vars" ]; then
            create_cmd="${create_cmd} --environment Variables=\\{${env_vars}\\}"
        fi
        
        eval "$create_cmd"
        
        # Create function URL
        echo -e "${YELLOW}Creating function URL...${NC}"
        aws lambda create-function-url-config \
            --function-name ${function_name} \
            --auth-type NONE \
            --region ${AWS_REGION}
        
        # Add permission for function URL
        aws lambda add-permission \
            --function-name ${function_name} \
            --statement-id FunctionURLAllowPublicAccess \
            --action lambda:InvokeFunctionUrl \
            --principal "*" \
            --function-url-auth-type NONE \
            --region ${AWS_REGION}
    fi
    
    # Get function URL
    local function_url=$(aws lambda get-function-url-config \
        --function-name ${function_name} \
        --region ${AWS_REGION} \
        --query 'FunctionUrl' \
        --output text)
    
    echo -e "${GREEN}✓ Function deployed: ${function_url}${NC}"
    echo ${function_url}
}

# Deploy MCP Server 1 - Query Conversations
create_ecr_repo "mcp-query-server"
build_and_push "mcp_query_server" "mcp-query-server"
QUERY_URL=$(deploy_lambda "mcp-query-server" "mcp-query-server" "")

# Deploy MCP Server 2 - Evaluation
create_ecr_repo "mcp-evaluation-server"
build_and_push "mcp_evaluation_server" "mcp-evaluation-server"
EVAL_URL=$(deploy_lambda "mcp-evaluation-server" "mcp-evaluation-server" "BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}")

# Deploy MCP Server 3 - GitHub PR
create_ecr_repo "mcp-github-server"
build_and_push "mcp_github_server" "mcp-github-server"
GITHUB_URL=$(deploy_lambda "mcp-github-server" "mcp-github-server" "GITHUB_TOKEN=${GITHUB_TOKEN},GITHUB_REPO=${GITHUB_REPO}")

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}MCP Server URLs:${NC}"
echo -e "Query Server:      ${QUERY_URL}"
echo -e "Evaluation Server: ${EVAL_URL}"
echo -e "GitHub Server:     ${GITHUB_URL}"
echo ""
echo -e "${YELLOW}Update your .env file with these URLs:${NC}"
echo "MCP_QUERY_URL=${QUERY_URL}"
echo "MCP_EVAL_URL=${EVAL_URL}"
echo "MCP_GITHUB_URL=${GITHUB_URL}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Update .env with the URLs above"
echo "2. Test the MCP servers with curl"
echo "3. Run the planner agent: cd planner_agent && python planner_agent.py"
echo ""
