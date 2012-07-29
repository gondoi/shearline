Overview
========

Shearline is an application to move files between [Amazon S3](http://aws.amazon.com/s3/) buckets and [Rackspace Cloud Files](http://www.rackspace.com/cloud/cloud_hosting_products/files/) containers.

Installation
============

To install Shearline, run:

```
$ python setup.py install
```

Running
=======

The first iteration of this is super simple. Export the following environment variables and run the script:

```
$ export S3_BUCKET="<S3 source container>"
$ export CF_USERNAME="<Cloud Files username>"
$ export CF_APIKEY="<Cloud Files apikey>"
$ export CF_CONTAINER="<Cloud Files Destination container>"
$ shearline
```

You can also pass the parameters directly to Shearline:

```
$ shearline --bucket S3_BUCKET --username CF_USERNAME --apikey CF_APIKEY --container CF_CONTAINER
```

For more information, run:

```
$ shearline --help
```
