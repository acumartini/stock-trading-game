"""
@newfield renders: Renders
@newflied redirects: Redirects
"""

from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404

from games.models import Game
from games.forms import GameForm
from agents.forms import CreateAgentForm

def index(request):
    """
    Renders a list of every user.

    @renders: users/index.html
    """
    all_games = Game.objects.all()
    return render(request, 'games/index.html', {'all_games': all_games})


def detail(request, gamename):
    """
    Renders a detailed game view of a single game.

    @param username: The username of the profile to render
    @renders: games/detail.html
    """    
    game = get_object_or_404(Game, game_name__exact=gamename)
    form = CreateAgentForm()
    creator = game.creator.user
    return render(request, 'games/detail.html', {'game': game, 'form': form, 'creator': creator})


def new(request):
    """
    Renders the signup form, allowing a user to create a new user.
    Processes results from the form, attempting to create a new user.
    If new user is created, redirects to the users profile

    @renders: users/new.html to show the signup form
    @redirects: /game/<username> to show the newly created users profile.
    """
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            new_game = form.save()
            profile = request.user.get_profile()
            new_game.creator = profile
            new_game.save()
            profile.join_game(new_game.pk)
            return redirect("/games/" + new_game.game_name)
    else:
        form = GameForm()
    return render(request, "games/new.html", {'form': form})


def add_agent(request):
    if request.method == 'POST':
        form = CreateAgentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            game = Game.objects.get(pk=data['game_pk'])
            
            if data['agent_aggression'] == "Normal":
                data['agent_aggression'] = ''
            
            game.add_agent(data['agent_name'], data['agent_aggression'] + data['agent_type'])
            
            return redirect("/games/" + game.game_name)
        else:
            print form.errors
    
    raise Http404
