from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

from stocks.models import Stock
import stocks.api as api

import random

class Portfolio(models.Model):
    """
    Maintains and manages the state of a users portfolio within a game.
    Tracks the following things:
        - Money: How much cash the user has to spend on stocks.
        - Stocks: What stocks are owned, what were paid for them.
        - Watchlist: Stocks that the user wants to keep an eye on.
        - History: A transaction history of stock trades.
    """

    # Belongs to a user profile and a game
    user_profile = models.ForeignKey('users.UserProfile', null=True)
    agent = models.OneToOneField('agents.Agent', null=True)
    game = models.ForeignKey('games.Game')

    cash = models.IntegerField()
    winnings = models.FloatField()
    active = models.BooleanField()
    ai_opponent = models.BooleanField()

    # Informational Methods

    def name(self):
        return self.game.game_name

    def update(self):
        if not self.active:
            return
        self.winnings = self.get_winnings()
        self.save()

    def get_username(self):
        if not self.ai_opponent:
            return self.user_profile.user.username
        else: # this is an ai opponent
            return self.agent.name

    def get_winnings(self):
        return self.get_equity() - self.game.initial_funds 

    def get_equity(self):
        equity = self.cash
        for owned_stock in self.ownedstock_set.all():
            stock = api.get_stock(owned_stock.ticker)
            equity += stock.current_price * owned_stock.quantity
        return equity
    
    def get_transaction_cost(self):
        return self.game.brokerage_fee

    def get_brief_stocks(self):
        """
        Generates a list of consise summaries for all currently owned stocks.
        
        This list should contain:
            - The company name and ticker.
            - The current price of the stock.
            - The net gain/loss on the owned stocks.
            
        @returns: A list of consise summaries.
        """
        self.update() # update portfolio info

        portfolio_stocks = self.ownedstock_set.order_by('ticker').all()
        port_summary = []
        for owned_stock in portfolio_stocks:
            if owned_stock.quantity > 0:
                stock = api.get_stock(owned_stock.ticker)
                port_summary.append((owned_stock, stock))

        return port_summary

    
    def get_brief_watched(self):
        """
        Generates a list of summaries for all currently watched stocks.

        This list should contain:
            - The company name and ticker.
            - The current price of the stock.
            - Some useful indicator of recent stock porformance.
            
        @returns: A list tuples containing the ownedstock, and the stock object for each watched stock.
        """
        watched_stocks = self.ownedstock_set.filter(watch=True, quantity=0)
        watch_summary = []
        for stock_data in watched_stocks:
            stock = api.get_stock(stock_data.ticker)
            watch_summary.append((stock_data, stock))
        return watch_summary


    def watch_stock(self, stock_ticker):
        """
        Adds the given stock to the portfolio's watch list.
        
        @param stock: The stock to be added to the watch list.
        """
        owned_stock, new = self.ownedstock_set.get_or_create(ticker=stock_ticker, defaults = { 
                'quantity': 0,
                'purchase_price': 0,
                'watch': True,
            })
        if not new:
            owned_stock.watch = True
        
        owned_stock.save()

    
    def unwatch_stock(self, stock_ticker):
        """
        Removes the given stock to the portfolio's watch list.
        
        @param stock: The stock to be removed from the watch list.
        """
        owned_stock = self.ownedstock_set.get(ticker=stock_ticker)
        # If stock exists in the portfolio change its watched state, else print Error
        if owned_stock != None:
            owned_stock.watch = False
            owned_stock.save()
        else:
            # TODO: add error to html
            print "Error: You are already watching this stock."         


    def create_order(self, stock_ticker, price, transaction, trade='sell', quantity=0):
        # get the owned stock object
        owned_stock, new = self.ownedstock_set.get_or_create(ticker=stock_ticker, defaults = { 
                'quantity': 0,
                'purchase_price': 0,
                'watch': False,
            })

        stock = api.get_stock(stock_ticker)
        # check for price equivalence before creating an order
        if price == stock.current_price:
            # get the portfolio associated with this owned stock to make transaction
            portfolio = Portfolio.objects.get(ownedstock_id=owned_stock.id)
            if transaction == 'STOP_LOSS':
                portfolio.sell_stock(owned_stock.ticker, owned_stock.quantity)
            if transaction == 'LIMIT':
                if trade == 'sell':
                    portfolio.sell_stock(owned_stock.ticker, quantity)
                else: # buy
                    portfolio.sell_stock(owned_stock.ticker, quantity)
            return

        # check the transaction type and create the order accordingly
        if transaction == 'STOP_LOSS':
            owned_stock.orders_set.create(ticker= owned_stock.ticker, 
                                          buy_sell=0,
                                          limit_stoploss=0, 
                                          order_quantity=quantity, 
                                          order_price=price, 
                                          creation_price=stock.current_price)
        elif transaction == 'LIMIT':
            trade_type = 0 if trade == 'sell' else 1
            owned_stock.orders_set.create(ticker= owned_stock.ticker,
                                          buy_sell=trade_type, 
                                          limit_stoploss=1,
                                          order_quantity=quantity,
                                          order_price=price,
                                          creation_price=stock.current_price)
        else:
            print 'create_order error: unrecognized transaction type'
            return False
        
        return True


    def purchase_stock(self, stock_ticker, quantity):
        """
        'Purchases' the given number of the given stock.
        Modeling this has three steps:
            - Deducting the money from the portfolio
            - Adding the stocks to the list of owned stocks.
            - Adding the transaction to the transaction history.
        
        @param stock: The stock to be purchased.
        @param quantity: The number of stocks to be purchased.
        
        @return: True if the purchase is successful, else False
        """
        # Error checking
        quantity = int(quantity)
        if quantity <= 0:
            print "Quantity"
            return False

        stock = api.get_stock(stock_ticker)
        if stock == None:
            return False

        purchase_cost = quantity * stock.current_price + self.get_transaction_cost()
        if purchase_cost > self.cash:
            print "cost"
            return False

        # Create or update the stock record
        # new is a boolean for whether or not it was created
        # get_or_create, filter, get...
        owned_stock, new = self.ownedstock_set.get_or_create(ticker=stock.ticker, defaults = { 
                'quantity': 0,
                'purchase_price': 0,
                'watch': False,
            })
        owned_stock.quantity += quantity
        owned_stock.purchase_price += purchase_cost
        owned_stock.save()

        # Create a transaction entry.
        transaction = owned_stock.transaction_set.create(trans_quantity=quantity, trans_price=stock.current_price, trans_date=timezone.now())
        transaction.save()       

        # Update the portfolio
        self.cash -= purchase_cost
        self.save()
        
        return True


    def sell_stock(self, stock_ticker, quantity):
        """
        'Sells' the given number of the given stock.
        Modeling this has three steps:
            - Removing the stocks from the list of owned stocks.
            - Adding the money to the portfolio
            - Adding the transaction to the transaction history.
        
        @param stock: The stock to be sold.
        @param quantity: The number of stocks to be sold.
        
        @return: True if the sale is successful, else False
        """

        stock = api.get_stock(stock_ticker)
        
        try:
            owned_stock = self.ownedstock_set.get(ticker=stock.ticker)
        except ObjectDoesNotExist:
            return False

        if quantity <= 0:
            return False
        if quantity > owned_stock.quantity:
            return False
        
        sale_price = quantity * stock.current_price - self.get_transaction_cost()
        owned_stock.quantity -= quantity
        owned_stock.save()
        
        # create a transaction entry
        entry_quantity = -1*quantity
        owned_stock.transaction_set.create(trans_quantity=entry_quantity, trans_price=stock.current_price, trans_date=timezone.now())
        
        self.cash += sale_price
        self.save()
        
        return True


class OwnedStock(models.Model):

    # Belongs to a portfolio and a stock
    portfolio = models.ForeignKey(Portfolio, null=True)
    stock_data = models.ForeignKey(Stock, null=True) # True for now, but should be False once the stock database is setup!
    
    ticker = models.CharField(max_length=10)
    quantity = models.IntegerField()
    purchase_price = models.IntegerField()
    watch = models.BooleanField()


class Orders(models.Model):

    # Belongs to a owned stock
    ownedstock = models.ForeignKey(OwnedStock, null=True)

    ticker = models.CharField(max_length=10) # to simplify getting a list of orders for a stock signal
    limit_stoploss = models.BooleanField() # True or 1 => limit, False or 0 => stop loss order
    buy_sell = models.BooleanField() # True or 1 => buy, False or 0 => sell
    order_quantity = models.IntegerField() # note: only used for limit orders beacuse stop loss referenes the current owned_stock.quantity
    creation_price = models.FloatField()
    order_price = models.FloatField()


class Transaction(models.Model):
  
    # Belongs to a owned stock
    ownedstock = models.ForeignKey(OwnedStock, null=True)
    
    trans_quantity = models.IntegerField()
    trans_price = models.FloatField()
    trans_date = models.DateTimeField()
    

# orders signals processessing
@receiver(post_save, sender=Stock)
def check_orders(sender, instance, **kwargs):

    # Ignore saves for brand new stocks.
    # - Raw saves imply inconsistant db (mid-syncdb)
    # - Newly created stocks can't yet have any orders.
    if kwargs['raw'] or kwargs['created']:
        return

    try:
        stock = Stock.objects.get(id=instance._get_pk_val())
    except:
        print 'check_orders error: unable to get stock from the database'
        return False
    # get a list of all orders dealing with this stock
    orders = Orders.objects.filter(ticker=stock.ticker)
    
    if len(orders) > 0:
        for order in orders:
            # get the owned_stock associated with this order
            owned_stock = OwnedStock.objects.get(id=order.ownedstock_id)
            # get the portfolio related with this owned_stock
            portfolio = Portfolio.objects.get(id=owned_stock.portfolio_id)    

            if order.limit_stoploss: # True, then it is a limit order
                if order.creation_price < order.order_price: # this person is looking for a value >= tp their order_price
                    if stock.current_price >= order.order_price:
                        if order.buy_sell:  # True, then it is a limit puchase order
                            portfolio.purchase_stock(order.ticker, order.order_quantity)
                            order.delete()
                        else: # sell
                            portfolio.sell_stock(order.ticker, order.order_quantity)
                            order.delete()
                elif order.creation_price > order.order_price: # this person is looking for a value >= tp their order_price
                    if stock.current_price <= order.order_price:
                        if order.buy_sell:  # True, then it is a limit puchase order
                            portfolio.purchase_stock(order.ticker, order.order_quantity)
                            order.delete()
                        else: # sell
                            portfolio.sell_stock(order.ticker, order.order_quantity)
                            order.delete()
            else: # order is a stop loss order
                if stock.current_price <= order.order_price:
                    portfolio.sell_stock(order.ticker, owned_stock.quantity) # sell all of the owned_stock
                    order.delete()
