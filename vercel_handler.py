import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
HEADERS = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}


def deploy(repo_name: str) -> str:
    """Deploy repo to Vercel. Returns live URL."""

    # Create deployment from GitHub repo
    res = requests.post(
        "https://api.vercel.com/v13/deployments",
        headers=HEADERS,
        json={
            "name": repo_name,
            "gitSource": {
                "type": "github",
                "repoId": get_repo_id(repo_name),
                "ref": "main"
            },
            "projectSettings": {
                "framework": "nextjs"
            }
        }
    )
    res.raise_for_status()
    data = res.json()
    deployment_id = data["id"]

    # Poll until ready
    return poll_deployment(deployment_id)


def get_repo_id(repo_name: str) -> str:
    """Get GitHub repo ID for Vercel."""
    import os
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME")
    res = requests.get(
        f"https://api.github.com/repos/{username}/{repo_name}",
        headers={"Authorization": f"token {token}"}
    )
    return str(res.json()["id"])


def poll_deployment(deployment_id: str, timeout: int = 120) -> str:
    """Poll Vercel until deployment is ready."""
    start = time.time()
    while time.time() - start < timeout:
        res = requests.get(
            f"https://api.vercel.com/v13/deployments/{deployment_id}",
            headers=HEADERS
        )
        data = res.json()
        status = data.get("status")
        if status == "READY":
            return f"https://{data['url']}"
        elif status == "ERROR":
            raise Exception("Vercel deployment failed")
        time.sleep(4)
    raise Exception("Deployment timed out")