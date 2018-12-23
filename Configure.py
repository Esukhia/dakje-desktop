import os

import django

from django.conf import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INSTALLED_APPS = [
    'storage'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

urlpatterns = []

def configure():
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF='Configure',
        DATABASES=DATABASES,
        INSTALLED_APPS=INSTALLED_APPS)
    django.setup()
