import requests
import re
import zipfile
import os
import json
import copy

# 全局变量，xmind的数据结构
children = []
node_file = {}
node_folder = {}
node_root = {}
JSON = {}
JSON["data"] = {}

# 把data写入content.json文件
def gen_json_file(data):
    json_str = json.dumps(data)
    filename = "content.json"
    json_file = open(filename, 'w')
    json_file.write(json_str)
    json_file.close()


# 创建nbmxd文件
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
    node_root["text"] = "简书"
    node_root["expandState"] = "expand"
    node_root["font-family"] = "黑体, SimHei"
    node_root["font-weight"] = "bold"

    JSON["children"] = []

    JSON["template"] = "right"
    JSON["theme"] = "classic"
    JSON["version"] = "1.3.5"

    # 文件
    node_file["data"] = {}
    node_file["data"]["text"] = "简书"
    node_file["data"]["connectColor"] = "#000000"
    node_file["data"]["connect-color"] = "#000000"  # 黑色
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

class JianshuSpider(object):
    def __init__(self):
        self.url = 'https://www.jianshu.com/users/5700d98f44e1/collections_and_notebooks?slug=5700d98f44e1' # 文集的url，详见印象笔记的request库内容
        self.page = 10                               # 爬取的页数
        self.notebooks = []
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}
        self.children = []
        self.notes = []

    # 获取notebook的链接和数目
    def get_home_list(self):
        home_code = requests.get(self.url, headers=self.headers)
        home_data = json.loads(home_code.text)
        self.notebooks = home_data["notebooks"]

    # 获取特定notebook下所有的note名称和链接
    def get_content(self):
        self.children[-1]["children"] = []
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
        children2 = []
        for i in article:
            node_file= {}
            node_file["data"] = {}
            node_file["data"]["text"] = i[1]
            node_file["data"]["connectColor"] = "#000000"
            node_file["data"]["connect-color"] = "#000000"
            node_file["data"]["hyperlink"] ="https://www.jianshu.com" + i[0]
            children2.append(copy.deepcopy(node_file))
        self.children[-1]["children"] = copy.deepcopy(children2)

    def parsing_codes(self, data):
        article = re.findall('<a class="title" target="_blank" href="(.*?)">(.*?)</a>', data, re.S)
        return article

    # 开始生成文件树
    def get_json_tree(self):
        for notebook in self.notebooks:
            self.url = "https://www.jianshu.com/nb/" + str(notebook["id"])
            # 先生存notebook的folder节点
            node_folder = {}
            node_folder["data"] = {}
            node_folder["data"]["text"] = notebook["name"]
            node_folder["data"]["connectColor"] = "#000000"
            node_folder["data"]["connect-color"] = "#000000"

            self.children.append(copy.deepcopy(node_folder))
            self.get_content()


if __name__ == "__main__":
    jianshu = JianshuSpider()
    jianshu.get_home_list()
    init_data()
    xmind_filename = "简书目录"  # xmind文件的无后缀名称
    jianshu.get_json_tree()
    JSON["children"] = jianshu.children
    gen_json_file(JSON)
    gen_xmind(xmind_filename)





