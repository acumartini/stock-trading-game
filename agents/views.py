"""
@newfield renders: Renders
@newflied redirects: Redirects
"""

from django.shortcuts import get_object_or_404, render, redirect

from agents.models import Agent


def detail(request, botname):
    """
    Renders a detailed profile view of a single AI Agent.
    
    @param username: The username of the profile to render
    @renders: users/detail.html
    """
    agent = get_object_or_404(Agent, name__exact=botname)
    portfolio = agent.portfolio

    return render(request, 'agents/detail.html', {
        'agent': agent,
        'portfolio': portfolio, 
    })
