import os
import time

from aiohttp import web
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

async def start(request):
    session = await get_session(request)
    session['should_persist'] = time.time()
    raise web.HTTPFound('/redirected')

async def redirected(request):
    session = await get_session(request)
    assert 'should_persist' in session
    return web.Response(text=f"should_persist: {session['should_persist']}")

app = web.Application()
secret_key = os.urandom(32)

cookie_storage = EncryptedCookieStorage(secret_key, cookie_name='AIOHTTP_SESSION')
setup(app, cookie_storage)

app.router.add_get('/start', start)
app.router.add_get('/redirected', redirected)

web.run_app(app)
