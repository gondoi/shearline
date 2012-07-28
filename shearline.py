#!/usr/bin/env python

from multiprocessing import Pool

import cloudfiles

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import signal, os, sys, time


def sync(key):
    s3 = S3Connection(is_secure=True, anon=True)
    bucket = s3.get_bucket(os.environ['S3_BUCKET'])
    item = bucket.get_key(key)
    cf = cloudfiles.get_connection(os.environ['CF_USERNAME'],
                                   os.environ['CF_APIKEY'])
    container = cf.create_container(os.environ['CF_CONTAINER'])
    cf_object = container.create_object(key)

    if item.size > 0:
        if cf_object.etag is None or item.etag != '"%s"' % cf_object.etag:
            print ("Creating %s on Cloud Files" % item.key)
            cf_object.send(item)
        else:
            print ("%s Already exists and is up-to-date" % item.key)

    else:
        print("Skipping %s of size %s" % (item.key, item.size))


def main():
    s3 = S3Connection(is_secure=True, anon=True)
    bucket = s3.get_bucket(os.environ['S3_BUCKET'])

    keys = []
    for item in bucket.list():
        keys.append(item.key)

    p = Pool(processes=4)
    p.map(sync, keys)


if __name__ == '__main__':
    main()
