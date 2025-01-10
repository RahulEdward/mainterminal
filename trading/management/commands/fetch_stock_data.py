from django.core.management.base import BaseCommand
from trading.models import Stock, StockPrice
from trading.utils.angel_broking import AngelBrokingAPI
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetch stock data from Angel Broking API'

    def handle(self, *args, **options):
        try:
            # Initialize API with your credentials
            api = AngelBrokingAPI(
                access_token=settings.ANGEL_ACCESS_TOKEN,
                api_key=settings.ANGEL_API_KEY
            )

            # Fetch ZOMATO data
            zomato_data = api.fetch_ohlc("5097")  # ZOMATO token
            
            if zomato_data and 'data' in zomato_data:
                stock, _ = Stock.objects.get_or_create(
                    symbol='ZOMATO',
                    token='5097',
                    exchange='NSE'
                )
                
                data = zomato_data['data']
                StockPrice.objects.create(
                    stock=stock,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    ltp=data['ltp']
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully fetched data for ZOMATO'
                ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))