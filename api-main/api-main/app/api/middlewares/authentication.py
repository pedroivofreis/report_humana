from fastapi import HTTPException, Request, status

from app.core.config import settings


async def verify_api_key(request: Request) -> str:
    """
    Dependency to verify the API key.
    Can be used with Depends() in any route.
    """
    api_key_header = request.headers.get("X-Api-Key")

    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is required",
        )

    api_key = settings.API_KEY

    if api_key_header != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    print("--------------------------------")
    print("API key is valid, carry on...")
    print("--------------------------------")

    return str(api_key_header)
