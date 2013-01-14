from lib.django_cron import cronScheduler, Job

from stocks.api import update_stocks

class UpdateStocks(Job):
    # Run every 2 hours
    run_every = 2*60*60
        
    def job(self):
        print "Django_cron is currently doing some batch work."
        update_stocks()
        print "Done :D"

cronScheduler.register(UpdateStocks)