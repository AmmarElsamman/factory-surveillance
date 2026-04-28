import requests

API_URL = "http://localhost:8000"

class APIClient:
    
    # --- Workers ---
    @staticmethod
    def get_workers(status: str = None):
        try:
            params = {"status": status} if status else {}
            response = requests.get(f"{API_URL}/api/workers", params=params)
            return response.json().get("workers", [])
        except Exception as e:
            raise Exception(f"Server error: Unable to fetch cameras: {e}")
        
    @staticmethod
    def get_worker_by_code(employee_code: str):
        try:
            response = requests.get(f"{API_URL}/api/workers/{employee_code}")
            return response.json().get("worker", None)
        except Exception as e:
            raise Exception(f"Server error: Unable to fetch cameras: {e}")
        
    @staticmethod
    def get_workers_embeddings():
        try:
            response = requests.get(f"{API_URL}/api/worker_embeddings")
            return response.json().get("embeddings", [])
        except Exception as e:
            raise Exception(f"Server error: Unable to fetch cameras: {e}")
        
    @staticmethod
    def toggle_worker_status(employee_code: str):
        try:
            response = requests.put(f"{API_URL}/api/workers/{employee_code}/toggle-status")
            return response.json()
        except Exception as e:
            raise Exception(f"Server error: Unable to fetch cameras: {e}")
        
    
    # --- Cameras ---
    @staticmethod
    def get_cameras():
        try:
            response = requests.get(f"{API_URL}/api/cameras")
            return response.json().get("cameras", [])
        except Exception as e:
            raise Exception(f"Server error: Unable to fetch cameras: {e}")