import time
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup, get_session, SimpleCookieStorage
from aiohttp_session.cookie_storage import EncryptedCookieStorage


async def handler(request):
    session = await get_session(request)
    print(f"session: {session}")
    last_visit = session['last_visit'] if 'last_visit' in session else None
    session['last_visit'] = time.time()
    text = 'Last visited: {}'.format(last_visit)
    return web.Response(text=text)


def make_app():
    app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    f = fernet.Fernet(fernet_key)
    setup(app, SimpleCookieStorage())
    # setup(app, EncryptedCookieStorage(f))
    app.router.add_get('/', handler)
    return app


web.run_app(make_app())
