from django.db import models
import pyodbc
import config
# Create your models here.

class Rabbitmq:
    hostname = config.MSSQL['HOSTNAME']
    db_name = config.MSSQL['DB_NAME']
    db_username = config.MSSQL['DB_USERNAME']
    db_password = config.MSSQL['DB_PASSWORD']
    driver = config.MSSQL['DRIVER']
    cursor = None

    @staticmethod
    def create_DB(db_server, db_uid, db_pwd):
        conn_str = (
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=%s;'
            r'Trusted_Connection=no;'
            r'uid=sa;'
            r'pwd=Your_password123;'
        )
        conn = pyodbc.connect(conn_str % (db_server), autocommit=True)

        cursor = conn.cursor()
        cursor.execute("If(db_id(N'%s') IS NULL)\
            BEGIN\
              CREATE DATABASE %s;\
            END" % (Rabbitmq.db_name, Rabbitmq.db_name))

    @staticmethod
    def create_connection():
        if (Rabbitmq.cursor is not None):
            return Rabbitmq.cursor
        conn = pyodbc.connect('Driver=%s;'
                              'Server=%s,1433;'
                              'Database=%s;'
                              'Trusted_Connection=no;'
                              'uid=%s;'
                              'pwd=%s;' % (Rabbitmq.driver, Rabbitmq.hostname, Rabbitmq.db_name,
                                           Rabbitmq.db_username, Rabbitmq.db_password), autocommit=True)

        Rabbitmq.cursor = conn.cursor()

        return Rabbitmq.cursor
    # create table
    @staticmethod
    def create_table(table_name, table_definition):
        Rabbitmq.create_connection()
        Rabbitmq.cursor.execute("if not exists (select * from sysobjects where name='%s' and xtype='U')\
        %s" % (table_name, table_definition))

    @staticmethod
    def create_table_users():
        Rabbitmq.create_table('users',
            "CREATE TABLE users( id INT IDENTITY, username varchar(MAX), tags varchar(256), password varchar(MAX), topic TEXT, permissions TEXT, "
            "stock_permission TEXT, queue_name TEXT, date datetime default CURRENT_TIMESTAMP)")

    @staticmethod
    def create_table_bindings():
        Rabbitmq.create_table('bindings',
            "CREATE TABLE bindings( id INT IDENTITY, username varchar(MAX), binding TEXT,"
            " date datetime default CURRENT_TIMESTAMP)")
    # insert data
    @staticmethod
    def insert_into_table(table_name, table_cols, cols_q, cols_val):
        Rabbitmq.create_connection()
        Rabbitmq.cursor.execute("insert into %s(%s) values( %s )" % (table_name, table_cols, cols_q),
                                cols_val)

    #########
    @staticmethod
    def insert_into_table_users(username, tags, password, topic, permissions, stock_permission, queue_name):
        Rabbitmq.insert_into_table('users',
            'username, tags, password, topic, permissions, stock_permission, queue_name',
            '?, ?, ?, ?, ?, ?, ?',
            (username, tags, password, topic, permissions, stock_permission, queue_name))

    @staticmethod
    def insert_into_table_binding(username, binding):
        Rabbitmq.insert_into_table('bindings', 'username, binding',
                '?, ?',
                (username, binding))
    ########


    @staticmethod
    def update_binding_by_username(username, binding):
        Rabbitmq.create_connection()
        Rabbitmq.cursor.execute("update bindings set binding=? where username=?", binding, username)

    @staticmethod
    def get_users_bindings():
        Rabbitmq.create_connection()
        Rabbitmq.cursor.execute("select * from users, bindings where users.username = bindings.username")
        return Rabbitmq.cursor.fetchall()

