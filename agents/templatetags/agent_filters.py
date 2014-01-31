from django import template
register = template.Library()


@register.inclusion_tag('agents/_agent_owned.html')
def list_agent_owned(portfolio):
    owned_stocks = portfolio.get_brief_stocks()
    return {'owned_stocks': owned_stocks}
