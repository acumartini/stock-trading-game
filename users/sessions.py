"""
These are basically helper functions that encapsulate session state.

Instead of trying to track down who uses what session keys, 
and dealing with what happens when multiple modules start sharing the session,
this lets us park the session information in one place.
"""

# Das keys
PARTY_TIME_KEY = 'experiencing_party_time'
ACTIVE_PORTFOLIO = 'active_portfolio_id'

# Active portfolio

def active_portfolio(request):
    return ACTIVE_PORTFOLIO in request.session

def get_active_portfolio(request):
    if not active_portfolio(request):
        return None
    return request.user.get_profile().portfolio_set.get(pk=request.session[ACTIVE_PORTFOLIO])

def set_active_portfolio(request, portfolio):
    request.session[ACTIVE_PORTFOLIO] = portfolio.pk

def set_active_portfolio_id(request, portfolio_id):
    request.session[ACTIVE_PORTFOLIO] = portfolio_id



# Party time easter egg fun.

def experiencing_party_time(request):
    
    return PARTY_TIME_KEY not in request.session or request.session[PARTY_TIME_KEY]
        

