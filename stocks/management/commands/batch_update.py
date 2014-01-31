from django.core.management.base import BaseCommand
import stocks.api as api

from optparse import make_option

class Command(BaseCommand):
    args = ''
    help = 'Batch updates stock data in the database'

    option_list = BaseCommand.option_list + (
        make_option('--tickers',
            action='store_true',
            dest='quick',
            default=False,
            help="Checks for and adds any stocks missing in the database"),
        )

    def handle(self, *args, **options):
        if options['quick']:
            api.update_industries()
            api.update_tickers()

        api.update_stocks()