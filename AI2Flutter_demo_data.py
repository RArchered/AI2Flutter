import tensorflow as tf
import random

"""schema中的text编码
1: type(1) ps:这是text类型的种类编码
1: ax(0)
1: ay(0)
1. width(20)
1. height(10)
# 7: text(20320, 22909, 0, 0, 0, 0, 0) ps:这是“你好”的unicode编码，超过7位被截断
1 : text(4) ps:指向一个序号
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: size(20)
1: height(10)

一共12个数字

example:
{"type":"text", "ax":2, "ay":5, "width":20, "height":52, "text":"你好", "color":"FFFF0000", "size":20, "height":10}
按照顺序转换后序列为：
1, 2, 5, 20, 52, 4, 255, 255, 0, 0, 20, 10

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
# 7: text(20320, 22909, 0, 0, 0, 0, 0) ps:这是“你好”的unicode编码，超过7位被截断
1 : text(4) ps:指向一个序号
4: color(255, 255, 0, 0) ps:这是颜色FFFF0000的编码
1: size(20)
1: height(10)

一共16个数字

example:
{"type":"TGText", "id":2, "parentId":1, "text":"你好", "color":"FFFF0000", "size":20, "height":10}
按照顺序转换后向量为：
[2, 2, 1, 4, 255, 255, 0, 0, 20, 10]

"""

def formatStrToInt(target):
    temp = []
    for i in range(min(len(target), 7)):
        temp.append(ord(target[i]))
    while (len(temp) < 7):
        temp.append(0)
    return temp

def formatColorStrToInt(target):
    assert len(target) == 8
    temp = []
    temp.append(int(target[0:2], 16))
    temp.append(int(target[2:4], 16))
    temp.append(int(target[4:6], 16))
    temp.append(int(target[6:8], 16))
    return temp;


# demo_texts_data = [
#     [20320, 22909, 0, 0, 0, 0, 0], # 你好
#     [25105, 29233, 80, 121, 116, 104, 111], # 我爱Python
#     [70, 108, 117, 116, 116, 101, 114], # Flutter
#     [33521, 38596, 32852, 30431, 25163, 28216, 0], # 英雄联盟手游
#     [29579, 32773, 33635, 32768, 0, 0, 0], # 王者荣耀
#     [97, 98, 99, 100, 101, 102, 103], # abcdefg
#     [27979, 35797, 100, 101, 109, 111, 0], # 测试demo
#     [100, 101, 109, 111, 27979, 35797, 0], # demo测试
#     [65, 73, 50, 70, 108, 117, 116], # AI2Flutter
#     [116, 101, 110, 115, 111, 114, 0], # tensor
#     [20013, 25991, 32534, 31243, 0, 0, 0], # 中文编程
# ]
# demo_texts= [
#     "你好", "我爱Python", "Flutter", "英雄联盟手游", "王者荣耀",
#  "abcdefg", "测试demo", "demo测试", "AI2Flutter", "tensor",
#   "中文编程", "", "avvwwe", "我i完成", "宋啊好吃呢", "澳产德拉克",
#   "撒了采集卡", "100", "121321", "sascm", "打卡了", "你是我的",
#    "我是你的", "鸡你太美", "vscode", "vs studio", "append", "正确的",
#    "Documents"
# ]
demo_texts_pool_length = 60
demo_texts_data = [i for i in range(1, demo_texts_pool_length)]
demo_colors = [
    "FFFF0000", "FF00FF00", "FF00FFAB", "FF8E8E93", "00FFAA8E", "00F38989", "34565634",
    "F087895F", "00000000", "F6786548", "98765678", "87654879", "F2565656", "FF242424"
]
demo_colors_data = [formatColorStrToInt(i) for i in demo_colors]



def process_output_data(output_data):
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
