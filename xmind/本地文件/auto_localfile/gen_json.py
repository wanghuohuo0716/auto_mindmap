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
id_pdf_image = "efae58ef600e7c1a7238e5be7bc30bf8575d06d7dc2f65b2dbc47a321236c78a.png"
id_evernote_image = "54755c7f4a9991774d371bc72d6b735778bedada4ea38af8e2c8cfecc32269b0.png"
id_xmind_image = "4ad6e2ee8a1fef693e63b9c2292d5f9099d34b0d03878bca2663afac31e27654.png"
id_folder_image = "037079d4a7b058a9f0b299a4311bf71d8ecd9b85d9d55f3b8e9176236c768d0d.png"
id_jianshu_image = "e3f75f2dacefc698033566b17f8d4933173f5a0ea5c5c7c3b125e62c39834037.png"
id_word_image = "a888d2db0002ce58fc70a40eb2154aea62048fb3ebd77aafcbd8d25bdddafd94.png"
id_ppt_image = "143e261d7339292e4bb670298d5108a52916f8679900477ba2d218122e0f4d3e.png"
id_json_image = "df1ee8c39bbb91b8f614bee10eed009425c3a9537975be6a25102d5639d04f8e.png"

# 把图片的id放入字典
type_dict= {}
type_dict["pdf"] = id_pdf_image
type_dict["evernote"] = id_evernote_image
type_dict["xmind"] = id_xmind_image
type_dict["folder"] = id_folder_image
type_dict["jianshu"] = id_jianshu_image
type_dict["word"] = id_word_image
type_dict["ppt"] = id_ppt_image
type_dict["json"] = id_json_image


# 全局变量，xmind的数据结构
data = []
node_sheet = {}
node_root = {}
children = {}
node_file = {}
node_folder = {}
image_dict = {}


# 获取指定目录下的文件夹和文件数目，不包括临时文件和隐藏文件
def get_num_nohidden(path):
    file_list = []
    for f in os.listdir(path):
        if not f.startswith('.') and not f.startswith('~$$'):
            file_list.append(f)
    return len(file_list)


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


def get_file_type_id(dir_or_file):
    if os.path.isdir(dir_or_file):  # 先判断是否是文件夹
        return id_folder_image

    file_type = os.path.splitext(dir_or_file)[-1][1:]
    if file_type in type_dict.keys():
        return type_dict[file_type]
    else:
        return id_pdf_image  # 这里暂时用pdf来返回，要修改！！！！！！！！！！！！！！！！！！！！！！！！！！


# 把data写入content.json文件
def gen_json_file(data):
    json_str = json.dumps(data)
    filename = "content.json"
    json_file = open(filename, 'w')
    json_file.write(json_str)
    json_file.close()


def get_file_folder_list(path):
    file_folder_list = []
    for f in os.listdir(path):
        if not f.startswith('.') and not f.startswith('~$$'):
            file_folder_list.append(f)
    return file_folder_list


# 开始生成文件树
def get_json_tree(path, children):
    children["attached"] = []
    dir_or_files = get_file_folder_list(path)
    for dir_or_file in dir_or_files:
        dir_or_file_path = path + '/' + dir_or_file  # 拼接成绝对路径
        if os.path.isdir(dir_or_file_path):
            # 填充node_folder，然后插入children中，最后以该folder为root，再遍历
            node_folder["id"] = gen_topic_id()
            node_folder["title"] = dir_or_file
            node_folder["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + get_file_type_id(dir_or_file_path)
            image_dict["align"] = "left"
            node_folder["image"] = copy.deepcopy(image_dict)

            get_json_tree(dir_or_file_path, node_folder["children"])  # 填充children
            children["attached"].append(copy.deepcopy(node_folder))
        else:
            # 填充node_file，然后插入children中
            node_file["id"] = gen_topic_id()
            node_file["title"] = os.path.splitext(dir_or_file)[0]  # 文件名，不含拓展名
            node_file["titleUnedited"] = True

            image_dict["src"] = "xap:resources/" + get_file_type_id(dir_or_file)
            image_dict["align"] = "left"
            node_file["image"] = copy.deepcopy(image_dict)

            node_file["href"] = dir_or_file_path
            children["attached"].append(copy.deepcopy(node_file))  # 插入children中


# 创建xmind文件
def gen_xmind(xmind_filename):
    # 生成xmind文件
    zip_name = xmind_filename+".zip"
    xmind_name = xmind_filename+".xmind"

    newZip = zipfile.ZipFile(zip_name, 'w') # 新建了一个名为 new.zip 的压缩文件，并以append模式打开。
    newZip.write("pdf.png", "resources\\" + id_pdf_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("ppt.png", "resources\\" + id_ppt_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("evernote.png", "resources\\" + id_evernote_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("folder.png", "resources\\" + id_folder_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("jianshu.png", "resources\\" + id_jianshu_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("word.png", "resources\\" + id_word_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("xmind.png", "resources\\" + id_xmind_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。
    newZip.write("json.png", "resources\\" + id_json_image, compress_type=zipfile.ZIP_DEFLATED) # 用 ZipFile 对象的 write() 方法添加文件到压缩包中，该方法的第一个参数为需要添加进去的文件名，第二个参数为压缩算法，通常使用如上代码中的 ZIP_DEFLATED 即可。

    # 创建一个空的metadata.json文件
    metadata = open("metadata.json", 'w')
    metadata.write("{}")
    metadata.close()
    newZip.write("metadata.json")
    os.remove("metadata.json")

    # 创建的manifest.json文件
    manifest = open("manifest.json", 'w')
    manifest_info = {"file-entries": {"content.json": {}, "metadata.json": {}, "Thumbnails/thumbnail.png": {}}}  # 不带附件
    resources_info = "resources/" + id_pdf_image  # 带上附件，pdf图片
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_ppt_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_evernote_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_folder_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_jianshu_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_word_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_xmind_image
    manifest_info["file-entries"][resources_info] = {}

    resources_info = "resources/" + id_json_image
    manifest_info["file-entries"][resources_info] = {}

    manifest.write(json.dumps(manifest_info))  # 将manifest_info转为json写入文件中

    manifest.close()
    newZip.write("manifest.json")
    os.remove("manifest.json")

    # 根据需求创建xmind文件内的具体内容
    newZip.write("content.json", compress_type=zipfile.ZIP_DEFLATED)
	
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
    node_root["title"] = os.path.dirname(__file__).split('/')[-1]  # 此python文件所在的父目录！！！！！！！！！！！！！！！！这个路径还要看下
    node_root["structureClass"] = "org.xmind.ui.map.unbalanced"
    #node_root["children"] = {}

    # 初始化node_root的image元素
    image_dict["src"] = "xap:resources/" + id_folder_image
    image_dict["align"] = "left"
    node_root["image"] = copy.deepcopy(image_dict)  # 一般都是folder，这里默认为folder！

    # 初始化node_root的extensions元素
    content_dict["content"] = str(get_num_nohidden("./"))  # 获取当前文件夹下非隐藏文件夹的数目！！！！！！！！！！！！！！！！这个路径还要看下
    content_dict["name"] = "right-number"
    content_list.append(content_dict)

    extensions_dict["content"] = content_list
    extensions_dict["provider"] = "org.xmind.ui.map.unbalanced"
    extensions.append(extensions_dict)

    node_root["extensions"] = extensions

    data.append(node_sheet)


if __name__ == "__main__":
    init_data()
    xmind_filename = "localfilemap"  # xmind文件的无后缀名称
    root_path = os.path.dirname(__file__)  # 获取当前python文件所在目录的绝对路径
    get_json_tree(root_path, children)
    node_root["children"] = children
    node_sheet["rootTopic"] = node_root
    # data.append(node_sheet)
    gen_json_file(data)
    gen_xmind(xmind_filename)
