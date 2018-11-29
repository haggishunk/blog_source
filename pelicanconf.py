#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Travis Mattera'
SITENAME = 'Pillow Talk'
SITEURL = 'http://blog.pantageo.us'
SITESUBTITLE = 'Meanderings and musings on building castles in the cloud'
PATH = 'content'
TIMEZONE = 'US/Pacific'
DEFAULT_LANG = 'en'

THEME = 'voidy-bootstrap-2'
STYLESHEET_FILES = ("pygment.css", "voidybootstrap.css",)
TYPOGRIFY = True
SUMMARY_MAX_LENGTH = 75
DEFAULT_PAGINATION = 5

SIDEBAR = ""

# SOCIAL =(('Twitter', 'https://twitter.com/slacknroll',
#          'fa fa-twitter-square fa-fw fa-lg'),
#         ('LinkedIn', 'http://linkedin.com/travis-mattera',
#          'fa fa-linkedin-square fa-fw fa-lg'),
#         ('GitHub', 'http://github.com/haggishunk',
#          'fa fa-github-square fa-fw fa-lg'),
#         )

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


# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
