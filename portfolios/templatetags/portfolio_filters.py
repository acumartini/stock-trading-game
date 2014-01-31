from django import template
register = template.Library()

import users.sessions as session

# I'm pretty sure this should actually be accomplished with a custom context 
# or middleware, but I don't actually have enough time to learn those.
@register.inclusion_tag('portfolios/_portfolio_bar.html', takes_context=True)
def portfolio_bar(context):
    portfolio = session.get_active_portfolio(context['request'])
    active_portfolios = context['request'].user.get_profile().get_active_portfolios()
    return {'portfolio': portfolio, 'active_portfolios': active_portfolios, 'return_address': context['request'].path}
    