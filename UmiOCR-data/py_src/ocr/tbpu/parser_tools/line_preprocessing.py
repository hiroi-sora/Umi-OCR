# =========================================
# =============== 按行预处理 ===============
# =========================================

from math import atan2, cos, sin, sqrt, pi, radians
from statistics import median  # 中位数

angle_threshold = 3  # 进行一些操作的最小角度阈值
angle_threshold_rad = radians(angle_threshold)


# 计算两点之间的距离
def _distance(point1, point2):
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)


# 计算一个box的旋转角度
def _calculateAngle(box):
    # 获取宽高
    width = _distance(box[0], box[1])
    height = _distance(box[1], box[2])
    # 选择距离较大的两个顶点对，计算角度弧度值
    if width < height:
        angle_rad = atan2(box[2][1] - box[1][1], box[2][0] - box[1][0])
    else:
        angle_rad = atan2(box[1][1] - box[0][1], box[1][0] - box[0][0])
    # 标准化角度到[-pi/2, pi/2)范围（加上阈值）
    if angle_rad < -pi / 2 + angle_threshold_rad:
        angle_rad += pi
    elif angle_rad >= pi / 2 + angle_threshold_rad:
        angle_rad -= pi
    return angle_rad


# 估计一组文本块的旋转角度
def _estimateRotation(textBlocks):
    # blocks["box"] = [左上角,右上角,右下角,左下角]
    angle_rads = (_calculateAngle(block["box"]) for block in textBlocks)
    median_angle = median(angle_rads)  # 中位数
    return median_angle


# 获取旋转后的标准bbox。angle_threshold为执行旋转的阈值（最小角度值）。
def _getBboxes(textBlocks, rotation_rad):
    # 角度低于阈值（接近0°），则不进行旋转，以提高性能。
    if abs(rotation_rad) <= angle_threshold_rad:
        bboxes = [
            (  # 直接构造bbox
                min(x for x, y in tb["box"]),
                min(y for x, y in tb["box"]),
                max(x for x, y in tb["box"]),
                max(y for x, y in tb["box"]),
            )
            for tb in textBlocks
        ]
    # 否则，进行旋转操作。
    else:
        print("进行旋转！")
        bboxes = []
        min_x, min_y = float("inf"), float("inf")  # 初始化最小的x和y坐标
        cos_angle = cos(-rotation_rad)  # 计算角度正弦值
        sin_angle = sin(-rotation_rad)
        for tb in textBlocks:
            box = tb["box"]
            rotated_box = [  # 旋转box的每个顶点
                (cos_angle * x - sin_angle * y, sin_angle * x + cos_angle * y)
                for x, y in box
            ]
            # 解包旋转后的顶点坐标，分别得到所有x和y的值
            xs, ys = zip(*rotated_box)
            # 构建标准bbox (左上角x, 左上角y, 右下角x, 右下角y)
            bbox = (min(xs), min(ys), max(xs), max(ys))
            bboxes.append(bbox)
            min_x, min_y = min(min_x, bbox[0]), min(min_y, bbox[1])
        # 如果旋转后存在负坐标，将所有包围盒平移，使得最小的x和y坐标为0，确保所有坐标非负
        if min_x < 0 or min_y < 0:
            bboxes = [
                (x - min_x, y - min_y, x2 - min_x, y2 - min_y)
                for (x, y, x2, y2) in bboxes
            ]
    return bboxes


# 预处理 textBlocks ，将包围盒 ["box"] 转为标准化 bbox
def linePreprocessing(textBlocks):
    # 判断角度
    rotation_rad = _estimateRotation(textBlocks)
    # 获取标准化bbox
    bboxes = _getBboxes(textBlocks, rotation_rad)
    # 写入tb
    for i, tb in enumerate(textBlocks):
        tb["normalized_bbox"] = bboxes[i]
    # 按y排序
    textBlocks.sort(key=lambda tb: tb["normalized_bbox"][1])
    return textBlocks
