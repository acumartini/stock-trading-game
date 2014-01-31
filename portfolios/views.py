# Create your views here.

from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from portfolios.forms import TransactionForm, OrderForm
import users.sessions as session


@require_http_methods(["POST"])
def trade_stock(request):
    form = TransactionForm(request.POST)
    if form.is_valid():
        portfolio = session.get_active_portfolio(request)
        data = form.cleaned_data
        if data['transaction'] == 'BUY':
            portfolio.purchase_stock(data['stock'], data['quantity'])
            # messages.add_message(request, messages.INFO, "Hypothetically, you've bought some stock.")

        elif data['transaction'] == 'SELL':
            portfolio.sell_stock(data['stock'], data['quantity'])
        
        return redirect("/user/" + request.user.username)


@require_http_methods(["POST"])
def watch_stock(request, watch=True):
    portfolio = session.get_active_portfolio(request)
    stock = request.POST['stock']
    # TODO error checking
    if watch:
        portfolio.watch_stock(stock)
    else:
        portfolio.unwatch_stock(stock)
        
    return redirect("/user/" + request.user.username)


@require_http_methods(["POST"])
def make_order(request):
    form = OrderForm(request.POST)
    if form.is_valid():
        portfolio = session.get_active_portfolio(request)
        data = form.cleaned_data
        if data['order_type'] == 'STOP_LOSS':
            portfolio.create_order(data['stock'], data['trigger_price'], data['order_type'])
        elif data['order_type'] == 'LIMIT':
            portfolio.create_order(data['stock'], data['trigger_price'], data['order_type'], data['trade_type'], data['quantity'])

    return redirect("/user/" + request.user.username)

