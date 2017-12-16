import requests
import json
import time
import logging
import hashlib
import os
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

TESTING_FROM_CMD_LINE = sys.argv[1:2] == ['test']

logger = logging.getLogger(__name__)

def do_query(url, params, headers):
    logger.info('BEGIN query')
    log_start = time.time()
    logger.info('Query url=' + url)
    logger.info('Query params=' + str(params))
    # logger.info('Query headers=' + headers_str)
    response = requests.get(url, params, headers=headers)
    logger.info(response.url)
    log_end = time.time()
    logger.info('END query; time=' + str(log_end - log_start))
    return response.json()


def make_str(coll):
    """
    :param coll: input dict or list
    :return: string that is always the same for coll: it does not depend on hashing
    """
    if isinstance(coll, dict):
        return str(sorted(coll.items(), key=lambda x: str(x[1])))
    return str(coll)


def query(url, params, headers):
    # print(url)
    # print(params)
    # print(headers)

    params_str = make_str(params)
    headers_str = make_str(headers)

    if TESTING_FROM_CMD_LINE:
        # try to retreive from disk
        # print (url+params_str+headers_str + ' -> ' + hashlib.md5((url+params_str+headers_str).encode('utf-8')).hexdigest())
        h = hashlib.md5((url+params_str+headers_str).encode('utf-8')).hexdigest()
        o = urlparse(url)
        filename = 'data/cache/' + o.netloc + '_' + h + '.dat'
        try:
            with open(filename, 'r') as json_file:
                result = json.load(json_file)
        except OSError:
            result = do_query(url, params, headers)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as json_file:
                json.dump(result, json_file)
    else:
        result = do_query(url, params, headers)
    return result
