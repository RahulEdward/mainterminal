from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from datetime import datetime
import pytz

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: call_command('update_instruments'),
        'cron',
        hour=8,
        minute=0,
        timezone=pytz.timezone('Asia/Kolkata')
    )
    scheduler.start()