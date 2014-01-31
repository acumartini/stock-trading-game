from django import template

from stocks.models import Stock
from users.models import User, UserProfile
from portfolios.forms import TransactionForm, OrderForm
import stocks.api as api


# register for template function calls to custom filters
register = template.Library()


@register.filter(name='get_stock_gains')
def get_stock_gains(owned_stock):
    stock_equity = 0
    for transaction in owned_stock.transaction_set.all():
        stock_equity += transaction.trans_price * transaction.trans_quantity
    stock = Stock.objects.get(ticker=owned_stock.ticker)
    return (stock.current_price * owned_stock.quantity) - stock_equity


@register.inclusion_tag('users/_owned.html')
def list_owned(portfolio):
    owned_stocks = portfolio.get_brief_stocks()
    return {'owned_stocks': owned_stocks}


@register.inclusion_tag('users/_watched.html')
def list_watched(portfolio):
    watched_stocks = portfolio.get_brief_watched()
    return {'owned_stocks': watched_stocks}


@register.inclusion_tag('users/_trade_form.html')
def trade_form(stock):
    form = TransactionForm()
    return {'form': form, 'stock': stock }


@register.inclusion_tag('users/_order_form.html')
def order_form(stock):
    form = OrderForm()
    return {'form': form, 'stock': stock }


@register.simple_tag(name="current_value")
def current_value(quantity, price):
    return quantity * price


@register.simple_tag()
def activate_portfolio_link(portfolio, return_address):
    return "/user/switch_portfolio?portfolio_id=%d&redirect_address=%s" % (portfolio.pk, return_address)

@register.inclusion_tag('users/_history.html')
def owned_history_table(owned):
    history = owned.transaction_set.all()
    return {'history': history}
    

# @register.filter(name='get_price')
# def get_price(self, stock_ticker):
#     return api.get_price(stock_ticker)

# @register.filter(name='get_change')
# def get_change(self, stock_ticker):
#     return api.get_change(stock_ticker)

# @register.filter(name='get_volume') 
# def get_volume(self, stock_ticker):
#     return api.get_volume(stock_ticker)

# @register.filter(name='get_username') 
# def get_username(self):
#     profile = UserProfile.objects.get(id=self.user_profile_id)
#     return User.objects.get(id=profile.user_id).username
