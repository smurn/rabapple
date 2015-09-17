'''
Created on 12.05.2015

@author: stefan
'''
import traceback
import sys

import OpenGL
OpenGL.FULL_LOGGING = True
import logging
import numpy as np

import rabapple
from rabappledemo import shaders

from OpenGL.GL import *  # @UnusedWildImport
from PyQt4 import QtGui, QtOpenGL
from PyQt4.QtOpenGL import QGLWidget

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def exit_on_error(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except:
            traceback.print_exc()
            sys.exit()
    return wrapper

class OpenglWidget(QGLWidget):
    def __init__(self, parent = None):
        request_format = QtOpenGL.QGLFormat()
        request_format.setVersion(3,3)
        request_format.setProfile(QtOpenGL.QGLFormat.CoreProfile)
        request_format.setAccum(False)
        request_format.setDoubleBuffer(True)
        request_format.setSampleBuffers(True)
        super(OpenglWidget, self).__init__(request_format)

    @exit_on_error
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        
        self.linerenderer.draw(0, self.vertexcount)
        
    @exit_on_error
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        
        self.model_to_flat = np.eye(4, dtype=np.single)
        self.model_to_flat[0,0] = width / 2.0;
        self.model_to_flat[0,3] = width / 2.0;
        self.model_to_flat[1,1] = height / 2.0;
        self.model_to_flat[1,3] = height / 2.0;

        
        self.flat_to_screen = np.eye(4, dtype=np.single)
        self.flat_to_screen[0,0] = 2.0 / width;
        self.flat_to_screen[0,3] = -1.0;
        self.flat_to_screen[1,1] = 2.0 / height;
        self.flat_to_screen[1,3] = -1.0;
        
        self.flat_to_pixel = np.eye(4, dtype=np.single)
        
        self.linerenderer.set_uniform("model_to_flat", 1, True, self.model_to_flat, glUniformMatrix4fv)
        self.linerenderer.set_uniform("flat_to_screen", 1, True, self.flat_to_screen, glUniformMatrix4fv)
        self.linerenderer.set_uniform("flat_to_pixel", 1, True, self.flat_to_pixel, glUniformMatrix4fv)
        
    def make_join_test_data2(self):
        
        n = 5
        
        offset = 1.0 / n - 1.0;
        spacing = 2.0 / n
        
        positions = np.zeros((5*n*n,4), dtype=np.single)
        styles = np.zeros(5*n*n, dtype=np.int8)
        nxt = 0
        
        start_angle = 0;
        
        for row in range(n):
            for col in range(n):
                
                i = row * n + col
                
                x = offset + col * spacing
                y = offset + row * spacing
                
                end_angle = 2*np.pi / (n*n) * i
                end_angle += start_angle
                
                xpre = np.cos(start_angle) * 0.6 * spacing + x
                ypre = np.sin(start_angle) * 0.6 * spacing + y 
                
                xstart = np.cos(start_angle) * 0.48 * spacing + x
                ystart = np.sin(start_angle) * 0.48 * spacing + y
                
                xend = np.cos(end_angle) * 0.4 * spacing + x
                yend = np.sin(end_angle) * 0.4 * spacing + y
                
                xpost = np.cos(end_angle) * 0.6 * spacing + x
                ypost = np.sin(end_angle) * 0.6 * spacing + y
                
                positions[nxt,:] = [xpre,ypre,0,1]
                styles[nxt] = rabapple.DISCARD
                nxt+=1
                positions[nxt,:] = [xstart,ystart,0,1]
                styles[nxt] = rabapple.FLAT_END
                nxt+=1  
                positions[nxt,:] = [x,y,0,1]
                styles[nxt] = rabapple.ROUND
                nxt+=1  
                positions[nxt,:] = [xend,yend,0,1]
                styles[nxt] = rabapple.FLAT_END
                nxt+=1  
                positions[nxt,:] = [xpost,ypost,0,1]
                styles[nxt] = rabapple.DISCARD
                nxt+=1
                
        return nxt, positions, styles

    def make_join_test_data(self):
        
        n = 5
        
        offset = 1.0 / n - 1.0;
        spacing = 2.0 / n
        
        positions = np.zeros((5*n*n,4), dtype=np.single)
        styles = np.zeros(5*n*n, dtype=np.int8)
        nxt = 0
        
        for row in range(n):
            for col in range(n):
                
                x = offset + col * spacing
                y = offset + row * spacing
                
                start_angle = 2*np.pi / n * row
                end_angle = 2*np.pi / n * col
                end_angle += start_angle
                
                xstart = np.cos(start_angle) * 0.48 * spacing + x
                ystart = np.sin(start_angle) * 0.48 * spacing + y
                
                xend = np.cos(end_angle) * 0.4 * spacing + x
                yend = np.sin(end_angle) * 0.4 * spacing + y
                
                positions[nxt,:] = [0,0,0,1]
                styles[nxt] = rabapple.DISCARD
                nxt+=1
                positions[nxt,:] = [xstart,ystart,0,1]
                styles[nxt] = rabapple.BUTT_END
                nxt+=1  
                positions[nxt,:] = [x,y,0,1]
                styles[nxt] = rabapple.MITER
                nxt+=1  
                positions[nxt,:] = [xend,yend,0,1]
                styles[nxt] = rabapple.BUTT_END
                nxt+=1  
                positions[nxt,:] = [0,0,0,1]
                styles[nxt] = rabapple.DISCARD
                nxt+=1
                
        return nxt, positions, styles
    
    @exit_on_error
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        
        positions = np.zeros((10,4), dtype=np.single)
        positions[0,:] = [-0.6, -0.3, 0, 1]
        positions[1,:] = [-0.3, -0.3, 0, 1]
        positions[2,:] = [ 0.3, -0.3, 0, 1]
        positions[3,:] = [ 0.3,  0.4, 0, 1]
        positions[4,:] = [-0.3,  0.4, 0, 1]
        positions[5,:] = [ 0.0,  0.0, 0, 1]
        positions[6,:] = [-0.8,  0.0, 0, 1]
        positions[7,:] = [-0.8,  0.8, 0, 1]
        positions[8,:] = [-0.8,  0.8, 0, 1]
        positions[9,:] = [ 0.0,  0.0, 0, 1]
        
        styles = np.zeros(10, dtype=np.int8)
        styles[0] = rabapple.DISCARD
        styles[1] = rabapple.BUTT_END
        styles[2:-2] = rabapple.MITER
        styles[-2] = rabapple.BUTT_END
        styles[-1] = rabapple.DISCARD
        
        self.vertexcount = 10
        
        self.vertexcount, positions, styles = self.make_join_test_data2()
        
        position_buffer = rabapple.BufferData(
                            make_buffer(positions, GL_STATIC_DRAW), 
                            4, GL_FLOAT, GL_FALSE, 0, 0, 
                            rabapple.AttributeType.float)

        
        styles_buffer = rabapple.BufferData(
                            make_buffer(styles, GL_STATIC_DRAW), 
                            1, GL_BYTE, GL_FALSE, 0, 0, 
                            rabapple.AttributeType.integer)
        
        self.linerenderer = rabapple.LineRenderPath()
        self.linerenderer.fragment_shader = shaders.load_code("demo_fragment.glsl")
        self.linerenderer.point_shader = shaders.load_code("demo_point.glsl")
        self.linerenderer.vertex_shader = shaders.load_code("demo_vertex.glsl")
        self.linerenderer.initialize()
        
        self.linerenderer.set_attribute("bfrPosition", 0, position_buffer)
        self.linerenderer.set_attribute("bfrStyle", 0, styles_buffer)

        
def make_buffer(array, usage):
    handle = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, handle)
    glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, usage)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    return handle

def main():
    app = QtGui.QApplication(["Rabapple Demo"])
    widget = OpenglWidget()
    widget.show()
    widget.setGeometry(100, 100, 300, 300)
    app.exec_()
    

if __name__ == '__main__':
    main()