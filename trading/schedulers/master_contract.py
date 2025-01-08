import requests
import json
import logging
import colorlog
import os
import time
from pathlib import Path
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from trading.models import Instrument
from django.db import transaction, connection
import threading

# Get the absolute path of the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_DIR = BASE_DIR / 'json_files'

# Ensure json_files directory exists
JSON_DIR.mkdir(exist_ok=True)

# Setup logging
logger = logging.getLogger('trading.master_contract')
logger.setLevel(logging.INFO)

# Remove existing handlers to avoid duplicate logs
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create color formatter
color_formatter = colorlog.ColoredFormatter(
    '%(log_color)s[%(asctime)s] %(message)s%(reset)s',
    datefmt='%H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'bold_green',
        'WARNING': 'yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    }
)

# Console Handler
console_handler = colorlog.StreamHandler()
console_handler.setFormatter(color_formatter)
logger.addHandler(console_handler)

def download_instruments():
    """Download and update instruments from Angel Broking API"""
    json_file_path = None
    start_time = time.time()
    
    try:
        # Download JSON with streaming
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        logger.info('📥 Downloading master contract data...')
        
        with requests.get(url, stream=True, timeout=30) as response:
            response.raise_for_status()
            
            # Create file path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_file_path = os.path.join(JSON_DIR, f"instruments_{timestamp}.json")
            
            # Stream download to file
            with open(json_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        
        download_time = time.time() - start_time
        logger.info(f'✅ Download completed in {download_time:.2f} seconds')

        # Process JSON
        logger.info('🔄 Processing data...')
        process_start = time.time()
        with open(json_file_path, 'r') as f:
            instruments_data = json.load(f)

        # Pre-process all instruments
        instruments_to_create = [
            Instrument(
                token=data.get('token', ''),
                symbol=data.get('symbol', ''),
                name=data.get('name', ''),
                expiry=data.get('expiry', ''),
                strike=float(data.get('strike', 0)) / 100,  # Divide by 100
                lotsize=int(data.get('lotsize', 0)),
                instrumenttype=data.get('instrumenttype', ''),
                exch_seg=data.get('exch_seg', ''),
                tick_size=float(data.get('tick_size', 0)) / 100  # Divide by 100
            )
            for data in instruments_data
        ]
        
        process_time = time.time() - process_start
        logger.info(f'✅ Data processing completed in {process_time:.2f} seconds')

        # Bulk insert
        insert_start = time.time()
        with transaction.atomic():
            logger.info('🗑️ Clearing existing data...')
            Instrument.objects.all().delete()
            
            # Reset auto-increment
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{Instrument._meta.db_table}'")
            
            # Bulk insert with large chunks
            total_created = 0
            batch_size = 20000
            total_instruments = len(instruments_to_create)
            
            for i in range(0, total_instruments, batch_size):
                batch = instruments_to_create[i:i + batch_size]
                Instrument.objects.bulk_create(
                    batch,
                    batch_size=batch_size,
                    ignore_conflicts=True
                )
                total_created += len(batch)
                progress = f'📊 Progress: {total_created:,}/{total_instruments:,} ({(total_created/total_instruments*100):.1f}%)'
                logger.info(progress)

        insert_time = time.time() - insert_start
        total_time = time.time() - start_time
        
        logger.info('=== Download Summary ===')
        logger.info(f'⏱️ Download time: {download_time:.2f} seconds')
        logger.info(f'⚡ Process time: {process_time:.2f} seconds')
        logger.info(f'💾 Insert time: {insert_time:.2f} seconds')
        logger.info(f'⌛ Total time: {total_time:.2f} seconds')
        logger.info(f'✨ Successfully created {total_created:,} instruments')
        
        return total_created

    except Exception as e:
        logger.error(f'❌ Error: {str(e)}')
        raise

    finally:
        # Clean up JSON file
        if json_file_path and os.path.exists(json_file_path):
            try:
                os.remove(json_file_path)
                logger.info('🧹 Cleaned up temporary files')
            except Exception as e:
                logger.error(f'❌ Error deleting file: {str(e)}')