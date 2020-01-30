from django.shortcuts import render
from response import *
from users.models import Rabbitmq
import config
import json
import requests
import rabbitmq_controller.RabbitmqHelper as RabbitmqHelper
# Create your views here.

auth = (config.RABBITMQ['USERNAME'], config.RABBITMQ['PASSWORD'])


def index(request):
    # TODO read from config
    if request.method == 'GET':
        users = RabbitmqHelper.get_users()
        users = json.loads(users.content.decode('utf-8'))
        return ok_response(users)
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data['username']
        queue_name = RabbitmqHelper.create_queue_name(username)

        response = RabbitmqHelper.create_user(data)

        status = response.status_code

        if status == 201:
            # TODO try catch!!!!
            # set permission for user
            permissions = {"username":username,"vhost":"/","configure":".*","write":".*","read":".*"}
            RabbitmqHelper.create_user_permissions(username, permissions)

            # set topic permission for user
            topic_permissions = {"username":username,"vhost":"/","exchange":".*","write":".*","read":".*"}
            RabbitmqHelper.create_topic_permissions(username, topic_permissions)

            # create queue
            queue_data = {"vhost":"/","name":queue_name,"durable":"true","auto_delete":"false","arguments":{}}
            RabbitmqHelper.create_queue(queue_data)

            Rabbitmq.insert_into_table_users(username, data['tags'], data['password'],
                    json.dumps(topic_permissions), json.dumps(permissions), None, queue_name)

            # set user access data (isin)
            args = RabbitmqHelper.create_user_access(data['isin'])

            RabbitmqHelper.create_bindings(config.RABBITMQ['HEADERS_EXCHANGE_NAME'], queue_name, args)

            Rabbitmq.insert_into_table_binding(username, json.dumps(args))
            return ok_response('created')
        elif status == 204:
            # TODO just for user exists?
            # set user access data (isin)
            args = RabbitmqHelper.create_user_access(data['isin'])
            RabbitmqHelper.delete_old_bindings(config.RABBITMQ['HEADERS_EXCHANGE_NAME'], queue_name)
            RabbitmqHelper.create_bindings(config.RABBITMQ['HEADERS_EXCHANGE_NAME'], queue_name, args)
            Rabbitmq.update_binding_by_username(username, json.dumps(args))
            return ok_response('user bindings have been updated!!')

        else:
            print(status)
            if response.text != '':
                return error_response(json.loads(response.text))
            else:
                return error_response('bad request')

    elif request.method == 'DELETE': # delete all users, queues from rabbitmq not mssql
        print("delete all users, queues!")
        RabbitmqHelper.delete_all()
        return ok_response("all users has been deleted!")

    else:
        return error_response(405)

def sync(request):
    if request.method == 'POST':
        RabbitmqHelper.delete_all()
        data = Rabbitmq.get_users_bindings()
        r = []
        for item in data:
            username = item.username
            queue_name = RabbitmqHelper.create_queue_name(username)
            # create user
            RabbitmqHelper.create_user({
                'username': item.username,
                'password': item.password,
                'tags': item.tags
            })
            # create permission
            RabbitmqHelper.create_user_permissions(username, json.loads(item.permissions))
            # create topic permission
            RabbitmqHelper.create_topic_permissions(username, json.loads(item.topic))
            # create queue
            queue_data = {"vhost": "/", "name": queue_name, "durable": "true", "auto_delete": "false", "arguments": {}}
            RabbitmqHelper.create_queue(queue_data)
            # create bindings
            RabbitmqHelper.create_bindings(config.RABBITMQ['HEADERS_EXCHANGE_NAME'], queue_name, json.loads(item.binding))
            # r = item.topic
        return ok_response("data has been synced!")

    else:
        return error_response(405)


