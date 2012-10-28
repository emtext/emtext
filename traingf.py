#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main trainer for emtext.

Will use RSS feeds as trainning data. (We guess RSS usually have no Ads and no menu things.)
"""

import random
import re
import urllib2
import chardet
import feedparser
from ann import train

import gfparse

def train_from_rss(feeds):
    all_lines = []
    for link, content in feeds:
        text_clean = re.sub('<[^<]+?>', '', content)
        raw = urllib2.urlopen(link).read()
        encoding = chardet.detect(raw)['encoding']
        raw_uni = raw.decode(encoding)
        line_list = gfparse.extract_text(raw_uni.encode('utf-8'))
        line_list = map(lambda x:[x.bytes, len(x.text), x.text], line_list)
        line_list = [[line[2].strip().decode('utf-8', 'ignore'), float(line[1]) / line[0], line[1], line[0]] for line in line_list]
        line_list = [line + [(1 if line[0] in text_clean else 0)] for line in line_list]
        # 大于2行才有意义
        # 获取最后一个是1的,这样所有判断的才是确定是正确的。
        lines = []
        start = 0
        last = 0
        for index, val in enumerate(line_list):
            if val[-1]:
                last = index
            if val[-1] and not start:
                start = index
#        for index in range(last):
#            print str(line_list[index][5]) + str(line_list[index][1])[:4] + line_list[index][0]

        if len(line_list) > 2:
            fake_line = ['', 0, 0, 0, 0]
            line_list = [fake_line] + line_list + [fake_line]
            lines = [[line_list[i][1], line_list[i - 1][1], line_list[i + 1][1], line_list[i][-1]] for i in range(1, len(line_list) - 1)]

        all_lines += lines
    # Balance positive samples and negative samples:
    positive = [line for line in all_lines if line[-1] > 0]
    negative = [line for line in all_lines if line[-1] <= 0]
    random.shuffle(positive)
    random.shuffle(negative)
    min_len = min(len(positive), len(negative), 100)  # Too many samples may not a good thing.
    all_lines = positive[:min_len] + negative[:min_len]
    random.shuffle(all_lines)
    train(all_lines)
    with open('train.csv', 'w') as f:
        for line in all_lines:
            print line
            f.write(','.join(map(str, (line[0], line[-1]))) + '\n')

if __name__ == '__main__':
    feed_url = 'http://www.ruanyifeng.com/blog/atom.xml'
    feed = feedparser.parse(feed_url)
    feeds = []
    for item in feed['entries']:
        feeds.append((item['link'], item['content'][0]['value']))
    train_from_rss(feeds)


