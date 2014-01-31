from django.core.exceptions import ValidationError
from django.db import models

from agents.models import *

from django.utils import timezone
import datetime
import re

def validate_direction_of_time(value):
    if value < timezone.now().date():
        raise ValidationError(u'End date must be after todays date.')


class Game(models.Model):
    """
    Maintains and manages the state of a game.
    Tracks the following things:
        - Start and End Date
        - Player performance
    """
    game_name = models.SlugField(max_length=30, unique=True, help_text="Only letters, numbers, underscores, and hyphens.")
    start_date = models.DateField(help_text='MM/DD/YY')
    end_date = models.DateField(help_text='MM/DD/YY', validators=[validate_direction_of_time])
    initial_funds = models.IntegerField(help_text="Whole dollars only. '10250'")
    brokerage_fee = models.FloatField(help_text='12.34', default=0)
    creator = models.ForeignKey('users.UserProfile', null=True)

    
    # Informational Methods
    def is_active(self):
        return datetime.date.today() < self.end_date


    def get_ordered_portfolios(self):
        portfolios = self.portfolio_set.all()
        # for p in portfolios:
        #     p.update()

        return sorted(portfolios, key=lambda p: p.winnings, reverse=True)
        # TODO: write a batch function so that you can use this.
        # return self.portfolio_set.all().order_by('winnings').reverse()
        

    def add_agent(self, agent_name, agent_type):
        """
        Pre:    A Game is been created for which the user wants to add a computer opponent.
        Post:   Creates an AI Agent with a profile based on user input and game specific portfolio

        @param  game: The game the agents will be participating in.
        @param  name: The name of the computer opponent entered by the user who creates the game.
        """

        # check for a valid name
        isvalid = re.match(r'[\w-]*$', agent_name)
        if isvalid and len(agent_name) <= 30 and len(agent_name) > 0:
            names = self.agent_set.values_list('name')
            names = [name[0] for name in names]
            if not agent_name in names:
                valid_name = agent_name
            else:
                # recreate form to create an angent
                print "create_agent error: agent name already exists"
                return None
        else:
            print "create_agent error: invalid agent name"
            return None

        new_agent = self.create_agent(valid_name, agent_type)      
        new_portfolio = self.portfolio_set.create(game=self, cash=self.initial_funds, winnings=0, active=self.is_active(), ai_opponent=True)
        
        self.agent_set.add(new_agent)
        # add agent after creation to allow Python to perform duck-typing on Agent subclasses
        new_portfolio.agent = new_agent # because this is a OneToOneField, portfolios and agents can access each other directly (i.e. agent.portfolio)
        
        self.save()
        new_portfolio.save()
        new_agent.save()

        return new_agent


    def create_agent(self, agent_name, agent_type):
        if agent_type == 'RandomAgent':
            return RandomAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveRandomAgent':
            return RandomAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyRandomAgent':
            return RandomAgent(name=agent_name, frequency=lazy)
        if agent_type == 'DiverseRandomAgent':
            return DiverseRandomAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveDiverseRandomAgent':
            return DiverseRandomAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyDiverseRandomAgent':
            return DiverseRandomAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'Top20Agent':
            return Top20Agent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveTop20Agent':
            return Top20Agent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyTop20Agent':
            return Top20Agent(name=agent_name, frequency=lazy)
        elif agent_type == 'HighVolumeAgent':
            return HighVolumeAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveHighVolumeAgent':
            return HighVolumeAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyHighVolumeAgent':
            return HighVolumeAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'BuyHighSellHighAgent':
            return BuyHighSellHighAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveBuyHighSellHighAgent':
            return BuyHighSellHighAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyBuyHighSellHighAgent':
            return BuyHighSellHighAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'BuyHighSellLowAgent':
            return BuyHighSellLowAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveBuyHighSellLowAgent':
            return BuyHighSellLowAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyBuyHighSellLowAgent':
            return BuyHighSellLowAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'BuyLowSellLowAgent':
            return BuyLowSellLowAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveBuyLowSellLowAgent':
            return BuyLowSellLowAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyBuyLowSellLowAgent':
            return BuyLowSellLowAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'BuyLowSellHighAgent':
            return BuyLowSellHighAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveBuyLowSellHighAgent':
            return BuyLowSellHighAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyBuyLowSellHighAgent':
            return BuyLowSellHighAgent(name=agent_name, frequency=lazy)
        elif agent_type == 'IntelligentAgent':
            return IntelligentAgent(name=agent_name, frequency=normal)
        elif agent_type == 'AggressiveIntelligentAgent':
            return IntelligentAgent(name=agent_name, frequency=aggressive)
        elif agent_type == 'LazyIntelligentAgent':
            return IntelligentAgent(name=agent_name, frequency=lazy)
        else:
            print 'create_agent error: unrecognized agent type' + agent_type
            return None
