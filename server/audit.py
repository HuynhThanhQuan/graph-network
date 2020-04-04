import os
import logging
import json
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


TOTAL_REQUESTS = 0
SYSTEM_KEY = os.getenv('SYSTEM_KEY')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def validate_system_key(system_key):
    return system_key == SYSTEM_KEY


def update_statistic():
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1
    if TOTAL_REQUESTS % 1000 == 0:
        logger.info('Total request is more than {}'.format(TOTAL_REQUESTS))


def verify_request(request):
    logger.info('=======================================')
    client_ip = get_client_ip(request)
    logger.info('User IP address: "{}"'.format(client_ip))
    update_statistic()
    try:
        request_body = json.loads(request.body)
        validation = validate_system_key(request_body['SYSTEM_KEY'])
        if validation is False:
            logger.error('{}'.format(client_ip))
        return validation
    except Exception as e:
        return False

