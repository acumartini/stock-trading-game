from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout, logout_then_login

# Admin stuff
from django.contrib import admin
admin.autodiscover()

# Django Cron
import lib.django_cron as django_cron
django_cron.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'trade_by_thursday.views.home', name='home'),

    url(r'^users/$', 'users.views.index', name='all_users'),
    url(r'^user/(?P<username>\w+)/$', 'users.views.detail'),
    url(r'^signup/$', 'users.views.new', name='signup'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    # This was from trying redirect logouts to a less useless page.
    # Can't use it until I have a way to tell people they logged out.
    # url(r'^logout/$', logout_then_login, {'login_url': 'login'}, name='logout'),
    url(r'^user/join_game$', 'users.views.join_game'),
    url(r'^user/switch_portfolio$', 'users.views.activate_portfolio'),


    url(r'^agent/(?P<botname>\w+)/$', 'agents.views.detail'), 
 
 
    url(r'^portfolio/trade$', 'portfolios.views.trade_stock', name='trade'),
    url(r'^portfolio/watch$', 'portfolios.views.watch_stock', name='watch'),
    url(r'^portfolio/unwatch$', 'portfolios.views.watch_stock', { 'watch': False }, name='unwatch'),
    url(r'^portfolio/make_order$', 'portfolios.views.make_order', name='make_order'),

    
    url(r'^games/$', 'games.views.index', name='all_games'),
    url(r'^games/(?P<gamename>[\w\s]+)/$', 'games.views.detail'),
    url(r'^games/new$', 'games.views.new'),
    url(r'^games/add_agent$', 'games.views.add_agent'),
    
    
    url(r'^stocks/search/$', 'stocks.views.search'),
    url(r'^stocks/top/(?P<num>\d+)/(?P<reverseSort>\w+)/$', 'stocks.views.get_top'),
    url(r'^stocks/top/(?P<num>\d+)/$', 'stocks.views.get_top'),
    url(r'^stocks/top/$', 'stocks.views.get_top'),
    # url(r'^stocks/mostsearched/$', 'stocks.views.get_mostSearched'),
    # url(r'^stocks/mosttrades/$', 'stocks.views.get_mostTrades'),
    url(r'^stock/$', 'stocks.views.search'),
    url(r'^stocks/(?P<page>\d+)/$', 'stocks.views.all'),
    url(r'^stocks/$', 'stocks.views.all'),
    url(r'^stock/(?P<ticker>\w+)/$', 'stocks.views.detail'),
    # url(r'^stock/(?P<ticker>\w+)/history/$', 'stocks.views.get_history'),
    # url(r'^stock/(?P<ticker>\w+)/history/(?P<daysbefore>\d+)/$', 'stocks.views.get_history'),
    # url(r'^stock/(?P<ticker>\w+)/history/(?P<daysbefore>\d+)/(?P<startDate>\d+)/$', 'stocks.views.get_history'),
)
