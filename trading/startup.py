import os
from django.core.management import call_command
from django.apps import apps

def initialize_app():
    """Initialize the trading app on startup"""
    if not apps.is_installed('trading'):
        return

    print("\n=== Initializing Trading System ===")
    print("Checking directories...")
    
    # Ensure json_files directory exists
    json_dir = os.path.join(os.getcwd(), 'json_files')
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
        print(f"Created json_files directory at: {json_dir}")
    
    # Start initial download
    try:
        from trading.schedulers.master_contract import download_instruments
        print("\nStarting master contract download...")
        result = download_instruments()
        print(f"\nDownload completed successfully!")
        print(f"Total instruments created: {result}")
        print("\n=== Initialization Complete ===\n")
    except Exception as e:
        print(f"\nError during initialization: {e}\n")

def run_at_startup():
    """Function to be called when Django starts"""
    initialize_app()