from django.shortcuts import render
from django.utils import timezone
from .models import Instrument
from mainterminal.logging_config import setup_logger

logger = setup_logger('trading.views')

def instruments_status(request):
    try:
        last_update = Instrument.objects.order_by('-updated_at').first()
        total_count = Instrument.objects.count()
        
        logger.info(f'Instruments status checked. Count: {total_count}')
        
        context = {
            'last_update': last_update.updated_at if last_update else None,
            'total_instruments': total_count
        }
        return render(request, 'trading/instruments_status.html', context)
        
    except Exception as e:
        logger.error(f'Error in instruments_status view: {str(e)}')
        return render(request, 'trading/error.html', {'error': str(e)})