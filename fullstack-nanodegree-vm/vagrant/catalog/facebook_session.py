from oauth2_session import Oauth2_Session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response, render_template
import json
import httplib2
import requests

class Facebook_Session(Oauth2_Session):
    """Support for a Facebook Oauth2 session.
    """
    def __init__(self, secrets_file):
        super(Facebook_Session, self).__init__(secrets_file)
        #self._client_id = json.loads(open(self.secrets_file, 'r')
        #                    .read())['web']['client_id']

    def connect(self, request, login_session, db_session):
        """ Respond to a login request.
        Args:
            request - the http request.
            login_session - flask session.
            db_session - sqlite database session.
        """
        api_version = '2.4'

        # Validate state token
        response = self.validateStateToken(login_session, request)
        if response:
            return response

        access_token = request.data

        app_id = json.loads(open(self.secrets_file, 'r').read())['web']['app_id']
        app_secret = json.loads(open(self.secrets_file, 'r').read())['web']['app_secret']
        url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        # Use token to get user info from API
        userinfo_url = "https://graph.facebook.com/v{API}/me".format(API=api_version)
        # strip expire tag from access token
        token = result.split("&")[0]

        url = 'https://graph.facebook.com/v{API}/me?{Token}&fields=name,id,email'.format(API=api_version, Token=token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        # print "url sent for API access:%s"% url
        # print "API JSON result: %s" % result
        data = json.loads(result)
        login_session['facebook_id'] = data["id"]
        user_name = data['name']
        user_email = data['email']

        # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
        stored_token = token.split("=")[1]
        login_session['access_token'] = stored_token

        # Get user picture
        url = 'https://graph.facebook.com/v{API}/me/picture?{Token}&redirect=0&height=200&width=200'.format(API=api_version, Token=token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)
        user_image_url = data["data"]["url"]

        # TODO: refactor so we don't need db_session passed in
        user_id = self.getUserID(db_session, user_email)
        if not user_id:
            user_id = self.createUser(user_name, user_email, user_image_url, db_session)

        self.setCurrentUserInfo(login_session, user_id, user_name, user_email, user_image_url)

        # ADD PROVIDER TO LOGIN SESSION
        login_session['provider'] = 'facebook'

        return render_template("login.html");

    def disconnect(self, login_session):
        """ Respond to a diconnect request.
        Args:
            login_session - flask session.
        """
        facebook_id = login_session['facebook_id']
        # The access token must me included to successfully logout
        access_token = login_session['access_token']
        url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]

        del login_session['access_token']
        if 'facebook_id' in login_session:
            del login_session['facebook_id']

        return "you have been logged out"
