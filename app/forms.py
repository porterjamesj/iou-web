from flask.ext.wtf import Form, TextField, PasswordField
from flask.ext.wtf import Required, Email

class LoginForm(Form):
    email = TextField('Email',validators = [Required(),Email()])
    password = PasswordField('Password',validators = [Required()])
