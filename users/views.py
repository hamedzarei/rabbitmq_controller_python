from django.shortcuts import render
from response import *
import config
import json
import requests
# Create your views here.

def index(request):
    # TODO read from config
    if request.method == 'GET':
        users = requests.get('http://localhost:15672/api/users',
                             auth=('rabbitmq', 'rabbitmq'))
        users = json.loads(users.content)
        return ok_response(users)
    elif request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']

        response = requests.put('http://localhost:15672/api/users/'+username,
                                json=data,
                     auth=('rabbitmq', 'rabbitmq'))


        status = response.status_code

        if status == 201:
            # TODO try catch!!!!
            # set permission for user
            requests.put('http://localhost:15672/api/permissions/%2F/'+username,
                         json={"username":username,"vhost":"/","configure":".*","write":".*","read":".*"},
                         auth=('rabbitmq', 'rabbitmq'))
            # set topic permission for user
            requests.put('http://localhost:15672/api/topic-permissions/%2F/' + username,
                         json={"username":username,"vhost":"/","exchange":".*","write":".*","read":".*"},
                         auth=('rabbitmq', 'rabbitmq'))
            # create queue
            queue_name = username+'_queue'
            requests.put('http://localhost:15672/api/queues/%2F/' + queue_name,
                         json={"vhost":"/","name":queue_name,"durable":"true","auto_delete":"false","arguments":{}},
                         auth=('rabbitmq', 'rabbitmq'))

            # set user access data (isin)
            args = {"x-match": "any"}

            user_isin = data['isin']
            for item in user_isin:
                args[item] = True
            r = requests.post('http://localhost:15672/api/bindings/%2F/e/headers1/q/' + queue_name,
                              json={"vhost": "/", "source": "headers1", "destination_type": "q",
                                    "destination": queue_name, "routing_key": "",
                                    "arguments": args},
                              auth=('rabbitmq', 'rabbitmq'))
            return ok_response({
                'd': r.text,
                's': r.status_code
            })


            return ok_response('created')
        elif status == 204:
            # TODO just for user exists?
            return error_response('user exists!!')
        else:
            print(status)
            if response.text != '':
                return error_response(json.loads(response.text))
            else:
                return error_response('bad request')

    else:
        return error_response(405)
