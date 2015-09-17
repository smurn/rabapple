'''
Created on 15.09.2015

@author: stefan
'''
from OpenGL.GL import *  # @UnusedWildImport
from . import api

class Program:
    
    def __init__(self, shaders):
        compiled = [_compile(code, stage) for stage, code in shaders.items()]
        self._program = _link(compiled)
        self._vao = glGenVertexArrays(1)
        
        for c in compiled:
            glDeleteShader(c)
            
        self._input_attribs = {}
        self._uniforms = {}
            
        for code in shaders.values():
            for name in _parse_in_pragma(code):
                location = glGetAttribLocation(self._program, (name).encode())
                self._input_attribs[name] = location
        
    def get_in_attributes(self):
        return list(self._input_attribs.keys())
    
    def use(self):
        glUseProgram(self._program)
        glBindVertexArray(self._vao)
        
    def unuse(self):
        glBindVertexArray(0)
        glUseProgram(0)
        
    def set_attribute(self, name, index, bufferdata):
        
        location = self._uniforms.get(name, None)
        if location is None:
            location = glGetAttribLocation(self._program, (name).encode())
            self._input_attribs[name] = location
            
        if location < 0:
            return
    
        glBindVertexArray(self._vao)
        
        location = self._input_attribs[name]
        glBindBuffer(GL_ARRAY_BUFFER, bufferdata.buffer_object)
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
        
        glBindBuffer(GL_ARRAY_BUFFER, 0);
        glBindVertexArray(0)
        
    def set_uniform(self, name, count, transpose, data, gl_function):
        location = self._uniforms.get(name, None)
        if location is None:
            location = glGetUniformLocation(self._program, name.encode())
            self._uniforms[name] = location
            
        if location < 0:
            return
        glUseProgram(self._program)
        gl_function(location, count, transpose, data)
        glUseProgram(0)



def _parse_in_pragma(code):
    collected_inputs = []
    pragma = "#pragma in_attribs"
    for line in code.splitlines():
        line = line.strip()
        if line.startswith(pragma):
            inputs = line[len(pragma):].split()
            collected_inputs.extend(inputs)
    return collected_inputs
        
def _compile(source, shader_type):
    obj = glCreateShader(shader_type)
    glShaderSource(obj, source)
    glCompileShader(obj)
    message = glGetShaderInfoLog(obj)
    if glGetShaderiv(obj, GL_COMPILE_STATUS) != GL_TRUE:
        raise ValueError("Failed to compile %s shader: %s" % (shader_type, message.decode(errors="replace")))
    return obj

def _link(shaders):
    obj = glCreateProgram()
    for shader in shaders:
        glAttachShader(obj, shader)
    glLinkProgram(obj)
    message = glGetProgramInfoLog(obj)
    if glGetProgramiv(obj, GL_LINK_STATUS) != GL_TRUE:
        raise ValueError("Failed to link shaders: %s" % message.decode(errors="replace"))
    for shader in shaders:
        glDetachShader(obj, shader)
    return obj