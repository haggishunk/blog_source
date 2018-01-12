Title:  Ceph Storage Cluster on Digital Ocean Using Terraform
Date: 2018-01-09
Tags: ceph,storage,cluster,digital_ocean,terraform,provisioning,automation
Category: blog

A couple weeks ago I got my first [Ceph][] storage cluster off the ground using the fantastic documentation on their website.  Today I sat down and fleshed out the infrastructure through another handy tool, [Terraform][], from the same [people][] that brought you Vagrant.  My github [repo][] haggishunk/ceph-digitalocean is out there for any to examine & experiment.

What makes Ceph neat is that it's open source _and_ it features device, block and object storage on a cluster of heterogenous machines and volumes.

In my hunt to automate the entire process I've so far got Terraform provisioning the droplets, connecting volumes, and setting up a ceph user account on each droplet node.  This accomplishes the [pre-flight][] steps outlined in Ceph's docs for `ceph-deploy`.  The docs also cover using `ceph` as a study in how the system works and `helm` to streamline incorporation into a Kubernetes environment.  I for sure plan on getting to the helm method once I master ceph-deploy.

Today went well and I learned a couple things:

* Got happiness using `self` inside a droplet provisioner to write host info into the SSH config files (see `"remote-exec"` below).
* Learned that ceph-deploy requires python2 installed on the cluster nodes.  Make sure to install it if using 16.04 LTS.

Here's the meat of the code from `instances.tf`:
```
resource "digitalocean_droplet" "ceph" {
    image                   = "${var.image}"
    count                   = "${var.instances}"
    name                    = "${var.prefix}-${count.index+1}"
    region                  = "${var.do_region}"
    size                    = "${var.size}"
    volume_ids              = ["${element(digitalocean_volume.ceph-vol.*.id, count.index)}"]
    backups                 = "False"
    ipv6                    = "False"
    private_networking      = "True"
    ssh_keys                = ["${var.ssh_id}"]


    # remote connection key
    connection {
        type                = "ssh"
        user                = "root"
        private_key         = "${file("~/.ssh/id_rsa")}"
    }

    # Update your remote VM
    # provision node user
    # setup ssh access for admin node
    provisioner "remote-exec" {
        inline =    [   "apt-get -qq -y update",
                        "apt-get -qq -y install ntp",
                        "apt-get -qq -y install openssh-server",
                        "useradd -d /home/${var.node_user} -m ${var.node_user}",
                        "echo '${var.node_user} ALL = (root) NOPASSWD:ALL' | tee /etc/sudoers.d/${var.node_user}",
                        "chmod 0440 /etc/sudoers.d/${var.node_user}",
                        "mkdir /home/${var.node_user}/.ssh",
                        "cp /root/.ssh/authorized_keys /home/${var.node_user}/.ssh/authorized_keys",
                        "chown -R ${var.node_user}:${var.node_user} /home/${var.node_user}",
                        "chmod 0700 /home/${var.node_user}/.ssh",
                        "chmod  600 /home/${var.node_user}/.ssh/authorized_keys",
                    ]
    }

    provisioner "local-exec" {
        command =   "echo '\nHost ${self.name}\n    HostName ${self.ipv4_address}\n    User ${var.node_user}' | tee -a ~/.ssh/config"
    }
}
```
[ceph]:             http://ceph.com
[terraform]:        https://www.terraform.io
[people]:           https://www.hashicorp.com
[repo]:             https://github.com/haggishunk/ceph-digitalocean
[pre-flight]:       http://docs.ceph.com/docs/master/start/quick-start-preflight/
