from django.forms import ModelForm

from games.models import Game

class GameForm(ModelForm):

    class Meta:
        model = Game
        fields = ("game_name", "start_date", "end_date", "initial_funds", "brokerage_fee")

