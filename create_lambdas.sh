#!/bin/bash

# Create Lambda functions from existing ECR images
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

AWS_REGION=${AWS_REGION:-us-east-1}
ECR_BASE="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "Creating Lambda functions..."

# Function 1: Query Server
echo "Creating mcp-query-server..."
aws lambda create-function \
    --function-name mcp-query-server \
    --package-type Image \
    --code ImageUri=${ECR_BASE}/mcp-query-server:latest \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/mcp-query-server-role \
    --timeout 30 \
    --memory-size 512 \
    --architectures arm64 \
    --region ${AWS_REGION} || echo "Function may already exist"

aws lambda create-function-url-config \
    --function-name mcp-query-server \
    --auth-type NONE \
    --region ${AWS_REGION} || echo "URL may already exist"

aws lambda add-permission \
    --function-name mcp-query-server \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region ${AWS_REGION} || echo "Permission may already exist"

# Function 2: Evaluation Server
echo "Creating mcp-evaluation-server..."
aws lambda create-function \
    --function-name mcp-evaluation-server \
    --package-type Image \
    --code ImageUri=${ECR_BASE}/mcp-evaluation-server:latest \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/mcp-evaluation-server-role \
    --timeout 30 \
    --memory-size 512 \
    --architectures arm64 \
    --environment "Variables={AWS_REGION=${AWS_REGION},BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID}}" \
    --region ${AWS_REGION} || echo "Function may already exist"

aws lambda create-function-url-config \
    --function-name mcp-evaluation-server \
    --auth-type NONE \
    --region ${AWS_REGION} || echo "URL may already exist"

aws lambda add-permission \
    --function-name mcp-evaluation-server \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region ${AWS_REGION} || echo "Permission may already exist"

# Function 3: GitHub Server  
echo "Creating mcp-github-server..."
aws lambda create-function \
    --function-name mcp-github-server \
    --package-type Image \
    --code ImageUri=${ECR_BASE}/mcp-github-server:latest \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/mcp-github-server-role \
    --timeout 30 \
    --memory-size 512 \
    --architectures arm64 \
    --environment "Variables={GITHUB_TOKEN=${GITHUB_TOKEN},GITHUB_REPO=${GITHUB_REPO}}" \
    --region ${AWS_REGION} || echo "Function may already exist"

aws lambda create-function-url-config \
    --function-name mcp-github-server \
    --auth-type NONE \
    --region ${AWS_REGION} || echo "URL may already exist"

aws lambda add-permission \
    --function-name mcp-github-server \
    --statement-id FunctionURLAllowPublicAccess \
    --action lambda:InvokeFunctionUrl \
    --principal "*" \
    --function-url-auth-type NONE \
    --region ${AWS_REGION} || echo "Permission may already exist"

# Get URLs
echo ""
echo "Function URLs:"
echo "Query Server: $(aws lambda get-function-url-config --function-name mcp-query-server --region ${AWS_REGION} --query 'FunctionUrl' --output text)"
echo "Evaluation Server: $(aws lambda get-function-url-config --function-name mcp-evaluation-server --region ${AWS_REGION} --query 'FunctionUrl' --output text)"
echo "GitHub Server: $(aws lambda get-function-url-config --function-name mcp-github-server --region ${AWS_REGION} --query 'FunctionUrl' --output text)"
