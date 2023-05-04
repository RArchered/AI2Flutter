import tensorflow as tf
import random
from node_processor import *

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
# 输入input、output、label三个数据，均为二维数组，一是batch，二是每一个节点序列
def demo_generate_data(num):
    input_seqs = []
    output_seqs = []
    for i in range(0, num):
        input_seq = []
        output_seq = []
        # 随机取各种属性
        ax, ay = [random.randint(0, 200) for i in range(2)]
        # 绝对位置有一定几率为0
        if (random.randint(0, 5) == 0):
            ax = 0de
            ay = 0
        # 绝对位置有
        if (random.randint(0, 5) == 0):
            ax, ay = [random.randint(1, 5) for i in range(2)]
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