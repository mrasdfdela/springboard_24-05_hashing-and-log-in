from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/tweets', methods=['GET','POST'])
def show_tweets():
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/")
    else:
        tweets = Tweet.query.all()
        form = TweetForm()
        if form.validate_on_submit():
            text = form.text.data
            new_tweet = Tweet(text=text, user_id=session['user_id'])
            db.session.add(new_tweet)
            db.session.commit()
            flash('Tweet Created!', "success")
            return redirect('/tweets')
        return render_template('tweets.html', form=form, tweets=tweets)

@app.route('/tweets/<int:id>',methods=['POST'])
def delete_tweet(id):
    """ Delete tweet """
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')

    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('Tweet deleted', "info")
        return redirect("/tweets")
        
    flash("You don't have permission to do that!", "danger")
    return redirect("/tweets")

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        flash('Welcome! Sucessfully creating your account!', "success")
        return redirect('/tweets')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome back, {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/tweets')
        else:
            form.username.errors = ['Invalid username/password']
            
    return render_template('/login.html', form=form)

@app.route('/logout') # some browsers pre-fetch routes upon loading, so is conventially done with post method
def logout_user():
    session.pop('user_id')
    flash('Goodbye!', "info")
    return redirect("/")