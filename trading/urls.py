from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    # Instrument related URLs
    path('instruments/status/', views.instruments_status, name='instruments_status'),
    
    # OHLC data URLs
    path('instrument/<str:symbol>/ohlc/', views.instrument_ohlc, name='instrument_ohlc'),
    path('api/ohlc/<str:symbol>/', views.fetch_latest_ohlc, name='fetch_latest_ohlc'),
    
    # Trading signals URLs
    path('signals/', views.trade_signals, name='trade_signals'),
    path('signals/<str:symbol>/', views.trade_signals, name='symbol_signals'),
    path('api/signals/create/', views.create_trade_signal, name='create_trade_signal'),
    
    # Dashboard URL
    path('dashboard/', views.dashboard, name='dashboard'),
]