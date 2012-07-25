import cloudfiles

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import os, time

while True:
    try:
        s3 = S3Connection(is_secure=True, anon=True)
        bucket = s3.get_bucket(os.environ['S3_BUCKET'])

        cf = cloudfiles.get_connection(os.environ['CF_USERNAME'], os.environ['CF_APIKEY'])
        container = cf.create_container(os.environ['CF_CONTAINER'])

        for item in bucket.list():
            cf_object = container.create_object(item.key)

            print '---------------------------------------------------------------------'
            print item.key
            print '---------------------------------------------------------------------'
            if item.size > 0:
                print 'CF Etag: "%s"' % cf_object.etag
                print 'S3 Etag: %s' % item.etag

                if cf_object.etag is None or item.etag != '"%s"' % cf_object.etag:
                    print ("Creating %s on Cloud Files" % item.key)
                    cf_object.send(item)
                    print ("File creation complete")
                else:
                    print ("%s Already exists and is up-to-date" % item.key)

            else:
                print("Skipping %s of size %s" % (item.key, item.size))

            print "====================================================================="
            print ""

        break

    except Exception, e:
        print "ERROR: %s" % e
        time.sleep(10)
