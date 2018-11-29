Title: Deploying My Very Own PaaS
Date: 2017-10-08
Tags: paas,dokku,terraform,automation
Category: blog

Tonight I can sleep soundly knowing that a very special little application is running out there on a virtual machine.  Check it out at [helloclock.mypaas.enjoyingmy.coffee](http://helloclock.mypaas.enjoyingmy.coffee).  I will admit it's not the most awesome thing ever, but if for some reason you cannot trust any of your timepieces yet you happen to have a browser (or [curl](https://curl.haxx.se)) this little ruby-on-rails app will let you know just how late you are.

Under the hood I have [terraform](https://www.terraform.io) spinning up a droplet (VM instance) on DigitalOcean and registering a DNS alias under GoogleCloud pointing to that machine.  Terraform also installs [Dokku](https://github.com/dokku/dokku) which is an open source PaaS tool.  Visit my github repo [haggishunk/proj_mypaas](https://github.com/haggishunk/proj_mypaas) for more details.

Here's one of the terraform `.tf` files that handles the virtual machine creation:

```
# digital ocean provider data cached in env variables
provider "digitalocean" {}

resource "digitalocean_droplet" "dokku" {
    image = "debian-9-x64"
    count = "${var.instances}"
    name = "${var.prefix}-${count.index+1}"
    region = "${var.do_region}"
    size = "${var.size}"
    backups = "False"
    ipv6 = "False"
    private_networking = "False"
    ssh_keys = ["${var.ssh_id}"]

    # Place your SSH public key on the
    # remote machine for dokku setup
    provisioner "file" {
        source = "~/.ssh/id_rsa.pub"
        destination = "/root/.ssh/id_rsa.pub"
        connection {
            type = "ssh"
            user = "root"
            private_key = "${file("~/.ssh/id_rsa")}"
        }
    }
    
    # Update your remote VM and install dokku
    provisioner "remote-exec" {
        inline = ["wget -nv -O - https://raw.githubusercontent.com/haggishunk/proj_mypaas/master/bootstrap.sh | bash",
                  "dokku apps:create ${var.appname}",
                  "dokku plugin:install https://github.com/dokku/dokku-postgres.git",
                  "dokku postgres:create rails-database",
                  "dokku postgres:link rails-database ${var.appname}"]
        connection {
            type = "ssh"
            user = "root"
            private_key = "${file("~/.ssh/id_rsa")}"
        }
    }
}

output "msg_hosts" {
    value = "Your are ready to go! Your dokku host is: ${join(", ", digitalocean_droplet.dokku.*.ipv4_address)}"
}

output "msg_apps" {
    value = "Your first application is deployed at: ${var.appname}.mypaas.${var.domain}"
}
```

Separate files store the variables referenced above and direct the Google Cloud DNS effort, which includes a wildcard 'A' record so the various apps that get deployed can reverse proxy through nginx on the dokku host.

You'll also notice a `bootstrap.sh` file gets pulled from github and run out on that remote machine.  Let me include that as well since the version I found on the official dokku github account didn't work for me.

```
# install prerequisites
apt-get update -qq > /dev/null
apt-get install -qq -y apt-transport-https

# install docker
wget -nv -O - https://get.docker.com/ | sh

# install dokku
wget -nv -O - https://packagecloud.io/gpg.key | apt-key add -
echo "deb https://packagecloud.io/dokku/dokku/ubuntu/ trusty main" | tee /etc/apt/sources.list.d/dokku.list
apt-get update -qq > /dev/null

echo "dokku dokku/web_config boolean false" | debconf-set-selections
echo "dokku dokku/vhost_enable boolean true" | debconf-set-selections
echo "dokku dokku/key_file string /root/.ssh/id_rsa.pub" | debconf-set-selections
# ***EDIT THE hostname string BELOW WITH YOUR DOMAIN NAME***
echo "dokku dokku/hostname string mypaas.enjoyingmy.coffee" | debconf-set-selections

apt-get install -qq -y --allow-unauthenticated dokku
dokku plugin:install-dependencies --core
```

I wasn't able to get a solid app pushed via terraform's `local-exec`, so I ran this script locally afterwards which essentially uploads the app via git.  Dokku processes the push into the app container, re-establishes the postgres db link and it's ready for viewing.

```
#!/usr/bin/bash

git clone git@github.com:heroku/ruby-rails-sample.git
cd ruby-rails-sample
git remote add dokku dokku@mypaas.enjoyingmy.coffee:helloclock
git push dokku master
```

The next iteration on this project will be to spin up several droplets, set them to have different roles, and tie them together as one unified front.
