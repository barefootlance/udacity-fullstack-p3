from oauth2_session import Oauth2_Session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response, render_template, url_for
import json
import httplib2
import requests
import requests.auth

class Reddit_Session(Oauth2_Session):
    """Support for a Reddit Oauth2 session.
    """
    def __init__(self, secrets_file):
        super(Reddit_Session, self).__init__(secrets_file)
        self._client_id = json.loads(open(self.secrets_file, 'r')
                            .read())['web']['client_id']

        self.user_agent = "web app:Udacity Project 3:v0.0.1 (by /u/AFinchIsNotABird)"

    def connect(self, request, login_session, db_session):
        # Validate state token
        response = self.validateStateToken(login_session, request)
        if response:
            return response

        error = request.args.get('error', '')
        if error:
            return "Error: " + error
        code = request.args.get('code')

        access_token = self.get_token(code, request.args['state'])

        headers = {"Authorization": "bearer " + access_token, "user-agent": self.user_agent}
        response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
        me_json = response.json()
        user_name = me_json.get('name')

        # HACK: Reddit doesn't currently give you access to an email. Bummer.
        # HOWEVER! Unlike other sources, we know the username is unique, so
        # we'll just use that (even though it's not a valid email!)
        #user_email = data.get('email')
        user_email = user_name

        # TODO: Reddit doesn't do pictures, either
        user_image_url = None

        # TODO: refactor so we don't need db_session passed in
        user_id = self.getUserID(db_session, user_email)
        if not user_id:
            user_id = self.createUser(user_name, user_email, user_image_url, db_session)

        self.setCurrentUserInfo(login_session, user_id, user_name, user_email, user_image_url)

        # ADD PROVIDER TO LOGIN SESSION
        login_session['provider'] = 'reddit'

        return render_template("category_all.html");

    def disconnect(self, login_session):
        # Reddit doesn't track sessions, so not much to do here
        return "you have been logged out"


    def get_token(self, code, state):
        client_secret = json.loads(open(self.secrets_file, 'r')
                            .read())['web']['client_secret']

        client_auth = requests.auth.HTTPBasicAuth(self._client_id, client_secret)

        # NOTE: the URI must *EXACTLY* match the redirect uri you've
        # given to reddit. For the purpose of this particular app, that's:
        # http://localhost:5000/connect/reddit
        redirect_uri = url_for('redditConnect', _external=True)

        post_data = {"grant_type": "authorization_code",
                     "code": code,
                     "state": state,
                     "redirect_uri": redirect_uri}

        headers = {"user-agent": self.user_agent}

        response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                                 auth=client_auth,
                                 data=post_data,
                                 headers=headers)

        token_json = response.json()

        # NOTE: I am getting 429 - which is a rate limiting response.
        # Note sure why, as it's a minute or two between submissions.
        # *sigh*
        # UPDATE: needed to include the user-agent string. All better now.
        return token_json.get("access_token")
