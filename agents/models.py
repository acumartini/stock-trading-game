from django.db import models
from django.utils import timezone
from lib.django_model_utils.model_utils.managers import InheritanceManager

from stocks.models import Stock
import stocks.api as api

import random, math


# frequency def
normal=28800 
aggressive=3600
lazy=86400
# top 20 key def
keys = ['volume', 'open_price', 'change', 'percent_change', 'days_low', 'year_low', 'year_high']


class Agent(models.Model):
    """
    This class defines the framework and methods for computer opponents to maintain 
    and manage portfolios within a game.
    Each agent tracks and makes decisions based on the following things:
        - Money: Current assets and how to best use them to increase equity.
        - Stocks: Status of owned stocks and what stocks are good to buy based on agent's 
          beliefs and utility function.
    """
    # Belongs to a user profile and a game
    game = models.ForeignKey('games.Game')
    name = models.SlugField(max_length=30, unique=True, help_text="Only letters, numbers, underscores, and hyphens.")
    frequency = models.IntegerField() # length of time in seconds between excution of Agent actions
    last_execute = models.DateTimeField(null=True)

    # Custom manager to resolve subclasses
    # Agent.objects.select_subclasses() gives resolved objects.
    # Note: this is a QuerySet just like any other, so you can chain this.
    # Agent.objects.select_subclasses().filter(thing=thang).reverse() works.
    objects = InheritanceManager()

    # Functional methods

    def ready_to_execute(self):
        """
        @returns: True if the agent is ready to make more trades.
        """
        if self.last_execute == None:
            return True
        time_delta = timezone.now() - self.last_execute
        #print time_delta.seconds
        #print time_delta.days
        if (time_delta.seconds + 86400*time_delta.days) >= self. frequency:
            return True # time (or past time) to execute again
        else:
            return False


    """
    #######################################
    # PRIVATE METHODS AND DATA STRUCTURES #
    #######################################
    """


    def purchase_stock(self, stock, quantity):
        self.portfolio.purchase_stock(stock.ticker, quantity)        

    def sell_stock(self, stock, quantity):
        self.portfolio.sell_stock(stock.ticker, quantity)

    def get_random_stock(self):
        all_tickers = Stock.objects.values_list('ticker')
        random_ticker = random.choice(all_tickers)[0]
        return api.get_stock(random_ticker)

    def get_random_top20(self, key=None):
        random_index = random.randint(0, 19)
        if key == None:
            random_key = random.choice(keys)
            stocks = Stock.objects.top20(random_key)
            return stocks[random_index]
        else:
            stocks = Stock.objects.top20(key)
            return stocks[random_index]

    def get_random_bottom20(self, key=None):
        random_index = random.randint(0, 19)
        if key == None:
            random_key = random.choice(keys)
            stocks = Stock.objects.bottom20(random_key)
            return stocks[random_index]
        else:
            stocks = Stock.objects.bottom20(key)
            return stocks[random_index]

    def get_random_owned_stock(self):
        owned_stocks = self.portfolio.ownedstock_set.filter(watch=False)
        return random.choice(owned_stocks)

    def get_top_owned(self, key, amount=None):
        tickers = [owned_stock.ticker for owned_stock in self.portfolio.ownedstock_set.all()]
        stocks = api.get_stocks(*tickers)
        try:
            if amount == 'large':
                num_sell = random.randint(int(.75*len(tickers), len(tickers)))
            elif amount == 'moderate':
                num_sell = random.randint(int(.40*len(tickers)), int(.60*len(tickers)))
            elif amount == 'small':
                num_sell = random.randint(0, int(.25*len(tickers)))
            elif amount == None:
                if self.frequency == aggressive:
                    num_sell = random.randint(int(.75*len(tickers)), len(tickers))
                elif self.frequency == normal:
                    return random.randint(int(.40*len(tickers)), int(.60*len(tickers)))
                elif self.frequency == lazy:
                    num_sell = random.randint(0, int(.25*len(tickers)))
        except:
            return stocks.order_by(key).reverse()[0:1]
        return stocks.order_by(key).reverse()[0:num_sell]

    def get_bottom_owned(self, key, amount=None):
        tickers = [owned_stock.ticker for owned_stock in self.portfolio.ownedstock_set.all()]
        stocks = api.get_stocks(*tickers)
        try:
            if amount == 'large':
                num_sell = random.randint(int(.75*len(tickers), len(tickers)))
            elif amount == 'moderate':
                num_sell = random.randint(int(.40*len(tickers)), int(.60*len(tickers)))
            elif amount == 'small':
                num_sell = random.randint(0, int(.25*len(tickers)))
            elif amount == None:
                if self.frequency == aggressive:
                    num_sell = random.randint(int(.75*len(tickers)), len(tickers))
                elif self.frequency == normal:
                    return random.randint(int(.40*len(tickers)), int(.60*len(tickers)))
                elif self.frequency == lazy:
                    num_sell = random.randint(0, int(.25*len(tickers)))
        except:
            return stocks.order_by(key)[0:1]
        return stocks.order_by(key)[0:num_sell]

    def get_cash_division_quant(self, stock, amount):
        return math.floor(amount / stock.current_price)

    def possible_quantity(stock):
        return (int(self.portfolio.cash) - self.portfolio.get_transaction_cost()) / int(math.ceil(stock.current_price))

    def get_random_purchase_quantity(self, stock):
        try:
            amount = random.randint(int(stock.current_price), int(self.portfolio.cash))
            return int(amount / stock.current_price)
        except:
            return 1

    def get_large_purchase_quantity(self, stock):
        try:
            return random.randint(int(.75*possible_quantity(stock)), possible_quantity(stock))
        except:
            return 1

    def get_moderate_purchase_quantity(self, stock):
        try:
            return random.randint(int(.40*possible_quantity(stock)), int(60*possible_quantity(stock)))
        except:
            return 1
        
    def get_small_purchase_quantity(self, stock):
        try:
            return random.randint(1, int(.25*possible_quantity(stock)))
        except:
            return 1

    def get_random_sale_quantity(self, owned_stock):
        try:
            return random.randint(1, owned_stock.quantity)
        except:
            return 1

    def get_large_sale_quantity(self, owned_stock):
        try:
            return random.randint(int(.75*owned_stock.quantity), owned_stock.quantity)
        except:
            return 1

    def get_moderate_sale_quantity(self, owned_stock):
        try:
            return random.randint(int(.40*owned_stock.quantity), int(.60*owned_stock.quantity))
        except:
            return 1

    def get_small_sale_quantity(self, owned_stock):
        try:
            return random.randint(1, int(.25*owned_stock.quantity))
        except:
            return 1

    def get_random_sell_list(self):
        num_sell = random.randint(1, len(self.portfolio.ownedstock_set.all()))
        sell_list = []
        count = 0
        while count < num_sell:
            sell_list.append(self.get_random_owned_stock())
            count += 1
        return sell_list

    def get_large_sell_list(self):
        try:
            num_sell = random.randint(int(.75*len(self.portfolio.ownedstock_set.all())), len(self.portfolio.ownedstock_set.all()))
        except:
            num_sell = 1
        sell_list = []
        count = 0
        while count < num_sell:
            sell_list.append(self.get_random_owned_stock())
            count += 1
        return sell_list

    def get_moderate_sell_list(self):
        try:
            num_sell = random.randint(int(.40*len(self.portfolio.ownedstock_set.all())), int(.60*len(self.portfolio.ownedstock_set.all())))
        except:
            num_sell = 1
        sell_list = []
        count = 0
        while count < num_sell:
            sell_list.append(self.get_random_owned_stock())
            count += 1
        return sell_list

    def get_small_sell_list(self):
        try:
            num_sell = random.randint(0, int(.25*len(self.portfolio.ownedstock_set.all())))
        except:
            num_sell = 1
        sell_list = []
        count = 0
        while count < num_sell:
            sell_list.append(self.get_random_owned_stock())
            count += 1
        return sell_list

    def __unicode__(self):
        return "%s - Agent" % self.name
        
               
class RandomAgent(Agent):
    """
    Buys and sells stock randomly.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(4, 18)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_stock()
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_stock()
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_stock()
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_stock()
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_large_sell_list():
                    sale_quantity = self.get_large_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == normal:
                for owned_stock in self.get_random_sell_list():
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_small_sell_list():
                    sale_quantity = self.get_small_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_small_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Random Agent" % self.name + " with frequency %s" %self.frequency


class DiverseRandomAgent(Agent):
    """
    Buys and sells stock randomly, maintaining a diverse portfolio.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(18, 25)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_stock()
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_stock()
                quantity = self.get_cash_division_quant(stock, cash_division)
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_stock()
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_stock()
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_large_sell_list():
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_small_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == normal:
                for owned_stock in self.get_random_sell_list():
                    sale_quantity = self.get_small_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_small_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_small_sell_list():
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_stock()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_stock()
                    quantity = self.get_small_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Diverse Random Agent" % self.name + " with frequency %s" %self.frequency


class Top20Agent(Agent):
    """
    Buys and sell stocks randomly from the top 20 lists.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(4, 18)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_top20()
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_top20()
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_top20()
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_top20()
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_large_sell_list():
                    sale_quantity = self.get_large_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20()
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == normal:
                for owned_stock in self.get_random_sell_list():
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20()
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_small_sell_list():
                    sale_quantity = self.get_small_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20()
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20()
                    quantity = self.get_small_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Random Top 20 Agent" % self.name + " with frequency %s" %self.frequency


class HighVolumeAgent(Agent):
    """
    Buys and stock based on greatest trading volume.
    Sells stock based on aggressiveness.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(15,20)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_top20('volume')
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_top20('volume')
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_top20('volume')
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_top20('volume')
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_large_sell_list():
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('volume')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('volume')
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity)
            elif self.frequency == normal:
                for owned_stock in self.get_random_sell_list():
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('volume')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('volume')
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_small_sell_list():
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('volume')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('volume')
                    quantity = self.get_moderate_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - High Volume Agent" % self.name + " with frequency %s" %self.frequency


class BuyHighSellHighAgent(Agent):
    """
    Buys and sells stock based on greatest positve change in price.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(15, 20)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_top20('percent_change')
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_top20('percent_change')
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_top20('percent_change')
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_top20('percent_change')
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity)
            elif self.frequency == normal:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_moderate_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Buy High Sell High Agent" % self.name + " with frequency %s" %self.frequency


class BuyHighSellLowAgent(Agent):
    """
    Buys stock based on greatest positve change in price.
    Sells stock based on greatest negative change in price.
    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(15, 20)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_top20('percent_change')
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_top20('percent_change')
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_top20('percent_change')
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_top20('percent_change')
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity)
            elif self.frequency == normal:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_top20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_top20('percent_change')
                    quantity = self.get_moderate_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Buy High Sell Low Agent" % self.name + " with frequency %s" %self.frequency


class BuyLowSellLowAgent(Agent):
    """
    Buys and sells stock based on greatest negative change in price.

    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(15, 20)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_bottom20('percent_change')
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_bottom20('percent_change')
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_bottom20('percent_change')
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_bottom20('percent_change')
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity)
            elif self.frequency == normal:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_bottom_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_moderate_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Buy Low Sell Low Agent" % self.name + " with frequency %s" %self.frequency


class BuyLowSellHighAgent(Agent):
    """
    Buys stock based on greatest negative change in price.
    Sells stock based on greatest positve change in price.

    """

    def execute(self):
        if self.last_execute == None:
            # new agent - populate the portfolio
            num_divisions = random.randint(15, 20)
            cash_division = int(self.portfolio.cash / num_divisions)
            count = 0
            while count < num_divisions:
                stock = self.get_random_bottom20('percent_change')
                while stock == None or stock.current_price > cash_division:
                    stock = self.get_random_bottom20('percent_change')
                quantity = self.get_cash_division_quant(stock, random.randint(0, cash_division))
                self.purchase_stock(stock, quantity)                
                count += 1
            while self.portfolio.cash > 50:
                stock = self.get_random_bottom20('percent_change')
                while stock == None or stock.current_price > self.portfolio.cash:
                    stock = self.get_random_bottom20('percent_change')
                quantity = self.get_random_purchase_quantity(stock)
                self.purchase_stock(stock, quantity)                
        else:
            # buy and sell randomly based on aggressiveness              
            if self.frequency == aggressive:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_large_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity)
            elif self.frequency == normal:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_random_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_random_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            elif self.frequency == lazy:
                for owned_stock in self.get_top_owned('percent_change'):
                    sale_quantity = self.get_moderate_sale_quantity(owned_stock)
                    self.sell_stock(owned_stock, sale_quantity)
                while self.portfolio.cash > 50:
                    stock = self.get_random_bottom20('percent_change')
                    while stock == None or stock.current_price > self.portfolio.cash:
                        stock = self.get_random_bottom20('percent_change')
                    quantity = self.get_moderate_purchase_quantity(stock)
                    self.purchase_stock(stock, quantity) 
            else:
                print "agent.execute error: frequency matching problem"

        # set the last_execute time and save the agent
        self.last_execute = timezone.now()
        self.save()

    def __unicode__(self):
        return "%s - Buy Low Sell High Agent" % self.name + " Frequency - %s" %self.frequency


class IntelligentAgent(Agent):
    """
    Buys and sells lots of stocks based on data mining of historical stock info.
    """

    def execute(self):
        pass

    def __unicode__(self):
        return "%s - Intellegent Agent" % self.name + " Frequency - %s" %self.frequency
   
