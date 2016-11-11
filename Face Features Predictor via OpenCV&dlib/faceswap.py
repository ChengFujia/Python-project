"""
faceswap can put facial features from one face onto another.

Usage: faceswap [options] <image1> <image2>

Options:
    -v --version     show the version.
    -h --help        show usage message.
"""

import cv2
import dlib
import numpy as np
from docopt import docopt

__version__ = '1.0'

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"	#加载训练模型
SCALE_FACTOR = 1 											#图像缩放因子
FEATHER_AMOUNT = 11
COLOUR_CORRECT_BLUR_FRAC = 0.6								#颜色矫正模糊量

FACE_POINTS = list(range(17, 68))  			#脸
MOUTH_POINTS = list(range(48, 61))  		#嘴
RIGHT_BROW_POINTS = list(range(17, 22))		#右眉毛
LEFT_BROW_POINTS = list(range(22, 27)) 		#左眉毛
RIGHT_EYE_POINTS = list(range(36, 42))		#右眼睛
LEFT_EYE_POINTS = list(range(42, 48)) 		#左眼睛
NOSE_POINTS = list(range(27, 35)) 			#鼻
JAW_POINTS = list(range(0, 17)) 			#下巴

#选取的特征点索引
ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS +
                               RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)
#选取用于叠加在第一张脸上的 第二张脸的面部特征索引
OVERLAY_POINTS = [
    LEFT_EYE_POINTS + RIGHT_EYE_POINTS + LEFT_BROW_POINTS + RIGHT_BROW_POINTS,
    NOSE_POINTS + MOUTH_POINTS,
]

detector = dlib.get_frontal_face_detector()		#脸部检测器
predictor = dlib.shape_predictor(PREDICTOR_PATH)#特征提取器

class TooManyFaces(Exception):
    pass

class NoFaces(Exception):
    pass

def get_landmarks(im):
    rects = detector(im, 1)
    if len(rects) > 1:
        raise TooManyFaces
    if len(rects) == 0:
        raise NoFaces
	#返回一个n*2维的矩阵，该矩阵由检测到的脸部特征点组成
    return np.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])


def annotate_landmarks(im, landmarks):
    im = im.copy()
    for idx, point in enumerate(landmarks):
        pos = (point[0, 0], point[0, 1])
        cv2.putText(im, str(idx), pos,
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.4,
                    color=(0, 0, 255))
        cv2.circle(im, pos, 3, color=(0, 255, 255))
    return im

#绘制凸多边形
def draw_convex_hull(im, points, color):
    points = cv2.convexHull(points)
    cv2.fillConvexPoly(im, points, color=color)

#获得面部的掩码
def get_face_mask(im, landmarks):
    im = np.zeros(im.shape[:2], dtype=np.float64)

    for group in OVERLAY_POINTS:
        draw_convex_hull(im,
                         landmarks[group],
                         color=1)

    im = np.array([im, im, im]).transpose((1, 2, 0))
	#应用高斯模糊
    im = (cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0) > 0) * 1.0
    im = cv2.GaussianBlur(im, (FEATHER_AMOUNT, FEATHER_AMOUNT), 0)

    return im

#计算转换信息，返回变换矩阵
def transformation_from_points(points1, points2):
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)

    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)
    points1 -= c1
    points2 -= c2

    s1 = np.std(points1)
    s2 = np.std(points2)
    points1 /= s1
    points2 /= s2

    U, S, Vt = np.linalg.svd(points1.T * points2)

    R = (U * Vt).T

    return np.vstack([np.hstack(((s2 / s1) * R,
                                       c2.T - (s2 / s1) * R * c1.T)),
                         np.matrix([0., 0., 1.])])


def read_im_and_landmarks(fname):
    im = cv2.imread(fname, cv2.IMREAD_COLOR)				#以RGB模式读取图像
    im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,		#对图像进行适当的缩放，针对尺寸不一致的情况
                         im.shape[0] * SCALE_FACTOR))
    s = get_landmarks(im)
    return im, s

#变换图像
def warp_im(im, M, dshape):
    output_im = np.zeros(dshape, dtype=im.dtype)
	#仿射函数，能对图像进行几何变换
	#三个主要参数，第一个输出图像，第二个变换矩阵，第三个是变换后的宽/高
    cv2.warpAffine(im,
                   M[:2],
                   (dshape[1], dshape[0]),
                   dst=output_im,
                   borderMode=cv2.BORDER_TRANSPARENT,
                   flags=cv2.WARP_INVERSE_MAP)
    return output_im

#修正颜色
def correct_colours(im1, im2, landmarks1):
    blur_amount = COLOUR_CORRECT_BLUR_FRAC * np.linalg.norm(
                              np.mean(landmarks1[LEFT_EYE_POINTS], axis=0) -
                              np.mean(landmarks1[RIGHT_EYE_POINTS], axis=0))
    blur_amount = int(blur_amount)
    if blur_amount % 2 == 0:
        blur_amount += 1
    im1_blur = cv2.GaussianBlur(im1, (blur_amount, blur_amount), 0)
    im2_blur = cv2.GaussianBlur(im2, (blur_amount, blur_amount), 0)

    im2_blur += (128 * (im2_blur <= 1.0)).astype(im2_blur.dtype)

    return (im2.astype(np.float64) * im1_blur.astype(np.float64) /
                                                im2_blur.astype(np.float64))


def main():
    arguments = docopt(__doc__, version=__version__)				#自动生成参数解析器

    im1, landmarks1 = read_im_and_landmarks(arguments['<image1>'])	#1.获取图像和特征点
    im2, landmarks2 = read_im_and_landmarks(arguments['<image2>'])

    M = transformation_from_points(landmarks1[ALIGN_POINTS],		#2.选取面部位置（即全局变量设置的提取点）
                                    landmarks2[ALIGN_POINTS])		#计算转换信息，返回变换矩阵
									
    mask = get_face_mask(im2, landmarks2)							#3.获取图像2的特征掩码
    warped_mask = warp_im(mask, M, im1.shape)						#通过变换，使2的特征掩码与1适配
    combined_mask = np.max([get_face_mask(im1, landmarks1), warped_mask],#连通二者的特征掩码
                                  axis=0)
    warped_im2 = warp_im(im2, M, im1.shape)							#通过变换，使2的特征掩码与1适配
	
    warped_corrected_im2 = correct_colours(im1, warped_im2, landmarks1)#4.根据1的特征对2的颜色进行修正，使更协调

    output_im = im1 * (1.0 - combined_mask) + warped_corrected_im2 * combined_mask#5.组合图像，获得结果

    cv2.imwrite('output.jpg', output_im)							#6.存储图片


if __name__ == '__main__':
    main()