# encoding:utf-8
import codecs
import os
import pickle
import re
import urllib2
import chardet
from lxml import etree
from lxml.html import soupparser
from html2text import html2text

__author__ = 'zhouqi'

class Parser(object):
    control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    tags_to_ignore=["head", "style", "script", "noscript", "<built-in function comment>", "option", "link", "meta", ]
#    tags_in_newline=["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br", "li"]
    tags_in_newline=["div"]
    result = []

    def parserBase(self, html):
        return soupparser.fromstring(html)

    def parserByDensity(self, html):
        """
        用比重来过滤文本
        """
#        self._checkUnicode(html)
        tree = soupparser.fromstring(html)
        self.result = []
        self._clear_ignore(tree)
        self._parser(tree)
        return self.result

    def parserWithMain(self, html):
        """
        抓取页面主要部分
        """
        tree = soupparser.fromstring(html)
        self._clear_ignore(tree)
        return self._findMain(tree)

    def parserWithMainLvl(self, tree):
        """
        抓取页面的主要层次
        """
        lvl = 1
        result = []
        while(True):
            cnt, subCnt = self._countByLvl(tree, lvl)
            result.append((cnt, lvl))
            lvl += 1
            if subCnt == 0:
                break
        d = dict(result)
        maxLvl = d[max(d.keys())]
        root = etree.Element("div")
        self._addToRoot(tree, root, maxLvl)
        return root

    def _addToRoot(self, tree, root, leftLvl=1):
        if leftLvl == 1:
            for each in tree:
                root.append(each)
        else:
            for each in tree:
                self._addToRoot(each, root, leftLvl-1)

    def _countByLvl(self, tree, leftLvl=1):
        if leftLvl == 1:
            cnt = 0
            subCnt = 0
            for each in tree:
                cnt += len(each.text if each.text else '')
                subCnt += len(each)
            return cnt,subCnt
        else:
            result = []
            for each in tree:
                result.append(self._countByLvl(each, leftLvl - 1))
            return reduce(lambda x, y: (x[0]+y[0], x[1]+y[1]), result, (0, 0))



    def _findMain(self, tree, pct=0.5):
        cnt = self._count(tree)
        (maxSubCnt, maxSubTree) = self._getMaxPart(tree)
        if 1.0 * maxSubCnt / cnt < pct:
            return tree
        else:
            return self._findMain(maxSubTree, pct)

    def _getMaxPart(self, tree):
        maxCnt = 0
        maxTree = None
        for each in tree:
            cnt = self._count(each)
            if maxCnt < cnt:
                maxCnt = cnt
                maxTree = each
        return maxCnt, maxTree

    def _count(self, tree):
        count = 0
        for each in tree.itertext():
            count += len(each.rstrip())
        return count

    def filterByReduceCount(self, tree):
        """
        根据reduce count过滤掉同级的元素，可用于过滤评论
        """
        l = [(self._countWithReduce(each), each) for each in tree]
        sum = reduce(lambda x,y: x + y, [each[0] for each in l], 0)
        for d in [each[1] for each in l if each[0] * len(l) < sum]:
            tree.remove(d)
        return tree

    def _countWithReduce(self, tree, reduce=1):
        """
        有递减的count
        """
        count = 0
        for each in tree:
            count += len(each.text.rstrip() if each.text else '') * 1.0 * reduce
            count += self._countWithReduce(each, reduce / 2)
        return count

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
    link = 'http://www.elias.cn/MyProject/ExtMainText'
    raw = urllib2.urlopen(link).read()
    encoding = chardet.detect(raw)['encoding']
    html = raw.decode(encoding)
#    html = open('3.html', 'r')
    p = Parser()
#    print '\n'.join([each for each in html2text(etree.tostring(p.filterByReduceCount(p.parserWithMain(html)), encoding=unicode)).split('\n') if len(each.rstrip())])
#    print '\n'.join([each for each in html2text(etree.tostring(p.parserWithMain(html), encoding=unicode)).split('\n') if len(each.rstrip())])
    print '\n'.join([each for each in html2text(etree.tostring(p.parserWithMainLvl(p.parserBase(html)), encoding=unicode)).split('\n') if len(each.rstrip())])

