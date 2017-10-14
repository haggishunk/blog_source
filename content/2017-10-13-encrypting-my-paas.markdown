Title: SSL Encryption for My PaaS
Date: 2017-10-13
Tags: dokku,letsencrypt,ssl,security,automation,beta
Category: blog

Getting your site and application equipped with SSL encryption and authentication is a basic requirement these days.  It can, however, be troublesome to get it implemented.  And it's easy to be conned into paying for a CA-signed cert.

Enter [Let's Encrypt](https://letsencrypt.org/).  LE is an open certificate authority (CA) that is for the people, complements of the Internet Security Research Group.  Their forte is automated certificate issuance and renewal.  There are a plethora of [ACME](https://ietf-wg-acme.github.io/acme/draft-ietf-acme-acme.html)-compliant avenues by which to grab yourself (or more accurately, your domain) a cert.

Today I opted for one of the web browser options, [https://gethttpsforfree.com/](https://gethttpsforfree.com/).  After a good bit of cutting & pasting command line action with `openssl`  I was presented with my signed certificate.  This was not a trivial process.  Even so, being involved in the exchange of information helped elucidate how the signing works.

When I later tried to apply the certs to my `helloclock` app on my [dokku host](2017-10-08-deploying-my-own-paas.markdown), I discovered one of the probably more common problems with SSL certs:  getting the domain right.  At the time I though I might be getting what I now know would be considered a wildcard domain cert (available through Let's Encrypt in [2018](https://letsencrypt.org/2017/07/06/wildcard-certificates-coming-jan-2018.html)), what with associating `www.pantageo.us`.  But when I planted it inside my dokku app, I found there was indeed a domain mismatch.

I didn't want to go through that cumbersome manual browser procedure again-- and Let's Encrypt is all but hyping you to use an automated agent.  Now with dokku running nginx I thought maybe I could just run `certbot` and point it to the `/var/www/` webroot folder as shown [here](https://certbot.eff.org/#debianstretch-nginx).  That didn't work as hoped.  So I did some searching and found this beauty:  a [dokku-letsencrypt](https://github.com/dokku/dokku-letsencrypt) plugin.

After merely entering these three commands, my [app](https://helloclock.mypaas.pantageo.us) was humming along on https:
```
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart helloclock DOKKU_LETSENCRYPT_EMAIL="<travis@pantageo.us>"
dokku letsencrypt helloclock
```

Note the second command sets an environment variable to my email address.  Running the `letsencrypt` plugin without an email specified will error out.
