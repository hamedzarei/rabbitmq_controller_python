from django.shortcuts import render
from response import *
import config
import json
import requests
# Create your views here.

auth = (config.RABBITMQ['USERNAME'], config.RABBITMQ['PASSWORD'])
def index(request):
    # TODO read from config
    if request.method == 'GET':
        users = requests.get(config.RABBITMQ['BASE_URL']+'users',
                             auth=auth)
        users = json.loads(users.content)
        return ok_response(users)
    elif request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']

        response = requests.put(config.RABBITMQ['BASE_URL']+'users/'+username,
                                json=data,
                     auth=auth)


        status = response.status_code

        if status == 201:
            # TODO try catch!!!!
            # set permission for user
            requests.put(config.RABBITMQ['BASE_URL']+'permissions/%2F/'+username,
                         json={"username":username,"vhost":"/","configure":".*","write":".*","read":".*"},
                         auth=auth)
            # set topic permission for user
            requests.put(config.RABBITMQ['BASE_URL']+'topic-permissions/%2F/' + username,
                         json={"username":username,"vhost":"/","exchange":".*","write":".*","read":".*"},
                         auth=auth)
            # create queue
            queue_name = username+'_queue'
            requests.put(config.RABBITMQ['BASE_URL']+'queues/%2F/' + queue_name,
                         json={"vhost":"/","name":queue_name,"durable":"true","auto_delete":"false","arguments":{}},
                         auth=auth)

            # set user access data (isin)
            args = {"x-match": "any"}

            user_isin = data['isin']
            for item in user_isin:
                args[item] = True
            r = requests.post(config.RABBITMQ['BASE_URL']+'bindings/%2F/e/headers1/q/' + queue_name,
                              json={"vhost": "/", "source": "headers1", "destination_type": "q",
                                    "destination": queue_name, "routing_key": "",
                                    "arguments": args},
                              auth=auth)


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
