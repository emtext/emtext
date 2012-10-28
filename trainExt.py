#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet
import re
import urllib2
import lxml

import ExtMainText

def train_from_rss(feeds):
    allLines = []
    for link, content in feeds:
        text_clean = re.sub('<[^<]+?>', '', content)
        raw = urllib2.urlopen(link).read()
        encoding = chardet.detect(raw)['encoding']
        raw_uni = raw.decode(encoding)
        tree = lxml.html.soupparser.fromstring(raw_uni)
        density_tree = ExtMainText._calcDensity(tree)
        # ToDo: 把 raw_uni 丢给密度计算器，算出每行文本的密度等属性。
        line_list = p.parserByDensity(raw_uni)
        # ToDo: 看每行文本是否出现在 text_clean 中，如果出现在里面，那么标记为 1 （也即：认为是正文）。
        for each in line_list:
#            each[5] = int(each[0] in text_clean)
            each[5] = int(each[0] in text_clean)

        # ToDo: 把训练集丢给 ann.py 里的 train 函数。
        # 保证所有的都是0或1
        [each.__setitem__(5, 0) for each in line_list if each[5]<0]
        first = True
        lines = []
        # 大于2行才有意义
        # 获取最后一个是1的,这样所有判断的才是确定是正确的。
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

