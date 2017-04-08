# -*- coding:UTF-8 -*-
import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from PIL import Image
from sklearn import tree
from skimage import io, color


def expand_colorspace_cv(img_str, printonff='on'):
    # param:
    #     img_str: the string of picture dir || picture list
    #     printonoff: print process in console whether or not
    # return: the list of expanded colorspace picture list
    t = time.time()
    if isinstance(img_str, str):
        if printonff == 'on': print('├┄ Convert classified picture [' + img_str + ']')
        RGB = io.imread(img_str)
        LAB = color.rgb2lab(RGB)
        if printonff == 'on': print('│   ├┄ lab converted')
        HSV = color.rgb2hsv(RGB)
        if printonff == 'on': print('│   ├┄ hsv converted')
        XYZ = color.rgb2xyz(RGB)
        if printonff == 'on': print('│   ├┄ xyz converted')
        (height, width, dimen) = RGB.shape
        rgb = RGB.reshape(height * width, dimen); del RGB
        lab = LAB.reshape(height * width, dimen); del LAB
        hsv = HSV.reshape(height * width, dimen); del HSV
        xyz = XYZ.reshape(height * width, dimen); del XYZ
        if printonff == 'on': print('│   └┄ reshaped')
        img_size = (height, width)
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1);del rgb, lab, hsv, xyz
        if printonff == 'on':
            print('│        ├┄ Combined = ' + str(round(sys.getsizeof(expand) / 8 / 1024 / 1024, 3)) + ' MB')
        if printonff == 'on': print('│        └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
        return expand, img_size
    else:
        RGB = img_str.reshape(1, img_str.shape[0], 3)
        LAB = color.rgb2lab(RGB)
        if printonff == 'on': print('│   │   ├┄ lab converted')
        HSV = color.rgb2hsv(RGB)
        if printonff == 'on': print('│   │   ├┄ hsv converted')
        XYZ = color.rgb2xyz(RGB)
        if printonff == 'on': print('│   │   ├┄ xyz converted')
        rgb = img_str; del RGB
        lab = LAB[0]; del LAB
        hsv = HSV[0]; del HSV
        xyz = XYZ[0]; del XYZ
        if printonff == 'on': print('│   │   └┄ reshaped')
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1); del rgb, lab, hsv, xyz
        if printonff == 'on':
            print('│   │        ├┄ Combined = ' + str(round(sys.getsizeof(expand)/8/1024/1024, 3)) + ' MB')
        if printonff == 'on': print('│   │        └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
        return expand


def training_data_generate(train_str):
    t = time.time()
    print('│   ├┄ Convert [' + train_str + '] to Training data')
    train = io.imread(train_str)
    (height, width, dimen) = train.shape
    if dimen == 4:
        train = train.reshape(height * width, dimen)
        train_index = np.nonzero(train[:, 3])
        train_select = train[train_index][:, 0:3]
        print('│   │   ├┄ Unused pixels deleted')
        print('│   │   │   └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
        train_array = expand_colorspace_cv(train_select)
        return train_array
    else:
        print('training image should have alpha layer')
        print('================Program end==================')
        return []


def training_kind_generate():
    print('├┄ Training data list generating')
    print('│   ├┄ Input training data')
    container = []
    add_field = 'y'
    while add_field == 'y':
        kind_name = input('│   │   ├┄ Please input kind name:')
        kind_dir = input('│   │   ├┄ Please input picture (training data) path for this kind: ')
        container.append((kind_name, kind_dir))
        if len(container) >= 2:
            add_field = input('│   │   ├┄ Add more new kind? (y/n)')
    print('│   │   └┄ Training data list generated')
    return container


def tree_train(training_list):
    # :param training_list: [('kind1':training_data_dir), ('kind2':training_data_dir),...]
    # :param classify_img:
    # :param img_size:
    # :return:
    training_data = np.empty((0, 12))    # training data
    training_result = []   # training data results
    kind_list = []
    for i, kind_couple in enumerate(training_list):
        kind_list.append(kind_couple[0])
        training_data_temp = training_data_generate(kind_couple[1])
        training_data = np.vstack((training_data, training_data_temp))
        training_result += len(training_data_temp) * [i]
    print('│   └┄ Training data preparing accomplished')
    print('├┄ Decision Tree Model application')
    clf = tree.DecisionTreeClassifier()  # import tree generator
    print('│   ├┄ Build Decision Tree model')
    clf = clf.fit(training_data, training_result)  # training tress
    print('│   ├┄ Decision Tree model generated')
    return clf


def tree_apply(clf, classify_img, img_size, printonoff='on'):
    classified_result = clf.predict(classify_img)  # classify new pixels
    if printonoff == 'on': print('│   └┄ Image successfully classified')
    image_out = classified_result.reshape(img_size)
    return image_out


def slice_picture(img_str, folder_name):
    im = Image.open(img_str)
    (w, h) = im.size
    if os.path.exists(folder_name) == False:
        os.mkdir(folder_name)
    if w * h <= 1500 * 1500:
        img_str_list = [img_str]
    else:
        num = ceil(w * h / (1500 * 1500))
        divide_list_st = [i * round(h / num) for i in range(num)]
        divide_list_ed = [(i+1) * round(h / num) for i in range(num-1)]
        divide_list_ed.append(h)
        i = 0
        img_str_list = []
        for st, ed in zip(divide_list_st, divide_list_ed):
            pic_name = folder_name + '/' + str(i) + img_str[-4:]
            img_str_list.append(pic_name)
            im.crop((0, st, w, ed)).save(pic_name)
            i += 1
    del im
    return img_str_list


def classify_img(imgdir, folder_name):
    pic_list = slice_picture(imgdir, folder_name)
    cls_name_list = []
    training_tuple = training_kind_generate()
    decision_tree = tree_train(training_tuple)
    # deal with each sliced image separately
    for i, img_dir in enumerate(pic_list):
        cls_name = folder_name + '/cls' + str(i) + '.jpg'
        cls_name_list.append(cls_name)
        img_prepare, img_size = expand_colorspace_cv(img_dir, printonff='off')
        image_out = tree_apply(decision_tree, img_prepare, img_size, printonoff='off')
        plt.imsave(cls_name, image_out, cmap=plt.cm.gray)
        del img_prepare, image_out
        percent = round(i / len(pic_list) * 100, 2)
        print('\r│   │' + '='*round(percent/2) + '>'+ ' '*round(50-percent/2) + '│' + str(percent) + '%', end="")
    print('\r│   │' + '='*49 + '>│100%')
    return cls_name_list, img_size


def image_combination(cls_name_list, img_size):
    images = map(Image.open, cls_name_list)
    widths, heights = zip(*(i.size for i in images))
    width = max(widths)
    sum_height = sum(heights)
    new_im = Image.new('RGBA', (width, sum_height))
    x_offset = 0
    for cls in cls_name_list:
        im = Image.open(cls)
        new_im.paste(im, (0, x_offset))
        x_offset += im.size[1]
    new_im.save('Linux_result.png')


def delete_file_folder(src):
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc = os.path.join(src, item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

if __name__ == '__main__':
    print('================Program start==================\n'
          '■ Main')
    Image2Classify = input('├┄ Please input the image path which need to classify: ')
    if os.path.exists(Image2Classify):
        t = time.time()
        folder_name = str(time.time())
        (cls_list, img_size) = classify_img(Image2Classify, folder_name)
        image_combination(cls_list, img_size)
        delete_file_folder(folder_name)
        print('│   └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
        print('└┄ Result image wrote')
    else:
        print('File not found')

    input('Press <Enter> to quit')
