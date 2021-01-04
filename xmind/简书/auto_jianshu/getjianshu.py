import requests
import re
import zipfile
import os
import json
import hashlib
import time
import copy

# 实例化创建加密对象，必须是全局变量，否则hash值会重复
hash_encoder = hashlib.sha3_256()

# 常量定义
theme = {"id":"508b628c872bcdebad590b9d62","importantTopic":{"type":"topic","properties":{"fo:font-weight":"bold","fo:color":"#434B54","svg:fill":"#62FFFF"}},"minorTopic":{"type":"topic","properties":{"fo:font-weight":"bold","fo:color":"#434B54","svg:fill":"#FAFF7E"}},"expiredTopic":{"type":"topic","properties":{"fo:font-style":"italic","fo:text-decoration":" line-through"}},"centralTopic":{"properties":{"line-width":"3pt","line-color":"#434B54","fo:color":"#434B54","svg:fill":"none","fo:font-size":"24pt","fo:font-family":"Montserrat","fo:font-weight":"700","fo:font-style":"normal"},"styleId":"53e97033f92b8bd3f4c78979c3","type":"topic"},"boundary":{"properties":{"fo:font-family":"Montserrat","fo:font-weight":"normal","line-color":"#FB5151","svg:fill":"#FCDBDA","fo:color":"#FFFFFF"},"styleId":"49a959f26a7811630973d8e2df","type":"boundary"},"floatingTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"normal","line-color":"#434B54","line-class":"org.xmind.branchConnection.curve","line-width":"1pt"},"styleId":"1a1aa0882bb9bcb55bc7889a27","type":"topic"},"subTopic":{"properties":{"fo:font-weight":"normal","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-size":"14pt","shape-class":"org.xmind.topicShape.roundedRect","fo:text-align":"left","border-line-width":"0","line-class":"org.xmind.branchConnection.curve"},"styleId":"719abce18ea9cf241bdeea7366","type":"topic"},"mainTopic":{"properties":{"fo:font-weight":"500","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-style":"normal","fo:font-size":"18pt","svg:fill":"none","line-width":"1pt","fo:text-align":"center","border-line-width":"3pt","line-class":"org.xmind.branchConnection.curve"},"styleId":"0bca341d27dbabf4d116fb3b67","type":"topic"},"calloutTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"normal"},"styleId":"78aa5283453b7fd33b3388bb57","type":"topic"},"summary":{"properties":{"line-color":"#FB5151"},"styleId":"b03a96d54f89a5862ed289bf3b","type":"summary"},"summaryTopic":{"properties":{"svg:fill":"#FB5151","border-line-width":"0","fo:font-family":"Montserrat","fo:font-weight":"400","fo:font-style":"normal","line-class":"org.xmind.branchConnection.curve"},"styleId":"e64865a4408a28ebcf9ca9c7f5","type":"topic"},"relationship":{"properties":{"arrow-begin-class":"org.xmind.arrowShape.dot","line-pattern":"dot","line-color":"#FB5151","fo:color":"#434B54","fo:font-family":"Montserrat","fo:font-weight":"normal","line-width":"3pt"},"styleId":"93c86baff3d8ee1505ed887476","type":"relationship"}}

id_jianshu_image = "e3f75f2dacefc698033566b17f8d4933173f5a0ea5c5c7c3b125e62c39834037.png"


# 把图片的id放入字典
type_dict= {}

type_dict["jianshu"] = id_jianshu_image

#
notebook_num = 0

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


def gen_image_id():
    randomcode = str(time.time() * 10000000)
    hash_encoder = hashlib.sha3_256()        #实例化创建加密对象
    hash_encoder.update(randomcode.encode("utf-8"))    #传入待加密的字符串
    return hash_encoder.hexdigest()


# 把data写入content.json文件
def gen_json_file(data):
    json_str = json.dumps(data)
    filename = "content.json"
    json_file = open(filename, 'w')
    json_file.write(json_str)
    json_file.close()


# 创建xmind文件
def gen_xmind(xmind_filename):
    # 生成xmind文件
    zip_name = xmind_filename+".zip"
    xmind_name = xmind_filename+".xmind"

    newZip = zipfile.ZipFile(zip_name, 'w') # 新建了一个名为 new.zip 的压缩文件，并以append模式打开。
    newZip.write("jianshu.png", "resources\\" + id_jianshu_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。

    # 创建一个空的metadata.json文件
    metadata = open("metadata.json", 'w')
    metadata.write("{}")
    metadata.close()
    newZip.write("metadata.json")
    os.remove("metadata.json")

    # 创建的manifest.json文件
    manifest = open("manifest.json", 'w')
    manifest_info = {"file-entries": {"content.json": {}, "metadata.json": {}, "Thumbnails/thumbnail.png": {}}}  # 不带附件

    resources_info = "resources/" + id_jianshu_image
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
    global data, node_sheet, node_file, node_folder, node_root, image_dict, children, notebook_num

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
    node_root["title"] = "简书"
    node_root["structureClass"] = "org.xmind.ui.map.unbalanced"
    #node_root["children"] = {}

    # 初始化node_root的image元素
    image_dict["src"] = "xap:resources/" + id_jianshu_image
    image_dict["align"] = "left"
    node_root["image"] = copy.deepcopy(image_dict)  # 一般都是folder，这里默认为folder！

    # 初始化node_root的extensions元素
    content_dict["content"] = notebook_num
    content_dict["name"] = "right-number"
    content_list.append(content_dict)

    extensions_dict["content"] = content_list
    extensions_dict["provider"] = "org.xmind.ui.map.unbalanced"
    extensions.append(extensions_dict)

    node_root["extensions"] = extensions

    data.append(node_sheet)


class JianshuSpider(object):
    def __init__(self):
        self.url = 'https://www.jianshu.com/users/5700d98f44e1/collections_and_notebooks?slug=5700d98f44e1' # 文集的url，详见印象笔记的request库内容
        self.page = 10                               # 爬取的页数
        self.notebook_num = 0
        self.notebooks = []
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
        self.children = {}
        self.children["attached"] = []

    # 获取notebook的链接和数目
    def get_home_list(self):
        home_code = requests.get(self.url, headers=self.headers)
        home_data = json.loads(home_code.text)
        self.notebook_num = len(home_data["notebooks"])
        self.notebooks = home_data["notebooks"]
        self.notes = []

    def get_notebook_num(self):
        return self.notebook_num

    # 获取特定notebook下所有的note名称和链接
    def get_content(self):
        self.children["attached"][-1]["children"] = {}
        home_code = requests.get(self.url, headers=self.headers)
        home_data = home_code.text
        token = re.findall('<meta name="csrf-token" content="(.*?)" />', home_data)[0]
        id = re.findall('data-note-id="(\d*)"', home_data, re.S)  # 获取第一页所有文章的ID
        home_page_article = self.parsing_codes(home_data)  # 使用正则处理请求，获取notebook中所有的文章的标题、链接，放入到home_page_article中
        self.notes = []  # 每个notebook都先清空
        self.notes = self.notes + home_page_article

        # 传入所需的token、id、爬取页数后，开始加载Ajax（爬取下一页）
        self.get_next_content(token, id, self.page)
        self.inser_note(self.notes)

    def get_next_content(self, token, id, pages):
        # 使用for循环
        for page in range(2, pages+1):
            # 准备请求头部
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
                "X-INFINITESCROLL": "true",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF-Token": token
            }
            # 需要提交的表单
            params = {
                "page": page,              # 页数
                "seen_snote_ids[]": id     # 帖子的ID
            }

            resp = requests.get(self.url, headers=headers, params=params)
            article = self.parsing_codes(resp.text)
            self.notes = self.notes + article

    def inser_note(self, article):  # article是个list
        if not article:
            return 0
        children2 = {}
        children2["attached"] = []
        for i in article:
            node_file= {}
            node_file["id"] = gen_topic_id()
            node_file["title"] = i[1]
            node_file["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + id_jianshu_image
            image_dict["align"] = "left"
            node_file["image"] = copy.deepcopy(image_dict)

            node_file["href"] ="https://www.jianshu.com" + i[0]
            children2["attached"].append(copy.deepcopy(node_file))
        self.children["attached"][-1]["children"] = children2

    def parsing_codes(self, data):
        article = re.findall('<a class="title" target="_blank" href="(.*?)">(.*?)</a>', data, re.S)
        return article

    # 开始生成文件树
    def get_json_tree(self):
        for notebook in self.notebooks:
            self.url = "https://www.jianshu.com/nb/" + str(notebook["id"])
            # 先生存notebook的folder节点
            node_folder = {}
            node_folder["id"] = gen_topic_id()
            node_folder["title"] = notebook["name"]
            node_folder["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + id_jianshu_image
            image_dict["align"] = "left"
            node_folder["image"] = copy.deepcopy(image_dict)
            self.children["attached"].append(copy.deepcopy(node_folder))
            self.get_content()


if __name__ == "__main__":
    jianshu = JianshuSpider()
    jianshu.get_home_list()
    notebook_num = jianshu.get_notebook_num()
    init_data()
    xmind_filename = "简书目录"  # xmind文件的无后缀名称
    jianshu.get_json_tree()
    node_root["children"] = jianshu.children
    node_sheet["rootTopic"] = node_root
    gen_json_file(data)
    gen_xmind(xmind_filename)





