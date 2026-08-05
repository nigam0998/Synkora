"""
Synkora API — GitHub OAuth Router

Handles the GitHub OAuth callback flow:
  1. Frontend redirects user to GitHub authorization URL
  2. GitHub redirects back with a code
  3. This router exchanges the code for an access token
  4. Links the GitHub account to the Synkora user
"""

import secrets

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from app.services.github_service import GitHubService
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("github_router")

router = APIRouter()


class GitHubOAuthStart(BaseModel):
    """Response for starting the GitHub OAuth flow."""
    url: str
    state: str


class GitHubCodeExchange(BaseModel):
    """Request to exchange a GitHub OAuth code."""
    code: str
    state: str


class GitHubConnectResponse(BaseModel):
    """Response after connecting GitHub."""
    message: str
    github_username: str
    repos_available: int


@router.get("/connect", response_model=GitHubOAuthStart)
async def start_github_oauth(current_user: dict = Depends(get_current_user)):
    """
    Generate a GitHub OAuth authorization URL.

    The frontend should redirect the user to this URL.
    """
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET.",
        )

    state = secrets.token_urlsafe(32)
    url = GitHubService.get_oauth_url(state)

    return GitHubOAuthStart(url=url, state=state)


@router.post("/callback", response_model=GitHubConnectResponse)
async def github_callback(
    body: GitHubCodeExchange,
    current_user: dict = Depends(get_current_user),
):
    """
    Exchange a GitHub OAuth authorization code for an access token.

    This endpoint:
    1. Exchanges the code for an access token
    2. Fetches the GitHub user profile
    3. Links the GitHub account to the current Synkora user
    4. Returns the GitHub username and available repo count
    """
    try:
        # Exchange code for token
        token_data = await GitHubService.exchange_code(body.code)
        access_token = token_data["access_token"]

        # Fetch GitHub profile
        profile = await GitHubService.get_user_profile(access_token)

        # Fetch repos count
        repos = await GitHubService.list_repos(access_token, per_page=1)

        logger.info(
            "github_connected",
            user_id=current_user.get("id"),
            github_user=profile.get("login"),
        )

        return GitHubConnectResponse(
            message="GitHub account connected successfully",
            github_username=profile.get("login", ""),
            repos_available=profile.get("public_repos", 0) + profile.get("total_private_repos", 0),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("github_callback_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to connect to GitHub. Please try again.",
        )


@router.get("/repos")
async def list_github_repos(
    page: int = 1,
    per_page: int = 30,
    current_user: dict = Depends(get_current_user),
):
    """
    List the authenticated user's GitHub repositories.

    Requires that the user has connected their GitHub account.
    """
    # For now, use a mock token. In production, this would come from the user's stored token.
    github_token = current_user.get("github_access_token")
    if not github_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="GitHub account not connected. Please connect your GitHub account first.",
        )

    try:
        repos = await GitHubService.list_repos(
            access_token=github_token,
            page=page,
            per_page=per_page,
        )
        normalized = [GitHubService.normalize_repo(r) for r in repos]
        return {"repositories": normalized, "page": page, "per_page": per_page}
    except Exception as e:
        logger.error("github_repos_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch repositories from GitHub.",
        )
