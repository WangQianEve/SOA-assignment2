# github.py
from flask import Flask, session, flash, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from rauth.service import OAuth2Service
import redis
# connect
r = redis.Redis(host='localhost', port=6379, db=0)

# Flask config
SQLALCHEMY_DATABASE_URI = 'sqlite:///github.db'
SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
DEBUG = True

# Flask setup
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)

# Use your own values in your real application
github = OAuth2Service(
    name='github',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id= 'b5a2a0cc0a16b9f6432f',
    client_secret= 'f74e87b1426f0266c7b481cb2e4a094017087268',
)

# models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(120))

    def __init__(self, login, name):
        self.login = login
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.login

    @staticmethod
    def get_or_create(login, name):
        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(login, name)
            db.session.add(user)
            db.session.commit()
        return user

# views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/DomainSearch', methods=['GET'])
def domainSearch():
    domain = request.args.get('domain')
    indexes = r.zrevrange('researchInterest:'+domain, 0, -1, withscores=True)
    authors = []
    print(type(indexes))
    for index in indexes:
        print(type(index))
        print(index[0])
        # authors.append(r.hget('author:'+index[0], 'name'))
    return render_template('domainSearchResult.html', authors = authors)

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', next=request.args.get('next') or
        request.referrer or None, _external=True)
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user:email'}
    return redirect(github.get_authorize_url(**params))

# same path as on application settings page
@app.route('/github/callback')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('index'))
    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri, scope='user:email,public_repo')
    auth = github.get_auth_session(data=data)
    me = auth.get('user').json()

    user = User.get_or_create(me['login'], me['name'])
    # save user
    session['token'] = auth.access_token
    session['user_id'] = user.id
    flash('Logged in as ' + me['name'])
    return render_template('index.html', email=me['email'])

if __name__ == '__main__':
    db.create_all()
    app.run()
