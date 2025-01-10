from django.core.management.base import BaseCommand
from trading.websocket.market_data import MarketDataManager
from users.models import User
from trading.logging_config import setup_logger

logger = setup_logger('trading.commands.market_data')

class Command(BaseCommand):
    help = 'Start market data WebSocket connection'

    def add_arguments(self, parser):
        parser.add_argument('client_id', type=str, help='Client ID to use for connection')
        parser.add_argument('--pin', type=str, required=True, help='PIN for authentication')
        parser.add_argument('--totp', type=str, required=True, help='TOTP for authentication')

    def handle(self, *args, **options):
        try:
            client_id = options['client_id']
            pin = options['pin']
            totp = options['totp']
            
            # Get user by client_id
            user = User.objects.get(client_id=client_id)
            
            # Refresh tokens
            success, message = user.refresh_tokens(pin=pin, totp=totp)
            if not success:
                self.stdout.write(self.style.ERROR(f'Token refresh failed: {message}'))
                return
                
            self.stdout.write(self.style.SUCCESS('Tokens refreshed successfully'))
            
            # Start market data connection
            manager = MarketDataManager(client_id)  # Pass client_id instead of username
            manager.start()
            
            self.stdout.write(self.style.SUCCESS(f'Market data connection started for client {client_id}'))
            
            # Keep the command running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Stopping market data connection...'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with client ID {client_id} not found'))
        except Exception as e:
            logger.error(f"Error in market data command: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))