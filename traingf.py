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
from ann import train, check

import gfparse

def train_from_rss(feeds):
    allLines = []
    for link, content in feeds:
        text_clean = re.sub('<[^<]+?>', '', content)
        raw = urllib2.urlopen(link).read()
        encoding = chardet.detect(raw)['encoding']
        raw_uni = raw.decode(encoding)
        lines = gfparse.extract_text(raw_uni.encode('utf-8'))
        lines = map(lambda x:[x.bytes, len(x.text), x.text], lines)
        lines = [[float(line[1]) / line[0], line[1], line[0], line[2].strip().decode('utf-8', 'ignore')] for line in lines]
        lines = [line + [(1 if line[3] in text_clean else 0)] for line in lines]
        lines = [[line[3]] + line for line in lines]
        # 大于2行才有意义
        # 获取最后一个是1的,这样所有判断的才是确定是正确的。
        line_list = lines
        lines = []
        start = 0
        last = 0
        for index, val in enumerate(line_list):
            if val[5]:
                last = index
            if val[5] and not start:
                start = index
        for index in range(last):
            print str(line_list[index][5]) + str(line_list[index][1])[:4] + line_list[index][0]

        if len(line_list) > 2:
            for index in range(len(line_list)):
#                if index < start:
#                    continue
                if index > last:
                    break
                if index == 0:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], 0, 0, 0,
                         line_list[index + 1][1], line_list[index + 1][2], line_list[index + 1][3], line_list[index][5]])
                if index == len(line_list) - 1:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], line_list[index - 1][1], line_list[index - 1][2], line_list[index - 1][3],
                         0, 0, 0, line_list[index][5]])
                else:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], line_list[index - 1][1], line_list[index - 1][2], line_list[index - 1][3],
                         line_list[index + 1][1], line_list[index + 1][2], line_list[index + 1][3], line_list[index][5]])

        allLines += lines
    # Balance positive samples and negative samples:
    positive = [line for line in allLines if line[-1] > 0]
    negative = [line for line in allLines if line[-1] <= 0]
    random.shuffle(positive)
    random.shuffle(negative)
    min_len = min(len(positive), len(negative))
    allLines = positive[:min_len] + negative[:min_len]
    random.shuffle(allLines)
    train(allLines)
    with open('train.csv', 'w') as f:
        for line in allLines:
            print line
            f.write(','.join(map(str, (line[0], line[-1]))) + '\n')

def extract(html):
    raw_uni = html
    lines = gfparse.extract_text(raw_uni.encode('utf-8'))
    lines = map(lambda x:[x.bytes, len(x.text), x.text], lines)
    lines = [[float(line[1]) / line[0], line[1], line[0], line[2].strip().decode('utf-8', 'ignore')] for line in lines]
    lines = [[line[3]] + line for line in lines]
    list = lines

    lines = []
    if len(list) > 2:
        for index in range(len(list)):
            if index == 0:
                lines.append(
                    [list[index][1], list[index][2], list[index][3], 0, 0, 0,
                     list[index + 1][1], list[index + 1][2], list[index + 1][3], list[index][0]])
            if index == len(list) - 1:
                lines.append(
                    [list[index][1], list[index][2], list[index][3], list[index - 1][1], list[index - 1][2], list[index - 1][3],
                     0, 0, 0, list[index][0]])
            else:
                lines.append(
                    [list[index][1], list[index][2], list[index][3], list[index - 1][1], list[index - 1][2], list[index - 1][3],
                     list[index + 1][1], list[index + 1][2], list[index + 1][3], list[index][0]])

    for line in lines:
        decision = check(line[:9])
        if decision:
            print str(line[1])[:4] , line[0], line[9]

def check_from_rss(feeds):
    p = Parser()
    allLines = []
    for link, content in feeds:
        text_clean = re.sub('<[^<]+?>', '', content)
        print text_clean
        raw = urllib2.urlopen(link).read()
        encoding = chardet.detect(raw)['encoding']
        raw_uni = raw.decode(encoding)
        # ToDo: 把 raw_uni 丢给密度计算器，算出每行文本的密度等属性。
        line_list = p.parserByDensity(raw_uni)

        lines = []
        if len(line_list) > 2:
            for index in range(len(line_list)):
                if index == 0:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], 0, 0, 0,
                         line_list[index + 1][1], line_list[index + 1][2], line_list[index + 1][3], line_list[index][0]])
                if index == len(line_list) - 1:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], line_list[index - 1][1], line_list[index - 1][2], line_list[index - 1][3],
                         0, 0, 0, line_list[index][0]])
                else:
                    lines.append(
                        [line_list[index][1], line_list[index][2], line_list[index][3], line_list[index - 1][1], line_list[index - 1][2], line_list[index - 1][3],
                         line_list[index + 1][1], line_list[index + 1][2], line_list[index + 1][3], line_list[index][0]])

    allLines += lines
    for line in allLines:
        if check(line[:9]):
            print str(line[1])[:4] + line[0]

def train_from_default():
    train([[i * 1.0 / 1000, 0, 0, 0, 0, 0, 0, 0, 0, int(i>= 500)]for i in range(1000)])

def train_from_random():
    l = [[i * 1.0 / 1000, 0, 0, 0, 0, 0, 0, 0, 0, int(i>= 500)]for i in range(1000)]
    random.shuffle(l)
    train(l)

def check_from_num():
#    l = [[i * 1.0 /100,] for i in range(100)]
#    for n,m in [(check(i),i[0]) for i in l]:
#        print str(n) + str(m)
    pass


if __name__ == '__main__':
#    feed_url = 'http://www.ruanyifeng.com/blog/atom.xml'
#    feed = feedparser.parse(feed_url)
#    feeds = []
#    for item in feed['entries'][:5]:
#        feeds.append((item['link'], item['content'][0]['value']))
#    train_from_rss(feeds)

    raw = urllib2.urlopen('http://www.ruanyifeng.com/blog/2012/02/44_weeks_of_words.html').read()
    encoding = chardet.detect(raw)['encoding']
    raw_uni = raw.decode(encoding)
    extract(raw_uni)

