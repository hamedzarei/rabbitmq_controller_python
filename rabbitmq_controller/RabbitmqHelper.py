import requests, json
import config

auth = (config.RABBITMQ['USERNAME'], config.RABBITMQ['PASSWORD'])


def get_users():
    users = requests.get(config.RABBITMQ['BASE_URL'] + 'users',
                         auth=auth)
    return users


def delete_user(username):
    response = requests.delete(config.RABBITMQ['BASE_URL'] + 'users/' + username,
                         auth=auth)
    return response


def create_user(data):
    username = data['username']
    response = requests.put(config.RABBITMQ['BASE_URL'] + 'users/' + username,
                 json=data,
                 auth=auth)

    return response


def create_user_permissions(username, permissions):
    response = requests.put(config.RABBITMQ['BASE_URL'] + 'permissions/%2F/' + username,
                 json=permissions,
                 auth=auth)

    return response


def create_topic_permissions(username, topic_permissions):
    response = requests.put(config.RABBITMQ['BASE_URL'] + 'topic-permissions/%2F/' + username,
                 json=topic_permissions,
                 auth=auth)

    return response


def get_queues():
    response = requests.get(config.RABBITMQ['BASE_URL'] + 'queues',
                         auth=auth)
    return response


def delete_queue(name):
    response = requests.delete(config.RABBITMQ['BASE_URL'] + 'queues/%2F/' + name,
                         auth=auth)
    return response


def create_queue(data):
    queue_name = data['name']
    response = requests.put(config.RABBITMQ['BASE_URL'] + 'queues/%2F/' + queue_name,
                 json=data,
                 auth=auth)

    return response


def create_bindings(exchange_name, queue_name, args):
    response = requests.post(config.RABBITMQ['BASE_URL'] + 'bindings/%2F/e/'+exchange_name+'/q/' + queue_name,
                  json={"vhost": "/", "source": exchange_name, "destination_type": "q",
                        "destination": queue_name, "routing_key": "",
                        "arguments": args},
                  auth=auth)
    print(response)

    return response

def get_bindings(queue_name):
    response = requests.get(config.RABBITMQ['BASE_URL'] + 'queues/%2F/' + queue_name + '/bindings', auth=auth)

    return response


def delete_binding(exchange_name, queue_name, properties_key):
    response = requests.delete(config.RABBITMQ['BASE_URL'] + 'bindings/%2F/e/' + exchange_name +
                               '/q/'+ queue_name + '/' + properties_key, auth=auth)
    return response

######
# high level helpers
######
def get_current_bindings(exchange_name, queue_name):
    response = get_bindings(queue_name)
    bindings = json.loads(response.content.decode('utf-8'))
    current_bindings = []
    for item in bindings:
        if item['source'] == exchange_name:
            current_bindings.append(item)
    return current_bindings


def delete_old_bindings(exchange_name, queue_name):
    bindings = get_current_bindings(exchange_name, queue_name)
    for item in bindings:
        delete_binding(exchange_name, queue_name, item['properties_key'])


def delete_all():
    users = get_users()
    users = json.loads(users.content.decode("utf-8"))
    print("users")
    for user in users:
        if user['name'] != config.RABBITMQ['USERNAME']:
            print("del user: " + json.dumps(user))
            delete_user(user['name'])
    queues = get_queues()
    queues = json.loads(queues.content.decode("utf-8"))
    print("queues")
    for queue in queues:
        print("del queue: " + json.dumps(queue))
        delete_queue(queue['name'])

def create_user_access(isin):
    # set user access data (isin)
    args = {"x-match": "any"}

    for item in isin:
        args[item] = True

    return args


def create_queue_name(username):
    return username+'_queue'
