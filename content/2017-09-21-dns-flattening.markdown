Title: DNS Flattening
Date: 2017-09-21
Tags: 
Category: blog


Well it all began with [RFC 1034](https://tools.ietf.org/html/rfc1034), which was drafted back when I was still wincing over my parents buying me C64 instead of what all the other kids were getting: a Nintendo.  But once my little digits figured out how to plug in a 300 baud modem and hook up to local BBS'... and rack up exorbitant long distance telephone bills (but that's a story for another time)... ha-HA!  Lo and behold!

And yet by that time the burgeoning internet was demanding something better than FTPing a common 'HOSTS.TXT' file around.  As the RFC so succinctly put it:

```The impetus for the development of the domain system was growth in the
Internet```

Well said, Mr Paul Mockapetris.

And here we are now (actually this was in 2014) with CloudFlare's [DNS CNAME flattening](https://blog.cloudflare.com/introducing-cname-flattening-rfc-compliant-cnames-at-a-domains-root/) which seems to go against RFC 1034 and a later effort at clarification, [RFC 2181](https://tools.ietf.org/html/rfc2181).  People and companies like it because you can now host your site at the apex of your domain name. Simply visit `example.com`, instead of `www.example.com` or `root.example.com` with no redirects required.  This move has it's [detractors](https://serverfault.com/questions/613829/why-cant-a-cname-record-be-used-at-the-apex-aka-root-of-a-domain) but as I read through these ancient RFCs, the wisdom therein rings out.  Isn't the web all about extensibility and pioneering?

Amazon claims it doesn't break DNS specs, so I did some `dig`-ing into one of their [happy customers'](https://genius.com) DNS records.  Indeed, no illegal `CNAME` RR under `genius.com`, just happy `A` records pointing to cloudflare servers.
