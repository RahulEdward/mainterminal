from django.apps import AppConfig

class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trading'  # Make sure this matches your app's actual location
    verbose_name = 'Trading'

    def ready(self):
        from . import scheduler
        scheduler.start()