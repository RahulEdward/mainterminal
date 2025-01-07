@echo off
cd /d "C:\Users\USER\Desktop\mainterminal"
call venv\Scripts\activate
python manage.py update_instruments
deactivate