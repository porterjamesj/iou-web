from app import app, login_manager, db
from app.forms import LoginForm
from flask import render_template, redirect, flash, url_for, request
from models import User
from flask.ext.login import login_user, logout_user, current_user, login_required

# the user loader class used by the login manager
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# the dashboard view

@app.route('/dash/')
@login_required
def dashboard():
    return str(current_user.id)

# logging in and out

@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # try to log the user in
        user = User.query.filter_by(email = form.email.data).first()
        if user == None:
            flash("No such user.")
            return render_template('login.html',form=form)
        elif not user.check_password(form.password.data):
            flash("Password incorrect.")
            return render_template('login.html',form=form)
        else:
            login_user(user)
            return redirect(request.args.get('next')) or \
                   redirect(url_for('dashboard'))
    else:
        return render_template('login.html',form = form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index')
