"""
Synkora API — GitHub Service

Handles GitHub OAuth token exchange, user profile retrieval,
and repository listing via the GitHub REST API.
"""

import httpx
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("github_service")

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"


class GitHubService:
    """Service for interacting with the GitHub API."""

    @staticmethod
    def get_oauth_url(state: str) -> str:
        """Generate the GitHub OAuth authorization URL."""
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "read:user user:email repo",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GITHUB_AUTH_URL}?{query}"

    @staticmethod
    async def exchange_code(code: str) -> dict:
        """
        Exchange an OAuth authorization code for an access token.

        Returns: {"access_token": "...", "token_type": "bearer", "scope": "..."}
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GITHUB_TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                logger.error("github_oauth_error", error=data.get("error_description", data["error"]))
                raise ValueError(data.get("error_description", "GitHub OAuth failed"))

            logger.info("github_code_exchanged", scope=data.get("scope"))
            return data

    @staticmethod
    async def get_user_profile(access_token: str) -> dict:
        """Fetch the authenticated GitHub user's profile."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_user_emails(access_token: str) -> list[dict]:
        """Fetch the authenticated user's email addresses."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def list_repos(
        access_token: str,
        page: int = 1,
        per_page: int = 30,
        sort: str = "updated",
    ) -> list[dict]:
        """
        Fetch the authenticated user's repositories.

        Returns a list of GitHub repository objects.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/user/repos",
                params={
                    "page": page,
                    "per_page": per_page,
                    "sort": sort,
                    "direction": "desc",
                    "affiliation": "owner,collaborator",
                },
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_repo(access_token: str, owner: str, name: str) -> dict:
        """Fetch details of a specific repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/repos/{owner}/{name}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_repo_languages(access_token: str, owner: str, name: str) -> dict:
        """Fetch the language breakdown for a repository."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/repos/{owner}/{name}/languages",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def search_repos(
        access_token: str,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Search GitHub repositories."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API_URL}/search/repositories",
                params={"q": query, "page": page, "per_page": per_page},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def normalize_repo(gh_repo: dict) -> dict:
        """
        Normalize a GitHub API repo response into our schema format.

        Maps GitHub's JSON structure to the fields expected by
        our RepositoryCreate Pydantic model.
        """
        return {
            "github_repo_id": gh_repo["id"],
            "name": gh_repo["name"],
            "full_name": gh_repo["full_name"],
            "description": gh_repo.get("description"),
            "html_url": gh_repo["html_url"],
            "clone_url": gh_repo["clone_url"],
            "default_branch": gh_repo.get("default_branch", "main"),
            "language": gh_repo.get("language"),
            "is_private": gh_repo.get("private", False),
            "stars_count": gh_repo.get("stargazers_count", 0),
            "forks_count": gh_repo.get("forks_count", 0),
            "open_issues_count": gh_repo.get("open_issues_count", 0),
            "size_kb": gh_repo.get("size", 0),
        }
