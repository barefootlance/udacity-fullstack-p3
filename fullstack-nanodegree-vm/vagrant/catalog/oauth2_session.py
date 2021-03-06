from database_setup import User # TODO: refactor so we don't have to import this?

class Oauth2_Session(object):

    def __init__(self, secrets_file):
        self.secrets_file = secrets_file


    def __del__(self):
        self.disconnect(None)


    def connect(self, request, login_session, db_session):
        """ Respond to a login request.
        Args:
            request - http request.
            login_session - flask session.
            db_session - sqlite database session.
        """
        raise NotImplementedError( "Should have implemented this" )


    def disconnect(self, login_session):
        """ Respond to a diconnect request.
        Args:
            login_session - flask session.
        """
        raise NotImplementedError( "Should have implemented this" )


    def createUser(self, name, email, image_url, db_session):
        """ Utility function for adding a new user to the database.

        Args:
            name - user name (display name)
            email - user "email". Used as a unique identifier for ownership
                of a catgory or item, so the unique part is more important
                that the email part (NOTE: Reddit doesn't provide emails...)
            image_url - optional picture to associate with this account.
            db_session - sqlite session
        """
        newUser = User(name=name, email=email, image_url=image_url)
        db_session.add(newUser)
        db_session.commit()
        user = db_session.query(User).filter_by(email=email).one()
        return user.id


    def validateStateToken(self, login_session, request):
        """ Make sure the nonce we get is the nonce we expected.

        Args:
            login_session - flask login session
            request - http request
        """
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 403)
            response.headers['Content-Type'] = 'application/json'
            return response
        return None


    def getUserID(self, db_session, email):
        """Convenience function for getting a user id from an email.

        Args:
            db_session - sqlite session
            email - email to search for
        """
        try:
            user = db_session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None


    # TODO: we should just be passing a User class object
    def setCurrentUserInfo(self, login_session, user_id, name, email, image_url):
        """Convenience method for setting storing the current user in the  login session.

        Args:
            login_session - flask login session
            user_id - internal user id
            name - display name
            email - user emails
            image_url - link to an image associated with the user
        """
        login_session['user_id'] = user_id
        login_session['username'] = name
        login_session['picture'] = image_url
        login_session['email'] = email


    def clearCurrentUserInfo(self, login_session):
        """Convenience method for un-setting what we set in setCurrentUserInfo.

        Args:
            login_session - flask login session
        """
        for key in ['user_id', 'username', 'picture', 'email']:
            if key in login_session:
                del login_session[key]
