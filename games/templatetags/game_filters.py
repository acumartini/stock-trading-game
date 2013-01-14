from django import template

from games.models import Game

# register for template function calls to custom filters
register = template.Library()

# custom filters
"""
Returns a list of games that are currently active
"""
@register.filter(name='get_active_games')
def get_active_games(all_games):
    active_games = []
    for game in all_games:
        if game.is_active():
            active_games.append(game)
    return active_games

"""
Returns a list of games that are past their ending date
"""
@register.filter(name='get_past_games')
def get_past_games(all_games):
    past_games = []
    for game in all_games:
        if not game.is_active():
            past_games.append(game)
    return past_games

@register.filter(name='get_num_players')
def get_num_players(game):
    return game.portfolio_set.all().count()


@register.filter(name='get_duration')
def get_duration(game):
    return (game.end_date - game.start_date).days

@register.filter(name='get_results')
def get_results(game):
    winner = game.get_winner()
    if winner != None:
        return winner.get_username + ' earned ' + winner.winnings
    else:
        return 'No Winner'