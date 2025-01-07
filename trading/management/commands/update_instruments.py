from django.core.management.base import BaseCommand
from django.utils import timezone
from trading.models import Instrument
from mainterminal.logging_config import setup_logger
import requests
import json
import traceback

logger = setup_logger('trading.instruments')

class Command(BaseCommand):
    help = 'Download and update instruments from Angel Broking API'

    def handle(self, *args, **options):
        logger.info('Starting instruments update process')
        
        try:
            # Download JSON
            url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
            logger.info(f'Downloading instruments from: {url}')
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            instruments_data = response.json()
            logger.info(f'Successfully downloaded {len(instruments_data)} instruments')

            # Clear existing data
            old_count = Instrument.objects.count()
            Instrument.objects.all().delete()
            logger.info(f'Cleared {old_count} existing instruments')

            # Prepare bulk create list
            instruments_to_create = []
            errors = []
            
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
                    
                    if idx % 1000 == 0:  # Log progress every 1000 instruments
                        logger.debug(f'Processed {idx} instruments')
                        
                except Exception as e:
                    error_msg = f'Error processing instrument {data.get("symbol")}: {str(e)}'
                    errors.append(error_msg)
                    logger.warning(error_msg)

            # Bulk create instruments
            try:
                Instrument.objects.bulk_create(instruments_to_create)
                logger.info(f'Successfully created {len(instruments_to_create)} instruments')
                
                if errors:
                    logger.warning(f'Completed with {len(errors)} errors')
                    for error in errors:
                        logger.warning(error)
                else:
                    logger.info('Update completed successfully with no errors')
                    
            except Exception as e:
                logger.error(f'Bulk create failed: {str(e)}')
                raise

        except requests.RequestException as e:
            error_msg = f'Network error downloading instruments: {str(e)}'
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise CommandError(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f'Error parsing JSON response: {str(e)}'
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise CommandError(error_msg)
            
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise CommandError(error_msg)