from django.contrib import admin
from .models import Instrument

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'token', 'name', 'instrumenttype', 'exch_seg', 'lotsize')
    list_filter = ('instrumenttype', 'exch_seg')
    search_fields = ('symbol', 'token', 'name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('token', 'symbol', 'name', 'instrumenttype', 'exch_seg')
        }),
        ('Trading Details', {
            'fields': ('strike', 'lotsize', 'expiry', 'tick_size')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )