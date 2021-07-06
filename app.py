from flask import Flask, render_template, redirect, session, flash

from models import connect_db, db, User, Feedback

from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask_feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "MissMillieIsGood"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

@app.route('/')
def home():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def reg_user():

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email, first_name, last_name)
      
        db.session.commit()
        session['username'] = new_user.username
        return redirect(f'/users/{session["username"]}')

    return render_template('register.html', form=form)

@app.route('/users/<username>')
def user_page(username):

    user = User.query.get(username)

    all_feedback = Feedback.query.all()

    return render_template('user.html', user=user, all_feedback=all_feedback)

### ADD FEEDBACK

@app.route('/users/<username>/add-feedback', methods=["GET", "POST"])
def add_feedback(username):

    user = User.query.get(username)

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=user.username)

        db.session.add(feedback)
        db.session.commit()

        return redirect('/')

    return render_template('add-feedback.html', form=form, user=user)

### VIEW/EDIT FEEDBACK

@app.route('/feedback/<int:feedback_id>')
def show_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    return render_template('feedback.html', feedback=feedback)


### LOGIN/LOGOUT ROUTES

@app.route('/login')
def login_user():

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
    
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
    
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/login')

@app.route('/secret')
def secret():
    return "it's a secret"