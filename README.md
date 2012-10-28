emtext
======

Main Repo of Project

注意：不同语言的文档需要分开训练！默认训练集是面向中文的。

如果训练数据本身矛盾太严重，可能造成训练失败—— Error 值不收敛。

ToDo: html 代码片段的划分粒度应该按照 div 块来。仅使用一句话一句话的效果不够好。


from emt import extract_url

extract_url('YOUR_URL_LINK')

