# CONFIGS

RABBITMQ = {
    'USERNAME': 'rabbitmq',
    'PASSWORD': 'rabbitmq',
    'BASE_URL': 'http://rabbitmq:15672/api/',
    'HEADERS_EXCHANGE_NAME': 'amq.headers'
}

MSSQL = {
    'HOSTNAME': 'db',
    'DRIVER': '/opt/microsoft/msodbcsql/lib64/libmsodbcsql-13.1.so.9.2',
    'DB_NAME': 'rabbitmq',
    'DB_USERNAME': 'sa',
    'DB_PASSWORD': 'Your_password123'
    # 'DRIVER': '/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1'
    # 'DRIVER': '{SQL Server}'
}