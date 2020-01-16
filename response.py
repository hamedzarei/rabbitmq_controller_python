##
# Response Helpers
##
from django.http import HttpResponse
import json

def error_response(data):
    response_data = dict()
    if (data == 405):
        response_data['status'] = 405
        response_data['message'] = 'Method not allowed!'
    else:
        response_data['status'] = 400
        response_data['message'] = data
    return HttpResponse(content=json.dumps(response_data), content_type="application/json", status=400)


def ok_response(data):
    response_data = dict()
    response_data['status'] = 200
    if str(type(data)) != "<class 'str'>":
        response_data['data'] = data
    else:
        response_data['message'] = data
    return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)