import requests
import json
import logging
import colorlog
import os
from pathlib import Path
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from trading.models import Instrument

# Create logs directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Setup logging
logger = logging.getLogger('trading.master_contract')
logger.setLevel(logging.DEBUG)

# Create formatters
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console Handler
console_handler = colorlog.StreamHandler()
console_handler.setFormatter(color_formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# File Handlers
log_file = os.path.join(LOGS_DIR, f'instruments_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Error File Handler
error_file = os.path.join(LOGS_DIR, f'instruments_errors_{datetime.now().strftime("%Y%m%d")}.log')
error_handler = logging.FileHandler(error_file)
error_handler.setFormatter(file_formatter)
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)

def download_instruments():
    """Download and update instruments from Angel Broking API"""
    try:
        logger.info('Starting instruments download process')
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        
        # Download JSON
        logger.info(f'Downloading from: {url}')
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        instruments_data = response.json()
        logger.info(f'Successfully downloaded {len(instruments_data)} instruments')

        # Clear existing data
        old_count = Instrument.objects.count()
        Instrument.objects.all().delete()
        logger.info(f'Cleared {old_count} existing instruments')

        # Process instruments in batches
        instruments_to_create = []
        errors = []
        batch_size = 5000
        total_created = 0

        for idx, data in enumerate(instruments_data, 1):
            try:
                instrument = Instrument(
                    token=data.get('token', ''),
                    symbol=data.get('symbol', ''),
                    name=data.get('name', ''),
                    expiry=data.get('expiry', ''),
                    strike=float(data.get('strike', 0)),
                    lotsize=int(data.get('lotsize', 0)),
                    instrumenttype=data.get('instrumenttype', ''),
                    exch_seg=data.get('exch_seg', ''),
                    tick_size=float(data.get('tick_size', 0))
                )
                instruments_to_create.append(instrument)

                # Batch processing
                if len(instruments_to_create) >= batch_size:
                    Instrument.objects.bulk_create(instruments_to_create)
                    total_created += len(instruments_to_create)
                    logger.info(f'Progress: {total_created}/{len(instruments_data)} instruments created ({(total_created/len(instruments_data)*100):.1f}%)')
                    instruments_to_create = []

            except Exception as e:
                error_msg = f'Error processing instrument {data.get("symbol")}: {str(e)}'
                errors.append(error_msg)
                logger.warning(error_msg)

        # Create remaining instruments
        if instruments_to_create:
            Instrument.objects.bulk_create(instruments_to_create)
            total_created += len(instruments_to_create)
            logger.info(f'Final batch: {total_created}/{len(instruments_data)} instruments created ({(total_created/len(instruments_data)*100):.1f}%)')

        # Report summary
        logger.info('=== Download Summary ===')
        logger.info(f'Total instruments processed: {len(instruments_data)}')
        logger.info(f'Successfully created: {total_created}')
        logger.info(f'Errors encountered: {len(errors)}')
        
        if errors:
            logger.warning('=== Error Details ===')
            for error in errors[:10]:  # Show first 10 errors
                logger.warning(error)
            if len(errors) > 10:
                logger.warning(f'...and {len(errors)-10} more errors')
        else:
            logger.info('Update completed successfully with no errors')

        # Verify final count
        final_count = Instrument.objects.count()
        logger.info(f'Final database count: {final_count} instruments')
        
        return total_created

    except requests.RequestException as e:
        logger.error(f'Network error: {str(e)}')
        raise
    except json.JSONDecodeError as e:
        logger.error(f'JSON parsing error: {str(e)}')
        raise
    except Exception as e:
        logger.error(f'Failed to update instruments: {str(e)}')
        raise

def start_scheduler():
    """Initialize and start the background scheduler for instrument updates"""
    try:
        logger.info('Initializing master contract scheduler...')
        scheduler = BackgroundScheduler()
        
        # Schedule the download_instruments job
        # Running at 9:15 AM IST every day (market opening)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        scheduler.add_job(
            download_instruments,
            trigger='cron',
            hour=9,
            minute=15,
            timezone=ist_timezone,
            name='download_instruments_job',
            misfire_grace_time=900  # 15 minutes grace time
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info('Master contract scheduler started successfully')
        return scheduler
        
    except Exception as e:
        logger.error(f'Failed to start scheduler: {str(e)}')
        raise

def run_immediate_download():
    """Run an immediate instrument download"""
    try:
        logger.info('Starting immediate instrument download...')
        download_instruments()
        logger.info('Immediate download completed')
    except Exception as e:
        logger.error(f'Immediate download failed: {str(e)}')
        raise

if __name__ == '__main__':
    # For testing purposes
    try:
        scheduler = start_scheduler()
        # Keep the script running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info('Scheduler shutdown completed')
    except Exception as e:
        logger.error(f'Main execution failed: {str(e)}')