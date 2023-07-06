"""
Django settings for autoscreenServer project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import environ
import os
# from django.core.files.storage import FileSystemStorage

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_DIR = os.path.dirname(os.path.dirname(SETTINGS_DIR))
PROJECT_DIR = os.path.dirname(DJANGO_DIR)

# Initialise environment variables for dev only
if  os.environ.get('mode') == 'dev':
    env = environ.Env()
    environ.Env.read_env(env_file=os.path.join(DJANGO_DIR,'.local.env'))
    BUILD_DIR = os.path.dirname(PROJECT_DIR)
    os.environ.setdefault('EXTERNAL_PLUGINS_DIRECTORY',os.path.join(BUILD_DIR, 'external_plugins'))
    os.environ.setdefault('AUTOSCREENDIR',os.path.join(BUILD_DIR, 'data', 'smartscope'))
    os.environ.setdefault('USE_LONGTERMSTORAGE', 'False')

AUTOSCREENDIR = os.getenv('AUTOSCREENDIR')
TEMPDIR = os.getenv('TEMPDIR')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = eval(os.getenv('DEBUG'))
DEPLOY = eval(os.getenv('DEPLOY'))


ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
CSRF_TRUSTED_ORIGINS = [f'https://*.{host}' for host in ALLOWED_HOSTS]

APP = os.getenv('APP')
# Application definition
# Storage locations
USE_STORAGE = eval(os.getenv('USE_STORAGE'))
USE_LONGTERMSTORAGE = eval(os.getenv('USE_LONGTERMSTORAGE'))
USE_AWS = eval(os.getenv('USE_AWS'))
USE_MICROSCOPE = eval(os.getenv('USE_MICROSCOPE'))

if USE_LONGTERMSTORAGE:
    AUTOSCREENSTORAGE = os.getenv('AUTOSCREENSTORAGE')
else:
    AUTOSCREENSTORAGE = None

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'storages',
    'channels',
    'Smartscope.core.settings.apps.Frontend',
    'Smartscope.core.settings.apps.API',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'Smartscope.server.main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(DJANGO_DIR, 'server/main/custom_templates'),
            os.path.join(DJANGO_DIR, 'server/main/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Smartscope.server.frontend.context_processors.base_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'Smartscope.server.main.wsgi.application'
ASGI_APPLICATION = 'Smartscope.server.main.asgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (os.getenv("REDIS_HOST"), 
                int(os.getenv("REDIS_PORT")))
            ],
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE'),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': os.getenv('MYSQL_PORT'),
        'CONN_MAX_AGE': 0,
    }
}

if os.getenv('MYSQL_HOST') == 'localhost':
    DATABASES['default']['OPTIONS'] = {
        'unix_socket': '/run/mysqld/mysqld.sock',
    }
    DATABASES['default']['USER'] = os.getenv('MYSQL_USER')
    DATABASES['default']['PASSWORD'] = os.getenv('MYSQL_PASSWORD')
else:
    DATABASES['default']['USER'] = os.getenv('MYSQL_USER')
    DATABASES['default']['PASSWORD'] = os.getenv('MYSQL_PASSWORD')

    ssl = eval(os.getenv('MYSQL_SSL', 'False'))
    if ssl:
        DATABASES['default']['OPTIONS'] = {
            'ssl': ssl,           
        }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'Smartscope.server.api.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_yaml.renderers.YAMLRenderer'
    ],
}


# Enable finders. List of tuples, where first value is the name and the is the method import path relative to Smartscope.Finders. Third value is the optional keyword arguments that can be supplemented to the function.
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIMEZONE', 'America/New_York')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'


if DEBUG is True:
    STATICFILES_DIRS = [
        os.path.join(PROJECT_DIR, "static"),
    ]
else:
    # only used for prod
    STATIC_ROOT = os.path.join(PROJECT_DIR, "static")

LOGIN_REDIRECT_URL = '/smartscope'
LOGOUT_REDIRECT_URL = '/login'
LOGIN_URL = '/login'
