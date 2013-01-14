from games.models import Game, Agent
from datetime import date, timedelta
from agents.cron import AgentExecuteCheck

sd = date.today()
ed = sd + timedelta(days=10)
g = Game.objects.get_or_create(game_name="bot game", start_date=sd, end_date=ed, initial_funds=10000)[0]

agent = g.add_agent('bob_bot', 'AggressiveRandomAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('sue_bot', 'LazyRandomAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('john_bot', 'RandomAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('wally_bot', 'AggressiveDiverseRandomAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('anna_bot', 'AggressiveTop20Agent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('fred_bot', 'Top20Agent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('sally_bot', 'AggressiveHighVolumeAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('tom_bot', 'AggressiveBuyHighSellHighAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('mary_bot', 'AggressiveBuyHighSellLowAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('gary_bot', 'AggressiveBuyLowSellHighAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name
agent = g.add_agent('ralph_bot', 'AggressiveBuyLowSellHighAgent')
print "game name: " + g.game_name
print "Agent: " + str(agent)
if agent != None:
	print "agent.name: " + agent.name

print ''
for a in Agent.objects.select_subclasses():
	print a
	print a.portfolio.cash
	print a.portfolio.ownedstock_set.all().count()

print ''

ec = AgentExecuteCheck()
ec.job()
