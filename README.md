# README by Thursday

## Preping the database
The database has gotten a little fancier, and now locally stores stock data. While there is an initial_data dump that will get loaded any time you run syncdb, we now have some commands to batch update the local data.

    # Created a db and populates it with data from 4am, 11/15
    # You're good to go if you want to, just with old data.
    python manage.py syncdb
    
    # Makes sure all stocks in database are relatively up to date
    python manage.py batch_update
    
    # Same as batch_update, but also checks for missing stocks
    python manage.py batch_update --tickers

