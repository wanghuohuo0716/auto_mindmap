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

# 全局变量，xmind的数据结构
children = []
node_file = {}
node_folder = {}
node_root = {}
JSON = {}
JSON["data"] = {}

# 全局变量，印象笔记数据结构
tag_list = []  # 所有tag
tag_dict = {}  # 未用的tag
tag_finish = {}  # 用过的tag
tag_root = []  # 存放根节点的tag
tag_insert = {}

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
            node_file= {}
            node_file["data"] = {}
            node_file["data"]["text"] = note.title
            node_file["data"]["connectColor"] = "#DE4F41"
            node_file["data"]["connect-color"] = "#DE4F41"
            node_file["data"]["hyperlink"] = "https://app.yinxiang.com/shard/s61/nl/12899539/" + note.guid

            result.append(copy.deepcopy(node_file))
    return result

# 给二级标签插子标签和所属的笔记，笔记和子标签在xmind数据结构中属于同一层级
def insert_sub2(children2, tag):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children3 = []#copy.deepcopy(children)

    if tag.guid not in tag_insert.keys():  # 防止重复插入note
        children3 = insert_notes(tag) + children3
        tag_insert[tag.guid] = True

    # 遍历非根节点的tag，把它们插到根节点的children中
    for tag_guid in tag_dict:
        if tag_dict[tag_guid].parentGuid == tag.guid:
            tag_finish[tag_guid] = tag_dict[tag_guid] # 把tag从tag_dict移入到tag_finish，建立此级的tag
            # 填充node_folder，然后插入children中，最后以该folder为root，再遍历
            node_folder = {}
            node_folder["data"] = {}
            node_folder["data"]["text"] = tag_finish[tag_guid].name
            node_folder["data"]["connectColor"] = "#DE4F41"
            node_folder["data"]["connect-color"] = "#DE4F41"

            # 给三级标签插入notes
            node_folder["children"] = insert_notes(tag_dict[tag_guid])
            children3.append(copy.deepcopy(node_folder))

    if children2:
        children2[-1]["children"] = children3  # 把所有叶子节点，temp，插到了parent后面

# 给一级标签插子标签和所属的笔记，笔记和子标签在xmind数据结构中属于同一层级
def insert_sub(children, tag):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children2 = []

    if tag.guid not in tag_insert.keys():  # 防止重复插入parent的note
        children2 = insert_notes(tag) + children2  # 先把A,B,C...的notes插进去
        tag_insert[tag.guid] = True

    # 遍历非根节点的tag，把它们插到根节点的children中
    for tag_guid in tag_dict:
        if tag_dict[tag_guid].parentGuid == tag.guid:
        # if tag_dict[tag_guid].parentGuid in tag_finish.keys(): # 若父节点是否存在才会处理；可能会先遍历到某个第三级tag，而此tag的第二级tag还未建立，则此时不做处理。一级一级的建立tag
            tag_finish[tag_guid] = tag_dict[tag_guid] # 把tag从tag_dict移入到tag_finish，建立此级的tag
            # 填充node_folder，然后插入children中，最后以该folder为root，再遍历

            node_folder = {}
            node_folder["data"] = {}
            node_folder["data"]["text"] = tag_finish[tag_guid].name
            node_folder["data"]["connectColor"] = "#DE4F41"
            node_folder["data"]["connect-color"] = "#DE4F41"
            children2.append(copy.deepcopy(node_folder))  # 再插parent的子tag,要先插folder，否则-1索引的不是标签而是note！！！

            insert_sub2(children2, tag_finish[tag_guid])

    children[-1]["children"] = children2  # 把所有叶子节点，temp，插到了parent后面


# 开始生成文件树
def get_json_tree(path, children):
    global tag_finish, tag_dict, tag_list, tag_root, tag_insert
    children = []
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
        node_folder = {}
        node_folder["data"] = {}
        node_folder["data"]["text"] = tag.name
        node_folder["data"]["connectColor"] = "#DE4F41"
        node_folder["data"]["connect-color"] = "#DE4F41"

        node_folder["children"] = []

        children.append(copy.deepcopy(node_folder))
        insert_sub(children, tag)
    return children

# 创建xmind文件
def gen_xmind(xmind_filename):
    # 生成xmind文件
    zip_name = xmind_filename+".zip"
    xmind_name = xmind_filename+".nbmx"

    newZip = zipfile.ZipFile(zip_name, 'w') # 新建了一个名为 new.zip 的压缩文件，并以append模式打开。

    # 根据需求创建xmind文件内的具体内容
    newZip.write("content.json", compress_type=zipfile.ZIP_DEFLATED)
	os.remove("content.json")
    newZip.close()

    # 修改后缀名
    os.rename(zip_name, xmind_name)


# 初始化xmind的数据结构
def init_data():
    global JSON, node_file, node_folder

    # root data
    node_root["text"] = "印象笔记"
    node_root["expandState"] = "expand"
    node_root["font-family"] = "黑体, SimHei"
    node_root["font-weight"] = "bold"

    JSON["children"] = []

    JSON["template"] = "right"
    JSON["theme"] = "classic"
    JSON["version"] = "1.3.5"

    # 文件
    node_file["data"] = {}
    node_file["data"]["text"] = "印象笔记"
    node_file["data"]["connectColor"] = "#DE4F41"
    node_file["data"]["connect-color"] = "#DE4F41"  # 黑色
    node_file["data"]["hyperlink"] = "https://www.jianshu.com/nb/45821676"

    # 文件夹
    node_folder["data"] = {}
    node_folder["children"] = []

    JSON["data"] = node_root

    # children.append(copy.deepcopy(node_folder))
    # for i in range(5):
    #     node_file["data"]["text"] = "简书" + str(i)
    #     children.append(copy.deepcopy(node_file))
    #
    # node_folder["data"] = node_file["data"]
    # node_folder["children"] = children
    #
    # JSON["children"].append(node_folder)


if __name__ == "__main__":
    get_evernote_data()
    init_data()
    xmind_filename = "印象笔记目录"  # xmind文件的无后缀名称
    root_path = os.path.dirname(__file__)  # 获取当前python文件所在目录的绝对路径
    children = get_json_tree(root_path, children)
    JSON["children"] = children
    # data.append(node_sheet)
    gen_json_file(JSON)
    gen_xmind(xmind_filename)

