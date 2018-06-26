def thresholding():
    pass

import cv2
import numpy as np
import matplotlib.pyplot as plt

image_color = cv2.imread("/Users/chenchang/project/python/image-recognition/tmp/text1.png")
# new_shape = (image_color.shape[1] * 2, image_color.shape[0] * 2)
# image_color = cv2.resize(image_color, new_shape)
image = cv2.cvtColor(image_color, cv2.COLOR_BGR2GRAY)

# 图片数据读到image_color和灰度image里面，为了方便查看，这里我把图片放大两倍了。
#
# 首先, 我们开始对图片进行二值化处理：
adaptive_threshold = cv2.adaptiveThreshold(
    image,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    cv2.THRESH_BINARY_INV, 11, 2)
cv2.imshow('binary image', adaptive_threshold)
cv2.waitKey(0)


# 可以看到，二值化的效果还是非常理想的，没有什么噪点。
#
# 现在的目标就是提取每行，然后分割每个字符。
horizontal_sum = np.sum(adaptive_threshold, axis=1)

plt.plot(horizontal_sum, range(horizontal_sum.shape[0]))
plt.gca().invert_yaxis()
plt.show()

# 上面的代码是把图像往水平方向的求和，然后画出结果。可以见到文本行被明显分隔出来。注意，这里我把y轴反了，因为图像的坐标0点在左上角。
#
# 接着需要提取数组里面的峰值，然后找出文本行，所以这里定义提取峰值函数：
def extract_peek_ranges_from_array(array_vals, minimun_val=10, minimun_range=2):
    start_i = None
    end_i = None
    peek_ranges = []
    for i, val in enumerate(array_vals):
        if val > minimun_val and start_i is None:
            start_i = i
        elif val > minimun_val and start_i is not None:
            pass
        elif val < minimun_val and start_i is not None:
            end_i = i
            if end_i - start_i >= minimun_range:
                peek_ranges.append((start_i, end_i))
            start_i = None
            end_i = None
        elif val < minimun_val and start_i is None:
            pass
        else:
            raise ValueError("cannot parse this case...")
    return peek_ranges

#有些图片比较多噪音，需要minimun_val和minimun_range用于过滤噪音。用这个函数提取峰值：
peek_ranges = extract_peek_ranges_from_array(horizontal_sum)

line_seg_adaptive_threshold = np.copy(adaptive_threshold)
for i, peek_range in enumerate(peek_ranges):
    x = 0
    y = peek_range[0]
    w = line_seg_adaptive_threshold.shape[1]
    h = peek_range[1] - y
    pt1 = (x, y)
    pt2 = (x + w, y + h)
    cv2.rectangle(line_seg_adaptive_threshold, pt1, pt2, 255)
cv2.imshow('line image', line_seg_adaptive_threshold)
cv2.waitKey(0)


#行文字都被提取出来，然后可以对中文字分割。相类似, 使用垂直方向的求和把字符也可以找出来。
vertical_peek_ranges2d = []
for peek_range in peek_ranges:
    start_y = peek_range[0]
    end_y = peek_range[1]
    line_img = adaptive_threshold[start_y:end_y, :]
    vertical_sum = np.sum(line_img, axis=0)
    vertical_peek_ranges = extract_peek_ranges_from_array(
        vertical_sum,
        minimun_val=40,
        minimun_range=1)
    vertical_peek_ranges2d.append(vertical_peek_ranges)

## Draw
color = (0, 0, 255)
for i, peek_range in enumerate(peek_ranges):
    for vertical_range in vertical_peek_ranges2d[i]:
        x = vertical_range[0]
        y = peek_range[0]
        w = vertical_range[1] - x
        h = peek_range[1] - y
        pt1 = (x, y)
        pt2 = (x + w, y + h)
        cv2.rectangle(image_color, pt1, pt2, color)
cv2.imshow('char image', image_color)
cv2.waitKey(0)


# 在没有文字信息情况下，还有是有一些细节问题可以解决，譬如有些包围盒连续在一起，譬如第三行最后“本上就”连在一起。
#
# 这个利用每行宽度的中位值进行切割来解决：
def median_split_ranges(peek_ranges):
    new_peek_ranges = []
    widthes = []
    for peek_range in peek_ranges:
        w = peek_range[1] - peek_range[0] + 1
        widthes.append(w)
    widthes = np.asarray(widthes)
    median_w = np.median(widthes)
    for i, peek_range in enumerate(peek_ranges):
        num_char = int(round(widthes[i]/median_w, 0))
        if num_char > 1:
            char_w = float(widthes[i] / num_char)
            for i in range(num_char):
                start_point = peek_range[0] + int(i * char_w)
                end_point = peek_range[0] + int((i + 1) * char_w)
                new_peek_ranges.append((start_point, end_point))
        else:
            new_peek_ranges.append(peek_range)
    return new_peek_ranges

# 上面的函数是利用中位置切割连在一起的包围盒。我们再分割一次，然后加上切割太长的包围盒。
vertical_peek_ranges2d = []
for peek_range in peek_ranges:
    start_y = peek_range[0]
    end_y = peek_range[1]
    line_img = adaptive_threshold[start_y:end_y, :]
    vertical_sum = np.sum(line_img, axis=0)
    vertical_peek_ranges = extract_peek_ranges_from_array(
        vertical_sum,
        minimun_val=40,
        minimun_range=1)
    vertical_peek_ranges = median_split_ranges(vertical_peek_ranges)
    vertical_peek_ranges2d.append(vertical_peek_ranges)

## Draw
color = (0, 0, 255)
for i, peek_range in enumerate(peek_ranges):
    for vertical_range in vertical_peek_ranges2d[i]:
        x = vertical_range[0]
        y = peek_range[0]
        w = vertical_range[1] - x
        h = peek_range[1] - y
        pt1 = (x, y)
        pt2 = (x + w, y + h)
        cv2.rectangle(image_color, pt1, pt2, color)
cv2.imshow('splited char image', image_color)
cv2.waitKey(0)