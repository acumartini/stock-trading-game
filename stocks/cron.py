from lib.django_cron import cronScheduler, Job

from stocks.api import update_stocks, update_industries, update_tickers

class UpdateStocks(Job):
    # Run every 2 hours
    run_every = 2*60*60
        
    def job(self):
        print "Django_cron is currently doing some batch work."
        try:
            update_stocks()
        except:
            print "UpdateStocks died for an unknown reason."
        print "Done :D"

cronScheduler.register(UpdateStocks)

class UpdateDB(Job):
    run_evere = 24*60*60
    
    def job(self):
        try:
            update_industries()
            update_tickers()
        except:
            print "UpdateDB died for an unknown reason."


cronScheduler.register(UpdateDB)
