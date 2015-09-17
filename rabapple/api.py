'''
Created on 05.09.2015

@author: stefan
'''
import enum

class AttributeType(enum.Enum):
    float = 1
    double = 2
    integer = 3
    
BEVEL = 0
MITER = 1
ROUND = 2
FLAT_END = 3
BUTT_END = 4
ROUND_END = 5
DISCARD = 6


class BufferData:
    
    def __init__(self, buffer_object, size, datatype, normalized, stride, offset, attribute_type = AttributeType.float):
        self.buffer_object = buffer_object
        self.size = size
        self.datatype = datatype
        self.normalized = normalized
        self.stride = stride
        self.offset = offset
        self.attribute_type = attribute_type


