from aiohttp import web, web_request
from loguru import logger

from moshi import UserAuthenticationError
from .. import util as sutil

CLIENT_ID = "462213871057-tsn4b76f24n40i7qrdrhflc7tp5hdqu2.apps.googleusercontent.com"

async def login(request: web_request.Request):
    """HTTP GET endpoint for login.html"""
    logger.info(request)
    error_message = request.query.get('error', '')  # TODO make a render wrapper (#32)
    template = sutil.env.get_template('login.html')
    logger.trace(f"Request originating IP address: {request.remote}")
    scheme = 'https' if sutil.HTTPS else 'http'
    if scheme == 'http':
        logger.warning("Using HTTP, no SSL - insecure!")
    # NOTE for google login button to appear, login_uri must be https on public site "[GSI_LOGGER]: Error parsing
    # configuration from HTML: Unsecured login_uri provided. client:44:322" otherwise;
    login_uri = request.url.with_scheme(scheme)
    logger.trace(f"Using login_uri for Google auth: {login_uri}")
    html = template.render(
        client_id=CLIENT_ID,
        login_uri=login_uri,
        error=error_message,
    )
    return web.Response(text=html, content_type='text/html')

def _handle_auth_error(e: UserAuthenticationError):
    """Raise the UserAuthenticationError to the user, redirecting them to the login page."""
    err_str = str(e)
    logger.debug(f"Presenting err_str to user: {err_str}")
    err_str = urllib.parse.quote(err_str)
    raise web.HTTPFound(f"/login?error={err_str}")

async def login_callback(request):
    """HTTP POST endpoint for handling Google OAuth 2.0 callback i.e. after user logs in.
    Sets up the user session, then redirects to main page.
    """
    logger.info(request)
    session = await new_session(request)
    data = await request.post()
    token = data['credential']
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request())
        if id_info['iss'] not in ALLOWED_ISS:
            raise UserAuthenticationError('Authentication failed')
        user_email = id_info['email'].lower()
        logger.debug(f'user_email={user_email}')
        authorized = await auth.is_email_authorized(user_email)
        if not authorized:
            raise UserAuthenticationError('Unrecognized user')  # TODO beta: please reach out to moshi.feedback@gmail.com for access
        user_id = id_info['sub']
        session['user_id'] = user_id
        session['user_given_name'] = id_info['given_name']
        session['user_email'] = user_email
        session.set_new_identity(user_id)
        # TODO make sure the user email is verified id_info['email_verified']
        logger.debug(f"Authentication successful for user: {user_email}")
        raise web.HTTPFound('/')
    except UserAuthenticationError as e:
        logger.error(f"User authentication failed: {e}")
        _handle_auth_error(e)

