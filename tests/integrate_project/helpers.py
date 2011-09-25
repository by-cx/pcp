class SessionWrapper(dict):
    pass

def build_request(get_query=None, post_query=None, session={}, cookies={}, ip_address=None, method='GET'):
    """
    Returns request object with useful attributes
    """
    from django.http import HttpRequest, QueryDict
    from django.contrib.auth.middleware import LazyUser
    request = HttpRequest()
    # Method
    request.method = method
    # GET and POST
    if get_query:
        request.GET = QueryDict(get_query)
    if post_query:
        request.POST = QueryDict(post_query)
    # Session and cookies
    request.session = SessionWrapper(session)
    request.session.session_key = 'XXX'
    request.COOKIES = cookies
    # User
    request.__class__.user = LazyUser()
    # Meta
    request.META['REMOTE_ADDR'] = ip_address or '0.0.0.0'
    return request
