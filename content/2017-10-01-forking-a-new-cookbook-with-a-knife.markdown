Title: Forking a Cookbook with a Knife (Overextending a Culinary Metaphor)
Date: 2017-10-01
Tags: automation,chef,knife,supermarket
Category: blog

Today I started using Chef, specifically `chef-solo`, to stand up an Apache server, and after some config file changes, swap it out for an Nginx server.  Part of the experiment here was that I wrote a custom `index.html` landing page and used a chef recipe to link that file into each server's content root.  Switching servers had no visible difference for the casual user.  This decouples the application from the content, which I'm learning is a good practice.

I also explored using the `knife` command which is bundled with the Chef suite.  I've heard some deriding the use of `knife` to fiddle with individual machines' runtime environs but in my research it turns out to be a great way to [grab community cookbooks](https://docs.chef.io/knife_cookbook_site.html) from the Chef Supermarket.

I used the following command to grab the tarball:

`knife cookbook site download nginx -f nginx_cookbook.tgz`

From there you simply extract into your cookbook directory and go forth calling it out in your recipes.
