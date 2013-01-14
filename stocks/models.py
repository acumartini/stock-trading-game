from django.db import models

from django.utils import timezone


class StockManager(models.Manager):
    
    def top20(self, key):
        """
        @returns the top 20 stocks based of the given key
        """
        
        return self.all().order_by(key).reverse()[0:20]

    def bottom20(self, key):
        """
        @returns the bottom 20 stocks based of the given key
        """
        
        return self.all().order_by(key)[0:20]


class Stock(models.Model):
    """
    A basic class to represent stock objects.
    These have the ability to, but are not currently, stored in the database
    """
    objects = StockManager()
    
    company_name = models.CharField(max_length=200)
    ticker = models.CharField(max_length=5, unique=True, db_index=True)
    current_price = models.FloatField()
    volume = models.IntegerField()
    open_price = models.FloatField(null=True, blank=True)
    change = models.FloatField(null=True, blank=True)
    percent_change = models.FloatField(null=True, blank=True)
    days_low = models.FloatField(null=True, blank=True)
    days_high = models.FloatField(null=True, blank=True)
    year_low = models.FloatField(null=True, blank=True)
    year_high = models.FloatField(null=True, blank=True)
    historical_prices = models.CharField(max_length=1000, null=True, blank=True)
    historical_price_date = models.DateTimeField(null=True, blank=True)

    last_updated = models.DateTimeField()
    searched_count = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        # Add a timestamp, so we know how outdated the data is.
        self.last_updated = timezone.now()
        super(Stock, self).save(*args, **kwargs)


    def __unicode__(self):
        return "%s (%s) $%.2f" % (self.company_name, self.ticker, float(self.current_price))
 
 
class StockTicker(models.Model):
    ticker = models.CharField(max_length=7)
    def __unicode__(self):
        return self.ticker


class Industry(models.Model):
    industry = models.CharField(max_length=200)
    industry_id = models.CharField(max_length=4)
    sector = models.CharField(max_length=200)
