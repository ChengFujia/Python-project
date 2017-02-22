#-*- coding:utf-8 -*-
from OpenGL.GL import glCallList, glClear, glClearColor, glColorMaterial, glCullFace, glDepthFunc, glDisable, glEnable,\
                      glFlush, glGetFloatv, glLightfv, glLoadIdentity, glMatrixMode, glMultMatrixf, glPopMatrix, \
                      glPushMatrix, glTranslated, glViewport, \
                      GL_AMBIENT_AND_DIFFUSE, GL_BACK, GL_CULL_FACE, GL_COLOR_BUFFER_BIT, GL_COLOR_MATERIAL, \
                      GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST, GL_FRONT_AND_BACK, GL_LESS, GL_LIGHT0, GL_LIGHTING, \
                      GL_MODELVIEW, GL_MODELVIEW_MATRIX, GL_POSITION, GL_PROJECTION, GL_SPOT_DIRECTION
from OpenGL.constants import GLfloat_3, GLfloat_4
from OpenGL.GLU import gluPerspective, gluUnProject
from OpenGL.GLUT import glutCreateWindow, glutDisplayFunc, glutGet, glutInit, glutInitDisplayMode, \
                        glutInitWindowSize, glutMainLoop, \
                        GLUT_SINGLE, GLUT_RGB, GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH, glutCloseFunc
import numpy
from numpy.linalg import norm, inv
import random
from OpenGL.GL import glBegin, glColor3f, glEnd, glEndList, glLineWidth, glNewList, glNormal3f, glVertex3f, \
                      GL_COMPILE, GL_LINES, GL_QUADS
from OpenGL.GLU import gluDeleteQuadric, gluNewQuadric, gluSphere

import color 
from scene import Scene
from primitive import init_primitives, G_OBJ_PLANE
from node import Sphere, Cube, SnowFigure
from interaction import Interaction

class Viewer(object):
    def __init__(self):
        """ Initialize the viewer. """
        #?????????????????
        self.init_interface()
        #???opengl???
        self.init_opengl()
        #???3d??
        self.init_scene()
        #????????????
        self.init_interaction()
        init_primitives()

    def init_interface(self):
        """ ???????????? """
        glutInit()
        glutInitWindowSize(640, 480)
        glutCreateWindow("3D Modeller")
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        #????????
        glutDisplayFunc(self.render)

    def init_opengl(self):
        """ ???opengl??? """
        #??????
        self.inverseModelView = numpy.identity(4)
        #??????????
        self.modelView = numpy.identity(4)

        #????????
        glEnable(GL_CULL_FACE)
        #??????????????????????????
        glCullFace(GL_BACK)
        #??????
        glEnable(GL_DEPTH_TEST)
        #??????????????????
        glDepthFunc(GL_LESS)
        #??0???
        glEnable(GL_LIGHT0)
        #???????
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        #?????????
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))
        #??????
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        #???????
        glClearColor(0.4, 0.4, 0.4, 0.0)

    def init_scene(self):
        #????????
        self.scene = Scene()
        #?????????
        self.create_sample_scene()

    def create_sample_scene(self):
        cube_node = Cube()
        cube_node.translate(2, 0, 2)
        cube_node.color_index = 1
        self.scene.add_node(cube_node)

        sphere_node = Sphere()
        sphere_node.translate(-2, 0, 2)
        sphere_node.color_index = 3
        self.scene.add_node(sphere_node)

        hierarchical_node = SnowFigure()
        hierarchical_node.translate(-2, 0, -2)
        self.scene.add_node(hierarchical_node)

    def init_interaction(self):
        #?????????????????
	self.interaction = Interaction()
	self.interaction.register_callback('pick',self.pick)
	self.interaction.register_callback('move',self.move)
	self.interaction.register_callback('place',self.place)
	self.interaction.register_callback('rotate_color',self.rotate_color)
	self.interaction.register_callback('scale',self.scale)

    def pick(self,x,y):
	#选中一个节点
	pass

    def move(self,x,y):
	#移动一个节点
	pass

    def place(self,shape,x,y)
	#放置一个新节点
	pass

    def rotate_color(self,forward):
	#更改选中节点的颜色
	pass

    def scale(self,up):
	#更改选中节点的大小
	pass

    def main_loop(self):
        #???????
        glutMainLoop()

    def render(self):
        #???????
        self.init_view()

        #????
        glEnable(GL_LIGHTING)
        #???????????
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #??????????????????????
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        #????
        self.scene.render()

        #???????????
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        #?????????
        glFlush()

    def init_view(self):
        """ ??????? """
        xSize, ySize = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        #???????
        aspect_ratio = float(xSize) / float(ySize)

        #??????
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        #???????????
        glViewport(0, 0, xSize, ySize)
        #??????????????70?
        #??????????1000??????
        gluPerspective(70, aspect_ratio, 0.1, 1000.0)
        #??????????15???
        glTranslated(0, 0, -15)



if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
