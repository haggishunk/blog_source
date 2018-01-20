Title:  Ceph Storage Cluster on Digital Ocean Using Terraform (Part 2)
Date: 2018-01-11
Tags: ceph,storage,cluster,digital_ocean,terraform,provisioning,automation
Category: blog

So that bit about me getting a Ceph cluster off the ground a couple weeks ago?  Well I managed to have forgotten quite a bit of the intricacies in those few weeks.  I'll chalk it up the holidaze.

Anyways, after two days of wrangling terraform code, troubleshooting hosts files and discovering how simple SSH public key comments mean more than maybe they should I've got some working code up on [haggishunk/ceph-digitalocean][].

**Some design decisions I made:**

1. Use SSH 7.3's `Include` statement inside the `~/.ssh/config` file to link in host configuration from a separate file.  I chose this (a) to avoid tainting any config file you have and (b) to easily clean up between runs.  If you weren't aware, SSH goes with the first host def in the config file so stale entries will have you hanging out in space or stranger still, trying to connect to someone else's machine that got assigned your old IP.

2. Create an admin node in Digital Ocean instead of using a local Ubuntu VM.  This added the convolution of having to generate an SSH keypair on that machine and distribute it to the other nodes; likewise with the SSH config file and the `/etc/hosts` file.  I found `scp -3` to be of use here which routes the secure copy through your local machine.  I feel this decision makes this project more portable, but I'd be delighted to discuss its virtues and drawbacks.
```
scp -3 -o StrictHostKeyChecking=no ceph-admin:~/.ssh/authorized_keys ceph-1:~/.ssh/authorized_keys
```

**New things learned (and some old things re-discovered!):**

1. Ceph-deploy uses SSH to connect to nodes for installation, but not for monitor dispatch.  You must ensure that hostnames are resolvable which I did by adding lines to `/etc/hosts` on the admin node.

2.  Most supported distros don't have ceph-deploy in their default repos.  Had fun adding the repo to Debian jessie with these commands. _Update 1/19/18:  Note that Ubuntu's default repos have an old version of ceph-deploy.  You will hate life if you try running a cluster with this outdated version!_
```                                                                  
wget -q -O- 'https://download.ceph.com/keys/release.asc' | sudo apt-key add -
echo deb http://download.ceph.com/debian $(lsb_release -sc) main | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get install ceph-deploy
```

3.  Terraform's [HCL interpolation][] supports path introspection, for example `${path.root}` which gives the path that Terraform was run from.  I used this to handily store host entries without tainting the local filesystem or heaven forbid the local hosts file.
```
echo '${self.ipv4_address} ${self.name} ${self.name}' | tee -a ${path.root}/hosts_file
```

4.  The SSH public keyfile generated remotely on the admin node comes with a comment field `cephalus@ceph-admin` but when I sent this over to the nodes and placed it in their `authorized_keys` file my connection from the admin node was blocked.  I stripped out the comment with the ssh-keygen command's `-C` switch as so and was permitted entry.  _Update 1/19/18: Also specified a blank password with `-N ''` to eliminate the need for user interaction._
```
ssh-keygen -t rsa -b 4096 -f /home/${var.admin_user}/.ssh/id_rsa -N '' -C ''
```

* * *

[haggishunk/ceph-digitalocean]:     https://github.com/haggishunk/ceph-digitalocean
[pre-flight]:                       http://docs.ceph.com/docs/master/start/quick-start-preflight/
[hcl interpolation]:                https://www.terraform.io/docs/configuration/interpolation.html
