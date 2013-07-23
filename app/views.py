from app import app, login_manager, db
from app.forms import LoginForm, RegisterForm
from flask import render_template, redirect, flash, url_for, request
from app.models import User, Group, Member
from flask.ext.login import login_user, logout_user,\
    current_user, login_required
import app.services.graph as graph


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # try to log the user in
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            # the user can't be found
            flash("No such user.")
            return render_template('login.html', form=form)
        elif not user.check_password(form.password.data):
            # the password is wrong
            flash("Password incorrect.")
            return render_template('login.html', form=form)
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
        return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/index")


@app.route('/dash')
@login_required
def dashboard():
    graphs = {}
    for group in current_user.groups:
        # get all transactions for this group
        transactions = group.transactions
        this_graph = graph.build_graph(group.members, transactions)
        graphs[group.name] = graph.display_graph(group.members, this_graph)

    return render_template('dash.html', user=current_user,
                           groups=graphs)


@app.route('/admin')
@login_required
def admin():
    # get all groups where this user is an admin
    # may be a better way to do this
    groups = {}
    for member in current_user.member:
        if member.admin is True:
            group = Group.query.get(member.group_id)
            for member in group.members:
                member.admin = Member.query\
                                     .filter(Member.user_id == member.id,
                                             Member.group_id == group.id)\
                                     .one().admin
                groups[group] = group.members
    return render_template('admin.html', user=current_user,
                           groups=groups)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # check that we don't already have a user for this email
        if User.query.filter_by(email=form.email.data).all() != []:
            flash("A user with that email already exists.")
            return render_template("register.html", form=form)
        # put the new user in the database
        user = User(name=form.name.data,
                    email=form.email.data,
                    dummy=False)
        # generate the user's password
        user.set_password(form.password.data)
        # add new user to db
        db.session.add(user)
        db.session.commit()
        # log them in and redirect to the dashboard
        login_user(user)
        return redirect(url_for('dashboard'))
    else:
        return render_template('register.html', form=form)
