import tensorflow as tf
import random

"""
schema中的节点不需要进行parentId、id的标记，网络应该根据ax、ay、width、height自动寻找节点之间的关系
"""

"""schema中的Text编码
1: type(1) ps:这是Text类型的种类编码
1: ax(0)
1: ay(0)
1: width(20)
1: height(10)
1: text(4) ps:指向一个序号
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: size(20)
1: line(10)

一共12个数字

example:
{"type":"text", "ax":2, "ay":5, "width":20, "height":52, "text":"你好", "color":"FFFF0000", "size":20, "line":10}
按照顺序转换后序列为：
1, 2, 5, 20, 52, 4, 255, 255, 0, 0, 20, 10

"""


"""schema中的Layer编码
1: type(2)
1: ax(0)
1: ay(0)
1: width(20)
1: height(10)
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
4: radius(12, 12, 12, 12) ps:这是左上右下的圆角编码
1: imgSrc(3) ps:指向背景图的常量
"""

"""schema中的Image编码
1: type(3)
1: ax(0)
1: ay(0)
1: width(20)
1: height(10)
1: imgSrc(1) ps:指向一个常量序号
"""

"""schema中的TGButton编码(组件库节点)
1: type(4)
1: ax(0)
1: ay(0)
1: width(20)
1: height(10)
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: text(4) ps:指向一个常量序号
"""

"""
------flutter的节点，期待网络按照广度遍历的方式进行组织，故一个节点下的子节点，默认按照从左到右的顺序来排列-------
"""

"""flutter中Padding的编码
1: type(1) ps:这是padding类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(8) ps:这是祖先节点的id，为0标识没有祖先节点
4: padding(20, 100, 0, 2) ps:这依次是左20，上100，右0，下2的编码

一共7个数字

example:
{"type":"Padding", "id":1, "parentId":0, "padding":"20, 20, 4, 10"}
按照顺序转换后向量为：
[1, 1, 0, 20, 20, 4, 10]

"""

"""flutter中的TGText编码
1: type(2) ps:这是TGText类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
1 : text(4) ps:指向一个序号
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: size(20)
1: height(10)

一共16个数字

example:
{"type":"TGText", "id":2, "parentId":1, "text":"你好", "color":"FFFF0000", "size":20, "line":10}
按照顺序转换后向量为：
[2, 2, 1, 4, 255, 255, 0, 0, 20, 10]
"""

"""flutter中的Row节点
1: type(3) ps:这是Row类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
"""

"""flutter中的Spacer节点
1: type(4) ps:这是Spacer类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
"""

"""flutter中TGRadiusImage节点
1: type(5) ps:这是TGRadiusImage类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
1: imgSrc(4)
"""

"""flutter中Container节点
1: type(6) ps:这是TGRadiusImage类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
4: radius(12, 12, 12, 12)
1: imgSrc(1)
"""

"""flutter中TGButton节点
1: type(7) ps:这是TGButton类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
1: width(20)
1: height(10)
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: text(4) ps:指向一个常量序号
"""

def formatColorStrToInt(target):
    assert len(target) == 8
    temp = []
    temp.append(int(target[0:2], 16))
    temp.append(int(target[2:4], 16))
    temp.append(int(target[4:6], 16))
    temp.append(int(target[6:8], 16))
    return temp;

def formatColorIntToStr(target):
    assert len(target) == 4
    temp = ""
    temp += "{:02X}".format(target[0])
    temp += "{:02X}".format(target[1])
    temp += "{:02X}".format(target[2])
    temp += "{:02X}".format(target[3])
    return temp;

demo_texts_pool_length = 60
demo_texts_data = [i for i in range(1, demo_texts_pool_length)]




def process_output_data(output_data):
    '''
    通过实际输出参数，增加开始标志997，给标签增加结束标志998
    '''
    out_data = []
    out_label = []
    for seq in output_data:
        out_data_seq = []
        out_label_seq = []
        # 997作为数据开始，998作为数据结束
        out_data_seq.append(997)
        for num in seq:
            out_data_seq.append(num)
            out_label_seq.append(num)
        out_label_seq.append(998)
        out_data.append(out_data_seq)
        out_label.append(out_label_seq)
    return [out_data, out_label]


# 生成num的序列构成的样本
def demo_generate_data(num):
    input_seqs = []
    output_seqs = []
    for i in range(0, num):
        input_seq = []
        output_seq = []
        # 随机取各种属性
        ax, ay = [random.randint(0, 200) for i in range(2)]
        # 绝对位置有一定几率为0‰
        if (random.randint(0, 5) == 0):
            ax = 0
            ay = 0
        width, height = [random.randint(20, 100) for i in range(2)]
        size, line = [random.randint(15, 120) for i in range(2)]
        text = demo_texts_data[random.randint(0, len(demo_texts_data)-1)]
        # color = demo_colors_data[random.randint(0, len(demo_colors_data)-1)]
        color = [random.randint(0, 255) for i in range(4)];
        # 构建一个输入node
        input_node = []
        input_node.append(1)
        input_node.extend([ax, ay, width, height])
        input_node.append(text)
        input_node.extend(color)
        input_node.extend([size, line])
        input_seq.extend(input_node)

        # 构建输出node
        if (ax == 0 and ay == 0):
            # TGButton节点，type为2，id为1，parentId为0
            output_node = []
            output_node.extend([2, 1, 0])
            output_node.append(text)
            output_node.extend(color)
            output_node.extend([size, line])
            output_seq.extend(output_node)
        else:
            # 构建Padding节点，type为1，id为1，parentId为0
            output_node = []
            output_node.extend([1, 1, 0, ax, ay, 0, 0])
            output_seq.extend(output_node)
            output_seq.append(999)

            # TGButton节点，type为2，id为2，parentId为1
            output_node = []
            output_node.extend([2, 2, 1])
            output_node.append(text)
            output_node.extend(color)
            output_node.extend([size, line])
            output_seq.extend(output_node) 
        # 加到训练集
        input_seqs.append(input_seq)
        output_seqs.append(output_seq)
        # 生成输入和标签
        processed_output = process_output_data(output_seqs)
    return [input_seqs, processed_output[0], processed_output[1]]