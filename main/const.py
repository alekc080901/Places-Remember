DOMAIN = 'http://127.0.0.1:8000'
# DOMAIN = 'https://places-remember-internship.herokuapp.com'
AUTH_URL = 'auth'
AUTH_ABS_URL = f'{DOMAIN}{"" if DOMAIN.endswith("/") else "/"}{AUTH_URL}'
