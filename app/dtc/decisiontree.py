import time
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from PIL import Image
from sklearn import tree
from skimage import io, color
from collections import Counter


def expand_colorspace_cv(img_str, printonoff='on'):
    # param:
    #     img_str: the string of picture dir || picture list
    #     printonoff: print process in console whether or not
    # return: the list of expanded colorspace picture list
    t = time.time()
    if isinstance(img_str, str):
        if printonoff == 'on': print('|--- Convert classified picture [' + img_str + ']')
        RGB = io.imread(img_str)
        if RGB.shape[2] == 4:    # exists alpha layer
            RGB = RGB[:,:,0:3]
        LAB = color.rgb2lab(RGB)
        if printonoff == 'on': print('|   |--- lab converted')
        HSV = color.rgb2hsv(RGB)
        if printonoff == 'on': print('|   |--- hsv converted')
        XYZ = color.rgb2xyz(RGB)
        if printonoff == 'on': print('|   |--- xyz converted')
        (height, width, dimen) = RGB.shape
        rgb = RGB.reshape(height * width, dimen); del RGB
        lab = LAB.reshape(height * width, dimen); del LAB
        hsv = HSV.reshape(height * width, dimen); del HSV
        xyz = XYZ.reshape(height * width, dimen); del XYZ
        if printonoff == 'on': print('|   ^--- reshaped')
        img_size = (height, width)
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1);del rgb, lab, hsv, xyz
        if printonoff == 'on':
            print('|        |--- Combined = ' + str(round(sys.getsizeof(expand) / 8 / 1024 / 1024, 3)) + ' MB')
        if printonoff == 'on': print('|        ^--- Cost ' + str(round(time.time() - t, 3)) + ' s')
        return expand, img_size
    else:
        RGB = img_str.reshape(1, img_str.shape[0], 3)
        LAB = color.rgb2lab(RGB)
        if printonoff == 'on': print('|   |   |--- lab converted')
        HSV = color.rgb2hsv(RGB)
        if printonoff == 'on': print('|   |   |--- hsv converted')
        XYZ = color.rgb2xyz(RGB)
        if printonoff == 'on': print('|   |   |--- xyz converted')
        rgb = img_str; del RGB
        lab = LAB[0]; del LAB
        hsv = HSV[0]; del HSV
        xyz = XYZ[0]; del XYZ
        if printonoff == 'on': print('|   |   ^--- reshaped')
        expand = np.concatenate((rgb, lab, hsv, xyz), axis=1); del rgb, lab, hsv, xyz
        if printonoff == 'on':
            print('|   |        |--- Combined = ' + str(round(sys.getsizeof(expand)/8/1024/1024, 3)) + ' MB')
        if printonoff == 'on': print('|   |        ^--- Cost ' + str(round(time.time() - t, 3)) + ' s')
        return expand


def training_data_generate(train_str, printonoff='on'):
    t = time.time()
    if printonoff == 'on': print('|   |--- Convert [' + train_str + '] to Training data')
    train = io.imread(train_str)
    (height, width, dimen) = train.shape
    if dimen != 3 and dimen != 4:
        if printonoff == 'on': print('[Error]: picture layer uncommon')
        if printonoff == 'on': print('================Program end==================')
        return []
    else:
        if dimen == 4:
            train = train.reshape(height * width, dimen)
            train_index = np.nonzero(train[:, 3])   # select alpha layer != 0 as training data
            train_select = train[train_index][:, 0:3]
        if dimen == 3:
            if printonoff == 'on': print('[Warning]: no alpha layer, count background as training data')
            train_select = train.reshape(height * width, dimen)
        if printonoff == 'on': print('|   |   |--- Unused pixels deleted')
        if printonoff == 'on': print('|   |   |   ^--- Cost ' + str(round(time.time() - t, 3)) + ' s')
        train_array = expand_colorspace_cv(train_select)
        return train_array


def training_kind_generate(interact, printonoff='on'):
    '''
    interact = 'on'
    else
    interact = (train_imgs, train_img_kinds)
    '''
    if printonoff == 'on': print('|--- Training data list generating')
    if printonoff == 'on': print('|   |--- Input training data')
    container = []
    if interact=='on':
        add_field = 'y'
        while add_field == 'y':
            kind_name = input('|   |   |--- Please input kind name:')
            kind_dir = input('|   |   |--- Please input picture (training data) path for this kind: ')
            container.append((kind_name, kind_dir))
            if len(container) >= 2:
                add_field = input('|   |   |--- Add more new kind? (y/n)')
            if printonoff == 'on': print('|   |   ^--- Training data list generated')
    else:   # interact = [train_dirs, train_kinds]
        (train_dirs, train_kinds) = interact
        for (train_dir, train_kind) in zip(train_dirs, train_kinds):
            container.append((train_kind, train_dir))
    return container


def tree_train(training_list, printonoff='on'):
    # :param training_list: [('kind1',training_data_dir), ('kind2',training_data_dir),...]
    # :param classify_img:
    # :param img_size:
    # :return:
    training_data = np.empty((0, 12))    # training data
    training_result = []   # training data results
    for kind_couple in training_list:
        training_data_temp = training_data_generate(kind_couple[1])
        training_data = np.vstack((training_data, training_data_temp))
        pixel_color_id = int(kind_couple[0])
        training_result += len(training_data_temp) * [pixel_color_id]
        if printonoff == 'on':print('|   ^--- Training data preparing accomplished')
    if printonoff == 'on': print('|--- Decision Tree Model application')
    clf = tree.DecisionTreeClassifier()  # import tree generator
    if printonoff == 'on': print('|   |--- Build Decision Tree model')
    clf = clf.fit(training_data, training_result)  # training tress
    if printonoff == 'on': print('|   |--- Decision Tree model generated')
    return clf


def tree_apply(clf, classify_img, img_size, printonoff='on'):
    classified_result = clf.predict(classify_img)  # classify new pixels
    if printonoff == 'on': print('|   ^--- Image successfully classified')
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


def classify_img(imgdir, folder_name, training_tuple, printonoff='on'):
    pic_list = slice_picture(imgdir, folder_name)
    cls_name_list = []
    decision_tree = tree_train(training_tuple)
    vfc = Counter({})
    # deal with each sliced image separately
    for i, img_dir in enumerate(pic_list):
        cls_name = folder_name + '/cls' + str(i) + '.jpg'
        cls_name_list.append(cls_name)
        img_prepare, img_size = expand_colorspace_cv(img_dir, printonoff='off')
        image_out = tree_apply(decision_tree, img_prepare, img_size, printonoff='off')
        plt.imsave(cls_name, image_out, cmap=plt.cm.Accent)
        # count number
        unique, counts = np.unique(image_out, return_counts=True)
        vfc = vfc + Counter(dict(zip(unique, counts)))
        del img_prepare, image_out
        percent = round(i / len(pic_list) * 100, 2)
        if printonoff == 'on': print('\r|   |' + '='*round(percent/2) + '>'+ ' '*round(50-percent/2) + '|' + str(percent) + '%', end="")
    total = sum(vfc.values())
    for i in vfc:
        vfc[i] = str(round(vfc[i] / total * 100, 2))
    if printonoff == 'on': print('\r|   |' + '='*49 + '>|100%')
    return cls_name_list, img_size, dict(vfc)


def image_combination(cls_name_list, img_size, combine_dir='..'):
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
    new_im.save(combine_dir + '/result.png')


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

def decision_tree_classifier(classify_img_dirs, training_img_dirs, training_img_kinds, project_dir):
    '''
    :param classify_img_dirs: string from DTC_Project.db, such as '[file/dir/image/name.jpg]'
    :param training_img_dirs: string from DTC_Project.db, such as '[file/dir/image/name1.jpg, file/dir/image/name2.jpg]'
    :param training_img_kinds: string from DTC_Project.db, such as '[0,1]'
    :param project_dir: string from DTC_Project.db, such as '[project/file/dir]'
    :return coverage: string to DTC_Project.db, such as '{'0':0.236; '1':0.546; '2':0.345}'
    '''
    image2classify = eval(classify_img_dirs)[0]
    training_dirs = eval(training_img_dirs)
    training_kinds = eval(training_img_kinds)
    folder_name = str(time.time())
    full_folder_name = project_dir + '/' + folder_name
    training_tuple = training_kind_generate(interact=[training_dirs, training_kinds])
    (cls_list, img_size, vfc) = classify_img(image2classify, full_folder_name, training_tuple)
    image_combination(cls_list, img_size, combine_dir=project_dir)
    delete_file_folder(full_folder_name)
    print('^--- Result image wrote')
    return vfc


if __name__ == '__main__':
    print('================Program start==================\n'+
          '[] Main')
    Image2Classify = input('|--- Please input the image path which need to classify: ')
    if os.path.exists(Image2Classify):
        t = time.time()
        folder_name = str(time.time())
        training_tuple = training_kind_generate(interact='on')
        (cls_list, img_size, vfc) = classify_img(Image2Classify, folder_name, training_tuple)
        image_combination(cls_list, img_size)
        print('|   ^--- Coverage=' + str(vfc))
        delete_file_folder(folder_name)
        print('|   ^--- Cost ' + str(round(time.time() - t, 3)) + ' s')
        print('^--- Result image wrote')
    else:
        print('File not found')

    input('Press <Enter> to quit')