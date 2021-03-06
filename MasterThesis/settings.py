"""
Django settings for SilburyDataGrabber project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'peq#qb7-@_fgg#l0@o!xb4rwpo@2vb@**1m+9h+ju*#b^dj_%k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*',
    '.ngrok.io',
    'localhost',
    '127.0.0.1',
    '192.168.34.106',
    '78.50.47.24',
    'masterthesis.ddns.net'
]

# Application definition

INSTALLED_APPS = [
    'webpack_loader',
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'config.apps.ConfigConfig',
    'chat.apps.ChatConfig',
    'data.apps.DataConfig',
    'bot.apps.BotConfig',
    'turns.apps.TurnsConfig',
    'content.apps.ContentConfig',
    'user.apps.UserConfig',
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

ROOT_URLCONF = 'MasterThesis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],

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

WSGI_APPLICATION = 'MasterThesis.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'chat', 'webpack-stats.json'),
    }
}

LOGIN_REDIRECT_URL = 'index'

DIALOG_FLOW_TOKEN = ''
SLACK_CLIENT_ID = '275554204848.276210618530'
SLACK_CLIENT_SECRET = 'a9428557db886305691d349ef2496835'
SLACK_VERIFICATION_TOKEN = 'KnyrygNd1a1jZ7opwdIp9p9k'
SLACK_BOT_USER_TOKEN = 'xoxb-276356850757-P2m9I8JTCxpTPzZSogVluKg6'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'default': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{levelname} {asctime}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'formatter': 'default',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'WARNING',
            'formatter': 'default',
            'propagate': False,
        },
        'turns': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'data': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'events': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'dialogflow': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'chat': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'bot': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        },
        'content': {
            'handlers': ['console'],
            'formatter': 'default',
            'level': 'DEBUG',
        }
    },
}
