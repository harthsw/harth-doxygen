#!/usr/bin/env python
#
# %%README%%
# %%LICENSE%%
#
# Harth-Doxygen Version %%VERSION%%
#
import sys
import xml.etree.ElementTree as ET

sys.path.append("%%LIBDIR%%")

# --------------------------------------------------------------------------------
# Class names and strcture almost match those in Doxygen's XSD:
# See: ~/Projects/harth-application/dep/harth-kernel/build/xml/index.xsd

class DoxygenIndex:
    def __init__(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    @property
    def version(self):
        return self.root.attrib["version"]

    @property
    def compounds(self):
        return self.root.iter("compound")

class Compound:
    def __init__(self, elem):
        self.elem = elem

    @property
    def refid(self):
        return self.elem.attrib["refid"]

    @property
    def kind(self):
        return self.elem.attrib["kind"]

    @property
    def names(self):
        return self.elem.findall("name")

class Name:
    def __init__(self, elem):
        self.elem = elem

    @property
    def text(self):
        return self.elem.text

class DoxygenDefIndex:
    def __init__(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    @property
    def defs(self):
        return self.root.iter("compounddef")

class CompoundDef:
    def __init__(self, elem):
        self.elem = elem

    @property
    def name(self):
        return Name(self.elem.find("compoundname"))

    @property
    def location(self):
        return Location(self.elem.find("location"))

class Location:
    def __init__(self, elem):
        self.elem = elem
    
    @property
    def file(self):
        return self.elem.attrib["file"]

    @property
    def line(self):
        return self.elem.attrib["line"]

    @property
    def column(self):
        return self.elem.attrib["column"]

class NamespaceDef(CompoundDef):
    def __init__(self, elem):
        self.elem = elem

    @property
    def child_namespaces(self):
        return self.elem.findall("innernamespace")
    
# --------------------------------------------------------------------------------


index = DoxygenIndex("../harth-application/dep/harth-kernel/build/xml/index.xml")

print "Index"
print "  Version:", index.version
print "  Compounds:"

for c in index.compounds:
    compound = Compound(c)

    if compound.kind == "namespace":
        print "  refid=", compound.refid
        print "  kind=", compound.kind
        
        # for child in compound.elem._children:
        #     print "   child.tag=", child.tag
        #     print "   child.text=", child.text
        print "  names=[" 
        for n in compound.names:
            print "    ", n.text
        print "  ]"

def_index = DoxygenDefIndex("../harth-application/dep/harth-kernel/build/xml/namespace_harth.xml")
for ns in def_index.defs:
    def_ns = NamespaceDef(ns)

    print "ns=", def_ns.name.text
    print "loc=", def_ns.location.file, def_ns.location.line
    print "children=", def_ns.child_namespaces
            
sys.exit(0)
