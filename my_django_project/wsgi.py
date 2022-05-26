"""
WSGI config for my_django_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os, sys, site

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
WORK_DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..')

#Add the site-packages
site.addsitedir('/home/SERVER_USERNAME/.virtualenvs/histology_env/lib/python2.6/site-packages')

#activate_env=os.path.expanduser("~/.virtualenvs/histology_env/bin/activate_this.py")
#execfile(activate_env, dict(__file__=activate_env))

#adding the project to the python path
sys.path.append(WORK_DIRECTORY)
#adding the parent directory to the python path
sys.path.append(os.path.join(WORK_DIRECTORY, '..'))
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')

application = get_wsgi_application()
