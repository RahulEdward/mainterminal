from django.apps import AppConfig
import threading
import logging
import colorlog
import sys
import time
from datetime import datetime

# Setup logger for apps.py
logger = logging.getLogger('trading.startup')
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
console_handler = colorlog.StreamHandler(sys.stdout)
console_handler.setFormatter(color_formatter)
logger.addHandler(console_handler)

def log_box(message, style='single'):
    """Create a box around the message with specified style"""
    lines = message.split('\n')
    max_length = max(len(line) for line in lines)
    
    if style == 'double':
        top = '╔' + '═' * (max_length + 4) + '╗'
        bottom = '╚' + '═' * (max_length + 4) + '╝'
        side = '║'
    else:
        top = '┌' + '─' * (max_length + 4) + '┐'
        bottom = '└' + '─' * (max_length + 4) + '┘'
        side = '│'

    logger.info(top)
    for line in lines:
        padding = ' ' * (max_length - len(line))
        logger.info(f"{side}  {line}{padding}  {side}")
    logger.info(bottom)

class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trading'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            from trading.schedulers.master_contract import download_instruments
            
            def start_download():
                start_time = time.time()
                
                log_box('Master Contract Download Starting', style='double')
                logger.info('⚡ Initializing download process...')
                
                try:
                    result = download_instruments()
                    execution_time = time.time() - start_time
                    
                    # Create summary message
                    summary = (
                        f"✨ Download Summary ✨\n"
                        f"📊 Instruments Created: {result:,}\n"
                        f"⏱️ Total Time: {execution_time:.2f} seconds"
                    )
                    log_box(summary)
                    
                except Exception as e:
                    error_msg = f"❌ Error During Download\n{str(e)}"
                    log_box(error_msg, style='double')
                
                finally:
                    log_box('Download Process Complete', style='double')

            thread = threading.Thread(target=start_download)
            thread.daemon = True
            thread.start()
            
            # Initial startup message
            log_box('Angel Broking Master Contract System Initialization Complete', style='double')