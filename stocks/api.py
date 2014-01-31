from django.utils import timezone

from stocks.models import Stock, Industry, StockTicker
import urllib, json, datetime, time


QUOTES_TABLE = "yahoo.finance.quotes"
HISTORICAL_TABLE = "yahoo.finance.historicaldata"
SECTORS_TABLE = "yahoo.finance.sectors"
INDUSTRY_TABLE = "yahoo.finance.industry"

QUOTES_SELECT = "Symbol, Name, LastTradePriceOnly, Volume, Open, Change, " + \
                "PercentChange, DaysLow, DaysHigh, YearLow, YearHigh"
HISTORICAL_SELECT = "Date, Close"


# Were going to keep this around for a bit to maintain some backwards compatability, and make things nice nice. Consider this guy deprecated however, and start moving towards accessing stocks through the Model interface.
def get_stock(ticker):
    """
    This returns a stock object populated with data from the Yahoo! API.
    
    @param ticker: The ticker of the stock to return data on.
    @return: A stock object containing information on the stock.
    """
    stocks = get_stocks(ticker)
    if stocks.count() != 1:
        return None
    
    if not stocks[0].historical_price_date or stocks[0].historical_price_date.date() < timezone.now().date():
        update_history(stocks[0])
    return stocks[0]


def get_stocks(*tickers):
    """
    Returns a Stock queryset based of all the tickers, wonderfully updated.
    
    @param *tickers: An arbitrary number of tickers of which to get the stock
    @return: A queryset of Stocks
    """
    stocks = Stock.objects.filter(ticker__in=(t.upper() for t in tickers))
    update_stock(*stocks.filter(last_updated__lt=time_hours_ago(1)))
    return stocks


"""
###################
# PRIVATE METHODS #
###################
"""

def update_stock(*stocks):
    if len(stocks) == 0:
        return
    
    where = 'symbol in ("%s")' % '","'.join([s.ticker for s in stocks])
    query = build_query(QUOTES_SELECT, QUOTES_TABLE, where)
    data_array = query_yahoo(query)

    if not data_array:
        print "Failed to retreive stocks where '%s'" % where
        return

    data_array = data_array['quote']
    
    # Package single elements in a list so we can loop through it
    if type(data_array) == dict:
        data_array = [data_array]

    for stock, data in zip(stocks, data_array):
        # Protect against zip getting offset somehow.
        if stock.ticker != data['Symbol']:
            print "Loop mismatch for %s : %s" % (stock.ticker, data['Symbol'])
            continue
        
        # Prune any stocks that appear to be dead.
        if float(data['LastTradePriceOnly']) == 0:
            try:
                stock.delete()
            except AssertionError:
                print "Error trying to delete stock: %s." % stock.ticker
            continue
        
        
        # Fill the data for the stock object
        update_stock_from_data(stock, data)
        # Check for bad data, and save
        if float(stock.current_price) != 0:
            stock.save()


def update_stock_from_data(stock, data_array):
    stock.ticker = data_array['Symbol']
    stock.company_name = data_array['Name']
    stock.current_price = data_array['LastTradePriceOnly']
    stock.volume = data_array['Volume']
    stock.open_price = data_array['Open']
    stock.change = data_array['Change']
    stock.percent_change = data_array['PercentChange'].rstrip('%')
    stock.days_low = data_array['DaysLow']
    stock.days_high = data_array['DaysHigh']
    stock.year_low = data_array['YearLow']
    stock.year_high = data_array['YearHigh']


def update_history(stock):
    # select * from yahoo.finance.historicaldata where symbol = "YHOO" and startDate = "2009-09-11" and endDate = "2010-03-10"

    where = 'symbol in ("%s") ' % stock.ticker
    where += 'and startDate = "%s" and endDate = "%s"' % (time_hours_ago(14*24).date(), timezone.now().date())
    query = build_query(HISTORICAL_SELECT, HISTORICAL_TABLE, where)
    data_array = query_yahoo(query)

    if not data_array:
        return

    data_array = data_array['quote']
    data_array.reverse()
    
    stock.historical_prices = json.dumps(data_array)
    stock.historical_price_date = timezone.now()
    stock.save()


# Another documentation line of demarcation

def build_query(keys, table, whereclause=None):
    query = 'select %s from %s ' % (keys, table)
    if whereclause:
        query += 'where %s ' % whereclause
    return query


def query_yahoo(query):
    url = 'http://query.yahooapis.com/v1/public/yql?q=' + urllib.quote(query) + '&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env'

    # Open url and get jason format data
    jdata = urllib.urlopen(url).read()

    # Convert jason formated data to normal array
    try:
        data_array = json.loads(jdata)
    except ValueError:
        return None
    
    if data_array['query']['results'] == None:
        return None
    
    return data_array['query']['results']



# Super ghetto db population

def update_industries():
    query = build_query("*", SECTORS_TABLE)
    data = query_yahoo(query)

    if not data:
        return

    for sector in data['sector']:
        sector_name = sector['name']
        sector = sector['industry']
        if type(sector) == dict:
            sector = [sector]

        for industry in sector:
            Industry.objects.get_or_create(industry_id=industry['id'], industry=industry['name'], sector=sector_name)


def update_tickers(industry=None):
    inds = Industry.objects.all()

    for ind in inds:
        where = 'id="%s"' % ind.industry_id
        query = build_query("company", INDUSTRY_TABLE, where)
        data = query_yahoo(query)
        
        if not data:
            print "Sad loading", ind.industry_id
            continue

        data = data['industry']
        if type(data) == dict:
            data = [data]

        stocks = Stock.objects.all()

        for company in data:
            c = company['company']
            if not stocks.filter(ticker=c['symbol']).exists():
                Stock.objects.create(ticker=c['symbol'], company_name=c['name'], current_price=0, volume=0)


def update_stocks():
    import string
    for letter in string.uppercase:
        # Grab any outdated or uninitialized Stocks for letter
        stocks = Stock.objects.filter(ticker__startswith=letter, last_updated__lt=time_hours_ago(6)) or Stock.objects.filter(ticker__startswith=letter, current_price=0)
        
        if stocks.count() > 0:
            # Split it in half, because sometimes YQL chokes on the big ones.
            mid = stocks.count() // 2
            update_stock(*stocks[:mid])
            update_stock(*stocks) # No indicies this time because of lazy eval.


def time_hours_ago(hours):
    return timezone.now() - datetime.timedelta(hours=hours)



# Stuff that will probably be necessary

def query_history(ticker, startDate="2012-11-13", endDate="2012-11-27"):
    query = 'select Date, Close from yahoo.finance.historicaldata where symbol ="'+ticker+'" and startDate ="'+startDate+'" and endDate="'+endDate+'"'
    
    url = 'http://query.yahooapis.com/v1/public/yql?q=' + urllib.quote(query) + '&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env'

    # Open url and get jason format data
    jdata = urllib.urlopen(url).read()
    
    try:
        data_array = json.loads(jdata)
    except ValueError:
        return None
    
    if data_array['query']['results'] == None:
        return None

    data_array = data_array['query']['results']
    data_array['quote'] = data_array['quote'].reverse()

    return json.dumps(data_array)
    


def get_historical_prices(symbol, start_date, end_date):
    """
    Get historical prices for the given ticker symbol.
    Date format is 'YYYYMMDD'
    
    Returns a nested list.
    """
    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % str(int(end_date[4:6]) - 1) + \
          'e=%s&' % str(int(end_date[6:8])) + \
          'f=%s&' % str(int(end_date[0:4])) + \
          'g=d&' + \
          'a=%s&' % str(int(start_date[4:6]) - 1) + \
          'b=%s&' % str(int(start_date[6:8])) + \
          'c=%s&' % str(int(start_date[0:4])) + \
          'ignore=.csv'
    days = urllib.urlopen(url).readlines()
    data = [day[:-2].split(',') for day in days]
    return data




# Stuff that probably isn't necissary

def query_for_ticker(ticker, datefrom="", dateto="" ):
    # This might be a handy helper function. It would do what get_stocks
    # does right now, building and sending a query and returning the data.
    # It might be helpful to define and use use the query_yahoo function below.

    #build yql query string
    query = 'select symbol, Name, LastTradePriceOnly, Volume, Open, AskRealtime, BidRealtime, ChangeRealtime from yahoo.finance.quotes where symbol="'
    query += ticker + '"'
    
    return query_yahoo(query)

def query_for_tickers(tickers):
    # This might be a handy helper function. It would do what get_stocks
    # does right now, building and sending a query and returning the data.
    # It might be helpful to define and use use the query_yahoo function below.

    keywords = "symbol, Name, LastTradePriceOnly, Volume, Open, AskRealtime, BidRealtime, ChangeRealtime"
    orderby = "ChangeRealtime"
    isDescending = "false"
    whereclause='symbol in (' +tickers+')'
    
    query = query_builder( keywords,whereclause, orderby, isDescending)
    return query_yahoo(query)

def query_builder(keywords, whereclause, orderby, isDescending):
    query = 'select ' + keywords + ' from yahoo.finance.quotes where ' + whereclause   
    query += '| sort(field="'+ orderby +'", descending="'+ isDescending + '")'
    return query

