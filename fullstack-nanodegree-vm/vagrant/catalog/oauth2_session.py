
class Oauth2_Session(object):

    def __init__(self, secrets_file):
        self.secrets_file = secrets_file

    def __del__(self):
        self.disconnect()

    def connect(self):
        raise NotImplementedError( "Should have implemented this" )


    def disconnect(self, request, session, db_session):
        raise NotImplementedError( "Should have implemented this" )
