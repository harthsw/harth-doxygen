#!/usr/bin/env python
#
# %%README%%
# %%LICENSE%%
#
# Harth-Doxygen Version %%VERSION%%
#
import sys
import re
import uuid
import xml.etree.ElementTree as ET

sys.path.append("%%LIBDIR%%")

# --------------------------------------------------------------------------------
# Helpers
#

class Name:
    def __init__(self, name):
        self.name = name

    def str(self):
        return self.name
        
    def __repr__(self):
        return self.str()
        
class Path:
    def __init__(self, pathstr):
        pathstr = "/" + pathstr
        p = re.split("::|/", pathstr)
        self.names = [Name(n) for n in p]
        self.path = "/".join(p)
        self.name = self.names[-1]

    def str(self):
        return self.path

    def __repr__(self):
        return self.str()

class Location:
    def __init__(self, path, line, col):
        self.path = path
        self.line = line
        self.column = col

    def str(self):
        return "{0}:{1}:{2}".format(self.path, self.line, self.column)

    def __repr__(self):
        return self.str()

# RefId is used by Doxygen for def-ref links, suitable for HTML links or file names.
# Locally unique
class RefId:
    def __init__(self, refid):
        self.refid = refid

    def str(self):
        return self.refid

    def __repr__(self):
        return self.str()

# GUID = Globally Unique Identifier
# Globally unique
class Guid:
    def __init__(self):
        self.guid = uuid.uuid1()

    def str(self):
        return str(self.guid)

    def __repr__(self):
        return repr(self.guid)
    
class Definition:
    def __init__(self, refid, path, loc):
        self.guid = Guid()
        self.refid = refid
        self.path = path
        self.location = loc

    @property
    def name(self):
        return self.path.name

    def str(self):
        return "Definition({0}, {1})".format(self.guid, self.path)

    def __repr__(self):
        return self.str()
    
class Reference:
    def __init__(self, elem):
        self.elem = elem
        # TODO: Look up reference by refid, to find definition (and guid)        
        self.guid = Guid()        
        self.refid = RefId(elem.attrib["refid"])
        self.kind = elem.attrib["kind"]
        self.path = Path(elem.find("name").text)

    def str(self):
        return "Reference({0}, {1})".format(self.guid, self.path)

    def __repr__(self):
        return self.str()
    
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
        self.version = self.root.attrib["version"]

    @property
    def references(self):
        return (Reference(e) for e in self.root.iter("compound"))

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
            
for ref in index.references:
    print ref
            
sys.exit(0)
