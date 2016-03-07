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
# Doxygen Index
#
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

    def dump(self, prefix=""):
        print "{0}[{0}]".format(prefix, repr(self))
        print "{0}Path: {1}".format(prefix, self.path)
        print "{0}Version: {1}".format(prefix, self.version)
        for c in self.compounds:
            # TODO: FIX
            compound = Compound(c)
            compound.dump(prefix + "  ")

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

    def dump(self, prefix=""):
        print "[{0}]".format(repr(self))
        print "RefId:", self.refid
        print "Kind:", self.kind
        for c in self.names:
            compound = Name(c)
            compound.dump(prefix + "  ")
    
class Name(Compound):
    def __init__(self, elem):
        Compound.__init__(self, elem)

    @property
    def text(self):
        return self.elem.text

    @property    
    def path(self):
        return "/" + self.elem.text.replace("::", "/")

    def dump(self, prefix=""):
        print "[{0}]".format(repr(self))
        print "Text:", self.text
        print "Path:", self.path

# --------------------------------------------------------------------------------
# Doxygen Definition Index
#
# Class names and strcture almost match those in Doxygen's XSD:
# See: ~/Projects/harth-application/dep/harth-kernel/build/xml/compound.xsd
#
class DoxygenDefIndex:
    def __init__(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    @property
    def version(self):
        return self.root.attrib["version"]
        
    @property
    def defs(self):
        return self.root.iter("compounddef")

    def dump(self, prefix=""):
        print "[{0}]".format(repr(self))
        print "Path:", self.path
        print "Version:", self.version
        for d in self.defs:
            # TODO: Fix with factory
            cd = CompoundDef(d)
            cd.dump(prefix + "  ")

class CompoundDef:
    def __init__(self, elem):
        self.elem = elem

    @property
    def id(self):
        return self.elem.attib["id"]
        
    @property
    def name(self):
        return Name(self.elem.find("compoundname"))

    @property
    def location(self):
        return LocationDef(self.elem.find("location"))

    def dump(self, prefix=""):
        print "[{0}]".format(repr(self))
        self.name.dump(prefix + "  ")
        self.location.dump(prefix + "  ")
    
class LocationDef(CompoundDef):
    def __init__(self, elem):
        CompoundDef.__init__(self, elem)
    
    @property
    def file(self):
        return self.elem.attrib["file"]

    @property
    def line(self):
        return self.elem.attrib["line"]

    @property
    def column(self):
        return self.elem.attrib["column"]

    def dump(self, prefix=""):
        print "{0}[{1}]".format(prefix, repr(self))
        print "{0}Location: {1}".format(prefix, self.file)
        print "{0}Line: {1}".format(prefix, self.line)
        print "{0}Column: {1}".format(prefix, self.column)

class NamespaceDef(CompoundDef):
    def __init__(self, elem):
        CompoundDef.__init__(self, elem)
        self.elem = elem

    @property
    def child_namespaces(self):
        return self.elem.findall("innernamespace")

    def dump(self, prefix=""):
        print "[{0}]".format(repr(self))

# --------------------------------------------------------------------------------


index = DoxygenIndex("../harth-application/dep/harth-kernel/build/xml/index.xml")

def print_compound(c, prefix=""):
    comp = Compound(c)
    if comp.kind == "namespace":
        print_namespace(c, prefix)

def print_namespace(c, prefix=""):
    comp = Compound(c)
    xml = "../harth-application/dep/harth-kernel/build/xml/{0}.xml".format(comp.refid)
    def_index = DoxygenDefIndex(xml)

    for d in def_index.defs:
        ns = NamespaceDef(d)
        print "{0}:{1}: Error: namespace {3}".format(ns.location.file, ns.location.line, prefix, ns.name.path)
        for ic in ns.child_namespaces:
            print_namespace(ic, prefix + "  ")
            
for c in index.compounds:
    print_compound(c)
            
sys.exit(0)
