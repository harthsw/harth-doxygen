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
import os
import xml.etree.ElementTree as ET

sys.path.append("%%LIBDIR%%")

# --------------------------------------------------------------------------------
# Helpers
#

class Name:
    def __init__(self, name):
        self.name = name

    def str(self):
        return "Name(\"{0}\")".format(self.name)
        
    def __repr__(self):
        return self.str()
        
class Path:
    def __init__(self, pathstr):
        pathstr = "/" + pathstr
        p = re.split("::|/", pathstr)
        self.names = [Name(n) for n in p]
        self.text = "/".join(p)
        self.name = self.names[-1]

    def str(self):
        return "Path(\"{0}\")".format(self.text)

    def __repr__(self):
        return self.str()

class Location:
    def __init__(self, elem):
        self.elem = elem
        if elem is not None:
            self.path = elem.attrib.get("file")
            self.line = elem.attrib.get("line")
            self.column = elem.attrib.get("column")
        else:
            self.path = None
            self.line = None
            self.column = None

    def str(self):
        return "Location(\"{0}:{1}:{2}\")".format(self.path, self.line, self.column)

    def __repr__(self):
        return self.str()

# RefId is used by Doxygen for def-ref links, suitable for HTML links or file names.
# Locally unique
class RefId:
    def __init__(self, text):
        self.text = text

    def str(self):
        return "RefId(\"{0}\")".format(self.text)

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

class Element:
    def __init__(self, index, elem, refid_key, name_key):
        self.index = index
        self.elem = elem
        self.kind = elem.attrib["kind"]
        self.refid = RefId(elem.attrib[refid_key])
        self.path = Path(elem.find(name_key).text)

    def str(self):
        return "{0}({1})".format(self.__class__.__name__, self.refid)

    def __repr__(self):
        return self.str()
        
class Index:
    def __init__(self, model, xml_file):
        self.model = model
        self.path = os.path.join(xml_root, xml_file)
        if verbose:
            print "Reading \"{0}\"...".format(self.path)
        self.tree = ET.parse(self.path)
        self.root = self.tree.getroot()
        self.version = self.root.attrib["version"]

# --------------------------------------------------------------------------------
# Doxygen Definition Index
#
# Class names and strcture almost match those in Doxygen's XSD:
# See: ~/Projects/harth-application/dep/harth-kernel/build/xml/compound.xsd
#
class DoxygenDefinitionIndex(Index):
    def __init__(self, model, xml_file):
        Index.__init__(self, model, xml_file)
        self.definitions = [self.make_definition(e) for e in self.root.iter("compounddef")]

    def make_definition(self, elem):
        kind = elem.attrib["kind"]
        if kind == "namespace":
            return NamespaceDefinition(self, elem)
        return CompoundDefinition(self, elem)

class Definition(Element):
    def __init__(self, index, elem):
        Element.__init__(self, index, elem, "id", "compoundname")
        # self.guid = Guid()
        self.location = Location(elem.find("location"))

    def build_definition_list(self, key_text):
        defs = []
        for ins in self.elem.findall(key_text):
            refid_text = ins.attrib["refid"]
            d = self.index.model.find_definition(refid_text)
            defs.append(d)
        return defs
    
class CompoundDefinition(Definition):
    def __init__(self, index, elem):
        Definition.__init__(self, index, elem)
        self.language = self.elem.attrib.get("language")
    
class NamespaceDefinition(CompoundDefinition):
    def __init__(self, index, elem):
        CompoundDefinition.__init__(self, index, elem)
        self._child_namespaces = None

    @property
    def child_namespaces(self):
        if self._child_namespaces is None:
            self._child_namespaces = self.build_definition_list("innernamespace")
        return self._child_namespaces
        
# --------------------------------------------------------------------------------
# Doxygen Reference Index
#
# Class names and strcture almost match those in Doxygen's XSD:
# See: ~/Projects/harth-application/dep/harth-kernel/build/xml/index.xsd

class DoxygenReferenceIndex(Index):
    def __init__(self, model, xml_file):
        Index.__init__(self, model, xml_file)
        self.references = [self.make_reference(e) for e in self.root.iter("compound")]

    def make_reference(self, elem):
        kind = elem.attrib["kind"]
        if kind == "namespace":
            return NamespaceReference(self, elem)
        return CompoundReference(self, elem)

class Reference(Element):
    def __init__(self, index, elem):
        Element.__init__(self, index, elem, "refid", "name")
        self.xml_path = self.refid.text + ".xml"
    
class CompoundReference(Reference):
    def __init__(self, index, elem):
        Reference.__init__(self, index, elem)

class NamespaceReference(CompoundReference):
    def __init__(self, index, elem):
        CompoundReference.__init__(self, index, elem)

# --------------------------------------------------------------------------------

class DoxygenModel:
    def __init__(self):
        self.ref_index = DoxygenReferenceIndex(self, "index.xml")
        self.definition_dict = {}
        for r in self.ref_index.references:
            self.add_definition_index(r)

    @property
    def definitions(self):
        return self.definition_dict.itervalues()

    def make_definition_index(self, ref):
        return DoxygenDefinitionIndex(self, ref.xml_path)
        
    def add_definition_index(self, ref):
        def_index = self.make_definition_index(ref)
        for d in def_index.definitions:
            refid_text = d.refid.text
            self.definition_dict[refid_text] = d

    @property
    def namespaces(self):
        return (d for d in self.definitions if d.kind == "namespace")

    def find_definition(self, refid_text):
        return self.definition_dict[refid_text]
    
# --------------------------------------------------------------------------------

verbose = False
# verbose = True
xml_root = "../harth-application/dep/harth-kernel/build/xml"
model = DoxygenModel()

# Namespaces
for ns in model.namespaces:
    print "{0}: {1}".format(ns.path, ns.location)
    for ins in ns.child_namespaces:
        print "  {0}: {1}".format(ins.path, ins.location)

# Classes

sys.exit(0)
