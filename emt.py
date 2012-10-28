#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main interface for emtext.
"""

import urllib2
import chardet

from ann import  check
import parse

def extract(raw_uni):
    lines = parse.extract_text(raw_uni.encode('utf-8'))
    lines = map(lambda x:[x.bytes, len(x.text), x.text], lines)
    lines = [[line[2].strip().decode('utf-8', 'ignore'), float(line[1]) / line[0], line[1], line[0]] for line in lines]
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

