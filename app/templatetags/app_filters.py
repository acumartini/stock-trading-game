from django import template
register = template.Library()


@register.simple_tag()
def moneyify(amount):
    return "${:.2f}".format(amount)