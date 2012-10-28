__author__ = 'zhouqi'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main trainer for emtext.

Will use RSS feeds as trainning data. (We guess RSS usually have no Ads and no menu things.)
"""

import urllib2
import chardet
import feedparser

from train import train_from_rss, check_from_num, check_from_rss
import emt


if __name__ == '__main__':
#    feed_url = 'http://www.ruanyifeng.com/blog/atom.xml'
#    feed = feedparser.parse(feed_url)
#    feeds = []
#    for item in feed['entries'][:5]:
#        feeds.append((item['link'], item['content'][0]['value']))
#    train_from_rss(feeds)
#    check_from_rss(feeds)
    raw = urllib2.urlopen('http://www.ruanyifeng.com/blog/2012/02/44_weeks_of_words.html').read()
    encoding = chardet.detect(raw)['encoding']
    raw_uni = raw.decode(encoding)
    emt.extract(raw_uni)

