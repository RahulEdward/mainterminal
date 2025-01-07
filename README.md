# MainTerminal - Trading Terminal

MainTerminal is a Django-based trading terminal that integrates with AngelOne Smart API to provide a seamless trading experience.

## Features

- 🔐 Secure user authentication with AngelOne credentials
- 📊 Real-time market data watchlists
- 📈 Quick order placement from watchlists
- 📗 Order Book, Trade Book, and Holdings management
- ⚡ Keyboard shortcuts for rapid trading
- 🎯 Trailing stoploss and MTM square-off capabilities
- 🎤 Voice-enabled trading commands

## Tech Stack

- Python 3.x
- Django
- DaisyUI + Tailwind CSS
- AngelOne Smart API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RahulEdward/mainterminal.git
cd mainterminal












mainterminal/
    ├── apps/
    │   ├── home/
    │   │   ├── migrations/
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   ├── tests.py
    │   │   └── views.py
    │   ├── trading/
    │   │   ├── migrations/
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── apps.py
    │   │   ├── models.py
    │   │   ├── urls.py
    │   │   ├── tests.py
    │   │   └── views.py
    │   └── users/
    │       ├── migrations/
    │       ├── __init__.py
    │       ├── admin.py
    │       ├── apps.py
    │       ├── models.py
    │       ├── urls.py
    │       ├── tests.py
    │       └── views.py
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── templates/
    │   ├── base.html
    │   ├── home/
    │   │   ├── index.html
    │   │   └── about.html
    │   ├── trading/
    │   │   ├── dashboard.html
    │   │   └── watchlist.html
    │   └── users/
    │       ├── login.html
    │       ├── register.html
    │       └── dashboard.html
    ├── mainterminal/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── manage.py
    ├── requirements.txt
    ├── .env
    ├── .gitignore
    └── README.md