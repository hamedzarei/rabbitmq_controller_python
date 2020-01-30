#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from users.models import Rabbitmq
import config

hostname = config.MSSQL['HOSTNAME']

def migrate():
    #
    Rabbitmq.create_DB(hostname, None, None)
#     create table
    Rabbitmq.create_table_users()
    Rabbitmq.create_table_bindings()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rabbitmq_controller.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    migrate()
    main()
