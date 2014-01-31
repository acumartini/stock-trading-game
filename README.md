# README by Thursday

## Main tools for website construction
This project uses Django which is a web framework developed in Python for constructing and maintaining the modules written within this API. This project also utilises Yahoo Finance and its YQL interface for stock information
retrieval.
    
### Django
Information for Django can be found here: https://www.djangoproject.com/ and its documentation can be found here: https://docs.djangoproject.com/en/1.4/

### YQL
Information about the Yahoo Finance API for the YQL interface can be found here: 
http://developer.yahoo.com/yql/    

## Preping the database
The database has gotten a little fancier, and now locally stores stock data. While there is an initial_data dump 
that will get loaded any time you run syncdb, we now have some commands to batch update the local data.

    # Created a db and populates it with data from 4am, 11/15
    # You're good to go if you want to, just with old data.
    python manage.py syncdb

    # Makes sure all stocks in database are relatively up to date
    python manage.py batch_update

    # Same as batch_update, but also checks for missing stocks
    python manage.py batch_update --tickers


## API documentation
Specific information about modules and functions of our projects API 
can be found here: http://ix.cs.uoregon.edu/~martini/cis422/apidocs/index.html

Listed below are all of the modules that can be found in our source code along with explanations of what they do and a quick explanation of what can be found in each module.

### General Scructure of a module
Includes four primary layers:

-The _init_.py layer initializes the module structure.
-The models.py layer establishes and defines the structure of the module class. Each Attribute in this layer represents a database field.
-The template layers are  text files that establish the look of each webpage that corresponds to the particule module.
-The views.py layer are a collection of Python functions which takes a web request and returns a web response.

### Agents
Defines the framework and methods for computer opponents to maintain and manage portfolios 
within a game.Each agent tracks and makes decisions based on the following things:

- Money: Current assets and how to best use them to increase equity.
- Stocks: Status of owned stocks and what stocks are good to buy based on agent's beliefs and utility function.
        
### Games
Maintains and manages the state of a game. Tracks the following things:

- Start and End Date
- Player performance
    
### Portfolios
Maintains and manages the state of a users portfolio within a game. Tracks the following things:

- Money: How much cash the user has to spend on stocks.
- Stocks: What stocks are owned, what were paid for them.
- Watchlist: Stocks that the user wants to keep an eye on.
- History: A transaction history of stock trades.

### Stocks
Maintains and manages representations stock objects. Stock tickers that are specifically looked up using the These are currently storred in the database

### Trade_by_thursday
Main module for setting up and maintaining all other modules within the website

### Users
Maintains any game specific data for the users. Because we're using django.contrib.auth for accounts, authentication, ect., this is where anything that isn't in .auth.User goes. Among other things, this will hold the users Portfolio(s).

##List of outside libraries

### django_cron
Functions and interfaces that provide tools to cyclicly run subroutines.    

### django_models_utils
Provides tools to automatically create and manage SQL Tables in a database.



