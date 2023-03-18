from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_db, db, User, Feedback
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError
from forms import RegisterForm, UserForm, DeleteForm, FeedbackForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
app.app_context().push()


toolbar = DebugToolbarExtension(app)


@app.route('/')
def direct_to_register():
    """redirect to the register page"""
    print("why you no work")

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user_form():
    """display new user form and handle submission"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email, first_name, last_name)

        db.session.add(new_user)
        print('into database')
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append(
                "Username already exists. Please pick another")
            return render_template('register.html', form=form)
        print('didnt log into session')
        session['user_id'] = new_user.username
        flash('Welcome! New Account Created', 'success')
        return redirect('users/<username:username>')

    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    """log in a user"""
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.username
            return redirect('/users/<username:username')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/users/<username>')
def details(username):
    """details of user"""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template("users/bio.html", user=user, form=form)


@app.route('/logout')
def logout():
    """logs current user out"""
    session.pop("user_id")
    return redirect('/')


@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user nad redirect to login."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")


@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """Show add-feedback form and process it."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(
            title=title,
            content=content,
            username=username,
        )

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/new.html", form=form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
