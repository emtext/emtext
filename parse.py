# encoding:utf-8
import codecs
import os
import pickle
import re
from lxml import etree
from lxml.html import soupparser

__author__ = 'zhouqi'

class Parser(object):
    control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    tags_to_ignore=["head", "style", "script", "noscript", "<built-in function comment>", "option", "link", "meta", ]
    tags_in_newline=["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br", "li"]
    result = []

    def parser(self, html):
#        self._checkUnicode(html)
        tree = soupparser.fromstring(html)
        self.result = []
        self._clear_ignore(tree)
        self._parser(tree)
        return self.result


    def _clear_ignore(self, tree):
        """
        remove nouse item in html
        """
        for each in tree:
            if each.tag in self.tags_to_ignore or each.tag is etree.Comment:
                tree.remove(each)
            else:
                self._clear_ignore(each)
        # 去除空的p及div
        for each in tree.getiterator():
            if each.tag.lower() in ['p', 'div'] and len(each) == 0 and len((each.text if each.text else '').lstrip()) == 0:
                each.getparent().remove(each)

    def _checkUnicode(self, html):
        """
        check html unicode
        """
        assert type(html) == unicode, 'Input html text must be unicode!'
        return self.control_char_re.sub(' ', html)

    def _parser(self, tree):
        f_each = True
        for each in tree.getiterator():
            if f_each:
                f_each = False
                continue
            if each.tag.lower() in self.tags_in_newline:
                htmllen = len(etree.tostring(each, encoding = unicode))
                hasSubLine = False
                text = each.text if each.text else ''
                f_sub = True
                for sub in each.getiterator():
                    if f_sub:
                        f_sub = False
                        continue
                    if sub.tag.lower() in self.tags_in_newline:
                        hasSubLine = True
#                        htmllen -= len(etree.tostring(sub, encoding = unicode))
                    if not hasSubLine:
                        text += sub.text if sub.text else ''
                if not hasSubLine:
                    text = ''
                    for t in each.itertext():
                        text += t
                text = text.lstrip()
                if text and htmllen:
                    self.result.append([text, float(len(text)) / htmllen, len(text), htmllen, each.tag, '', -1])


if __name__ == '__main__':
    html = open('2.html', 'r')
    p = Parser()
    f = codecs.open("text.txt", "w", "utf-8")
    p.parser(html)
#    pickle.dump(p.parser(html), f)
    f.close()
#    print ''.join([each[0] for each in p.result])
    print '\n'.join([each[0] for each in p.result if each[1]>0.5])


