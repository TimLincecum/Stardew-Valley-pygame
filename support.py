from os import walk
import pygame

def import_folder(path) :
    surface_list = []

    for folder_name,sub_folder,img_files in walk(path) : # 遍历指定路径及其子文件夹下的文件
        # print(img_files)
        # print('qwe')
        for image in img_files : # 遍历当前文件夹下的所有文件
            # print(image)
            full_path = path + '/' + image# 构建完整路径
            # print(full_path)
            # 加载并转换图像表面，加入表面列表
            image_surf = pygame.image.load(full_path).convert_alpha() # ?
            surface_list.append(image_surf)

    return surface_list