"""
schema中的节点不需要进行parentId、id的标记，网络应该根据ax、ay、width、height自动寻找节点之间的关系
"""

"""schema中的text编码
1: type(1) ps:这是text类型的种类编码
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
4: radius(12, 12, 12, 12) ps:这是左上右下的圆角编码
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
1: width(20)
1: height(10)
4: radius(12, 12, 12, 12) ps:这是左上右下的圆角编码
1: imgSrc(4)
"""

"""flutter中Container节点
1: type(6) ps:这是TGRadiusImage类型的种类编码
1: id(3) ps:这是当前节点的唯一标识
1: parentId(0) ps:这是祖先节点的id，为0标识没有祖先节点
1: width(0)
1: height(0)
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
    '''颜色字符串转换为数字数组
    "FFFF0000" 转化为 [255, 255, 0, 0]
    '''
    assert len(target) == 8
    temp = []
    temp.append(int(target[0:2], 16))
    temp.append(int(target[2:4], 16))
    temp.append(int(target[4:6], 16))
    temp.append(int(target[6:8], 16))
    return temp;

def formatColorIntToStr(target):
    '''数字数组转换为颜色字符串
    [255, 255, 0, 0]转化为"FFFF0000"
    '''
    assert len(target) == 4
    temp = ""
    temp += "{:02X}".format(target[0])
    temp += "{:02X}".format(target[1])
    temp += "{:02X}".format(target[2])
    temp += "{:02X}".format(target[3])
    return temp;

def formatIntListToStr(target):
    '''数字数组转化为字符串
    [16, 16, 16, 0]转化为"16,16,16,0"
    '''
    return ','.join(str(x) for x in target)

def formatStrToIntList(target):
    '''字符串转化为数字数组
    "16,16,16,0"转化为[16, 16, 16, 0]
    '''
    re = target.split(',')
    return [int(i) for i in re]

# node描述
schema_text_node = ["type", "ax", "ay", "width", "height", "text", "color", "size", "line"]
schema_layer_node = ["type", "ax", "ay", "width", "height", "color", "radius", "imgSrc"]
schema_image_node = ["type", "ax", "ay", "width", "height", "radius", "imgSrc"]
schema_tgButton_node = ["type", "ax", "ay", "width", "height", "color", "text"]

flutter_padding_node = ["type", "id", "parentId", "padding"]
flutter_tgText_node = ["type", "id", "parentId", "text", "color", "size", "height"]
flutter_row_node = ["type", "id", "parentId"]
flutter_spacer_node = ["type", "id", "parentId"]
flutter_tgRadiusImage_node = ["type", "id", "parentId", "width", "height", "radius", "imgSrc"]
flutter_container_node = ["type", "id", "parentId", "width", "height", "color", "radius", "imgSrc"]
flutter_tgButton_node = ["type", "id", "parentId", "width", "height", "color", "text"]

# node对于的type数字
schema_nodes = {
    "Text": 1, "Layer": 2, "Image": 3, "TGButton": 4
}
schema_nodes_decode = {v : k for k, v in schema_nodes.items()}
flutter_nodes = {
    "Padding": 1, "TGText": 2, "Row": 3, "Spacer": 4,
    "TGRadiusImage": 5, "Container": 6, "TGButton": 7
}
flutter_nodes_decode = {v : k for k, v in flutter_nodes.items()}

# node type对应的定义
schema_nodes_description = {
    "Text": schema_text_node,
    "Layer": schema_layer_node,
    "Image": schema_image_node, "TGButton": schema_tgButton_node
}
flutter_nodes_description = {
    "Padding": flutter_padding_node,
    "TGText": flutter_tgText_node,
    "Row": flutter_row_node,
    "Spacer": flutter_spacer_node,
    "TGRadiusImage": flutter_tgRadiusImage_node,
    "Container": flutter_container_node,
    "TGButton": flutter_tgButton_node
}

text_pool = [
    "你好", "我爱Python", "Flutter", "英雄联盟手游", "王者荣耀",
 "abcdefg", "测试demo", "demo测试", "AI2Flutter", "tensor",
  "中文编程", "", "avvwwe", "我i完成", "宋啊好吃呢", "澳产德拉克",
  "撒了采集卡", "100", "121321", "sascm", "打卡了", "你是我的",
   "我是你的", "vscode", "vs studio", "append", "正确的",
   "Documents"
]
imgSrc_pool = ["https://www.baidu.com", "https://weini.com"]


def encode_node(content_dict, node_category, text_pool, imgSrc_pool):
    re = []
    node_discription = []
    type_dict = {}
    if (node_category == "Schema"):
        node_discription = schema_nodes_description[content_dict["type"]]
        type_dict = schema_nodes
    elif (node_category == "Flutter"):
        node_discription = flutter_nodes_description[content_dict["type"]]
        type_dict = flutter_nodes
    for key in node_discription:
        if (key == "type"):
            re.append(type_dict[content_dict[key]])
        elif (key == "color"):
            re.extend(formatColorStrToInt(content_dict[key]))
        elif (key == "radius"):
            re.extend(formatStrToIntList(content_dict[key]))
        elif (key == "text"):
            re.append(text_pool.index(content_dict[key]))
        elif (key == "imgSrc"):
            re.append(imgSrc_pool.index(content_dict[key]))
        else:
            re.append(content_dict[key])
    return re

def decode_node(content_vec, node_category,  text_pool, imgSrc_pool):
    re = {}
    node_discription = []
    type_dict = {}
    if (node_category == "Schema"):
        type_dict = schema_nodes_decode
        node_discription = schema_nodes_description[schema_nodes_decode[content_vec[0]]]
    elif (node_category == "Flutter"):
        type_dict = flutter_nodes_decode
        node_discription = flutter_nodes_description[flutter_nodes_decode[content_vec[0]]]
    pointer = 0
    for key in node_discription:
        if (key == "type"):
            re[key] = type_dict[content_vec[pointer]]
            pointer += 1
        elif (key == "color"):
            re[key] = formatColorIntToStr(content_vec[pointer : pointer+4])
            pointer += 4
        elif (key == "radius"):
            re[key] = formatIntListToStr(content_vec[pointer : pointer+4])
            pointer += 4
        elif (key == "padding"):
            re[key] = formatIntListToStr(content_vec[pointer : pointer+4])
            pointer += 4
        elif (key == "text"):
            # 超出常量池范围，便使用最后一个常量
            re[key] = text_pool[
                content_vec[pointer] 
                if content_vec[pointer] < len(text_pool)
                else len(text_pool)-1]
            pointer += 1
        elif (key == "imgSrc"):
            re[key] = imgSrc_pool[
                content_vec[pointer] 
                if content_vec[pointer] < len(imgSrc_pool)
                else len(imgSrc_pool)-1]
            pointer += 1
        else:
            re[key] = content_vec[pointer]
            pointer += 1
    return re



    
    
