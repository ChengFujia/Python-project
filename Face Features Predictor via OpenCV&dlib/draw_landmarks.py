import cv2
import dlib

#加载面部检测器
detector = dlib.get_frontal_face_detector()
#加载训练模型并获取面部特征提取器
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
#以RGB模式读入图像
im = cv2.imread('hc.jpg',cv2.IMREAD_COLOR)
#使用检测器检测人脸
rects = detector(im,1)
#使用特征提取器获取面部特征点
l = [(p.x,p.y) for p in predictor(im,rects[0]).parts()]
#遍历面部特征点并绘制出来
for (cnt,p) in enumerate(l):
	cv2.circle(im,p,5,(0,255,255),2)
	cv2.putText(im,str(cnt),(p[0]+5,p[1]-5),0,0.75,color=(0,0,255))
#保存图像
cv2.imwrite('landmarks.jpg',im)
cv2.waitKey(0)

