from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from v1.clients.redis import RedisSession
from v1.utils.misc import get_hash, generate_code
from v1.analytics import process_analytics, reset_analytics
from v1.schemas import User, NewShort, EditShort
from v1.autho import get_current_user

router = APIRouter()


@router.get("/{code:str}")
async def redirect_url_route(request: Request, code: str):
    """Redirect to the URL associated with the code."""
    async with RedisSession() as cache:
        url = await cache.get(code)

    if url:
        process_analytics(request, url, code)
        return RedirectResponse(url)
    else:
        return JSONResponse(content={"error": "URL not found"}, status_code=404)


@router.post("/")
async def create_code_route(payload: NewShort, user: User = Depends(get_current_user)):
    """
    Create a new short URL.
    Only authenticated users can create short URLs.
    Users can provide a custom code, otherwise a random code will be generated.
    """
    url = payload.url
    code = payload.code

    url_hash = get_hash(url)

    async with RedisSession() as cache:
        # They want a custom code
        if code:
            cache_url = await cache.get(code)
            if cache_url:
                return JSONResponse(
                    content={"error": f"Code already exists"},
                    status_code=409,
                )
            else:
                await cache.set(code, url)
                await cache.set(url_hash, code)

        else:
            code = await cache.get(url_hash)

            if code:
                return JSONResponse(
                    content={"error": f"Code already exists"},
                    status_code=409,
                )
            else:
                code = generate_code()
                await cache.set(code, url)
                await cache.set(url_hash, code)

    return JSONResponse(content={"code": code})


@router.put("/{code:str}")
async def update_code_route(
    code: str,
    payload: EditShort,
    reset: bool = False,
    user: User = Depends(get_current_user),
):
    """Update the URL associated with the code."""
    url = payload.url

    async with RedisSession() as cache:
        old_url = await cache.get(code)
        if not old_url:
            return JSONResponse(content={"error": "Code not found"}, status_code=404)

        await cache.delete(get_hash(old_url))

        await cache.set(code, url)
        await cache.set(get_hash(url), code)

    if reset:
        reset_analytics(url, code)

    return JSONResponse(content={"code": code})


@router.delete("/{code:str}")
async def delete_code_route(code: str, user: User = Depends(get_current_user)):
    """Delete the URL associated with the code."""
    async with RedisSession() as cache:
        url = await cache.get(code)
        if not url:
            return JSONResponse(content={"error": "Code not found"}, status_code=404)

        await cache.delete(code)
        await cache.delete(get_hash(url))

    reset_analytics(url, code)

    return JSONResponse(content={"code": code})


@router.delete("/{code:str}/analytics")
async def reset_analytics_route(code: str, user: User = Depends(get_current_user)):
    """Reset the analytics for the code."""
    async with RedisSession() as cache:
        url = await cache.get(code)
        if not url:
            return JSONResponse(content={"error": "Code not found"}, status_code=404)

    reset_analytics(url, code)

    return JSONResponse(content={"code": code})
