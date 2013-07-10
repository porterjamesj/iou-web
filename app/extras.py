from app import app
# Extras

def toalnum(s):
    return filter(str.isalnum,str(s))

app.jinja_env.filters['toalnum'] = toalnum
