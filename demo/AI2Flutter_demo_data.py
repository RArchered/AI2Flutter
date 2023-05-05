import tensorflow as tf
import random
from node_processor import *

'''
魔法数字描述:
999:node之间的分隔符
998:输出结束位置
997:输入开始位置

'''

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


# 生成text构成的样本
# 输出input、output、label三个数据，均为二维数组，一是batch，二是每一个节点序列
def generate_text_data(num):
    input_seqs = []
    output_seqs = []
    text_pool_len = 40
    for i in range(0, num):
        input_seq = []
        output_seq = []
        # 随机取各种属性
        ax, ay = [random.randint(0, 200) for i in range(2)]
        if (random.randint(0, 3) == 0):
            ax, ay = [random.randint(0, 32) for i in range(2)]
        width, height = [random.randint(20, 100) for i in range(2)]
        size, line = [random.randint(15, 120) for i in range(2)]
        text = random.randint(0, text_pool_len)
        color = [random.randint(0, 255) for i in range(4)];
        # 构建一个Schema text node
        input_node = []
        input_node.append(1)
        input_node.extend([ax, ay, width, height])
        input_node.append(text)
        input_node.extend(color)
        input_node.extend([size, line])
        input_seq.extend(input_node)

        # 构建输出node
        # Flutter TGText节点，type为2，id为1，parentId为0
        output_node = []
        output_node.extend([2, 1, 0])
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

# 生成layer构成的样本
# 输出input、output、label三个数据，均为二维数组，一是batch，二是每一个节点序列
def generate_layer_data(num):
    input_seqs = []
    output_seqs = []
    img_pool_len = 40
    for i in range(0, num):
        input_seq = []
        output_seq = []
        # 随机取各种属性
        ax, ay = [random.randint(0, 200) for i in range(2)]
        if (random.randint(0, 3) == 0):
            ax, ay = [random.randint(0, 32) for i in range(2)]
        width, height = [random.randint(20, 360) for i in range(2)]
        color = [random.randint(0, 255) for i in range(4)]
        radius = [random.randint(0, 16) for i in range(4)]
        imgSrc = random.randint(0, img_pool_len)
        # 构建一个Schema layer node
        input_node = []
        input_node.append(2)
        input_node.extend([ax, ay, width, height])
        input_node.extend(color)
        input_node.extend(radius)
        input_node.append(imgSrc)
        input_seq.extend(input_node)

        # 构建输出node
        # Flutter Container节点，type为2，id为1，parentId为0
        output_node = []
        output_node.extend([6, 1, 0])
        output_node.extend([width, height])
        output_node.extend(color)
        output_node.extend(radius)
        output_node.append(imgSrc)
        output_seq.extend(output_node)
        # 加到训练集
        input_seqs.append(input_seq)
        output_seqs.append(output_seq)
        # 生成输入和标签
        processed_output = process_output_data(output_seqs)
    return [input_seqs, processed_output[0], processed_output[1]]

# 生成tgbutton构成的样本
# 输出input、output、label三个数据，均为二维数组，一是batch，二是每一个节点序列
def generate_tgButton_data(num):
    input_seqs = []
    output_seqs = []
    text_pool_len = 40
    img_pool_len = 40
    for i in range(0, num):
        input_seq = []
        output_seq = []
        # 随机取各种属性
        ax, ay = [random.randint(0, 200) for i in range(2)]
        if (random.randint(0, 3) == 0):
            ax, ay = [random.randint(0, 32) for i in range(2)]
        width, height = [random.randint(20, 360) for i in range(2)]
        color = [random.randint(0, 255) for i in range(4)]
        radius = [random.randint(0, 16) for i in range(4)]
        text = random.randint(0, text_pool_len)
        # 构建一个Schema layer node
        input_node = []
        input_node.append(4)
        input_node.extend([ax, ay, width, height])
        input_node.extend(color)
        input_node.append(text)
        input_seq.extend(input_node)

        # 构建输出node
        # Flutter TGButton节点，type为2，id为1，parentId为0
        output_node = []
        output_node.extend([7, 1, 0])
        output_node.extend([width, height])
        output_node.extend(color)
        output_node.append(text)
        output_seq.extend(output_node)
        # 加到训练集
        input_seqs.append(input_seq)
        output_seqs.append(output_seq)
        # 生成输入和标签
        processed_output = process_output_data(output_seqs)
    return [input_seqs, processed_output[0], processed_output[1]]