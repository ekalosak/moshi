import os

from aiohttp import web
from aiohttp_session import setup, get_session, SimpleCookieStorage
from aiohttp_session.cookie_storage import EncryptedCookieStorage

async def handler(request):
    session = await get_session(request)
    print(f"session: {session}")
    print(f"request.cookies: {request.cookies}")
    cookie = request.headers.get('Cookie')
    agent = request.headers.get('User-Agent')
    print(f"header.user-agent: {agent}")
    print(f"header.cookie: {cookie}")
    session['counter'] = session.get('counter', 0) + 1
    # breakpoint()
    print()
    return web.Response(text=f"Counter: {session['counter']}")

app = web.Application()
# cookie_storage = EncryptedCookieStorage(os.urandom(32), httponly=True, secure=True)
cookie_storage = SimpleCookieStorage(secure=False, httponly=True, samesite="Strict")
# cookie_storage.cookie_params['samesite'] = "Strict"
# cookie_storage.cookie_params['secure'] = True
setup(app, cookie_storage)
app.router.add_get('/', handler)
web.run_app(app)
