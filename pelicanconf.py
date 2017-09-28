#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Travis Mattera'
SITENAME = 'Pillow Talk'
SITEURL = 'http://www.pantageo.us'
SITESUBTITLE = 'Daily meanderings and musings on building castles in the cloud'
LANDING_PAGE_ABOUT = 'hmm'
PATH = 'content'

TIMEZONE = 'US/Pacific'

DEFAULT_LANG = 'en'

THEME = 'voidy-bootstrap'
TYPOGRIFY = True
SUMMARY_MAX_LENGTH = 150

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
