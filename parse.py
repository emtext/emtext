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
    result = []

    def Parser(self, html):
        self._checkUnicode(html)
        tree = soupparser.fromstring(html)
        self.result = []
        self.garbage = []
        self._parser2(tree)
        return self.result, self.garbage

    tags_to_ignore=["head", "style", "script", "noscript", "<built-in function comment>", "option", "link", "meta", ]
    tags_in_newline=["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br", "li"]

    def _clear_ignore(self, tree):
        for each in tree:
            if each.tag in self.tags_to_ignore or each.tag is etree.Comment:
                tree.remove(each)
            else:
                self._clear_ignore(each)

    def _get_content(self, tree):
        text = ''
        if (str(tree.tag).lower() in self.tags_to_ignore):
            return ''
        if tree.text != None:
            text += tree.text
        for child in tree:
            text += self._get_content(child)
        if str(tree.tag).lower() in self.tags_in_newline:
            text += '\n'
        if tree.tail != None:
            text += tree.tail
        return text

    def _get_html(self, tree):
        text = ''
        if (str(tree.tag).lower() in self.tags_to_ignore):
            return ''
        if tree.text != None:
            text += tree.text
        for child in tree:
            text += self._get_html(child)
        if str(tree.tag).lower() in self.tags_in_newline:
            text += '\n'
        if tree.tail != None:
            text += tree.tail
        return text

    def _checkUnicode(self, html):
        assert type(html) == unicode, 'Input html text must be unicode!'
        return self.control_char_re.sub(' ', html)

    def _parser2(self, tree):
#        content = self._get_content(tree)
        text = tree.text if tree.text != None else ''
        tail = tree.tail if tree.tail != None else ''
        content = text + tail
        html = etree.tostring(tree, encoding = unicode)
        parentTag = tree.getparent().tag if tree.getparent() else ''
        child = []
        for each in tree:
            child.append(self._parser2(each))
        return {'self': ['', (1.0 * len(content)) / len(html), len(content), len(html), tree.tag, parentTag], 'child': child}

#    def _parser(self, tree):
#        text = tree.text if tree.text != None else ''
#        tail = tree.tail if tree.tail != None else ''
#        content = text + tail
#
#        if str(tree.tag).lower() == 'br':
#            return {'self': [content, 1.0 / len(totalLen), 1, totalLen, tree]}
#
#        html = etree.tostring(tree, encoding = unicode)
#        parentTag = tree.getparent().tag if tree.getparent() else ''
#        child = []
#        for each in tree:
#            child.append(self._parser(each))
#        return {'self': ['', (1.0 * len(content)) / len(html), len(content), len(html), tree.tag, parentTag], 'child': child}

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


                if htmllen:
                    self.result.append([text, float(len(text)) / htmllen, len(text), htmllen, each.tag, ''])

    list = []
    def _getDensity2(self, result):
        self.list.append(result['self'][1])
        for each in result['child']:
            self._getDensity2(each)

    def _getDensity(self):
        self.list = [each[1] for each in self.result]

    def _content(self, v=0.3):
        return [each[0] for each in self.result if each[1]>v]

if __name__ == '__main__':
    html = open('1.html', 'r')
    p = Parser()
    root = soupparser.fromstring(html)
    p._clear_ignore(root)
    result = p._parser2(root)
    p.list = []
    p._getDensity2(result)

    p._parser(root)
    p._getDensity()

    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'list.txt')
    f = open('list.txt', 'w')
    s = '\n'.join([str(each) for each in p.list if each!= 0])
    f.write(s)
    f.close()

    f = codecs.open("text.txt", "w", "utf-8")
    pickle.dump(p.result, f)
#    s = '\n'.join([str(each[1])+each[0] for each in p.result])
#    f.write(s)
    f.close()
#    print len(p._get_content(root))


