#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main interface for emtext.
"""

from ann import train, check
from parse import Parser

def extract(html):
    p = Parser()
    # ToDo: 把 raw_uni 丢给密度计算器，算出每行文本的密度等属性。
    list = p.parserByDensity(html)

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

