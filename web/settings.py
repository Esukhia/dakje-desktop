import os


SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

# update this to the dakje folder
BASE_DIR = os.path.dirname(SETTINGS_DIR)
# might not work if user moved Documents
# refer to https://stackoverflow.com/a/6227623
# TODO create if not exist by copying files from the pkg directory. Reset?
FILES_DIR = os.path.expanduser('~/Documents/Dakje/')
DESKTOP = os.path.expanduser('~/Desktop/')

SECRET_KEY = '30mc!-oq02xh=^letug)p6vwmc8t2i0nz=q0jaj6x22d1y+v3)'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SETTINGS_DIR, '../storage/db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

from django.utils.translation import gettext_lazy as _
LANGUAGES = (
    ('zh-hant', _('Traditional Chinese')),
    ('en-us', ('English')),
    ('tibetan', ('Tibetan'))
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

_SEG_TRIGGERS = ['་', '།', '\n', ',']

TEST_BY_ENG = False

if TEST_BY_ENG:
    from tests import createDebugLogger as createLogger

    _SEG_TRIGGERS.append('.')
else:
#     from tests import createDebugLogger as createLogger
    import logging
    createLogger = lambda name, *args, **kws: logging.Logger(name)
