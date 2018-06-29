#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree as ET
import re

# xml file's path and filename
filename = '/srcdata/sle1/SNW03016146.xml'

etr = ET.parse(filename)
root = etr.iter()
for child in root:
    if child.text is None:
#        print(type(child.text))
        print(etr.getpath(child), '\t', '')
    elif len(child.text.strip()) > 0:
        print(etr.getpath(child), '\t', child.text)

