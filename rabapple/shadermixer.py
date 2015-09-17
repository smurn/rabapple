
from OpenGL.GL import *  # @UnusedWildImport
import re

from . import api

_maindef_pattern = re.compile(r"(\s*)void\s+main\s*\(([^\)]*)\)")
_arg_pattern = re.compile("^((in)|(inout)|(out))\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s*((\[\s*\d*\s*\]\s*)*)$")
_dimensions_pattern = re.compile("\[(\s*\d+\s*)\]")


class MixedProgram:

    def __init__(self, base_codes, mixins):
        self._attrib_locations = {}
        self._uniform_locations = {}
        
        self._vao = None
        self._program = None
    
    def attrib_pointer(self, name, index, bufferdata):
        
        location = self._attrib_locations.get(name, None)
        if location is None:
            location = glGetAttribLocation(self._program, name.encode())
            self._attrib_locations[name] = location
        if location < 0:
            return
        
        location += index
        
        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, bufferdata.buffer_object)
        
        if bufferdata is None:
            glDisableVertexAttribArray(location)
        else:
            glEnableVertexAttribArray(location)
            if bufferdata.attribute_type == api.AttributeType.float:
                glVertexAttribPointer(location,
                                      bufferdata.size,
                                      bufferdata.datatype,
                                      bufferdata.normalized,
                                      bufferdata.stride,
                                      ctypes.c_void_p(bufferdata.offset))
            elif bufferdata.attribute_type == api.AttributeType.integer:
                glVertexAttribIPointer(location,
                                      bufferdata.size,
                                      bufferdata.datatype,
                                      bufferdata.stride,
                                      ctypes.c_void_p(bufferdata.offset))
            elif bufferdata.attribute_type == api.AttributeType.double:
                glVertexAttribLPointer(location,
                                      bufferdata.size,
                                      bufferdata.datatype,
                                      bufferdata.stride,
                                      ctypes.c_void_p(bufferdata.offset))
            else:
                raise ValueError("Invalid attribute type.")
            
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    def set_uniform(self, name, count, transpose, data, gl_function):
        
        loc = self._uniform_locations.get(name, None)
        if loc is None:
            loc = glGetUniformLocation(self._program, name.encode())
            self._uniform_locations[name] = loc
            
        if loc < 0:
            return
        
        glUseProgram(self._program)
        gl_function(loc, count, transpose, data)
        glUseProgram(0)


def prepare(code, functionname, explicit_params, inarray, outarray):
    
    def format_param(param):
        direction, datatype, name, dimensions = param
        dimensions = "".join("[{}]".format(dim) for dim in dimensions)
        return "{} {} {}{}".format(direction, datatype, name, dimensions)
    
    renamedcode, all_params = parse(code, "_" + functionname)
    
    if not set(explicit_params).issubset(set(all_params)):
        missing = set(explicit_params) - set(all_params)
        missing = ", ".join(format_param(p) for p in missing)
        raise ValueError("Missing parameters: " + missing)
    explict_names = set(p[2] for p in explicit_params)

    wrapper_params = list(explicit_params)
    if inarray:
        wrapper_params.append(("in", "int", "in_index", ()))
    if outarray:
        wrapper_params.append(("in", "int", "out_index", ()))
    wrapper_params_str = ", ".join(format_param(p) for p in wrapper_params)
    
    declarations = []
    arguments = []
    custom_params = []
    for param in all_params:
        direction, datatype, name, dimensions = param
        if name in explict_names:
            arguments.append(name)
        else:
            custom_params.append((direction, datatype, name, dimensions))
            if direction == "in":
                if inarray:
                    arguments.append("U_" + name + "[in_index]")
                    declarations.append(format_param((direction, datatype, "U_" + name, dimensions)) + "[]")
                else:
                    arguments.append("U_" + name)
                    declarations.append(format_param((direction, datatype, "U_" + name, dimensions)))
            elif direction == "out":
                if outarray:
                    arguments.append("U_" + name + "[out_index]")
                    declarations.append(format_param((direction, datatype, "U_" + name, dimensions)) + "[]")
                else:
                    arguments.append("U_" + name)
                    declarations.append(format_param((direction, datatype, "U_" + name, dimensions)))
            else:
                raise ValueError("Unsupported direction")
            
    declarations = "\n".join("{};".format(d) for d in declarations) + "\n"
    arguments = ", ".join(arguments)
        
    
    
    wrapper = "void {name}({params}){{\n    _{name}({args});\n}}"
    wrapper = wrapper.format(
                    name = functionname, 
                    params=wrapper_params_str, 
                    args=arguments)
    
    return declarations + renamedcode + "\n" + wrapper, custom_params
    

def parse(code, functionname):
    lines = []
    args = None
    for i, line in enumerate(code.splitlines(), 1):
        match = _maindef_pattern.match(line)
        if match:
            if args is not None:
                raise ValueError("Parsing error (%d) Two definitions of 'main' found" % i)
            args = match.group(2).split(",")
            args = list(_parse_arg(arg, i) for arg in args)
            args = [arg for arg in args if arg]
            line = "%svoid %s(%s)%s" % (match.group(1), functionname, match.group(2), line[match.end(0):])
        lines.append(line)
    if args is None:
        raise ValueError("Syntax error: void main(..) not found.")
    return "\n".join(lines), args
        
        
def _parse_arg(arg, linenr):
    arg = arg.strip()
    if not arg:
        return None
    match = _arg_pattern.match(arg)
    if not match:
        raise ValueError("Syntax error (%d): %r" %(linenr, arg))
    direction = match.group(1)
    gltype = match.group(5)
    name = match.group(6)
    dimensions = match.group(7)
    matches = _dimensions_pattern.finditer(dimensions)
    dimensions = tuple(int(match.group(1).strip()) for match in matches)
        
    
    return direction, gltype, name, dimensions

