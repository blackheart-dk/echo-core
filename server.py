import os
import json
import base64
from datetime import datetime
import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

# Initialize FastMCP Server
mcp = FastMCP("Personal Persona Sync")

# Fetch user configurations from environment variables
GITHUB_TOKEN = os.environ.get("GITHUB_PAT")
REPO_NAME = os.environ.get("GITHUB_PER_REPO")  # Format: "username/repo"

# Ensure environment variables are present before starting
if not GITHUB_TOKEN or not REPO_NAME:
    print("Warning: GITHUB_PAT or GITHUB_PER_REPO environment variables are missing.")

def get_github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def fetch_from_github(file_path: str, default_structure: dict) -> tuple[dict, str | None]:
    """Helper to fetch a file's structured content and its current SHA hash from GitHub."""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
    
    with httpx.Client() as client:
        response = client.get(url, headers=get_github_headers())
        
        if response.status_code == 200:
            file_data = response.json()
            # Decode base64 content from GitHub
            content_str = base64.b64decode(file_data["content"]).decode("utf-8")
            return json.loads(content_str), file_data["sha"]
        elif response.status_code == 404:
            # File doesn't exist yet, return the default template structure
            return default_structure, None
        else:
            raise Exception(f"GitHub API Error ({response.status_code}): {response.text}")

def save_to_github(file_path: str, data: dict, sha: str | None) -> bool:
    """Helper to push base64-encoded JSON updates back to the private GitHub repo."""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{file_path}"
    
    updated_json = json.dumps(data, indent=4)
    encoded_content = base64.b64encode(updated_json.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": f"AI Auto-Update: Syncing {file_path}",
        "content": encoded_content
    }
    if sha:
        payload["sha"] = sha

    with httpx.Client() as client:
        res = client.put(url, headers=get_github_headers(), json=payload)
        return res.status_code in [200, 201]


# =====================================================================
# TOOLS FOR CORE PERSONA MANAGEMENT
# =====================================================================

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,      # Tells the client this tool does not change the environment
    idempotentHint=True     # Tells the client it can safely retry this call if it fails
)

@mcp.tool(annotations=READ_ONLY)
def read_profile() -> str:
    """
    Reads your comprehensive personal identity, health history, and general hobbies.
    Call this at the beginning of a session to gain context on who the user is.
    """
    default_profile = {
        "core": {},
        "health_log": [],
        "hobbies": {
            "hobbies": [],
            "interests": [],
            "skills": [],
            "languages": [],
            "education": [],
            "work": [],
            "projects": [],
            "certifications": [],
            "awards": [],
        }
    }
    try:
        profile_data, _ = fetch_from_github("persona_profile.json", default_profile)
        return json.dumps(profile_data, indent=4)
    except Exception as e:
        return f"Error reading profile: {str(e)}"

@mcp.tool()
def patch_profile(category: str, key_or_event: str, value: str = None) -> str:
    """
    Updates your general profile. Call this whenever the user shares a significant life update,
    physical injury, weight change, or a change in high-level life goals.
    
    category: must be 'core', 'health_log', or 'hobbies'
    key_or_event: The metric name (e.g., 'weight', 'current_location') OR the full log entry text.
    value: The value to update (optional if appending directly to the timeline log).
    """
    default_profile = {
        "core": {},
        "health_log": [],
        "hobbies": {}
    }
    
    try:
        profile_data, sha = fetch_from_github("persona_profile.json", default_profile)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if category == "health_log":
            log_entry = f"[{timestamp}] {key_or_event}" if not value else f"[{timestamp}] {key_or_event}: {value}"
            profile_data["health_log"].append(log_entry)
            
        elif category in ["core", "hobbies"]:
            profile_data[category][key_or_event] = value
        else:
            return f"Error: Invalid category '{category}'. Must be 'core', 'health_log', or 'hobbies'."

        success = save_to_github("persona_profile.json", profile_data, sha)
        return "Successfully updated profile context on GitHub." if success else "Failed to save profile changes to GitHub."
        
    except Exception as e:
        return f"Error patching profile: {str(e)}"

if __name__ == "__main__":
    mcp.run()