"""
通过 项目根目录的绝对路径和 相对于项目根目录的相对路径进行拼接,得到绝对路径
"""
#1.获取项目的根目录绝对路径
import os
print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
root_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#2.写个方法,将项目根目录的绝对路径和项目的相对路径进行拼接,得到文件的绝对路径,项目根目录的绝对路径+文件相对项目的路径
def get_file_path(relative_path,root_dir=root_dir):
    #把两个路径join,连到一块
    abs_path =os.path.join(root_dir,relative_path)
    print(abs_path)
    return abs_path

if __name__ == '__main__':
    get_file_path("common/path_utils.py")