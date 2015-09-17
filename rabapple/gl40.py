'''
Created on 06.09.2015

@author: stefan
'''

from OpenGL.GL import *  # @UnusedWildImport
from . import shaders, gltools
import numpy as np
from rabapple import api

def load(base, mixin):
    code = shaders.load_code(base)
    code += "\n\n" + mixin
    return code

class LineRenderPath:
    
    def __init__(self):
        self._program = None
        self.max_vertices = 1024
        self.point_shader = ""
        self.vertex_shader = ""
        self.fragment_shader = ""
        
    def initialize(self):
        self._direct_prog = gltools.Program({
                         GL_VERTEX_SHADER:load("gl40_direct.vert", self.point_shader),
                         GL_GEOMETRY_SHADER:load("gl40_direct.geom", self.vertex_shader),
                         GL_FRAGMENT_SHADER:load("gl40_direct.frag", self.fragment_shader)})
        
        self._round_prog = gltools.Program({
                         GL_VERTEX_SHADER:load("gl40_round.vert", ""),
                         GL_TESS_CONTROL_SHADER:load("gl40_round.tesc", ""),
                         GL_TESS_EVALUATION_SHADER:load("gl40_round.tese", self.vertex_shader),
                         #GL_GEOMETRY_SHADER:load("gl40_round.geom", ""),
                         GL_FRAGMENT_SHADER:load("gl40_round.frag", self.fragment_shader)})
        
        bytes_per_circle_segment = 42
        self.fb_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.fb_buffer)
        glBufferData(GL_ARRAY_BUFFER, self.max_vertices*bytes_per_circle_segment, ctypes.c_void_p(0), GL_STREAM_COPY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        test_data = np.zeros(1, dtype=[
                           ('center',np.float32, (4,)),
                           ('start',np.float32, (2,)),
                           ('end',np.float32, (2,)),
                           ('other',np.float32, (2,))
                           ])

#         test_data["center"][0] = [0,0,0,1]
#         test_data["start"][0] = [0.8,0.0]
#         test_data["end"][0] = [0,0.8]
#         test_data["other"][0] = [0.0,-0.8]
        test_data["center"][0] = [20,20,0,1]
        test_data["start"][0] = [300,000]
        test_data["end"][0] = [000,300]
        test_data["other"][0] = [000,000]
        glBindBuffer(GL_ARRAY_BUFFER, self.fb_buffer)
        glBufferSubData(GL_ARRAY_BUFFER, 0, test_data.nbytes, test_data)
        glBindBuffer(GL_ARRAY_BUFFER, self.fb_buffer)
        
        center = api.BufferData(self.fb_buffer, 4, GL_FLOAT, GL_FALSE, 40,  0, api.AttributeType.float)
        start_end  = api.BufferData(self.fb_buffer, 4, GL_FLOAT, GL_FALSE, 40, 16, api.AttributeType.float)
        #end    = api.BufferData(self.fb_buffer, 2, GL_FLOAT, GL_FALSE, 40, 24, api.AttributeType.float)
        other  = api.BufferData(self.fb_buffer, 2, GL_FLOAT, GL_FALSE, 40, 32, api.AttributeType.float)
        
        self._round_prog.set_attribute("bfrCenter", 0, center)
        self._round_prog.set_attribute("bfrStart_bfrEnd", 0, start_end)
        #self._round_prog.set_attribute("bfrEnd", 0, end)
        self._round_prog.set_attribute("bfrOther", 0, other)
        
    
    def draw(self, first_vertex, vertex_count):
        
        if vertex_count > self.max_vertices:
            raise ValueError("Too many verticies")
        
        self._direct_prog.use()
        glDrawArrays(GL_LINE_STRIP_ADJACENCY, first_vertex, vertex_count)
        self._direct_prog.unuse()

#         self._round_prog.use()
#         glPatchParameteri(GL_PATCH_VERTICES, 1)
#         glDrawArrays(GL_PATCHES, 0, 1)
#         self._round_prog.unuse()
      
    def set_attribute(self, name, index, bufferdata):
        self._direct_prog.set_attribute(name, index, bufferdata)
        
    def set_uniform(self, name, count, transpose, data, gl_function):
        self._direct_prog.set_uniform(name, count, transpose, data, gl_function)
        self._round_prog.set_uniform(name, count, transpose, data, gl_function)
