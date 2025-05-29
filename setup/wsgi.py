"""
WSGI config for setup project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
'''
import os

from django.core.wsgi import get_wsgi_application

print("⚙️ WSGI: Inicializando aplicação Django")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

application = get_wsgi_application()

print("✅ WSGI carregado com sucesso.")

app = application
'''

import os
import sys

print("⚙️ WSGI: Inicializando aplicação Django")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ WSGI carregado com sucesso.")
except Exception as e:
    print("❌ Erro ao carregar aplicação WSGI:")
    print(e)
    sys.exit(1)

app = application