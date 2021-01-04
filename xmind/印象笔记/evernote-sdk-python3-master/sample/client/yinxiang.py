# coding = utf-8
import sys
sys.path.append(r'./../../lib')

import zipfile
import os
import json
import hashlib
import time
import copy

import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import os
import time
import re


from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter
from evernote.edam.type.ttypes import NoteSortOrder
from evernote.edam.notestore.ttypes import NotesMetadataResultSpec
# auth_token申请地址：https://dev.yinxiang.com/doc/articles/dev_tokens.php
auth_token = "xxx"





# 实例化创建加密对象，必须是全局变量，否则hash值会重复
hash_encoder = hashlib.sha3_256()

# 常量定义
theme = {"id":"508b628c872bcdebad590b9d62","importantTopic":{"type":"topic","properties":{"fo:font-weight":"bold","fo:color":"#434B54","svg:fill":"#62FFFF"}},"minorTopic":{"type":"topic","properties":{"fo:font-weight":"bold","fo:color":"#434B54","svg:fill":"#FAFF7E"}},"expiredTopic":{"type":"topic","properties":{"fo:font-style":"italic","fo:text-decoration":" line-through"}},"centralTopic":{"properties":{"line-width":"3pt","line-color":"#434B54","fo:color":"#434B54","svg:fill":"none","fo:font-size":"24pt","fo:font-family":"Montserrat","fo:font-weight":"700","fo:font-style":"normal"},"styleId":"53e97033f92b8bd3f4c78979c3","type":"topic"},"boundary":{"properties":{"fo:font-family":"Montserrat","fo:font-weight":"normal","line-color":"#FB5151","svg:fill":"#FCDBDA","fo:color":"#FFFFFF"},"styleId":"49a959f26a7811630973d8e2df","type":"boundary"},"floatingTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"normal","line-color":"#434B54","line-class":"org.xmind.branchConnection.curve","line-width":"1pt"},"styleId":"1a1aa0882bb9bcb55bc7889a27","type":"topic"},"subTopic":{"properties":{"fo:font-weight":"normal","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-size":"14pt","shape-class":"org.xmind.topicShape.roundedRect","fo:text-align":"left","border-line-width":"0","line-class":"org.xmind.branchConnection.curve"},"styleId":"719abce18ea9cf241bdeea7366","type":"topic"},"mainTopic":{"properties":{"fo:font-weight":"500","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-style":"normal","fo:font-size":"18pt","svg:fill":"none","line-width":"1pt","fo:text-align":"center","border-line-width":"3pt","line-class":"org.xmind.branchConnection.curve"},"styleId":"0bca341d27dbabf4d116fb3b67","type":"topic"},"calloutTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"normal"},"styleId":"78aa5283453b7fd33b3388bb57","type":"topic"},"summary":{"properties":{"line-color":"#FB5151"},"styleId":"b03a96d54f89a5862ed289bf3b","type":"summary"},"summaryTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"400","fo:font-style":"normal","line-class":"org.xmind.branchConnection.curve"},"styleId":"e64865a4408a28ebcf9ca9c7f5","type":"topic"},"relationship":{"properties":{"arrow-begin-class":"org.xmind.arrowShape.dot","line-pattern":"dot","line-color":"#FB5151","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-weight":"normal","line-width":"3pt"},"styleId":"93c86baff3d8ee1505ed887476","type":"relationship"}}
id_evernote_image = "54755c7f4a9991774d371bc72d6b735778bedada4ea38af8e2c8cfecc32269b0.png"

# 把图片的id放入字典
type_dict= {}
type_dict["evernote"] = id_evernote_image

# 全局变量，印象笔记数据结构
tag_list = []  # 所有tag
tag_dict = {}  # 未用的tag
tag_finish = {}  # 用过的tag
tag_root = []  # 存放根节点的tag
tag_insert = {}

# 全局变量，xmind的数据结构
data = []
node_sheet = {}
node_root = {}
children = {}
node_file = {}
node_folder = {}
image_dict = {}



def gen_topic_id():
    global hash_encoder
    randomcode = str(time.time())
    hash_encoder.update(randomcode.encode("utf-8"))    #传入待加密的字符串
    return hash_encoder.hexdigest()[0:26]


# 把data写入content.json文件
def gen_json_file(data):
    json_str = json.dumps(data)
    filename = "content.json"
    json_file = open(filename, 'w')
    json_file.write(json_str)
    json_file.close()

def notebooks_sort(notebooks):
    list_temp = []
    index = {}
    for i in range(len(notebooks)):
        index[str(notebooks[i].name[0])] = i  # 名称第一位必须是数字
    for i in range(len(notebooks)):
        cnt = index[str(i)]
        list_temp.append(notebooks[cnt])
    return list_temp

def tags_sort(tag_list):
    global tag_dict, tag_finish
    list_temp = []
    index = {}
    for i in range(len(tag_list)):
        if str(tag_list[i].name[0]).isdigit():
            index[str(tag_list[i].name[0])] = i  # 名称第一位必须是数字
    for i in range(len(index)):  # 先把数字放在前面
        cnt = index[str(i)]
        list_temp.append(tag_list[cnt])
        tag_finish[tag_list[cnt].guid] = tag_dict.pop(tag_list[cnt].guid)  # 在tag_dict中删除已经用过的tag


    index = {}  # 清空
    for i in range(len(tag_list)):
        if str(tag_list[i].name[0]).isalpha():
            index[str(tag_list[i].name[0])] = i  # 名称第一位必须是字母,index的key为A-Z!!!
    for i in range(ord("A"), ord("Z")+1):  # 顺序不是1开始了，而是A开始
        if chr(i) in index.keys():
            cnt = index[chr(i)]
            list_temp.append(tag_list[cnt])
            tag_finish[tag_list[cnt].guid] = tag_dict.pop(tag_list[cnt].guid)  # 在tag_dict中删除已经用过的tag

    return list_temp

# 获取印象笔记数据
# 创建一个印象笔记client对象
client = EvernoteClient(token=auth_token, sandbox=False, china=True)
note_store = client.get_note_store()  # 通过client对象获取note_store对象

def get_evernote_data():
    global tag_dict, tag_list
    # 获取所有标签
    tag_list = note_store.listTags()
    for tag in tag_list:
        tag_dict[tag.guid] = tag


def get_tags_num():
    return str(len(tag_list))

def unique_note(notes):
    temp = {}
    for note in notes:
        if note.guid  not in temp.keys():
            temp[note.guid] = note
    notes = list(temp)

def insert_notes(tag):
    result = []
    offset = 0  # 偏移0
    max_notes = 99999
    spec = NotesMetadataResultSpec(1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0)
    updated_filter = NoteFilter(order=NoteSortOrder.UPDATED, tagGuids=[tag.guid])
    notes = note_store.findNotesMetadata(updated_filter, offset, max_notes, spec)
    if notes.notes:
        for note in notes.notes:
            node_file["id"] = gen_topic_id()
            node_file["title"] = note.title
            node_file["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + id_evernote_image
            image_dict["align"] = "left"
            node_file["image"] = copy.deepcopy(image_dict)

            node_file["href"] = "https://app.yinxiang.com/shard/s61/nl/12899539/" + note.guid
            result.append(copy.deepcopy(node_file))
    return result

# 给二级标签插子标签和所属的笔记，笔记和子标签在xmind数据结构中属于同一层级
def insert_sub2(children2, tag):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children3 = {}#copy.deepcopy(children)
    children3["attached"] = []

    if tag.guid not in tag_insert.keys():  # 防止重复插入note
        children3["attached"] = insert_notes(tag) + children3["attached"]
        tag_insert[tag.guid] = True

    # 遍历非根节点的tag，把它们插到根节点的children中
    for tag_guid in tag_dict:
        if tag_dict[tag_guid].parentGuid == tag.guid:
        # if tag_dict[tag_guid].parentGuid in tag_finish.keys(): # 若父节点是否存在才会处理；可能会先遍历到某个第三级tag，而此tag的第二级tag还未建立，则此时不做处理。一级一级的建立tag
            tag_finish[tag_guid] = tag_dict[tag_guid] # 把tag从tag_dict移入到tag_finish，建立此级的tag
            # 填充node_folder，然后插入children中，最后以该folder为root，再遍历
            node_folder["id"] = gen_topic_id()
            node_folder["title"] = tag_finish[tag_guid].name
            node_folder["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + id_evernote_image
            image_dict["align"] = "left"
            node_folder["image"] = copy.deepcopy(image_dict)

            # 给三级标签插入notes
            node_folder["children"] = insert_notes(tag_dict[tag_guid])
            # node_folder["branch"] = "folded"

            children3["attached"].append(copy.deepcopy(node_folder))
            # 其实temp还有children
    if children2["attached"]:
        children2["attached"][-1]["children"] = children3  # 把所有叶子节点，temp，插到了parent后面

# 给一级标签插子标签和所属的笔记，笔记和子标签在xmind数据结构中属于同一层级
def insert_sub(children, tag):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children2 = {}#copy.deepcopy(children)
    children2["attached"] = []

    if tag.guid not in tag_insert.keys():  # 防止重复插入parent的note
        children2["attached"] = insert_notes(tag) + children2["attached"]  # 先把A,B,C...的notes插进去
        tag_insert[tag.guid] = True

    # 遍历非根节点的tag，把它们插到根节点的children中
    for tag_guid in tag_dict:
        if tag_dict[tag_guid].parentGuid == tag.guid:
        # if tag_dict[tag_guid].parentGuid in tag_finish.keys(): # 若父节点是否存在才会处理；可能会先遍历到某个第三级tag，而此tag的第二级tag还未建立，则此时不做处理。一级一级的建立tag
            tag_finish[tag_guid] = tag_dict[tag_guid] # 把tag从tag_dict移入到tag_finish，建立此级的tag
            # 填充node_folder，然后插入children中，最后以该folder为root，再遍历
            node_folder["id"] = gen_topic_id()
            node_folder["title"] = tag_finish[tag_guid].name
            node_folder["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + id_evernote_image
            image_dict["align"] = "left"
            node_folder["image"] = copy.deepcopy(image_dict)

            node_folder["children"] = insert_sub2(children2, tag_finish[tag_guid])

            children2["attached"].append(copy.deepcopy(node_folder))  # 再插parent的子tag


        # 其实temp还有children
    children["attached"][-1]["children"] = children2  # 把所有叶子节点，temp，插到了parent后面

    # node_folder["children"] = insert_sub(children, tag_finish[tag_guid])

# 开始生成文件树
def get_json_tree(path, children):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children["attached"] = []
    # for tag_guid in tag_dict:
    #     if not tag_dict[tag_guid].parentGuid:
    #         tag_root.append(tag_dict[tag_guid])
    #         tag_finish[tag_guid] = tag_dict.pop(tag_guid)
    # tag_root = notebooks_sort(tag_root)

    # 生成根节点的json数据，并且对tag进行排序
    for tag in tag_list:
        if not tag.parentGuid:
            tag_root.append(tag)
    tag_root = tags_sort(tag_root)

    for tag in tag_root:
        node_folder["id"] = gen_topic_id()
        node_folder["title"] = tag.name
        node_folder["titleUnedited"] = True

        image_dict["src"] = "xap:resources/" + id_evernote_image
        image_dict["align"] = "left"
        node_folder["image"] = copy.deepcopy(image_dict)

        node_folder["children"] = {}

        children["attached"].append(copy.deepcopy(node_folder))
        insert_sub(children, tag)




# 创建xmind文件
def gen_xmind(xmind_filename):
    # 生成xmind文件
    zip_name = xmind_filename+".zip"
    xmind_name = xmind_filename+".xmind"

    newZip = zipfile.ZipFile(zip_name, 'w') # 新建了一个名为 new.zip 的压缩文件，并以append模式打开。
    newZip.write("evernote.png", "resources\\" + id_evernote_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。

    # 创建一个空的metadata.json文件
    metadata = open("metadata.json", 'w')
    metadata.write("{}")
    metadata.close()
    newZip.write("metadata.json")
    os.remove("metadata.json")

    # 创建的manifest.json文件
    manifest = open("manifest.json", 'w')
    manifest_info = {"file-entries": {"content.json": {}, "metadata.json": {}, "Thumbnails/thumbnail.png": {}}}  # 不带附件


    resources_info = "resources/" + id_evernote_image
    manifest_info["file-entries"][resources_info] = {}

    manifest.write(json.dumps(manifest_info))  # 将manifest_info转为json写入文件中

    manifest.close()
    newZip.write("manifest.json")
    os.remove("manifest.json")

    # 根据需求创建xmind文件内的具体内容
    newZip.write("content.json", compress_type=zipfile.ZIP_DEFLATED)
    os.remove("content.json")

    newZip.close()

    # 修改后缀名
    os.rename(zip_name, xmind_name)


# 初始化xmind的数据结构
def init_data():
    global data, node_sheet, node_file, node_folder, node_root, image_dict, children

    # 画布
    node_sheet["id"] = ""
    node_sheet["class"] = ""
    node_sheet["title"] = ""
    node_sheet["rootTopic"] = {}
    node_sheet["theme"] = {}
    node_sheet["topicPositioning"] = ""

    # 文件
    node_file["id"] = ""
    node_file["title"] = ""
    node_file["titleUnedited"] = True
    node_file["image"] = {}
    node_file["href"] = ""

    # 文件夹
    node_folder["id"] = ""
    node_folder["title"] = ""
    node_folder["titleUnedited"] = True
    node_folder["image"] = {}
    node_folder["children"] = {}

    # 根节点
    node_root["id"] = ""
    node_root["class"] = ""
    node_root["title"] = ""
    node_root["structureClass"] = ""
    node_root["children"] = {}
    node_root["extensions"] = []
    node_root["image"] = {}
    node_root["href"] = ""

    # 根节点的extensions元素数据结构
    content_list = []
    content_dict = {}
    content_dict["content"] = ""
    content_dict["name"] = ""

    extensions = []
    extensions_dict = {}
    extensions_dict["content"] = []
    extensions_dict["provider"] = ""

    # 根节点的image元素数据结构
    image_dict["src"] = ""
    image_dict["align"] = ""

    # 根节点的children元素数据结构
    children["attached"] = []

    # attached = []  # 存放的元素其实就是node_file或者node_folder
    # attached_dict = {}  # 实际就是file noe

    # 初始化node_sheet
    node_sheet["id"] = gen_topic_id()
    node_sheet["class"] = "sheet"
    node_sheet["title"] = "sheet0"
    #node_sheet["rootTopic"] = {}  # 遍历完后最后要得到的数据结构，无法初始化
    node_sheet["theme"] = theme
    node_sheet["topicPositioning"] = "fixed"

    # 初始化node_root
    node_root["id"] = gen_topic_id()  # b9aa22deba98b3b20c7ac8aca2
    node_root["class"] = "topic"
    node_root["title"] = "印象笔记"  # 此python文件所在的父目录！！！！！！！！！！！！！！！！这个路径还要看下
    node_root["structureClass"] = "org.xmind.ui.map.unbalanced"
    #node_root["children"] = {}

    # 初始化node_root的image元素
    image_dict["src"] = "xap:resources/" + id_evernote_image
    image_dict["align"] = "left"
    node_root["image"] = copy.deepcopy(image_dict)  # 一般都是folder，这里默认为folder！

    # 初始化node_root的extensions元素
    content_dict["content"] = get_tags_num() #str(get_num_nohidden("./"))  # 获取当前文件夹下非隐藏文件夹的数目！！！！！！！！！！！！！！！！这个路径还要看下
    content_dict["name"] = "right-number"
    content_list.append(content_dict)

    extensions_dict["content"] = content_list
    extensions_dict["provider"] = "org.xmind.ui.map.unbalanced"
    extensions.append(extensions_dict)

    node_root["extensions"] = extensions

    data.append(node_sheet)


if __name__ == "__main__":
    get_evernote_data()
    init_data()
    xmind_filename = "印象笔记目录"  # xmind文件的无后缀名称
    root_path = os.path.dirname(__file__)  # 获取当前python文件所在目录的绝对路径
    get_json_tree(root_path, children)
    node_root["children"] = children
    node_sheet["rootTopic"] = node_root
    # data.append(node_sheet)
    gen_json_file(data)
    gen_xmind(xmind_filename)

