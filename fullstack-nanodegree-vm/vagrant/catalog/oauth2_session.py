from database_setup import User # TODO: refactor so we don't have to import this?

class Oauth2_Session(object):

    def __init__(self, secrets_file):
        self.secrets_file = secrets_file


    def __del__(self):
        self.disconnect()


    def connect(self, request, login_session, db_session):
        raise NotImplementedError( "Should have implemented this" )


    def disconnect(self, request, login_session, db_session):
        raise NotImplementedError( "Should have implemented this" )


    def createUser(self, name, email, image_url, db_session):
        newUser = User(name=name, email=email, image_url=image_url)
        db_session.add(newUser)
        db_session.commit()
        user = db_session.query(User).filter_by(email=email).one()
        return user.id


    def validateStateToken(self, login_session, request):
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        return None


    def getUserID(self, db_session, email):
        try:
            user = db_session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None


    # TODO: we should just be passing a User class object
    def setCurrentUserInfo(self, login_session, user_id, name, email, image_url):
        login_session['user_id'] = user_id
        login_session['username'] = name
        login_session['picture'] = image_url
        login_session['email'] = email


    def clearCurrentUserInfo(self, login_session):
        for key in ['user_id', 'username', 'picture', 'email']:
            if key in login_session:
                del login_session[key]
