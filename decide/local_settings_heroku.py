ALLOWED_HOSTS = ["*"]

# Modules in use, commented modules that you won't use
MODULES = [
    'authentication',
    'base',
    'booth',
    'census',
    'mixnet',
    'postproc',
    'store',
    'visualizer',
    'voting',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'decide',
        'USER': 'decide',
        'PASSWORD': 'decide',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256

APIS = {}

SOCIAL_AUTH_GITHUB_KEY = '0a9955030c3867eccf81' #Client ID
SOCIAL_AUTH_GITHUB_SECRET = '26a6c676110f2650318780a9d06017f5e64b4142' #Secret Key

SOCIAL_AUTH_FACEBOOK_KEY = '381742635893877'
SOCIAL_AUTH_FACEBOOK_SECRET = 'ee5b1845b005cce3610c084fd6790b62'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'locale': 'es_ES',
  'fields': 'id, name, email, age_range'
}