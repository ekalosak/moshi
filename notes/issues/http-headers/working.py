from http import cookies
from http.cookies import SimpleCookie

from aiohttp.test_utils import make_mocked_request

hdr = {'Cookie': 'invalid={"json":0}; valid=cookie; another=1'}
req = make_mocked_request(method="POST", path="/login", headers=hdr)

assert len(req.cookies) == 0

def remove_non_session_cookies(req, session_name="another") -> 'aiohttp.web_request.Request':
    cs = req.headers.get('Cookie')
    cook = None
    for chunk in cs.split(';'):
        ck = SimpleCookie(chunk)
        assert len(ck) in (0, 1)
        if session_name in ck.keys():
            cook = ck
            break
    if cook is None:
        cookie_str = ""
    else:
        cs = cook.output()
        cookie_str = cs.split(': ')[1]
    hdr = req.headers.copy()
    hdr['Cookie'] = cookie_str
    out = req.clone(headers=hdr)
    return out

res = remove_non_session_cookies(req)
breakpoint()
a=1
