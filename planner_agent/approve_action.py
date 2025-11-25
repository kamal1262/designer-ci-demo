#!/usr/bin/env python3
"""
Approval CLI - Simple command-line tool for managing approval requests
"""
import argparse
import sys
import os
from typing import List, Dict, Any, Optional

from approval_store import ApprovalStore

def list_pending_approvals():
    """List all pending approval requests"""
    store = ApprovalStore()
    pending = store.get_pending_requests()
    
    if not pending:
        print("No pending approval requests.")
        return False
    
    print(f"Found {len(pending)} pending approval requests:\n")
    
    for i, req in enumerate(pending, 1):
        print(f"{i}. Request ID: {req.get('id', 'Unknown')}")
        print(f"   Action: {req.get('action', 'Unknown')}")
        
        if req.get('action') == 'submit_prompt_update':
            print(f"   Reason: {req.get('reason', 'None provided')}")
            prompt_text = req.get('prompt_text', '')
            if prompt_text:
                preview = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
                print(f"   Prompt: {preview}")
        
        print(f"   Created: {req.get('created_at', 'Unknown')}")
        print()
    
    return True

def approve_request(request_id: str, notes: Optional[str] = None):
    """Approve a request"""
    store = ApprovalStore()
    request = store.get_request(request_id)
    
    if not request:
        print(f"Error: Request ID '{request_id}' not found.")
        return False
    
    if request.get('status') != 'pending':
        print(f"Error: Request ID '{request_id}' is not pending (current status: {request.get('status')}).")
        return False
    
    result = store.update_request(request_id, "approved", notes)
    
    if result:
        print(f"✓ Request {request_id} approved successfully.")
        print(f"  - Action: {request.get('action', 'Unknown')}")
        if notes:
            print(f"  - Notes: {notes}")
        print("\nThe approved action will be executed the next time the agent runs.")
    else:
        print(f"❌ Failed to approve request {request_id}.")
    
    return result

def reject_request(request_id: str, notes: Optional[str] = None):
    """Reject a request"""
    store = ApprovalStore()
    request = store.get_request(request_id)
    
    if not request:
        print(f"Error: Request ID '{request_id}' not found.")
        return False
    
    if request.get('status') != 'pending':
        print(f"Error: Request ID '{request_id}' is not pending (current status: {request.get('status')}).")
        return False
    
    result = store.update_request(request_id, "rejected", notes)
    
    if result:
        print(f"✓ Request {request_id} rejected successfully.")
        if notes:
            print(f"  - Notes: {notes}")
    else:
        print(f"❌ Failed to reject request {request_id}.")
    
    return result

def show_request_details(request_id: str):
    """Show detailed information about a request"""
    store = ApprovalStore()
    request = store.get_request(request_id)
    
    if not request:
        print(f"Error: Request ID '{request_id}' not found.")
        return False
    
    print(f"Request ID: {request.get('id', 'Unknown')}")
    print(f"Status: {request.get('status', 'Unknown')}")
    print(f"Action: {request.get('action', 'Unknown')}")
    
    if request.get('action') == 'submit_prompt_update':
        print(f"Reason: {request.get('reason', 'None provided')}")
        print(f"\nPrompt Text:")
        print("-" * 60)
        print(request.get('prompt_text', ''))
        print("-" * 60)
    
    print(f"\nCreated: {request.get('created_at', 'Unknown')}")
    
    if request.get('updated_at'):
        print(f"Updated: {request.get('updated_at')}")
    
    if request.get('notes'):
        print(f"\nNotes: {request.get('notes')}")
    
    if request.get('processed'):
        print(f"\nProcessed: {request.get('processed_at', 'Yes')}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Approval CLI for managing approval requests')
    
    # Command group
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='List all pending approval requests')
    group.add_argument('--approve', metavar='REQUEST_ID', help='Approve a specific request')
    group.add_argument('--reject', metavar='REQUEST_ID', help='Reject a specific request')
    group.add_argument('--show', metavar='REQUEST_ID', help='Show details of a specific request')
    
    # Optional arguments
    parser.add_argument('--notes', metavar='TEXT', help='Notes to include with approval/rejection')
    
    args = parser.parse_args()
    
    # Create approval_requests directory if it doesn't exist
    if not os.path.exists('./approval_requests'):
        os.makedirs('./approval_requests')
    
    # Handle commands
    if args.list or (len(sys.argv) == 1):
        list_pending_approvals()
    elif args.approve:
        approve_request(args.approve, args.notes)
    elif args.reject:
        reject_request(args.reject, args.notes)
    elif args.show:
        show_request_details(args.show)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
