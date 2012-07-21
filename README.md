Overview
========

Shearline is an application to move files between [Amazon S3](http://aws.amazon.com/s3/) buckets and [Rackspace Cloud Files](http://www.rackspace.com/cloud/cloud_hosting_products/files/) containers.

Dependencies
============

Python CloudFiles and Boto are required.  To install the dependencies, use:

```
$ sudo apt-get install python-cloudfiles python-boto
```

Running
=======

The first iteration of this is super simple. Export the following environment variables and run the script:

```
$ export S3_BUCKET="<S3 source container>"
$ export CF_USERNAME="<Cloud Files username>"
$ export CF_APIKEY="<Cloud Files apikey>"
$ export CF_CONTAINER="<Cloud Files Destination container>"
$ python shearline.py
```
