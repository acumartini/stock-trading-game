from django import template
register = template.Library()

import users.sessions as session

@register.filter()
def experiencing_party_time(request):
    session.experiencing_party_time(request)

@register.filter()
def has_active_portfolio(request):
    return session.active_portfolio(request)
