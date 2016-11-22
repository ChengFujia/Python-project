#-*- coding:utf8 -*-
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
                        GLUT_SINGLE, GLUT_RGB, GLUT_WINDOW_HEIGHT, GLUT_WINDOW_WIDTH
import numpy
from numpy.linalg import norm, inv
import random
from OpenGL.GL import glBegin, glColor3f, glEnd, glEndList, glLineWidth, glNewList, glNormal3f, glVertex3f, \
                      GL_COMPILE, GL_LINES, GL_QUADS
from OpenGL.GLU import gluDeleteQuadric, gluNewQuadric, gluSphere
import color
from scene import Scene
from primitive import init_primitives
from node import Sphere,SnowFigure

class Viewer(object):
	def __init__(self):
		self.init_interface()
		self.init_opengl()
		self.init_scene()
		self.init_interaction()
		init_primitives()
		
	def init_interface(self):
		#初始化窗口并注册渲染函数
		glutInit()
		glutInitWindowSize(640,480)
		glutCreateWindow("3D Modeller")
		glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
		#注册渲染函数
		glutDisplayFunc(self.render)
	def init_opengl(self):
		#初始化openGL的配置
		self.modelView = numpy.identity(4)		#模型视图矩阵
		self.inverseModelView = numpy.identity(4)	#模型视图矩阵的逆矩阵
		glEnable(GL_CULL_FACE)				#开启剔除操作效果
		glCullFace(GL_BACK)				#取消对多边形背面进行渲染的操作（看不到的部分不渲染）
		glEnable(GL_DEPTH_TEST)				#开启深度测试
		glDepthFunc(GL_LESS)				#测试是否被遮挡（被遮挡的物体不渲染）
		glEnable(GL_LIGHT0)				#启动0号光源
		glLightfv(GL_LIGHT0,GL_POSITION,GLfloat_4(0,0,1,0))	#设置光源的位置
		glLightfv(GL_LIGHT0,GL_SPOT_DIRECTION,GLfloat_3(0,0,-1))#设置光源的照射方向
		glEnable(GL_COLOR_MATERIAL)			#启动材质颜色
		glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)#设置材质
		glClearColor(0.4,0.4,0.4,0.0)				#设置颜色
	def init_scene(self):
		#初始化场景
		self.scene = Scene()
		self.create_sample_scene()
	def create_sample_scene(self):
		#创建一个场景实例
		sphere_node = Sphere()			#创建一个球体
		sphere_node.color_index = 2		#设置球体颜色
		sphere_node.translate(2,2,0)
		sphere_node.scale(4)
		self.scene.add_node(sphere_node)	#将球体放在场景中，模人在正中央
		hierarchical_node = SnowFigure()	#创建一个小雪人
		hierarchical_node.translate(-2,0,-2)
		hierarchical_node.scale(2)
		self.scene.add_node(hierarchical_node)
	def init_interaction(self):
		#初始化交互操作
		pass
	def init_view(self):
		#初始化投影矩阵
		xSize,ySize = glutGet(GLUT_WINDOW_WIDTH),glutGet(GLUT_WINDOW_HEIGHT)
		aspect_ratio = float(xSize) / float(ySize)		#得到屏幕宽高比
		glMatrixMode(GL_PROJECTION)				#设置投影矩阵
		glLoadIdentity()
		glViewport(0,0,xSize,ySize)				#设置视口，应和窗口重合
		gluPerspective(70,aspect_ratio,0.1,1000.0)		#设置透视，摄影机上下视野幅度70度
									#视野范围到摄像机1000个单位
		glTranslated(0,0,-15)					#摄像机镜头从原点后退15个单位
	def render(self):
		#程序进入主循环后每一次循环调用的渲染函数
		self.init_view()
		glEnable(GL_LIGHTING)					#启动光照
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	#清空颜色缓存和深度缓存
		glMatrixMode(GL_MODELVIEW)				#设置模型视图矩阵
		glPushMatrix()
		glLoadIdentity()
		self.scene.render()					#渲染场景				
		glDisable(GL_LIGHTING)					#每次渲染后复位光照状态
		glPopMatrix()
		glFlush()						#将数据刷新到显存
	def main_loop(self):
		#程序主循环
		glutMainLoop()
	
if __name__ == "__main__":
	viewer = Viewer()
	viewer.main_loop()
