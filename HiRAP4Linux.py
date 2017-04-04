# -*- coding:UTF-8 -*-
import time
import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree
from skimage import io, color


def expand_colorspace_cv(img_str):
    '''
    :param img_str: the string of picture dir || picture list
    :return: the list of expanded colorspace picture list
    '''
    t = time.time()
    if isinstance(img_str, str):
        print('├┄ Convert classified picture [' + img_str + ']')
        RGB = io.imread(img_str)
        LAB = color.rgb2lab(RGB)
        print('│   ├┄ lab converted')
        HSV = color.rgb2hsv(RGB)
        print('│   ├┄ hsv converted')
        XYZ = color.rgb2xyz(RGB)
        print('│   ├┄ xyz converted')
        (height, width, dimen) = RGB.shape
        rgb = RGB.reshape(height * width, dimen);del RGB
        lab = LAB.reshape(height * width, dimen);del LAB
        hsv = HSV.reshape(height * width, dimen);del HSV
        xyz = XYZ.reshape(height * width, dimen);del XYZ
        print('│   └┄ reshaped')
        img_size = (height, width)
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1);del rgb, lab, hsv, xyz
        print('│        ├┄ Combined = ' + str(round(sys.getsizeof(expand) / 8 / 1024 / 1024, 3)) + ' MB')
        print('│        └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
        return expand, img_size
    else:
        RGB = img_str.reshape(1, img_str.shape[0], 3)
        LAB = color.rgb2lab(RGB)
        print('│   │   ├┄ lab converted')
        HSV = color.rgb2hsv(RGB)
        print('│   │   ├┄ hsv converted')
        XYZ = color.rgb2xyz(RGB)
        print('│   │   ├┄ xyz converted')
        rgb = img_str;del RGB
        lab = LAB[0];del LAB
        hsv = HSV[0];del HSV
        xyz = XYZ[0];del XYZ
        print('│   │   └┄ reshaped')
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1);del rgb, lab, hsv, xyz
        print('│   │        ├┄ Combined = ' + str(round(sys.getsizeof(expand)/8/1024/1024, 3)) + ' MB')
        print('│   │        └┄ Cost ' + str(round(time.time() - t, 3)) + ' s')
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


def tree_result(training_list, classify_img, img_size):
    '''
    :param training_list: [('kind1':training_data_dir), ('kind2':training_data_dir),...]
    :param classify_img: 
    :param img_size:
    :return: 
    '''
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
    try:
        classified_result = clf.predict(classify_img)  # classify new pixels
    except MemoryError:
        classified_result = np.empty((0, 1))
        for sub_array in np.vsplit(classify_img, len(classify_img)):
            classified_sub_result = clf.predict(sub_array)
            print(classified_sub_result.shape)
            classified_result = np.concatenate((classified_result, classified_sub_result))
    print('│   └┄ Image successfully classified')
    image_out = classified_result.reshape(img_size)
    return image_out

if __name__ == '__main__':
    print('================Program start==================\n'
          '■ Main')
    Image2Classify = input('├┄ Please input the image path which need to classify: ')
    try:
        if Image2Classify == 't':    # text mode open
            Image2Classify = 'preview.tif'
            Img_prepare, Img_size = expand_colorspace_cv(Image2Classify)
            training_tuple = [('0', "SandTD170104.png"), ('1', "Tree&ShrubTD170104.png")]
        else:
            Img_prepare, Img_size = expand_colorspace_cv(Image2Classify)
            training_tuple = training_kind_generate()
        Image_out = tree_result(training_tuple, Img_prepare, Img_size)
        plt.imsave('Linux_result.png', Image_out, cmap=plt.cm.gray)
        print('└┄ Result image wrote')
    except FileNotFoundError:
        print('File not found')

    input('Press <Enter> to quit')
