from OpenGL.GL import glBegin, glColor3f, glEnd, glEndList, glLineWidth, glNewList, glNormal3f, glVertex3f, \
                      GL_COMPILE, GL_LINES, GL_QUADS
from OpenGL.GLU import gluDeleteQuadric, gluNewQuadric, gluSphere

G_OBJ_SPHERE = 2
def make_sphere():
	glNewList(G_OBJ_SPHERE,GL_COMPILE)
	quad = gluNewQuadric()
	gluSphere(quad,0.5,30,30)
	gluDeleteQuadric(quad)
	glEndList()

def init_primitives():
	make_sphere()
