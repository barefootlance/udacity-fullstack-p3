import random, string
from flask import session as login_session

def generate_csrf_token():
    """ Create a nonce.
    """
    if '_csrf_token' not in login_session:
        # from: http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
        length = 32
        some_random_string = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in xrange(length))
        login_session['_csrf_token'] = some_random_string
    return login_session['_csrf_token']
