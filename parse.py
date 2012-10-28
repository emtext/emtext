#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copied from http://gfnpad.blogspot.ca/2009/11/blog-post.html
"""

import chardet
import htmllib,urllib2
import formatter,StringIO

class TrackParser(htmllib.HTMLParser):

    def __init__(self, writer, *args):
        htmllib.HTMLParser.__init__(self,*args)
        self.writer = writer
  
    def parse_starttag(self,i):
        index = htmllib.HTMLParser.parse_starttag(self,i)
        self.writer.index = index
        return index

    def parse_endtag(self,i):
        self.writer.index = i
        return htmllib.HTMLParser.parse_endtag(self,i)


class Para:

    def __init__(self):
        self.text = ''
        self.bytes = 0
        self.density = 0.0

class LineWirter(formatter.AbstractWriter):
    """
    a Formatter instance to get text in lines
    """

    def __init__(self):
        self.last_index = 0
        self.lines = [Para()]
        formatter.AbstractWriter.__init__(self)

    def send_flowing_data(self, data):
        t = len(data)
        self.index += t
        b = self.index - self.last_index
        self.last_index = self.index
        l = self.lines[-1]
        l.text += data
        l.bytes += b

    def send_paragraph(self,blankline):
        if self.lines[-1].text == '':
            return
        self.lines[-1].text += ' '*(blankline+1)
        self.lines[-1].bytes += 2*(blankline+1)
        self.lines.append(Para())
      
    def send_literal_data(self,data):
        self.send_flowing_data(data)
  
    def send_line_break(self):
        self.send_paragraph(0)



def extract_text(html):

    writer = LineWirter()
    fmt = formatter.AbstractFormatter(writer)
    parser = TrackParser(writer,fmt)
    parser.feed(html)
    parser.close()
    return writer.lines


if __name__ == '__main__':
    htmls = urllib2.urlopen('http://www.ruanyifeng.com/blog/2012/02/44_weeks_of_words.html')
    raw = htmls.read()
    encoding = chardet.detect(raw)['encoding']
    raw_uni = raw.decode(encoding)
    s = map(lambda x:[x.bytes, len(x.text), x.text],extract_text(raw_uni.encode('utf-8')))
    for line in s:
        print line[0], line[1], line[2]

