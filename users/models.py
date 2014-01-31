from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from portfolios.models import Portfolio
from games.models import Game


class UserProfile(models.Model):
    """
    Maintains any game specific data for the users.
    Because we're using django.contrib.auth for accounts, authentication, 
    ect., this is where anything that isn't in .auth.User goes.
    
    Among other things, this will hold the users Portfolio(s).
    """

    # Links the profile to a user.
    user = models.OneToOneField(User)

    def get_active_portfolios(self):
        return self.portfolio_set.filter(active=True)

    def join_game(self, game_id):
        game = Game.objects.get(pk=game_id)
        return Portfolio.objects.create(user_profile=self, game=game, cash=game.initial_funds, winnings=0, active=True)

    def current_games_pks(self):
        return self.portfolio_set.values_list('game', flat=True)


# This creates a UserProfile for a new User whenever one is created.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile.objects.create(user=instance)
