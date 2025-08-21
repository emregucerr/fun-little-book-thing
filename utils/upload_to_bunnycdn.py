import os
import uuid
import requests
from pathlib import Path
from typing import Optional
from datetime import datetime

def upload_to_bunnycdn(
    file_path: str,
    task_id: str,
    storage_zone_name: Optional[str] = os.getenv("BUNNY_STORAGE_ZONE"),
    access_key: Optional[str] = os.getenv("BUNNY_API_KEY"),
    cdn_region: Optional[str] = os.getenv("BUNNY_REGION"),
) -> Optional[str]:
    """
    Upload a file to BunnyCDN Storage and return the CDN URL.
    
    Args:
        file_path (str): Path to the local file
        storage_zone_name (str): BunnyCDN storage zone name
        access_key (str): BunnyCDN storage zone access key
        cdn_region (str): CDN region code (e.g., 'sg' for Singapore)
    
    Returns:
        Optional[str]: CDN URL of the uploaded file if successful, None if failed
    """
    try:
        if not storage_zone_name or not access_key or not cdn_region:
            raise ValueError("BunnyCDN configuration missing. Ensure BUNNY_STORAGE_ZONE, BUNNY_API_KEY and BUNNY_REGION are set.")
        # Ensure file exists
        file_path_path = Path(file_path)
        if not file_path_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get the file extension
        file_extension = file_path_path.suffix  # This includes the dot, e.g., '.png'
        
        # Generate timestamp first
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        id = str(uuid.uuid4())
        
        # Generate a URL-safe filename with extension
        filename = f"{task_id}/{timestamp}_{id}{file_extension}"
        
        # Construct the API endpoint
        base_url = f"https://{cdn_region}.storage.bunnycdn.com"
        endpoint = f"{base_url}/{storage_zone_name}/{filename}"

        # Read file content
        with open(file_path_path, 'rb') as file:
            file_content = file.read()

        # Upload to BunnyCDN
        headers = {
            'AccessKey': access_key,
            'Content-Type': 'application/octet-stream'
        }
        
        response = requests.put(endpoint, data=file_content, headers=headers)
        
        if response.status_code == 201:
            # Return the CDN URL
            cdn_url = f"https://{storage_zone_name}.b-cdn.net/{filename}"
            return cdn_url
        else:
            print(f"Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"Error uploading file to BunnyCDN: {str(e)}")
        return None
    