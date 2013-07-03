from app import app, login_manager, db
from app.forms import LoginForm
from flask import render_template, redirect, flash, url_for, request
from models import User, Member, Group
from flask.ext.login import login_user, logout_user, current_user, login_required

# the user loader class used by the login manager
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# logging in and out

@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # try to log the user in
        user = User.query.filter_by(email = form.email.data).first()
        if user == None:
            # the user can't be found
            flash("No such user.")
            return render_template('login.html',form=form)
        elif not user.check_password(form.password.data):
            # the password is wrong
            flash("Password incorrect.")
            return render_template('login.html',form=form)
        else:
            # login was successful
            login_user(user)
            if request.args.get('next'):
                # redirect if the user came from somewhere
                return redirect(request.args.get('next'))
            else:
                # otherwise just show the dashboard
                return redirect(url_for('dashboard'))
    else:
        return render_template('login.html',form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/index")

# the dashboard view

@app.route('/dash')
@login_required
def dashboard():
    # find all of this user's groups
    groupnames = []
    for u,m in db.session.query(User, Member).\
                          filter(Member.user_id == User.id):
        groupnames.append(Group.query.get(m.group_id).name)

    return render_template('dash.html',user=current_user,
                           toolbar = True,
                           groups = groupnames)
