from http.cookies import SimpleCookie

_ffx = 'g_state={"i_l":0}; g_csrf_token=397d85fedc4b26b9; MOSHI-001="{\\"created\\": 1686788627\\054 \\"session\\": {\\"user_id\\": \\"107351735327079456170\\"\\054 \\"user_given_name\\": \\"Eric\\"\\054 \\"user_email\\": \\"helloateric@gmail.com\\"}}"'
sfi = 'MOSHI-001="{\\"created\\": 1686788761\\054 \\"session\\": {\\"user_id\\": \\"107351735327079456170\\"\\054 \\"user_given_name\\": \\"Eric\\"\\054 \\"user_email\\": \\"helloateric@gmail.com\\"}}"; g_csrf_token=1461f42980e37b1b; g_state={"i_l":0}'
ffx = _ffx

def parse(s):
    print(s)
    p = SimpleCookie(s)
    print(p)

print('---')
parse(ffx)
print('---')
parse(sfi)

ffx = 'MOSHI-001="{\\"created\\": 1686788627\\054 \\"session\\": {\\"user_id\\": \\"107351735327079456170\\"\\054 \\"user_given_name\\": \\"Eric\\"\\054 \\"user_email\\": \\"helloateric@gmail.com\\"}}"'
sfi = 'MOSHI-001="{\\"created\\": 1686788761\\054 \\"session\\": {\\"user_id\\": \\"107351735327079456170\\"\\054 \\"user_given_name\\": \\"Eric\\"\\054 \\"user_email\\": \\"helloateric@gmail.com\\"}}"'
print('---')
parse(ffx)
print('---')
parse(sfi)

print('---')
ffx = 'g_state="{\\"i_l\\":0}"; g_csrf_token=397d85fedc4b26b9; MOSHI-001="{\\"created\\": 1686788627\\054 \\"session\\": {\\"user_id\\": \\"107351735327079456170\\"\\054 \\"user_given_name\\": \\"Eric\\"\\054 \\"user_email\\": \\"helloateric@gmail.com\\"}}"'
parse(ffx)

print()
print()
print()
from aiohttp.test_utils import make_mocked_request
h = {'Cookie': _ffx}
r = make_mocked_request(method="POST", path="/login", headers=h)
print(r)
print(r.headers)
