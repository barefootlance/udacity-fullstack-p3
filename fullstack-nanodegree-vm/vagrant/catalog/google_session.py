from oauth2_session import Oauth2_Session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response, render_template
import json
import httplib2
import requests

class Google_Session(Oauth2_Session):
    """Support for a Google Oauth2 session.
    """
    def __init__(self, secrets_file):
        super(Google_Session, self).__init__(secrets_file)
        self._client_id = json.loads(open(self.secrets_file, 'r')
                            .read())['web']['client_id']


    def connect(self, request, login_session, db_session):
        # Validate state token
        response = self.validateStateToken(login_session, request)
        if response:
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
            return response

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

        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token in the session for later use.
        login_session['credentials'] = credentials
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        # TODO: refactor so we don't need db_session passed in
        user_id = self.getUserID(db_session, data["email"])
        if not user_id:
            user_id = self.createUser(login_session, db_session)
        self.setCurrentUserInfo(login_session, user_id, data['name'], data['email'], data['picture'])

        # ADD PROVIDER TO LOGIN SESSION
        login_session['provider'] = 'google'

        return render_template("login_confirm.html");


    def disconnect(self, login_session):

        # Only disconnect a connected user.
        credentials = login_session.get('credentials')

        if 'gplus_id' in login_session:
            del login_session['gplus_id']
        if 'credentials' in login_session:
            del login_session['credentials']

        if credentials is None:
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token = credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] != '200':
            # For whatever reason, the given token was invalid.
            response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            return "You have been logged out."
