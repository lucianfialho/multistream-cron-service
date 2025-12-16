"""
Proxy endpoints for external resources
Needed to bypass CORS and Cloudflare protection
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from curl_cffi import requests
import io

router = APIRouter()

@router.get("/proxy/team-logo")
async def proxy_team_logo(url: str):
    """
    Proxy team logos from HLTV to bypass Cloudflare protection
    
    Args:
        url: Full HLTV image URL
    
    Returns:
        Image bytes with proper content-type
    """
    # Validate it's an HLTV URL
    if 'hltv.org' not in url:
        raise HTTPException(status_code=400, detail="Invalid URL - must be from hltv.org")
    
    try:
        # Use curl_cffi with browser impersonation to bypass Cloudflare
        response = requests.get(
            url,
            impersonate="chrome110",
            timeout=10
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch image: {response.status_code}"
            )

        # Get content type from response
        content_type = response.headers.get('content-type', 'image/png')

        # Return image with proper headers
        return Response(
            content=response.content,
            media_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
                'Access-Control-Allow-Origin': '*',
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")
