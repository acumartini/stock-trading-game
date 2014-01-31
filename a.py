from stocks.models import Stock
import stocks.api as api
# from users.models import User, Portfolio, Orders
# from games.models import Game, RandomAgent, Agent
# from datetime import date, timedelta
# from lib.django_cron.models import Cron

a = Stock.objects.get(ticker="AAPL")

# agents = Agent.objects.select_subclasses()
# for a in agents:
# 	print a.name
# 	print a.portfolio.cash
# 	print len(a.portfolio.ownedstock_set.all())
# 	print ''