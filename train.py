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
from ann import train
from html2text import html2text
from parse import Parser

if __name__ == '__main__':
    feed_list = (
#        'http://www.ifanr.com/feed',
#        'http://rss.mydrivers.com/rss.aspx?Tid=1',
        'http://www.ruanyifeng.com/blog/atom.xml',
        )
    p = Parser()
    for feed_url in feed_list:

        feed = feedparser.parse(open('atom.xml').read())
        allLines = []
        for item in feed['entries'][:5]:
            url = item['link']
            print url
            text_clean = re.sub('<[^<]+?>', '', item['content'][0]['value'])
#            text_clean = html2text(item['content'][0]['value'])
            print text_clean
            raw = urllib2.urlopen(item['link']).read()
            encoding = chardet.detect(raw)['encoding']
            raw_uni = raw.decode(encoding)
            print raw_uni
            # ToDo: 把 raw_uni 丢给密度计算器，算出每行文本的密度等属性。
            list = p.parser(raw_uni)
            # ToDo: 看每行文本是否出现在 text_clean 中，如果出现在里面，那么标记为 1 （也即：认为是正文）。
            for each in list:
                each[5] = int(each[0] in text_clean)
            # 检查被过滤掉的内容
            for t in [each[0] for each in list if each[5]==0]:
                print t
            # ToDo: 把训练集丢给 ann.py 里的 train 函数。
            # 保证所有的都是0或1
            [each.__setitem__(5, 0) for each in list if each[5]<0]
            first = True
            lines = []
            # 大于2行才有意义
            if len(list) > 2:
                for index in range(len(list)):
                    if index == 0:
                        lines.append(
                            [list[index][1], list[index][2], list[index][3], 0, 0, 0,
                             list[index + 1][1], list[index + 1][2], list[index + 1][3], list[index][5]])
                    if index == len(list) - 1:
                        lines.append(
                            [list[index][1], list[index][2], list[index][3], list[index - 1][1], list[index - 1][2], list[index - 1][3],
                             0, 0, 0, list[index][5]])
                    else:
                        lines.append(
                            [list[index][1], list[index][2], list[index][3], list[index - 1][1], list[index - 1][2], list[index - 1][3],
                             list[index + 1][1], list[index + 1][2], list[index + 1][3], list[index][5]])

        allLines += lines
        for each in allLines:
            print ','.join([str(e) for e in each])
        train(lines)

