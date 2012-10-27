#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main trainer for emtext.

Will use RSS feeds as trainning data. (We guess RSS usually have no Ads and no menu things.)
"""

import re
import urllib2
import chardet
import feedparser

if __name__ == '__main__':
    feed_list = ('http://www.ifanr.com/feed',
                 'http://rss.mydrivers.com/rss.aspx?Tid=1',
                 )
    for feed_url in feed_list:
        feed = feedparser.parse(feed_url)
        for item in feed['items']:
            url = item['link']
            print url
            text_clean = re.sub('<[^<]+?>', '', item['description'])
            print text_clean
            raw = urllib2.urlopen(item['link']).read()
            encoding = chardet.detect(raw)['encoding']
            raw_uni = raw.decode(encoding)
            print raw_uni
            # ToDo: 把 raw_uni 丢给密度计算器，算出每行文本的密度等属性。
            # ToDo: 看每行文本是否出现在 text_clean 中，如果出现在里面，那么标记为 1 （也即：认为是正文）。
            # ToDo: 把训练集丢给 ann.py 里的 train 函数。

