import sys
import copy
import cv2
import getopt
import math

# 使用 Canny 算法检测边界
def detectEdges(image):
    edges = cv2.Canny(image, 100, 100)
    cv2.imwrite("edges.jpg", edges)			# 保存图片
    return edges

# 先分隔，再根据边界处理图片，提取有效信息
def isolateUnique(image, edges):
    blocksize = 64							# 纵向分割为 64 个块
    varianceThreshold = 95					# 方差阈值
    cellPx = image.shape[1] // blocksize	# 设定每一块的边长，shape[1] 为图片宽度
    rows = image.shape[0] // cellPx			# 分割后的行数
    cols = blocksize						# 分割后的列数
    blockPx = cellPx * cellPx				# 每一块的像素数量
    cellValues = [0] * (rows)
    imgR = 0
    imgG = 0
    imgB = 0
    imgCells = (blockPx) * (rows * cols)
    for i in range(rows):					# 遍历每一行
        cellValues[i] = [0] * blocksize
        for j in range(cols):				# 遍历每一列
            rbeg = cellPx * i				# 遍历每一个分割块
            rend = rbeg + cellPx
            cbeg = cellPx * j
            cend = cbeg + cellPx
            r = 0
            g = 0
            b = 0
            hasEdge = False
            for ii in range(rbeg, rend):	# 遍历每一个分割块的 行像素点
                for jj in range(cbeg, cend):# 遍历每一个分割块的 列像素点
                    if edges[ii][jj] > 0:
                        hasEdge = True
                    r = r + image[ii][jj][0]
                    g = g + image[ii][jj][1]
                    b = b + image[ii][jj][2]

            imgR = imgR + r
            imgG = imgG + g
            imgB = imgB + b
            rv = int(r / blockPx)
            gv = int(g / blockPx)
            bv = int(b / blockPx)
            value = [rv, gv, bv] if hasEdge == True else [0, 0, 0]
            cellValues[i][j] = value
            cv2.rectangle(image, (cbeg, rbeg), (cend, rend), (rv, gv, bv), -1)	# 绘制实心矩形，颜色各异
    avgR = imgR // imgCells
    avgG = imgG // imgCells
    avgB = imgB // imgCells
    cv2.rectangle(image, (0, 0), (image.shape[1], image.shape[0]), (0, 0, 0),-1)# 绘制实心矩形--（0，0，0）为黑色，这里把前面的都覆盖了
	
    for i in range(len(cellValues)):			# 二次处理
        for j in range(len(cellValues[i])):
            rdiff = abs(cellValues[i][j][0] - avgR)
            gdiff = abs(cellValues[i][j][1] - avgG)
            bdiff = abs(cellValues[i][j][2] - avgB)
            rbeg = cellPx * i
            rend = rbeg + cellPx
            cbeg = cellPx * j
            cend = cbeg + cellPx
            pxDiff = True if (rdiff > varianceThreshold or
                              gdiff > varianceThreshold or
                              bdiff > varianceThreshold) else False
            isBlack = True if (cellValues[i][j][0] < 30 and
                               cellValues[i][j][1] < 30 and
                               cellValues[i][j][2] < 30) else False
            if pxDiff and (isBlack == False):	# 针对超过设定阈值且不是黑色的小块，设置为白色，视为有效信息
                cv2.rectangle(image, (cbeg, rbeg), (cend, rend), (255, 255, 255), -1)
            else:								# 针对其他小块，设置为黑色，视为无效信息，即为背景色
                cv2.rectangle(image, (cbeg, rbeg), (cend, rend), (0, 0, 0), -1)
    cv2.imwrite("blocks.png", image)

def main(argv):
    # 加载训练好的脸、眼分类器
    face_cascade = cv2.CascadeClassifier(
        '/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier(
        '/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')
    inputFile = ''
    outputFile = ''
    width = 300
    height = 300
    blocksize = 64
    # 处理命令行参数
    opts, args = getopt.getopt(argv, "hi:o:x:y:b:", ["ifile=", "ofile="])
    for opt, arg in opts:
        if opt == "-i":
            inputFile = arg
        if opt == "-o":
            outputFile = arg
        if opt == "-y":
            height = arg
        if opt == "-x":
            width = arg
        if opt == "-b":
            blocksize = arg
    if outputFile == "":
        outputFile = inputFile
    orgHeight = height
    orgWidth = width
    img = cv2.imread(inputFile)
    original = copy.copy(img)					# 返回 img 的浅拷贝
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)# 转换为灰度图
    faces = face_cascade.detectMultiScale(		# 检测人脸
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)
		
    edgeRef = detectEdges(img)					# 检测边缘
    isolateUnique(img, edgeRef)
    maxFaceCenter = 0							# 最大脸的中心位置
    maxFaceRight = 0							# 最大脸的右端位置
    print("Found {0} faces!".format(len(faces)))

    # 裁剪定位
    imHeight, imWidth = img.shape[:2]
    cropBias = imWidth
    for (x, y, w, h) in faces:
        # 人脸部分用实心矩形框选
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)
        cropBias = cropBias - x
        # 找出最大人脸
        if (x + w) > maxFaceRight:
            maxFaceCenter = (x + w) - (w // 2)
            maxFaceRight = x + w
        # 截出人脸
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        # 检测眼睛
        eyes = eye_cascade.detectMultiScale(roi_gray)
        # 框选出人眼
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0),
                          2)
    cropBiasPerc = cropBias / imWidth	# 裁剪偏差精度
    ratio = int(height) / img.shape[0]	# 比率
    height = img.shape[0]
	
	# 在保证输入分辨率的情况下 对尺寸进行变换（高度不变，宽度伸缩）
    middleY = 0
    newRatio = height / int(orgHeight)
    width = round(int(width) * newRatio)
    rawCols = math.ceil(img.shape[1] / width)

    mostPosIndex = 0
    bestPosValue = 0
    for i in range(rawCols):
        positiveCount = 0
        startx = i * width
        endx = startx + width
        endx = img.shape[1] if endx > img.shape[1] else endx
        for col in range(startx, endx):
            for row in range(img.shape[0]):
                pxval = img[row][col][0] + img[row][col][1] + img[row][col][2]
                if pxval > 0:
                    positiveCount = positiveCount + 1
        if positiveCount > bestPosValue:
            mostPosIndex = i
            bestPosValue = positiveCount
        print(i, positiveCount)
    print("Best Index: ", str(mostPosIndex))
    middleX = mostPosIndex * width

    if middleX + width > img.shape[1]:
        middleX = img.shape[1] - width

    cv2.rectangle(img, (middleX, middleY),
                  (middleX + width, middleY + height), (0, 255, 0),
                  2)

    cropped = copy.copy(original)
    copyName = "ref_" + outputFile
    croppedName = "cropped_" + outputFile
    cropX1 = middleX + width
    cropY1 = middleY + height
    croppedData = original[middleY:cropY1, middleX:cropX1]
    
    cv2.imwrite(copyName, original)
    cv2.imwrite(croppedName, croppedData)
    cv2.imwrite(outputFile, img)


if __name__ == "__main__":
    main(sys.argv[1:])
