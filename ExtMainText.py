#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parses HTML and extracts main text parts.

ExtMainText parses HTML document, extracts main text, and filters out
advertisements and common menus from it.

This module bases on version 0.1a of http://www.elias.cn/En/ExtMainText ,
but rewrite using lxml, and counts on the density of pure text versus total
length of original html description. Current algorithm is inspired by
http://ai-depot.com/articles/the-easy-way-to-extract-useful-text-from-arbitrary-html/

The old version (0.1a and earlier) bases on the measure of html tag
density, and determines density threshold according to historical
experience. Related algorithm comes from
http://www.xd-tech.com.cn/blog/article.asp?id=59

Attention:
    Current module can not pick up short message such as Twitter ones,
    because very small text looks the same as ads and common parts of pages.

    For sites like Twitter, analyzing html tag and CSS class structure
    is a better way to get main text.

Usage:
    There are two modes to call ExtMainText according to the 'filterMode'
    parameter:
    * When 'filterMode' is False (by default), it's the normal 'Extract'
    mode, which will try to find out and return the major content of html
    document, and filter out all rubbish, even comments relate to the
    document. And it's possible that the module eat the title of the
    document for specific page style.
    * When 'filterMode' is True, it's the 'Filter' mode, which will
    filter out all invaluable parts, such as ads, spams, menu links, etc,
    and return the remain part (Not really ALL of them, most of them
    in fact, depends on page presentation style). Normally, this mode
    is safer than the other, because it reserve as many material as it can.
    Usually, comments could be reserved in this mode.

    The "if __name__ == '__main__'" block gives out simple demo for how
    to use ExtMainText.

    The static threshold 0.5 works good enough for most web sites in
    English language. For other language, such as Chinese, you need to
    analyze the distribution of density for each html tag branch, and
    choose a threshold clearly distinguish main content and others.

Here, have some legalese:

Copyright (c) 2009, Elias Soong

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of its author nor the names of its contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE, DAMMIT.

"""

__author__ = "Elias Soong (elias.soong@gmail.com)"
__version__ = "0.2a"
__copyright__ = "Copyright (c) 2009 Elias Soong"
__license__ = "New-style BSD"

import re
from lxml import etree
#_parser = etree.HTMLParser()
#parse = lambda x: etree.fromstring(x, _parser)
# SoupParser is more robust than lxml's default html parser sometimes:
import lxml.html.soupparser

def extMainText(html, threshold = 0.5, filterMode = False):
    """
    Parses HTML and keeps only main text parts.

    PARAMETERS:
    html - Input html text, MUST BE UNICODE!
    threshold - The density threshold to distinguish major content & others.
    filterMode - Use normal 'Extract' mode or the other 'Filter' mode.

    RETURN:
    html fragments of main text
    """
    html = _removeControlChars(html)
    # If we prepare a BeautifulSoup instance manually and pass it to lxml.html.soupparser.convert_tree()
    # then this func work well as 'import ExtMainText' but will throw strange error for 'import jqhtml.ExtMainText'.
    root = lxml.html.soupparser.fromstring(html)
    densDic = _calcDensity(root)
    if filterMode:
        return _filterSpam(densDic, threshold)
    else:
        maxPart, textLen, maxPartChilds, textLenChilds = _getMainText(densDic, threshold)
        if textLenChilds > textLen:
            return ''.join(map(lambda tree: etree.tostring(tree, encoding = unicode) if tree != None else '', maxPartChilds))
        else:
            return etree.tostring(maxPart, encoding = unicode) if maxPart != None else ''

#import unicodedata
#all_chars = (unichr(i) for i in xrange(0x110000))
#control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
# or equivalently and much more efficiently
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def _removeControlChars(html):
    """
    Replace null bytes in html text with space char to walk around lxml bug in _convert_tree func.

    PARAMETERS:
    html - The original html text (must be unicode).

    RETURN:
    replaced html text.
    """
    assert type(html) == unicode, 'Input html text must be unicode!'
    return control_char_re.sub(' ', html)

def _getMainText(densDic, threshold):
    """
    Get the largest html fragment with text density larger than threshold according 
    to density dictionary.

    And the largest html fragment could be made up of several continuous brother
    html branches.

    Return: (etree instance, text length, list of child etrees, total text length of child etrees)
    """
    dens, textLen, totalLen, tree = densDic['self']
    maxChildTrees = []
    maxChildTreesTextLen = 0
    # If density is bigger than threshold, current tag branch is the largest:
    if dens >= threshold:
        maxTree = tree
        maxTextLen = textLen
    # If density of current tag branch is too small, check its children:
    else:
        maxTree = None
        maxTextLen = 0
        maxChildSubTrees = []
        maxChildSubTreesTextLen = 0
        childTreesTmp = []
        childTreesTmpTextLens = []
        childTreesTmpTotalLens= []
        if densDic.has_key('child'):
            for childDic in densDic['child']:
                childDens, childTextLen, childTotalLen, childTree = childDic['self']
                tree, textLen, childTrees, childTreesTextLen = _getMainText(childDic, threshold)
                # Remember the largest tag branches of children:
                if childTreesTextLen > maxChildSubTreesTextLen:
                    maxChildSubTrees, maxChildSubTreesTextLen = childTrees, childTreesTextLen
                childTreesTmp.append(childTree)
                childTreesTmpTextLens.append(childTextLen)
                childTreesTmpTotalLens.append(childTotalLen)
                if textLen > maxTextLen:
                    maxTree = tree
                    maxTextLen = textLen
            # Find the largest html fragment under current tag branch:
            for j in range(1, len(childTreesTmp) + 1):
                for i in range(j):
                    childTreesTmpTotalLen= sum(childTreesTmpTotalLens[i:j])
                    childTreesTmpTextLen = sum(childTreesTmpTextLens[i:j])
                    childTreesTmpTotalLen = 1 if childTreesTmpTotalLen == 0 else childTreesTmpTotalLen
                    if float(childTreesTmpTextLen) / childTreesTmpTotalLen >= threshold:
                        if childTreesTmpTextLen > maxChildTreesTextLen:
                            maxChildTrees = childTreesTmp[i:j]
                            maxChildTreesTextLen = childTreesTmpTextLen
            # Compare html fragment of current tag branch and the ones of children:
            if maxChildSubTreesTextLen > maxChildTreesTextLen:
                maxChildTrees, maxChildTreesTextLen = maxChildSubTrees, maxChildSubTreesTextLen
    return (maxTree, maxTextLen, maxChildTrees, maxChildTreesTextLen)

def _filterSpam(densDic, threshold):
    """
    Walk through html document, drop off all etree branches that having low text
    density, and return the left parts of fragments.

    Return: html fragments of main text
    """
    dens, textLen, totalLen, tree = densDic['self']
    # If density is larger than threshold, keep and return current tag branch:
    if dens >= threshold:
        return etree.tostring(tree, encoding = unicode)
    if str(tree.tag).lower() == 'br':
        return etree.tostring(tree, encoding = unicode)
    # If density of current tag branch is too small, check its children:
    else:
        frags = []
        if densDic.has_key('child'):
            for childDic in densDic['child']:
                frags.append(_filterSpam(childDic, threshold))
        return ''.join(frags)

def _calcDensity(tree):
    """
    Calculate the text density for every etree branch. The define of text density is:
    (the length of pure text content under current html tag) / (total length of all content under current html tag)

    Return: {'self': (tag density, length of pure text, total length of html tags and text, etree instance), 
    'child': list of density dics for child entities }
    """
    tag = str(tree.tag).lower()
    if (tag == '<built-in function comment>' or
       tag == 'script' or
       tag == 'noscript' or
       tag == 'style'):
        return {'self': (0.0, 0, 0, tree)}
    text = tree.text if tree.text != None else ''
    tail = tree.tail if tree.tail != None else ''
    countTextLen = len(text.strip()) + len(tail.strip())
    totalLen = len(etree.tostring(tree, encoding = unicode)) if tree != None else 0
    if str(tree.tag).lower() == 'br':
        return {'self': (1.0 / totalLen, 1, totalLen, tree)}
    dicList = []
    treeOrig = tree[:]
    for subtree in treeOrig:
        textNode = None
        if subtree.tail and len(subtree.tail.strip()) > 0:
            index = tree.index(subtree)
            textNode = subtree.tail
            subtree.tail = ''
        dic = _calcDensity(subtree)
        dicList.append(dic)
        textLen = dic['self'][1]
        countTextLen += textLen
        # Treat subtree.tail as an independent etree branch:
        if textNode != None:
            textNodeTotalLen = len(textNode)
            textNodeTextLen = len(textNode.strip())
            textTree = etree.Element('span')
            textTree.text = textNode
            tree.insert(index + 1, textTree)
            dicList.append({'self': (float(textNodeTextLen) / textNodeTotalLen, textNodeTextLen, textNodeTotalLen, textTree)})
            countTextLen += textNodeTextLen
    density = float(countTextLen) / totalLen if totalLen != 0 else 0.0
    return {'self': (density, countTextLen, totalLen, tree), 'child': dicList}

if __name__ == '__main__':
    def get_text(html):
        root = lxml.html.soupparser.fromstring(html)
        tags_to_ignore=["head", "style", "script", "noscript", "<built-in function comment>", "option"],
        tags_in_newline=["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br", "li"]
        def _get_text(tree):
            text = ''
            tag = str(tree.tag).lower()
            if (tag == '<built-in function comment>' or 
               tag == 'style' or
               tag == 'script' or
               tag == 'noscript' or
               str(tree.tag).lower() in tags_to_ignore):
                return ''
            if tree.text != None:
                text += tree.text
            for child in tree:
                text += _get_text(child)
            if str(tree.tag).lower() in tags_in_newline:
                text += '\n'
            if tree.tail != None:
                text += tree.tail
            return text
        return _get_text(root)
        
    import sys, os
    if len(sys.argv) < 2:
        print """Extract the main text of a html document.
  Usage: python ExtMainText.py %HTML_FILE_NAME% %THRESHOLD%
         %HTML_FILE_NAME% is the file name of target html document
         %THRESHOLD% the text density threshold (Default: 0.5)
  Suggest: English document could choose %THRESHOLD% as 0.5
           Chinese document could try %THRESHOLD% as 0.5 either
           But you should find suitable threshold for specific site yourself!
        """
    else:
        argv = sys.argv
        argv.extend((None, None))
        fileName, threshold, filter = sys.argv[1:4]
        threshold = threshold == None and 0.5 or float(threshold)
        filter = filter != None and True or False
        if os.path.exists(fileName):
            f = open(fileName, 'r')
            html = f.read()
            f.close()
            html = unicode(html, 'gb18030')
            mtHtml = extMainText(html, threshold, filter)
            # Transfer to plain text:
            text = get_text(mtHtml)
            print text
        else:
            print "Can not open target html document!"
