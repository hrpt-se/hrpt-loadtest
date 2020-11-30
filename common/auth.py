
CSRF_HEADER = "X-CSRFToken"
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
WELCOME_URL = "/sv/valkommen/"


def get_token(http_client) -> str:
    token = http_client.cookies.get("csrftoken", "")
    return token


def get_session(http_client) -> str:
    return http_client.cookies.get("sessionid", "")
