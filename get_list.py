import os
 
path = '/Users/liyun/Desktop/video_pics'  # 要遍历的目录
txt_path = '/Users/liyun/Desktop/video.txt'
# with open(txt_path, 'w') as f:
#   for root, dirs, names in os.walk(path):
#     for name in names:
#         ext = os.path.splitext(name)[1]  # 获取后缀名
#         if ext == '.mp4':
#             video_path = os.path.join(root, name)  # mp4文件原始地址
#             video_name = name.split('.')[0]
#             f.write(video_name+'\t'+video_path+'\n')



with open(txt_path, 'w') as f:
    video_list = os.listdir(path)
    video_list = sorted(video_list)  
    video_list = [item for item in video_list if item != '.DS_Store']
    for name in video_list:
        video_path = os.path.join(path, name)
        f.write(name+'\t'+video_path+'\n')  

# print(path_list)
