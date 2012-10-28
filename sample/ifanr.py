#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

__author__ = 'zhouqi'


"""
Main trainer for emtext.

Will use RSS feeds as trainning data. (We guess RSS usually have no Ads and no menu things.)
"""
import feedparser
from train import train_from_rss, check_from_num, check_from_rss

if __name__ == '__main__':
    feed_url = 'http://www.ifanr.com/feed'
    feed = feedparser.parse(feed_url)
    feeds = []
    for item in feed['items'][:5]:
        content = item['description']
        if u'爱范儿 · Beats of Bits' in content:
            content[:content.index(u'爱范儿 · Beats of Bits')]
#        text_clean = re.sub('<[^<]+?>', '', content)

        feeds.append((item['link'], content))
    train_from_rss(feeds)
    check_from_rss(feeds)

