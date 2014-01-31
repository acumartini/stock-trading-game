"""
@newfield renders: Renders
@newflied redirects: Redirects
"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test

def home(request):
    """
    Displays the home screen for the application.
    
    @renders: app/home.html
    @redirects: users profile if they're currently logged in.
    """
    if request.user.is_authenticated():
        return redirect('user/' + request.user.username)
    
    return render(request, 'app/home.html')


def help(request):
    """
    Displays a help screen for the application.
    
    @renders: app/help.html
    """
    pass