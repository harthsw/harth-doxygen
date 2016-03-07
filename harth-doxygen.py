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

class XMLDoxygenIndex:
    def __init__(self, tree):
        self.tree = tree
        self.root = tree.getroot()

    @property
    def version(self):
        return self.root.attrib["version"]

    @property
    def compounds(self):
        return self.root.iter("compound")

class XMLCompound:
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

class XMLName:
    def __init__(self, elem):
        self.elem = elem

    @property
    def text(self):
        return self.elem.text

class XMLDoxygen:
    def __init__(self, tree):
        self.tree = tree
        self.root = tree.getroot()

    @property
    def defs(self):
        return self.root.iter("compounddef")

class XMLCompoundDef:
    def __init__(self, elem):
        self.elem = elem

    @property
    def name(self):
        return XMLName(self.elem.find("compoundname"))

    @property
    def location(self):
        return XMLLocation(self.elem.find("location"))

class XMLLocation:
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
    
# --------------------------------------------------------------------------------

xml = "../harth-application/dep/harth-kernel/build/xml/index.xml"
tree = ET.parse(xml)

def_xml = "../harth-application/dep/harth-kernel/build/xml/struct_harth_1_1_kernel_1_1_meta_1_1_all_helper.xml"
def_tree = ET.parse(def_xml)

index = XMLDoxygenIndex(tree)
def_index = XMLDoxygen(def_tree)

print "Index"
print "Version:", index.version
print "Compounds:"

for c in index.compounds:
    compound = XMLCompound(c)

    print "  refid=", compound.refid
    print "  kind=", compound.kind
    for child in compound.elem._children:
        print "   child.tag=", child.tag
        print "   child.text=", child.text
    print "  names=[" 
    for n in compound.names:
        print "    ", n.text
    print "  ]"

    for d in def_index.defs:
        compoundDef = XMLCompoundDef(d)
        name = compoundDef.name
        loc = compoundDef.location        
        print "Def Name=", name.text
        print "At ", loc.file, loc.line, loc.column
    sys.exit(0)

    


