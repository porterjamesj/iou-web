from app import app
from functools import wraps
from flask.ext.login import current_user

# Extras


def toalnum(s):
    return filter(str.isalnum, str(s))

app.jinja_env.filters['toalnum'] = toalnum


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'LOGIN' in app.config and app.config['LOGIN'] is False:
            return func(*args, **kwargs)
        if not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view
