from datetime import timedelta
from pathlib import Path
import os

import logging




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o&jaw6hh_h3j(42rgcyl+#(hqr+bujhqv^50ae+6oza6br$o#j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['cmvp-api-v1.onrender.com', 'localhost', '127.0.0.1','jumia-clone-api-11vb.onrender.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    'storages',
    #Second Party Apps
    'users',        # Make sure this is included
    'certificates',  # Make sure this is included
    'subscription',  # Make sure this is included
    'newsletterSubscription',    

    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]




ROOT_URLCONF = 'core.urls'


AUTH_USER_MODEL = 'users.Organization'

# Configure CORS
# Enable CORS headers for specified origins


CORS_ALLOWED_ORIGINS = [
    "https://cmvp-project.vercel.app",

    "http://localhost:3000", 

    "http://localhost:5173", 

    "https://cmvp.net",

    "https://new-cmvp-site.vercel.app",  

    "http://localhost:5173",
]


# Allow credentials if necessary
# CORS_ALLOW_CREDENTIALS = True

# # Allow all origins for development (use only if you trust all origins)
# CORS_ALLOW_ALL_ORIGINS = True


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 10 messages per page

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Email settings for Hostinger
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.hostinger.com'
# EMAIL_PORT = 465 
# EMAIL_USE_SSL = True 
# EMAIL_USE_TLS = False  
# EMAIL_HOST_USER = 'ekenehanson@sterlingspecialisthospitals.com' 
# EMAIL_HOST_PASSWORD = '123@Qwertyqwerty@123'
# DEFAULT_FROM_EMAIL = 'ekenehanson@sterlingspecialisthospitals.com'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'support@cmvp.net'
EMAIL_HOST_PASSWORD = 'qwertyqwerty'
DEFAULT_FROM_EMAIL = 'support@cmvp.net'




# DEFAULT_WEB_PAGE_BASE_URL = "http://localhost:5173"
# DEFAULT_WEB_PAGE_BASE_URL = "https://cmvp-project.vercel.app"
DEFAULT_WEB_PAGE_BASE_URL = "https://cmvp.net"


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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cmvp_db_c26x',
        'USER': 'cmvp_db_c26x_user',
        'PASSWORD': 'LzRpuDeBZ0SeWaEVzLN61u3IdADsaql3',
        'HOST': 'dpg-cucfe7rv2p9s73d71pc0-a.oregon-postgres.render.com',
        'PORT': '5432',  # Default PostgreSQL port
    }
}



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
}


# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # If using a 'static' folder for development
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Used when collecting static files for deployment


# STATIC_URL = 'static/'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Default primary key fiel d type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cmvp-files'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'eu-north-1'
AWS_S3_FILE_OVERWRITE = False  # Prevents overwriting files with the same name
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_S3_ADDRESSING_STYLE = "virtual"  # Helps resolve issues in some regions

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },

    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'


# Set MEDIA_ROOT to an empty string (not needed for S3)
MEDIA_ROOT = ''




REMITA_API_KEY = "abc12345xyz67890mnopqrstuv"
REMITA_MERCHANT_ID = "your_remita_merchant_id_here"
REMITA_SERVICE_TYPE_ID = "your_remit_service_type_id_here"
REMITA_BASE_URL = "https://remita.net" 




