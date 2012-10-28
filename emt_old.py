#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main interface for emtext.
"""

import urllib2
import chardet

from ann import  check
import parse_old

def extract(raw_uni):
    parser = parse_old.Parser()
    line_list = parser.parserByDensity(raw_uni)
    lines = [line[:4] for line in line_list]
    fake_line = ['', 0, 0, 0]
    lines = [fake_line] + lines + [fake_line]
    lines = [[lines[i][1], lines[i - 1][1], lines[i + 1][1], lines[i][0]] for i in range(1, len(lines) - 1)]

    for line in lines:
        decision = check(line[:3])
        if decision > 0.4:
#            print line[0], line[-1]
            yield line[-1]

def extract_url(url):
    raw = urllib2.urlopen(url).read()
    encoding = chardet.detect(raw)['encoding']
    raw_uni = raw.decode(encoding)
    for line in extract(raw_uni):
        yield line

if __name__ == '__main__':
    for line in extract_url('http://www.ruanyifeng.com/blog/2012/02/44_weeks_of_words.html'):
        print line
    print '===='
    for line in extract_url('http://news.mydrivers.com/1/245/245054.htm'):
        print line


