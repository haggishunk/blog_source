Title: Fabric with s3cmd
Date: 2017-09-30
Tags: automation,ssh,python
Category: blog

I use s3cmd to publish my static blog to my Amazon S3 bucket.  [Pelican docs](http://docs.getpelican.com/en/stable/publish.html) suggest using [Fabric](http://docs.fabfile.org/en/1.13/index.html) as a publishing engine as it is written in python... and since you probably use Pelican because *it's* written in python... well you see the allure.

Pelican's `pelican-quickstart` command writes a pre-fabbed `fabfile.py` in your root blog directory but I noticed only swift (for Rackspace Cloud), rsync and github support.  So I tried putting in a little tweak for s3cmd:

```
# Amazon S3 config settings
s3bucket = "blog.pantageo.us"      

def publish_s3cmd():
    """Publish to Amazon s3 via s3cmd"""
    options = ["acl-public", "delete-removed"]
    opt_string = ' '.join(['--%s' % o for o in options])
    command_string = "s3cmd %s sync %s/* s3://%s" % (opt_string, DEPLOY_PATH, s3bucket)
    local(command_string)
```

And it works!  I love python.
