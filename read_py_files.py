import os

def read_py_files():
    # 获取当前目录
    current_dir = os.getcwd()
    
    # 用于存储所有内容的列表
    all_content = []
    
    # 遍历所有目录和文件
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.py'):
                # 获取完整的文件路径
                file_path = os.path.join(root, file)
                # 获取相对路径
                rel_path = os.path.relpath(file_path, current_dir)
                
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 添加路径和内容到列表
                    all_content.append(f"路径：{rel_path}\n")
                    all_content.append(f"内容：\n{content}\n")
                    all_content.append("-" * 80 + "\n")  # 分隔线
                except Exception as e:
                    print(f"读取文件 {rel_path} 时出错：{str(e)}")
    
    # 将内容写入txt文件
    with open('python_files_content.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_content))

if __name__ == "__main__":
    read_py_files()
    print("文件内容已保存到 python_files_content.txt") 