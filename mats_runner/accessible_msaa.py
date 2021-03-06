# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

#this file is born in frustration of COM in python. Welcome to code-glue hell.

# there are two important things to remember while working with MSAA:
# 1) not every accessible node in tree is actually IAccessible. some of leafs in the tree
# are represented solely as an child_id to parent IAccessible, and do not implement the
# interface themselves. In this implementation therefore, an AccessibleElement is identified
# as pair of (IAccessible , integer)
# 2) child_id is 1-based, 0 means "node itself". You know, just so you make more mistakes.


#maybe initiate everything lazy?

from lxml import etree

from accessible import AccessibleElement, AccessibleTree
import comtypes
import ctypes
from ctypes import c_long, byref
from comtypes.automation import IDispatch, VARIANT, VT_I4, POINTER, VT_DISPATCH, BSTR
import winconstants

# from http://lxml.de/element_classes.html#setting-up-a-class-lookup-scheme
# TODO: should this be here?            

parser_lookup = etree.ElementDefaultClassLookup(element=AccessibleElement)
parser = etree.XMLParser()
parser.set_element_class_lookup(parser_lookup)
Element = parser.makeelement

def intToVariant(i):
    '''
    helper method, constructs Windows "VARIANT" object representing an integer
    '''
    v = VARIANT()
    v.vt = VT_I4
    v.value = i
    assert( isinstance(i, int) )
    return v

def getAccessibleTreeFromMsaa(root):
    '''
    method constructing a AccessibleTree from a given root AccessibleElement.
    
    WARNING:
    Please do not change order of operation. AccesibleTree constructor needs to
    fire first, AccessibleElement._init() relies on singleton mapping it
    provides, and for some reason _init() is called by lxml several times
    during tree construction.
    '''
    
    mapping = {'num' : 0}
    at = AccessibleTree(element = None, file = None, mapping = mapping)
    root = getAccessibleElementFromMsaa(root, winconstants.CHILDID_SELF, mapping)
    at._setroot(root)
    return at

def getAccessibleElementFromMsaa(node, id, mapping):
    '''
    creates AccessibleElement from MSAA, given the reference to AccessibleTree
    mapping.
    '''
    
    num = mapping['num']
    mapping['num'] += 1
    mapping[num] = (node, id)
    
    role = getRole(node, id)
    
    attrib = {
              'name' : getName(node, id),
              'description' : getDescription(node, id), 
              'value' : getValue(node, id),
              'role' : role,
              'state' : getState(node,id),
              'default-action' : getDefaultAction(node,id),
              'help' : getHelp(node,id),
              'keyboard-shortcut' : getKeyboardShortcut(node,id),
              'child-id' : str(id),
              }
    
    
    
    location = getLocation(node, id)
    for k, v in location.iteritems():
        attrib[k] = v
    
    attrib["mapping"] = str(num)
    
    notNoneAttrib = {k:v for k,v in attrib.iteritems() if v != None and v != ''}
    
    res = Element('accessible', attrib = notNoneAttrib)
    
    children = getMsaaChildren(node, id)
    res.extend([getAccessibleElementFromMsaa(node, id, mapping) for (node, id) in children])
            
    return res

def updateElement(element, mapping):
    '''
    this method updates a single element by permanently removing all it's children
    and regenerating subtree. It *does not* update argument element itself.
    '''
    
    def recursiveRemoveMapping(element):
        mapping_key = int(element.get("mapping"))
        del mapping[mapping_key]
        for child in element:
            recursiveRemoveMapping(child)
            
    node, id = element.os_spec
    
    for child in element:
        recursiveRemoveMapping(child)
    
    new_children = getMsaaChildren(node, id)
    element.extend([getAccessibleElementFromMsaa(node, id, mapping) for (node, id) in new_children])
    

def doDefaultAction(os_spec):
    '''
    calls accDoDefaultAction on MSAA node.
    '''
    
    node, id = os_spec
    
    variant = intToVariant(id)
    
    try:
        HRESULT = node._IAccessible__com_accDoDefaultAction(variant)
        #HRESULT = node.accDoDefaultAction(variant)
    except Exception as e:
        print "COM error in doDefaultAction: " + e.text + " details : " + str(e.details)
        return False
    
    if HRESULT == comtypes.hresult.S_OK:
        return True
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument") 
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND :
        raise Exception("Member not found")
    else:
        raise Exception("Unexpected behavior")
    
def select(os_spec, flag):
    node, id = os_spec
    variant = intToVariant(id)
    assert(isinstance(flag, int))
    c_flag = c_long(flag)

    try:
        HRESULT = node._IAccessible__com_accSelect(flag, variant)
        #HRESULT = node.accDoDefaultAction(variant)
    except Exception as e:
        print "COM error in accSelect: " + e.text + " details : " + str(e.details)
        return False
    
    if HRESULT == comtypes.hresult.S_OK:
        return True
    elif HRESULT == comtypes.hresult.S_FALSE:
        return False
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument") 
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND :
        raise Exception("Member not found")
    else:
        raise Exception("Unexpected behavior")

def putValue(os_spec, input_string):
    node, id = os_spec
    variant = intToVariant(id)
    s = BSTR(input_string)
    
    try:
        HRESULT = node.__com__set_accValue(variant) # no clue why no IAc... prefix!
    except Exception as e:
        print "COM error in putValue: " + e.text + " details : " + str(e.details)
        return False
    
    if HRESULT == comtypes.hresult.S_OK:
        return True
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument") 
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND :
        raise Exception("Member not found")
    else:
        raise Exception("Unexpected behavior")
    

def getRole(node, id):
    variant = intToVariant(id)
    res = intToVariant(0)
    HRESULT = node._IAccessible__com__get_accRole(variant, byref(res))
    if HRESULT == comtypes.hresult.S_OK:
        return getRoleName(res.value) 
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior")
    
def getLocation(node, id):
    variant = intToVariant(id)
    res = [c_long(), c_long(), c_long(), c_long()] #left, top, width, height
    HRESULT = node._IAccessible__com_accLocation(byref(res[0]),
                                                  byref(res[1]),
                                                  byref(res[2]),
                                                  byref(res[3]),
                                                  variant)
    if HRESULT == comtypes.hresult.S_OK:
        return {'left'      : str(res[0].value),
                'top'       : str(res[1].value), 
                'width'     : str(res[2].value),
                'height'    : str(res[3].value)
                }
    elif HRESULT == comtypes.hresult.S_FALSE:
        return {}
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND:
        return {}
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior: " + str(HRESULT))
    
def getDefaultAction(node, id):
    variant = intToVariant(id)
    s = BSTR()    
    
    try:
        HRESULT = node._IAccessible__com__get_accDefaultAction(variant, byref(s))
    except Exception as e:
        print 'COM error in get_accDefaultAction: ' + e.text + " details : " + str(e.details)
        return None
    
    if HRESULT == comtypes.hresult.S_OK:
        return s.value
    elif HRESULT == comtypes.hresult.S_FALSE:
        return None
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND:
        return None
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior: " + str(HRESULT))

def getValue(node, id):
    if id != winconstants.CHILDID_SELF:
        return None #TODO this condition was added to remove some of warnings - chceck if that's the way it should work
    
    
    variant = intToVariant(id)
    s = BSTR()    
    
    try:
        HRESULT = node._IAccessible__com__get_accValue(variant, byref(s))
    except Exception as e:
        print 'COM error in accValue: ' + e.text + " details : " + str(e.details)
        
        return None
    
    if HRESULT == comtypes.hresult.S_OK:
        return s.value
    elif HRESULT == comtypes.hresult.S_FALSE: #not in documentation, but happens.
        return None
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND:
        return None
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior: " + str(HRESULT))

def getKeyboardShortcut(node, id):
    variant = intToVariant(id)
    s = BSTR()    
    
    try:
        HRESULT = node._IAccessible__com__get_accKeyboardShortcut(variant, byref(s))
    except Exception as e:
        print 'COM error in accKeyboardShortcut: ' + e.text + " details : " + str(e.details)
        return None
    
    if HRESULT == comtypes.hresult.S_OK:
        return s.value
    elif HRESULT == comtypes.hresult.S_FALSE:
        return None
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND:
        return None
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior: " + str(HRESULT))


def getHelp(node, id):
    variant = intToVariant(id)
    s = BSTR()    
    
    try:
        HRESULT = node._IAccessible__com__get_accHelp(variant, byref(s))
    except Exception as e:
        print 'COM error in get_accHelp: '+ e.text + " details : " + str(e.details)
        return None
    
    if HRESULT == comtypes.hresult.S_OK:
        return s.value
    elif HRESULT == comtypes.hresult.S_FALSE:
        return None
    elif HRESULT == comtypes.hresult.DISP_E_MEMBERNOTFOUND:
        return None
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Invalid argument")
    else:
        raise Exception("Unexpected behavior: " + str(HRESULT))

def getState(node, id):
        
    variant = VARIANT(id, VT_I4)
    res = VARIANT()

    HRESULT = node._IAccessible__com__get_accState(variant, byref(res))
  
    if HRESULT == comtypes.hresult.S_OK:
        return str(res.value) #TODO add int->name mapping
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Argument not valid")
    else:
        raise Exception("Function output not valid!")

def getName(node, id):
    s = BSTR()
        
    variant = VARIANT(id, VT_I4)

    HRESULT = node._IAccessible__com__get_accName(variant, byref(s))
  
    if HRESULT == comtypes.hresult.S_OK:
        return s.value
    elif HRESULT == comtypes.hresult.S_FALSE:
        return None
    elif HRESULT == comtypes.hresult.E_INVALIDARG:
        raise Exception("Argument not valid")
    else:
        raise Exception("Function output not valid!")
    
def getDescription(node, id):
    if id != winconstants.CHILDID_SELF: #TODO not sure if that's correct
        return None
    else:
        s = BSTR()
        variant = intToVariant(id)
        HRESULT = node._IAccessible__com__get_accDescription(variant, byref(s))
          
        if HRESULT == comtypes.hresult.S_OK:
            return s.value
        elif HRESULT == comtypes.hresult.S_FALSE:
            return None
        elif HRESULT == comtypes.hresult.E_INVALIDARG:
            raise Exception("Arguemnt not valid")
        elif HRESULT == DISP_E_MEMBERNOTFOUND:
            raise Exception("Member not found, node = " + str(node) + " id = " + str(id) + ".")
        
def getChildCount(node, id):
    if id != winconstants.CHILDID_SELF:
        return 0 #leaves have no children
    else:
                
        num_c = ctypes.wintypes.LONG()
        HRESULT = node._IAccessible__com__get_accChildCount(byref(num_c))
        
        if HRESULT == comtypes.hresult.S_OK:
            return num_c.value
        else:
            raise Exception("Some unimplemented error")

def getMsaaChildren(node, id):
    if id != winconstants.CHILDID_SELF:
        return [] #leaves have no chlidren
    else:   
        numChildren = getChildCount(node, id)
        array = (VARIANT * numChildren)()
        rescount = c_long()
                
        HRESULT1 = comtypes.oledll.oleacc.AccessibleChildren(node, 0, numChildren, array, byref(rescount))
        
        if HRESULT1 == comtypes.hresult.E_INVALIDARG:
            raise Exception("Invalid argument")
        elif HRESULT1 == comtypes.hresult.S_FALSE:
            raise Exception("The function succeeded, but there are fewer elements in the array than requested.")
        
        assert(numChildren == rescount.value)
        
        children = [(x.value, winconstants.CHILDID_SELF) if x.vt == VT_DISPATCH else (node, x.value) for x in array] #see comment in the beginnning of the file        
        
        return children
    
#a function below is adapted from pyia https://github.com/eeejay/pyia

def getAccStateSetFromInt(state_int):
    states = []
    for shift in xrange(64):
        state_bit = 1 << shift
        if state_bit & state_int:
            states.append(
                winconstants.UNLOCALIZED_STATE_NAMES.get(
                    (state_bit & state), 'unknown'))
    return states

def getRoleName(role_int):
    return winconstants.UNLOCALIZED_ROLE_NAMES.get(role_int, 'unknown')
