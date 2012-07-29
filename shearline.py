import multiprocessing
import os
import sys
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


class Shearline(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", "--verbose", action="store_true",
                                 help="enable verbose output")
        self.parser.add_argument("--bucket", default=env('S3_BUCKET'),
                                 help='defaults to env[S3_BUCKET]')
        self.parser.add_argument("--username",
                                 default=env('CF_USERNAME'),
                                 help='defaults to env[CF_USERNAME]')
        self.parser.add_argument("--apikey",
                                 default=env('CF_APIKEY'),
                                 help='defaults to env[CF_APIKEY]')
        self.parser.add_argument("--container",
                                 default=env('CF_CONTAINER'),
                                 help='defaults to env[CF_CONTAINER]')
        self.parser.add_argument("--processes", type=int, default=1,
                                 help='number of synchronization processes at a time')


    def synchronize(self, key):
        if self.verbose:
            print 'Started: %s' % key
    
        s3 = S3Connection(is_secure=True, anon=True)
        bucket = s3.get_bucket(self.s3_bucket)
        item = bucket.get_key(key)
        cf = cloudfiles.get_connection(self.cf_username, self.cf_apikey)
        container = cf.create_container(self.cf_container)
        cf_object = container.create_object(key)
    
        if item.size > 0:
            if cf_object.etag is None or item.etag != '"%s"' % cf_object.etag:
                cf_object.send(item)
                status = "Created on Cloud Files: %s" % item.key
            else:
                status = "Already exists and is up-to-date: %s" % item.key
        else:
            status = "Skipping empty item: %s" %item.key
    
        if self.verbose:
            print status

        return status

    
    def process(self, total, job_queue, result_queue):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while not job_queue.empty():
            try:
                progress = 100 - float(job_queue.qsize()) / total * 100
                print "Progress: %.2f%%" % progress
    
                job = job_queue.get(block=False)
                result_queue.put(self.synchronize(job))
            except Queue.Empty:
                pass
    

    def main(self, argv):
        args = self.parser.parse_args(argv)

        self.s3_bucket = args.bucket
        self.cf_username = args.username
        self.cf_apikey = args.apikey
        self.cf_container = args.container
        self.processes = args.processes
        self.verbose = args.verbose

        if not self.s3_bucket:
            raise CommandError("You must provide an S3 bucket, either via "
                               "--bucket or via env[S3_BUCKET]")
        if not self.cf_username:
            raise CommandError("You must provide a Cloud Files username, either via "
                               "--username or via env[CF_USERNAME]")
        if not self.cf_apikey:
            raise CommandError("You must provide a Cloud Files API key, either via "
                               "--apikey or via env[CF_APIKEY]")
        if not self.cf_container:
            raise CommandError("You must provide a Cloud Files container, either via "
                               "--container or via env[CF_CONTAINER]")
    
        job_queue = multiprocessing.Queue()
        result_queue = multiprocessing.Queue()
    
        s3 = S3Connection(is_secure=True, anon=True)
        bucket = s3.get_bucket(self.s3_bucket)
    
        for item in bucket.list():
            job_queue.put(item.key)
        total = job_queue.qsize()
    
        workers = []
        for i in range(self.processes):
            tmp = multiprocessing.Process(target=self.process,
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
    

def main():
    try:
        Shearline().main(sys.argv[1:])
    except CommandError, e:
        print >> sys.stderr, e
        sys.exit(1)
