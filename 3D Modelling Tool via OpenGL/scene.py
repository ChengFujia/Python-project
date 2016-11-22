#-*- coding:utf8 -*-
class Scene(object):
	PLACE_DEPTH = 15.0			#设置节点的深度，放置的节点距离摄像机15个单位
	def __init__(self):
		self.node_list = list()		#场景下的节点队列
	def add_node(self,node):
		self.node_list.append(node)	#场景中增加一个节点
	def render(self):
		for node in self.node_list:	#遍历场景中所有节点并渲染
			node.render()
