from django.apps import AppConfig

class TradingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trading'

    def ready(self):
        try:
            from trading.schedulers.master_contract import start_scheduler
            start_scheduler()
        except Exception as e:
            print(f"Error starting scheduler: {str(e)}")