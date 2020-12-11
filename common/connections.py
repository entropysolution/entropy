# -*- coding: utf-8 -*-
# ~
# Vortex
# entropysoln
# ~

import ujson
import logging
from time import sleep
from os import environ
from minio import Minio
from sentry_sdk import capture_exception
from redis import ConnectionPool, StrictRedis
from minio.error import ResponseError

log = logging.getLogger('vortex.connections')

# from pprint import pprint
# pprint(environ)

# GLOBAL_REDIS_HOST = environ.get('GLOBAL_REDIS_HOST')
# LOCAL_REDIS_HOST = environ.get('LOCAL_REDIS_HOST')
# S3_ACCESS_KEY_ID = environ.get('S3_ACCESS_KEY_ID')
# S3_SECRET_ACCESS_KEY = environ.get('S3_SECRET_ACCESS_KEY')
# S3_REGION = environ.get('S3_REGION')
# S3_HOSTNAME = environ.get('S3_HOSTNAME')

redis_pools = {}
def getRedis(host, db=0, pool_id=0):
    # host = LOCAL_REDIS_HOST if local else GLOBAL_REDIS_HOST
    pool_key = '%s:%s:%s' % (host, pool_id, db)
    if pool_key not in redis_pools:
        redis_pools[pool_key] = ConnectionPool(host=host, port=6379, db=db)
    return StrictRedis(connection_pool=redis_pools[pool_key])


class MinioObject:
    def __init__(self, bucket_name, object_name, client):
        self.client = client
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.object = None
        try:
            self.object = self.client.get_object(bucket_name, object_name)
        except Exception as ex:
            pass

    def exists(self):
        return self.object != None

    def load(self):
        return self.object

    def delete(self):
        if self.exists():
            self.client.remove_object(self.bucket_name, self.object_name)

    def get(self):
        if self.exists():
            return self.client.stat_object(self.bucket_name, self.object_name)
        return None

    def copy_from(self, target_bucket_name, target_object_name):
        if self.exists():
            raise Exception('Target name already exists')
        else:
            open('buffer.tmp', 'w').close()
            self.client.fput_object(self.bucket_name, self.object_name, file_path='buffer.tmp')
        target = MinioObject(target_bucket_name, target_object_name, self.client)
        if target.exists():
            self.client.copy_object(self.bucket_name, self.object_name, '/%s/%s' % (target_bucket_name, target_object_name))
        else:
            raise Exception('Failed to copy from %s/%s' % (target_bucket_name, target_object_name))


class Client(Minio):
    def Object(self, bucket_name, object_name):
        return MinioObject(bucket_name, object_name, self)


class Bucket:
    def __init__(self):
        return None

    # def Object(self, bucket_name, object_name):
    #     return MinioObject(bucket_name, object_name, self)

    def delete(self):
        pass

    def put_object():
        pass


def getS3(bucket_name, retries=3, timeout=5, S3_HOSTNAME=None, S3_ACCESS_KEY_ID=None, S3_SECRET_ACCESS_KEY=None, S3_REGION=None):
    log.info('Connecting to S3 Server (%s)...', S3_HOSTNAME)
    client = None
    bucket = None
    for _ in range(retries):
        try:
            client = Client(S3_HOSTNAME, access_key=S3_ACCESS_KEY_ID, secret_key=S3_SECRET_ACCESS_KEY, region=S3_REGION, secure=False)
        except ResponseError as ex:
            log.error('S3 Server connection failed: %s', ex)
            capture_exception()
            sleep(timeout)
    if client is None:
        raise Exception('Failed to connect to S3 %s' % (S3_HOSTNAME))

    buckets = list([bucket.name for bucket in client.list_buckets()])
    if bucket_name not in buckets:
        try:
            log.info('Bucket %s not found, creating', bucket_name)
            client.make_bucket(bucket_name, location=S3_REGION)
        except Exception as ex:
            log.error('CreateBucket error: %s' % (ex))
            capture_exception()

    policy_json = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:GetBucketLocation"
                ],
                "Resource": "arn:aws:s3:::{}".format(bucket_name)
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": "arn:aws:s3:::{}".format(bucket_name)
            },
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": "arn:aws:s3:::{}/*".format(bucket_name)
            }
        ]
    }
    client.set_bucket_policy(bucket_name, ujson.dumps(policy_json))
    # bucket = Bucket(bucket_name)
    log.info('S3 connected (%s/%s)', S3_HOSTNAME, bucket_name)
    return client
