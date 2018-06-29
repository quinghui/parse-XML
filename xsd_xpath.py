#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree as ET
import sys, os
import re

def get_xsd_loct(filename):
    schm_loct = {}
    context = ET.parse(filename)
    root = context.iter()
    for elem in root:
        #        print elem.tag, elem.attrib
        if (elem.attrib.get('schemaLocation') is not None):
            for ns in elem.nsmap:
                #                print elem.attrib['namespace'], elem.nsmap[ns]
                if elem.attrib['namespace'] == elem.nsmap[ns]:
                    #                   print ns
                    schm_loct[ns] = elem.attrib['schemaLocation']
    return schm_loct

def get_xpath(pathbase, filename):
    fxpath, elemnt, level = [], [], 0
    if pathbase:
        if pathbase[0] == '/': pathbase = pathbase[1:]
        if pathbase[-1] == '/': pathbase = pathbase[:-1]
    context = ET.iterparse(filename, events=('start', 'end'))
    for event, elem in context:
        if elem.tag in ('{http://www.w3.org/2001/XMLSchema}element', '{http://www.w3.org/2001/XMLSchema}complexType'):
            if (elem.attrib.get('name') is not None):
                #                print level, event, elem.tag, elem.attrib
                if event == 'start':
                    level += 1
                    #                    print(event, level, elem.tag, elem.attrib, len(elemnt))
                    if level > len(elemnt):
                        if len(elemnt) == 0 and pathbase:
                            elemnt.append(pathbase)
                        else:
                            elemnt.append(elem.attrib['name'])
                    else:
                        if level - 1 == 0 and pathbase:
                            elemnt[0] = pathbase
                        else:
                            elemnt[level - 1] = elem.attrib['name']
                        while len(elemnt) > level:
                            elemnt.pop(len(elemnt) - 1)
                    if elem.attrib.get('type') is not None:
                        subpath = ''
                        for child in elemnt:
                            subpath += '/' + child
                        subpath += '/'
                        fxpath.append((subpath, elem.attrib['type']))
                if event == 'end':
                    level -= 1
    return fxpath

def get_fullxpath(root, schm_dir, xsd_file):
    if schm_dir: os.chdir(schm_dir)
    cwd = os.getcwd() + '/'
    print cwd, xsd_file

    xpath_itme = get_xpath(root, xsd_file)
    xsdfile = get_xsd_loct(xsd_file)
    ns_itme = []

    for path in xpath_itme:
        if re.search('xsd:', path[1]):
            print path[0]+'text()' + '\t' + re.sub('xsd:', '', path[1])
        elif re.search('ns', path[1]):
            print path[0] + '\t' + path[1]
        if path[1][:2] == 'ns':
            nstag = path[1].split(':')[0]
            ns_itme.append((path[0], path[1], cwd, xsdfile[nstag]))
#            print xpath_itme_ns
    print xsdfile, '\n\n'

    for path in ns_itme:
        print path
        cwd = os.chdir(path[2])
        restr = re.search('(^.+\/)([^/]*\.xsd)', path[3])
        if restr:
            subdir, xsdfn = restr.group(1), restr.group(2)
            schm_dir = os.getcwd() + '/' + subdir
            xsd_file = xsdfn
        # print cwd, path[1][:3], subdir, xsdfn
        else:
            schm_dir, xsd_file = path[2], path[3]
        get_fullxpath(path[0], schm_dir, xsd_file)
    return

if not len(sys.argv) >= 3:
    print('Usage:\n\t{} schema_dir schema_file_name prefix_xpath'
          .format(sys.argv[0]))
    sys.exit(-1)

schema_dir, file_name = sys.argv[1], sys.argv[2]
try:
    base = sys.argv[3]
except IndexError:
    base =''

if not os.path.isdir(schema_dir):
    print 'The schema_dir', schema_dir, 'is not existed. Please check.'
    sys.exit(-1)
else:
    os.chdir(schema_dir)
    if not os.path.isfile(file_name):
        print 'The schema_file',file_name, 'is not existed. Please check.'
        sys.exit(-1)

get_fullxpath(base, schema_dir, file_name)
