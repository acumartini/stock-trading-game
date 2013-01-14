"""
@newfield renders: Renders
@newflied redirects: Redirects
"""

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from users.forms import RegisterForm
import users.sessions as session


def index(request):
    """
    Renders a list of every user.
    
    @renders: users/index.html
    """
    all_users = User.objects.all()
    return render(request, 'users/index.html', {'all_users': all_users})


def detail(request, username):
    """
    Renders a detailed profile view of a single user.
    
    @param username: The username of the profile to render
    @renders: users/detail.html
    """
    profile = get_object_or_404(User, username__exact=username)
    active_portfolios = profile.get_profile().get_active_portfolios()

    if profile == request.user and session.active_portfolio(request):
        portfolio = session.get_active_portfolio(request)
    else:
        portfolio = None

    return render(request, 'users/detail.html', {
        'profile': profile,
        'portfolio': portfolio, 
        'active_portfolios': active_portfolios, 
    })


def new(request):
    """
    Renders the signup form, allowing a user to create a new user.
    Processes results from the form, attempting to create a new user.
    If new user is created, redirects to the users profile
    
    @renders: users/new.html to show the signup form
    @redirects: /user/<username> to show the newly created users profile.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            login(request, new_user)
            return redirect("/user/" + new_user.username)
    else:
        form = RegisterForm()
    return render(request, "users/new.html", {'form': form})


def join_game(request):
    if request.method == 'POST':
        profile = request.user.get_profile()
        portfolio = profile.join_game(int(request.POST['game_id']))
        set_active_portfolio(request, portfolio)
        return redirect("/user/" + request.user.username)


def activate_portfolio(request):
    if request.method == 'GET':
        session.set_active_portfolio_id(request, request.GET['portfolio_id'])
    return redirect(request.GET['redirect_address'])
