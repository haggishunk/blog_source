Title:  Ceph Storage Cluster on Digital Ocean Using Terraform (Part 3)
Date: 2018-01-16
Tags: ceph,storage,cluster,digital_ocean,terraform,provisioning,automation,version
Category: blog

This [Ceph project][] is almost finished.  The terraform code now sets out properly configured servers ready for ceph-deploy to do its work, which sets me up nicely to perform a demo.

![squid](https://cdn.brainpop.com/science/diversityoflife/giantsquid/screenshot1.png)

A basic demo script would go as such after connecting to `ceph-admin`:

Designate a cluster monitor.  In production use one would deploy 3 or more but this is a simple demo.
```
ceph-deploy new ceph-1
```

Add these two lines to `ceph.conf` to inform the cluster which network to use for what communication.  Monitors like to talk on the public network, while the OSDs' heartbeat traffic is offloaded to the private network.
```
public network = 0.0.0.0/0
private network = 10.138.0.0/16
```

Install ceph on each of the nodes.
```
ceph-deploy install ceph-1 ceph-2 ceph-3
```

Spin up the monitor
```
ceph-deploy mon create-initial
```

Distribute keys
```
ceph-deploy admin ceph-1 ceph-2 ceph-3
```

Rev up the OSDs which are the nodes with extra storage attached.
```
ceph-deploy osd create ceph-1:sda ceph-2:sda ceph-3:sda
```

At this point you should check the health of your cluster.
```
ssh ceph-1 sudo ceph health

HEALTH OK
```

Or more verbosely,
```
ssh ceph-1 sudo ceph -s

    cluster 0006732f-d4d2-4377-9afb-85d59175db6f
     health HEALTH_OK
     monmap e1: 1 mons at {ceph-2=165.227.5.141:6789/0}
            election epoch 3, quorum 0 ceph-2
     osdmap e14: 3 osds: 3 up, 3 in
            flags sortbitwise,require_jewel_osds
      pgmap v26: 64 pgs, 1 pools, 0 bytes data, 0 objects
            101 MB used, 15225 MB / 15326 MB avail
                  64 active+clean
```

Before designating a Rados object storage gateway node, add these two lines to the `ceph.conf` file.  This will tell the [civetweb][] frontend to serve on port 80.
```
[client.rgw.ceph-3]
rgw_frontends = "civetweb port=80"
```

Deploy RadosGW on the node you specified in the above config.  You'll have to use the `--overwrite-conf` option and the logging output will report (incorrectly) that RGW is open on the default port 7480.
```
ceph-deploy --overwrite-conf rgw create ceph-3
```

If you wish to make any changes to the cluster configuration you'll have to push the config out to the affected node(s) and restart the applicable services on the node(s).
```
ceph-deploy --overwrite-conf config push ceph-3
ssh ceph-3 sudo systemctl restart ceph-radosgw@rgw.ceph-3
```

A quick test of the endpoint should show this XML response.
```
curl 138.197.208.154

<?xml version="1.0" encoding="UTF-8"?><ListAllMyBucketsResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>anonymous</ID><DisplayName></DisplayName></Owner><Buckets></Buckets></ListAllMyBucketsResult>
```

To use the gateway comfortably you can set up an `A` DNS record pointing to your `rgw` node.

To enable smooth interfacing with `s3cmd` add a wildcard `CNAME` DNS entry pointing to your (sub)domain.  Then add this line to your `ceph.conf` file under the rgw heading, push the configuration and restart the RadosGW service as noted above.
```
rgw dns name = "enjoyingmy.coffee"
```

Create a new user and display the creds (neatly thanks to [jq][])
```
ssh ceph-3 sudo radosgw-admin user create --uid="testuser" --display-name="First User"
ssh ceph-3 sudo radosgw-admin user info --uid="testuser" | jq -r '.keys'

[
  {
    "secret_key": "YGHb3Rhjkj22380Fjj2339f82ja93zlaKWwQzEV4",
    "access_key": "1L8OBBN92kd7HDjLER5Y",
    "user": "testuser"
  }
]
```

You are now ready to connect to your object storage gateway with [Boto][], for example.  Ceph has some [code snippets][] to get you going with Boto.

I've been messing with `s3cmd` following common sense and this fella's [blogpost][] but have not been able to store and retrieve objects.  _Update: adding the rgw dns name to the ceph configuration file solved this problem.  See next post._

Next step for this project:

* Automate the above ceph cluster deployment.  Probably would have to use some python or awk glue to swap out the monitor IPs in `ceph.conf`.  I'm also thinking how there are fancy tools like Ansible, Chef and Salt to handle those details.

* Put up a web front end where you could sign up for access and use the cluster just like s3.  Not sure if I'm going to get _right_ to that, though. ;)

* _Update: Implement a firewall!_

* * *

[ceph project]:     https://github.com/haggishunk/ceph-digitalocean
[ceph quickstart]:                  http://docs.ceph.com/docs/master/start/quick-ceph-deploy/
[ceph object gateway]:              http://docs.ceph.com/docs/master/install/install-ceph-gateway/
[jq]:                               https://stedolan.github.io/jq/
[boto]:                             http://docs.pythonboto.org/en/latest/s3_tut.html
[blogpost]:                         http://lollyrock.com/articles/s3cmd-with-radosgw/
[civetweb]:                         https://github.com/civetweb/civetweb
[code snippets]:                         http://docs.ceph.com/docs/master/radosgw/s3/python/
