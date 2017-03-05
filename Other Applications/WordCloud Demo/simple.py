#! /usr/bin/env python
#-*- coding:utf-8 -*-

"""
Created on Sun 5th March 2017 18:34
@author:David
=============
Minimal Example
===============
Generating a square wordcloud from the US constitution using default arguments.
"""

from os import path
from wordcloud import WordCloud

d = path.dirname(__file__)

# Read the whole text.
# text = open(path.join(d,'constitution.txt')).read()	# An English one
font = path.join(d,'DroidSansFallbackFull.ttf')
text = open(u'santi.txt').read().decode('gbk')		# A Chinese one

# Generate a word cloud image
wordcloud = WordCloud(font_path=font).generate(text)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud)
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(font_path=font,max_font_size=40).generate(text)
plt.figure()
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

