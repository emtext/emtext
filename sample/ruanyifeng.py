__author__ = 'zhouqi'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main trainer for emtext.

Will use RSS feeds as trainning data. (We guess RSS usually have no Ads and no menu things.)
"""
import feedparser
from train import train_from_rss, check_from_num

if __name__ == '__main__':
    feed_url = 'http://www.ruanyifeng.com/blog/atom.xml'
    feed = feedparser.parse(feed_url)
    feeds = []
    for item in feed['entries'][:5]:
        feeds.append((item['link'], item['content'][0]['value']))
    train_from_rss(feeds)
    check_from_num()

