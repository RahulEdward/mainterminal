# trading/management/commands/download_instruments.py
from django.core.management.base import BaseCommand, CommandError
from trading.schedulers.master_contract import download_instruments
import time

class Command(BaseCommand):
    help = 'Manually download and update instruments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting manual instrument download...'))
        start_time = time.time()
        
        try:
            total_created = download_instruments()
            execution_time = time.time() - start_time
            
            self.stdout.write(self.style.SUCCESS(
                f'\nDownload completed successfully!'
                f'\nTotal instruments created: {total_created}'
                f'\nExecution time: {execution_time:.2f} seconds'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise CommandError('Download failed')