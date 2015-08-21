from oauth2_session import Oauth2_Session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response, render_template
import json
import httplib2
import requests

class Amazon_Session(Oauth2_Session):
    """Support for a Facebook Oauth2 session.
    """
    def __init__(self, secrets_file):
        super(Amazon_Session, self).__init__(secrets_file)
        #self._client_id = json.loads(open(self.secrets_file, 'r')
        #                    .read())['web']['client_id']

    def connect(self, request, login_session, db_session):

        # Validate state token
        response = self.validateStateToken(login_session, request)
        if response:
            return response

        import urllib

        access_token = request.args.get('access_token')

        url = "https://api.amazon.com/auth/o2/tokeninfo?access_token=" + urllib.quote_plus(access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        d = json.loads(result)
        if d['aud'] != 'amzn1.application-oa2-client.5e6d87e81aa74317a22bcf656a98b22b' :
            # the access token does not belong to us
            raise BaseException("Invalid Token")

        # Exchange the access token for user profile
        # The token must NOT be url-encoded when passed to profile
        url = "https://api.amazon.com/user/profile"
        headers = {'Authorization' : "bearer " + access_token}
        h = httplib2.Http()
        result = h.request(url, 'GET', headers=headers)[1]

        d = json.loads(result)

        # TODO: refactor so we don't need db_session passed in
        user_id = self.getUserID(db_session, d['email'])
        if not user_id:
            user_id = self.createUser(d['name'], d['email'], None, db_session)

        self.setCurrentUserInfo(login_session, user_id, d['name'], d['email'], None)

        login_session['amazon_user_id'] = d['user_id']

        # ADD PROVIDER TO LOGIN SESSION
        login_session['provider'] = 'amazon'

        return render_template("category_all.html");

    def disconnect(self, login_session):
        # TODO: log out from amazon - there's more to it than this, isn't there?
        if 'amazon_user_id' in login_session:
            del login_session['amazon_user_id']

        return "you have been logged out"
