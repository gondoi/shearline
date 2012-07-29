#!/usr/bin/env python

import multiprocessing
import os
import signal
import time
import Queue
import argparse

import cloudfiles

from boto.s3.connection import S3Connection
from boto.s3.key import Key

class CommandError(Exception):
    pass

def env(e):
    return os.environ.get(e, '')

def synchronize(key):
    print 'Started: %s' % key

    s3 = S3Connection(is_secure=True, anon=True)
    bucket = s3.get_bucket(os.environ['S3_BUCKET'])
    item = bucket.get_key(key)
    cf = cloudfiles.get_connection(os.environ['CF_USERNAME'],
                                   os.environ['CF_APIKEY'])
    container = cf.create_container(os.environ['CF_CONTAINER'])
    cf_object = container.create_object(key)

    if item.size > 0:
        if cf_object.etag is None or item.etag != '"%s"' % cf_object.etag:
            cf_object.send(item)
            status = "Created on Cloud Files: %s" % item.key
        else:
            status = "Already exists and is up-to-date: %s" % item.key
    else:
        status = "Skipping empty item: %s" %item.key

    print status
    return status

def process(total, job_queue, result_queue):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    while not job_queue.empty():
        try:
            progress = 100 - float(job_queue.qsize()) / total * 100
            print "Progress: %.2f%%" % progress

            job = job_queue.get(block=False)
            result_queue.put(synchronize(job))
        except Queue.Empty:
            pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="enable verbose output",
                        action="store_true")
    parser.add_argument("--bucket", default=os.environ.get('S3_BUCKET', ''),
                        help='defaults to env[S3_BUCKET]')
    parser.add_argument("--username", default=os.environ.get('CF_USERNAME', ''),
                        help='defaults to env[CF_USERNAME]')
    parser.add_argument("--apikey", default=os.environ.get('CF_APIKEY', ''),
                        help='defaults to env[CF_APIKEY]')
    parser.add_argument("--container", default=os.environ.get('CF_CONTAINER', ''),
                        help='defaults to env[CF_CONTAINER]')
    parser.add_argument("--processes", type=int, default=1,
                        help='number of synchronization processes at a time')
    args = parser.parse_args()

    user, apikey = args.username, args.apikey
    if not user:
        raise CommandError("You must provide a username, either via "
                           "--username or via env[CLOUD_SERVERS_USERNAME]")
    if not apikey:
        raise CommandError("You must provide an API key, either via "
                           "--apikey or via env[CLOUD_SERVERS_API_KEY]")

    job_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    s3 = S3Connection(is_secure=True, anon=True)
    bucket = s3.get_bucket(os.environ['S3_BUCKET'])

    for item in bucket.list():
        job_queue.put(item.key)
    total = job_queue.qsize()

    workers = []
    for i in range(1):
        tmp = multiprocessing.Process(target=process,
                                      args=(total, job_queue, result_queue))
        tmp.start()
        workers.append(tmp)

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        print 'parent received ctrl-c'
        for worker in workers:
            worker.terminate()
            worker.join()

    while not result_queue.empty():
        print result_queue.get(block=False)

if __name__ == "__main__":
    main()
