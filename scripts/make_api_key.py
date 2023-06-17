import os
with open('session_cookie_key_32', 'wb') as f:
    f.write(os.urandom(32))
