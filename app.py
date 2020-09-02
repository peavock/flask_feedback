from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
# from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def redirect_register():
    return redirect('/register')

@app.route('/register', methods = ["GET","POST"])
def register_page():
    """Show a page to register and register upon submit"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data 
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, pwd, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session["username"] = username   
        flash(f"Welcome to the Feedback Portal {new_user.first_name}!","primary")
        return redirect(f"/users/{username}")

    else:             
        return render_template("register.html", form = form)

@app.route('/login', methods = ["GET","POST"])
def login_page():
    """Show a login page to log in"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.login(username, pwd)

        if user:
            session["username"] = username
            flash(f"Welcome Back {user.first_name}!","primary")
            return redirect(f"/users/{username}")
        else:
            flash("Bad username / password","danger")

    return render_template("login.html", form = form)

@app.route('/users/<username>', methods = ["GET","POST"])
def show_user_profile(username):


    if "username" in session:
        user = User.query.filter_by(username = username).first()
        feedback_list = user.feedback

        return render_template("users.html",user = user, feedback_list = feedback_list)
    else:
        flash("Please log-in first!","warning")
        return redirect("/login")

@app.route('/users/<username>/feedback/add', methods = ["GET","POST"])
def add_feedback_form(username):

    form = FeedbackForm()

    if form.validate_on_submit() and "username" in session:
        feedback = Feedback(
            title = form.title.data,
            content = form.content.data,
            username = session["username"]
        )
        db.session.add(feedback)
        db.session.commit()

        flash("Feedback added!","success")
        return redirect(f"/users/{username}")

    elif "username" in session:
        user = User.query.filter_by(username = username).first()
        return render_template("feedback/add.html",user = user, form = form)
    
    else:
        flash("Please log-in first!","warning")
        return redirect("/login")

@app.route('/users/<username>/delete', methods = ["POST"])
def delete_user(username):

    if "username" in session:
        active_user = session["username"]

        if active_user == username:
            user = User.query.filter_by(username = username).first()
            db.session.delete(user)
            db.session.commit()
            flash("User deleted","warning")
            return redirect("/logout")

        else:
            flash(f"Please log-in as {username}", "warning")
            return redirect (f"/users/{active_user}")

    else:
        flash("Please log-in first!", "warning")
        return redirect("/login")

@app.route('/feedback/<int:feedback_id>/update', methods = ["GET","POST"])
def update_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj = feedback)

    if form.validate_on_submit() and "username" in session:
        active_user = session["username"]
        if active_user == feedback.user.username:

            feedback.title = form.title.data,
            feedback.content = form.content.data,
        
            db.session.add(feedback)
            db.session.commit()

            flash(f"Feedback Updated!","success")
            return redirect(f"/users/{active_user}")

        else:
            flash(f"Please log-in as {feedback.user.username}","warning")
            return redirect(f"/users/{active_user}")


    elif "username" in session:
        active_user = session["username"]
        user = User.query.filter_by(username = active_user).first()
        
        return render_template("feedback/update.html", form = form, user = user)

    else:
        flash("Please log-in first!", "warning")
        return redirect("/login")


@app.route('/feedback/<int:feedback_id>/delete', methods = ["POST"])
def delete_feedback(feedback_id):
    if "username" in session:
        active_user = session["username"]
        feedback = Feedback.query.get_or_404(feedback_id)

        if active_user == feedback.user.username:
            db.session.delete(feedback)
            db.session.commit()
            flash("Feedback Deleted","success")
            return redirect(f"/users/{active_user}")

        else:
            flash(f"Please log-in as {feedback.user.username}", "warning")
            return redirect (f"/users/{active_user}")

    else:
        flash("Please log-in first!", "warning")
        return redirect("/login")



@app.route('/secret')
def show_secret_page():
    if "username" in session:
        return render_template('secret.html')
    else:
        flash("Please log-in first!","warning")
        return redirect("/login")

@app.route('/logout')
def log_out_user():
    session.pop("username")
    flash("Come back Soon!","info")

    return redirect("/login")