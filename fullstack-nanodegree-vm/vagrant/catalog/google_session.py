from oauth2_session import Oauth2_Session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import json
import httplib2
import requests
from database_setup import User # TODO: refactor so we don't have to import this?
from flask import flash # TODO: don't like having UI in this module

class Google_Session(Oauth2_Session):
    """Support for a Google Oauth2 session.
    """
    def __init__(self, secrets_file):
        super(Google_Session, self).__init__(secrets_file)
        self._client_id = json.loads(open(self.secrets_file, 'r')
                            .read())['web']['client_id']

    def connect(self, request, session, db_session):
        # Validate state token
        print 'CONNECTING'
        if request.args.get('state') != session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data

        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(self.secrets_file, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != self._client_id:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_credentials = session.get('credentials')
        stored_gplus_id = session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        session['credentials'] = credentials
        session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        session['username'] = data['name']
        session['picture'] = data['picture']
        session['email'] = data['email']
        # ADD PROVIDER TO LOGIN SESSION
        session['provider'] = 'google'

        # TODO: refactor so we don't need db_session passed in
        user_id = self.getUserID(db_session, data["email"])
        if not user_id:
            user_id = self.createUser(session, db_session)
        session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        output += session['username']
        output += '!</h1>'
        output += '<img src="'
        output += session['picture']
        output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
        flash("you are now logged in as %s" % session['username'])
        print "done!"
        return output


    def getUserID(self, db_session, email):
        try:
            user = db_session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None


    def createUser(self, login_session, db_session):
        newUser = User(
                    name=login_session['username'],
                    email=login_session['email'],
                    image_url=login_session['picture'])
        db_session.add(newUser)
        db_session.commit()
        user = db_session.query(User).filter_by(email=login_session['email']).one()
        return user.id


    def disconnect(self, session):
        print 'DISCONNECTING'
        # Only disconnect a connected user.
        credentials = session.get('credentials')
        print 'credentials', credentials
        if credentials is None:
            print 'NOT A CONNECTED USER'
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        print 'IS A CONNECTED USER'
        access_token = credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] != '200':
            print 'TOKEN WAS INVALID'
            # For whatever reason, the given token was invalid.
            response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return "You have been logged out."
