Title:  Rancher UI Secured with SSL Using Nginx
Date: 2018-02-11
Tags: rancher,secure,ssl,nginx,lets_encrypt,cert
Category: blog

Don't you all want to deal with your cluster UI through a secure channel?  I sure did and yesterday I figured out how to do it.  Since Rancher runs in a docker container I am going to show you how to link up an Nginx container as a proxy server.

Rancher has some [documentation][] to this effect but here's a little more I wanted to fill in and update with this how-to.

The salient points:

* Obtain certificates (I prefer using [Let's Encrypt][], and in particular, [jrcs/letsencrypt-nginx-proxy-companion][])

* Start the Rancher server, preferably with a fixed name

* Configure Nginx to pipe inbound https requests to your Rancher UI and serve up the above certs

* Run Nginx and link it to the Rancher server

### Obtain certificates

You can purchase a certificate, use a self-signed cert, or go the cheap but secure route using Let's Encrypt.

For this demo I deployed a droplet on DigitalOcean, generated an alias 'A' DNS record with the desired domain name for my Rancher cluster and pointed it to the droplet's public IP address.

On that box, make a directory to store the SSL certs and keys.
```
mkdir $HOME/certs
```

Following the instructions on the letsencrypt-nginx-proxy-companion page, start an nginx-proxy container and link the `certs` folder as readonly.  The reverse proxy will be the linkage between the faux webpage (existing only for the purpose of domain verification) and the letsencrypt containers that you start next.
```
docker run -d \
    --name nginx-proxy \
    -p 80:80 -p 443:443 \
    -v $HOME/certs:/etc/nginx/certs:ro \
    -v /etc/nginx/vhost.d \
    -v /usr/share/nginx/html \
    -v /var/run/docker.sock:/tmp/docker.sock:ro \
    --label com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy \
    jwilder/nginx-proxy
```

Start the ole proxy companion (such an endearing name... reminds me of _Little House on the Prairie_).  This container does the heavy lifting of interfacing your faux webpage with the Let's Encrypt API and writing the SSL certs/keys to the `certs` folder you made.
```
docker run -d \
    --name nlepc \
    -v $HOME/certs:/etc/nginx/certs:rw \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    --volumes-from nginx-proxy \
    jrcs/letsencrypt-nginx-proxy-companion
```

Now stand up an nginx container to serve the default webpage with a `VIRTUAL_HOST` environment variable set to the domain you are registering.  The Let's Encrypt CSR requires two bits of information: the `LETSENCRYPT_HOST` which is the domain in question and a `LETSENCRYPT_EMAIL` to associate the request with.
```
docker run -d \
    --name nginx \
    -p 8000:80 \
    -e "VIRTUAL_HOST=$SSL_DOMAIN" \
    -e "LETSENCRYPT_HOST=$SSL_DOMAIN" \
    -e "LETSENCRYPT_EMAIL=$EMAIL" \
    nginx
```

Take a look at the `nlepc` container logs and you should see messages saying the certificates were received for the domain specified by `SSL_DOMAIN`.  The true domain name is redacted below.  You should see your domain name in place of `SSL_DOMAIN`.
```
docker logs -f nlepc

2018/02/11 19:27:40 Received event start for container 592c3a0c81ae
2018/02/11 19:27:55 Debounce minTimer fired
2018/02/11 19:27:55 Generated '/app/letsencrypt_service_data' from 3 containers
2018/02/11 19:27:55 Running '/app/update_certs'
/etc/nginx/certs/SSL_DOMAIN /app
Reloading nginx proxy (nginx-proxy)...
Q2018/02/11 19:27:55 Generated '/etc/nginx/conf.d/default.conf' from 3 containers
;2018/02/11 19:27:55 [notice] 53#53: signal process started
Creating/renewal SSL_DOMAIN certificates... (SSL_DOMAIN)
2018-02-11 19:27:55,810:INFO:simp_le:1538: Retrieving Let's Encrypt latest Terms of Service.
2018-02-11 19:27:56,434:INFO:simp_le:1356: Generating new account key
2018-02-11 19:27:57,999:INFO:simp_le:1455: Generating new certificate private key
2018-02-11 19:27:59,171:INFO:simp_le:463: Saving account_key.json
2018-02-11 19:27:59,173:INFO:simp_le:463: Saving key.pem
2018-02-11 19:27:59,173:INFO:simp_le:463: Saving chain.pem
2018-02-11 19:27:59,174:INFO:simp_le:463: Saving fullchain.pem
2018-02-11 19:27:59,175:INFO:simp_le:463: Saving cert.pem
```

Check out the `certs` folder.  Again, real domain names have been redacted.
```
ls certs/

accounts                            SSL_DOMAIN.crt
dhparam.pem                         SSL_DOMAIN.dhparam.pem
SSL_DOMAIN                          SSL_DOMAIN.key
SSL_DOMAIN.chain.pem
```

### Start the Rancher Server

Stop the three containers you used to get the certificates.  This command will stop all running containers-- use it only if you don't have other containers you'd like to keep running.
```
docker stop $(docker ps -aq)
```

Start your rancher server container and specify a name for it, vis-a-vis `$UI_NAME`.
```
docker run -d \
    --restart=unless-stopped \
    -p 8080:8080 \
    --name=$UI_NAME \
    rancher/server:stable
```

### Configure the Nginx Server

Make an nginx conf.d directory
```
mkdir -p ~/nginx/conf.d
```

Create a `rancher.conf` file in that directory with these contents.  Replace the server `$UI_NAME` with the name of the rancher server container.  Use the same `$ARBITRARY_NAME` in both the 443 and 80 listeners.  Put the `.crt` filename in place of $SSL_CERT_FILE and the `.key` filename in place of $SSL_KEY_FILE.  Since we will be mounting the `certs` directory as `/etc/nginx/certs` in the nginx container, that path will proceed the filenames. 
```
upstream rancher {
    server $UI_NAME:8080;
}

map $http_upgrade $connection_upgrade {
    default Upgrade;
    ''      close;
}

server {
    listen 443 ssl http2;
    server_name $ARBITRARY_NAME;
    ssl_certificate /etc/nginx/certs/$SSL_CERT_FILE;
    ssl_certificate_key /etc/nginx/certs/$SSL_KEY_FILE;

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://rancher;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        # This allows the ability for the execute shell window to remain open for up to 15 minutes. Without this parameter, the default is 1 minute and will automatically close.
        proxy_read_timeout 900s;
    }
}

server {
    listen 80;
    server_name $ARBITRARY_NAME;
    return 301 https://$server_name$request_uri;
}
```

The current nginx docker image does not support SPDY which is now superseded by HTTP/2.  The one change I had to make to Rancher's instructions was to change the line:
```
    listen 443 ssl spdy;
```
to
```
    listen 443 ssl http2;
```

### Run the Nginx Server

Seal the deal by starting an nginx container linked to the rancher server container.  Include the `certs` and `nginx/conf.d` directories as volumes so nginx knows to secure the rancher UI with the certificates you obtained above.
```
docker run -d \
    -p 80:80 -p 443:443 \
    -v $HOME/nginx/conf.d:/etc/nginx/conf.d:ro \
    -v $HOME/certs:/etc/nginx/certs:ro \
    --link=$UI_NAME \
    --name=$UI_NAME-nginx \
    nginx
```

Once the DNS record percolates down to the appropriate nameservers you should be able to browse to the Rancher server UI at the domain name you selected above.
<img src="{filename}/images/secured-rancher-ui.png" width="97%" align="middle">

And before you go running off spawning stacks, make sure to take care of **Access Controls** under the **Admin** tab!

* * *
[documentation]:        http://rancher.com/docs/rancher/v1.5/en/installing-rancher/installing-server/basic-ssl-config/
[let's encrypt]:                                https://letsencrypt.org/
[jrcs/letsencrypt-nginx-proxy-companion]:       https://hub.docker.com/r/jrcs/letsencrypt-nginx-proxy-companion/
