"""
Approval Store - Simple file-based storage for approval requests
"""
import os
import time
import uuid
import json
from datetime import datetime

class ApprovalStore:
    """Simple file-based approval request storage"""
    
    def __init__(self, store_path="./approval_requests"):
        """Initialize the approval store with path to store approval requests"""
        self.store_path = store_path
        os.makedirs(store_path, exist_ok=True)
    
    def create_request(self, request_data):
        """
        Create a new approval request
        
        Args:
            request_data: Dictionary with request details
            
        Returns:
            str: Unique request ID
        """
        request_id = f"req_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        request_data["id"] = request_id
        request_data["status"] = "pending"
        request_data["created_at"] = datetime.now().isoformat()
        
        # Store request
        with open(os.path.join(self.store_path, f"{request_id}.json"), "w") as f:
            json.dump(request_data, f, indent=2)
            
        return request_id
    
    def get_request(self, request_id):
        """
        Get a request by ID
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            dict: Request data or None if not found
        """
        try:
            with open(os.path.join(self.store_path, f"{request_id}.json"), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def update_request(self, request_id, status, notes=None):
        """
        Update request status
        
        Args:
            request_id: Unique request identifier
            status: New status ('approved', 'rejected', etc.)
            notes: Optional notes about the decision
            
        Returns:
            bool: True if updated successfully, False if not found
        """
        request_file = os.path.join(self.store_path, f"{request_id}.json")
        
        try:
            with open(request_file, "r") as f:
                request_data = json.load(f)
                
            request_data["status"] = status
            request_data["updated_at"] = datetime.now().isoformat()
            
            if notes:
                request_data["notes"] = notes
                
            with open(request_file, "w") as f:
                json.dump(request_data, f, indent=2)
                
            return True
        except FileNotFoundError:
            return False
    
    def get_pending_requests(self):
        """
        Get all pending approval requests
        
        Returns:
            list: List of pending request dictionaries
        """
        pending_requests = []
        
        for filename in os.listdir(self.store_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.store_path, filename), "r") as f:
                    request_data = json.load(f)
                    
                if request_data.get("status") == "pending":
                    pending_requests.append(request_data)
                    
        return pending_requests
    
    def get_approved_requests(self):
        """
        Get all approved requests that haven't been processed
        
        Returns:
            list: List of approved request dictionaries
        """
        approved_requests = []
        
        for filename in os.listdir(self.store_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.store_path, filename), "r") as f:
                    request_data = json.load(f)
                    
                if (request_data.get("status") == "approved" and 
                    not request_data.get("processed", False)):
                    approved_requests.append(request_data)
                    
        return approved_requests
    
    def mark_as_processed(self, request_id):
        """
        Mark a request as processed
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            bool: True if updated successfully, False if not found
        """
        request_file = os.path.join(self.store_path, f"{request_id}.json")
        
        try:
            with open(request_file, "r") as f:
                request_data = json.load(f)
                
            request_data["processed"] = True
            request_data["processed_at"] = datetime.now().isoformat()
                
            with open(request_file, "w") as f:
                json.dump(request_data, f, indent=2)
                
            return True
        except FileNotFoundError:
            return False
