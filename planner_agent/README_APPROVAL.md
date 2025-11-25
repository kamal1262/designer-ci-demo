# Human Approval Workflow for Planner Agent

This extension to the MCP Server Demo project adds a human approval workflow for critical operations. The system allows non-technical users to request changes through natural language while requiring technical approval before those changes are committed.

## Overview

The approval workflow consists of three main components:

1. **ApprovalStore**: A simple file-based storage system for approval requests
2. **PlannerAgentWithApproval**: An enhanced version of the planner agent that requires approvals for critical operations
3. **ApprovalCLI**: A command-line tool for reviewing, approving, or rejecting pending requests

## How It Works

1. When the agent determines that a PR creation is needed (e.g., low evaluation scores or explicit request):
   - Instead of creating the PR directly, it creates an approval request
   - The request is stored in a JSON file with a unique ID
   - The agent returns a message indicating that approval is required

2. A human approver can then:
   - View pending approval requests
   - Examine the details of each request
   - Approve or reject requests with optional notes

3. The next time the agent runs:
   - It checks for any approved requests that haven't been processed
   - If found, it executes the approved actions
   - The requests are marked as processed to prevent duplicate execution

## Using the Approval Workflow

### Running the Agent with Approval

```bash
cd planner_agent
python planner_agent_with_approval.py --goal "Review last 5 conversations and update prompt if needed"
```

Options:
- `--goal TEXT`: The natural language goal to execute
- `--debug`: Enable debug mode for verbose output
- `--prompt TEXT`: Custom prompt text for PR creation
- `--prompt-file PATH`: Path to file containing custom prompt text
- `--no-approval`: Skip approval for actions (not recommended for production)

### Using the Approval CLI

View pending requests:
```bash
cd planner_agent
python approve_action.py --list
```

Approve a request:
```bash
python approve_action.py --approve REQUEST_ID --notes "Looks good to me"
```

Reject a request:
```bash
python approve_action.py --reject REQUEST_ID --notes "Please revise the prompt"
```

Show request details:
```bash
python approve_action.py --show REQUEST_ID
```

## Example Workflow

### Step 1: User requests to review conversations and update prompt

```bash
python planner_agent_with_approval.py --goal "Review last 5 conversations and create PR if score is below 3.5"
```

Output:
```
✓ Retrieved 5 conversations

📊 Evaluating 5 responses...
  Evaluating [conv_006]... Score: 2/5
  Evaluating [conv_007]... Score: 5/5
  Evaluating [conv_008]... Score: 4/5
  Evaluating [conv_009]... Score: 5/5
  Evaluating [conv_010]... Score: 2/5

📊 Evaluation Results:
Average score: 3.6/5

[conv_006] Score: 2/5
Comment: The response is extremely brief and lacks detail...

[conv_007] Score: 5/5
Comment: Excellent response that provides a comprehensive explanation...

...

🚀 Creating PR (avg score: 3.6)...
Using custom prompt (428 characters)

⏳ PR creation requires approval (ID: req_1732693428_a1b2c3)
Reason: Automated prompt update based on evaluation. Average score: 3.6/5. 2 conversations scored below 3.
Run `python approve_action.py --approve req_1732693428_a1b2c3` to approve
```

### Step 2: Approver reviews pending requests

```bash
python approve_action.py
```

Output:
```
Found 1 pending approval requests:

1. Request ID: req_1732693428_a1b2c3
   Action: submit_prompt_update
   Reason: Automated prompt update based on evaluation. Average score: 3.6/5. 2 conversations scored below 3.
   Prompt: You are a helpful AI assistant focused on providing...
   Created: 2025-11-25T08:10:28.123456
```

### Step 3: Approver examines the request details

```bash
python approve_action.py --show req_1732693428_a1b2c3
```

Output:
```
Request ID: req_1732693428_a1b2c3
Status: pending
Action: submit_prompt_update
Reason: Automated prompt update based on evaluation. Average score: 3.6/5. 2 conversations scored below 3.

Prompt Text:
------------------------------------------------------------
You are a helpful AI assistant focused on providing accurate, complete, and clear responses.

Guidelines:
- Provide comprehensive answers that fully address the user's question
- Use clear, easy-to-understand language
- Include relevant examples when helpful
- Be accurate and factual
- Structure responses logically
- Anticipate follow-up questions

Always aim to be helpful, informative, and user-friendly.
------------------------------------------------------------

Created: 2025-11-25T08:10:28.123456
```

### Step 4: Approver approves the request

```bash
python approve_action.py --approve req_1732693428_a1b2c3 --notes "Looks good, this should improve responses to technical questions"
```

Output:
```
✓ Request req_1732693428_a1b2c3 approved successfully.
  - Action: submit_prompt_update
  - Notes: Looks good, this should improve responses to technical questions

The approved action will be executed the next time the agent runs.
```

### Step 5: Agent runs again and executes the approved action

```bash
python planner_agent_with_approval.py --goal "Get last 3 conversations"
```

Output:
```
✓ Created PR from approved request req_1732693428_a1b2c3: https://github.com/username/repo/pull/123

✓ Retrieved 3 conversations
...
```

## Extending the Approval System

This approval system is designed to be simple and file-based for demonstration purposes. For production use, consider these enhancements:

1. **Database Storage**: Replace file-based storage with a database (e.g., DynamoDB, MongoDB)
2. **Web Interface**: Create a simple web UI for approvers to review and manage requests
3. **Notifications**: Add email or Slack notifications when requests are pending or processed
4. **Multi-Level Approval**: Implement approval workflows requiring sign-off from multiple approvers
5. **Audit Logging**: Add comprehensive logging for all approval actions

## File Structure

```
planner_agent/
├── approval_store.py           # File-based storage for approval requests
├── planner_agent_with_approval.py  # Enhanced agent with approval workflow
└── approve_action.py           # CLI tool for managing approval requests
