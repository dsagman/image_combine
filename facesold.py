"""Take a set of image PNGs and combine their alpha channels into random faces.

All subdirectories of the current directory will be scanned for images and then combined.
Images will be added based on the alphabetic order of subdirectories.
Also scans for rare images in /Rare subdirectory
The subdirectory /Faces will not be scanned and is used for output.
"""
import os
import random
from itertools import accumulate
from more_itertools import last, nth_product
from PIL import Image
from icecream import ic     # for debugging only. can be removed

root_dir_default = os.getcwd()
rare_dir_default = '/Rare'
out_dir_default = '/Output'

rare_pct_default = 0.2     # How often to select a rare face part
num_to_make_default = 5    # How many images to output
out_file_default = 1       # 1 for screen output, 2 for file output


class FaceImage:
    def __init__(self, kind='', common=[], rare=[], output=[]):
        self.kind = kind      # kind -> face_dir items without the '/'
        self.common = common  # the common images
        self.rare = rare      # the rare images


def get_ims(directory: str):
    im_files = []
    if os.path.isdir(root_dir+directory):
        os.chdir(root_dir+directory)
        for f_name in os.listdir():
            if f_name.lower().endswith('.png'):
                im_files.append(Image.open(f_name).convert('RGBA'))
    return im_files


def set_arg(prompt: str, err_msg: str, def_val: str, test: object):
    while True:
        val = input(prompt+def_val+'\n: ') or def_val
        try:
            if test(val):
                break
            else:
                print(val+err_msg)
        except:
            print(val+err_msg)
    return val


def mkdir_if_none(directory: str):
    if not os.path.isdir(directory):
        os.mkdir(directory)


if __name__ == "__main__":

    print('I will search all subdirectories for PNG files and combine them via their alpha channel.')
    print('Images will be added based on the alphabetical order of the subdirectories.')

    # set the constants
    root_dir = set_arg(
        'What is the root directory to search for image directories? \nOr press <enter> for default: ',
        ' is not a directory.',
        root_dir_default,
        lambda x: os.path.isdir(x))
    rare_dir = set_arg(
        'What are the subdirectories holding rare images (optional)? \nNote: you can have a rare subdirectory on the root and any/all image subdirecory\nOr press <enter> for default: ',
        ' needs to be of the form /directory-name or \\directory-name.',
        rare_dir_default,
        lambda x: x[0] == '/' or x[0] == '\\')
    # need to change the out_dir check. if the directory doesn't exist, try to create it.
    out_dir = set_arg(
        'What is the subdirectory where you want the images output? \nOr press <enter> for default: ',
        ' needs to be of the form /directory-name or \\directory-name.',
        out_dir_default,
        lambda x: x[0] == '/' or x[0] == '\\')
    mkdir_if_none(root_dir+'/'+out_dir)
    rare_pct = float(set_arg(
        'What percentage of rare images do you want (0.00 to 1.00)? \nOr press <enter> for default: ',
        ' is not a number between 0 and 1.',
        str(rare_pct_default),
        lambda x: float(x) <= 1.0 and float(x) >= 0.0))
    num_to_make = int(set_arg(
        'How many images do you want? \nOr press <enter> for default: ',
        ' is not a number greater than 1.',
        str(num_to_make_default),
        lambda x: int(x) >= 1))
    out_file = int(set_arg(
        'Do you want the output to screen(1) or file(2) or both(3)? \nOr press <enter> for default: ',
        ' is not a number between 1 and 3.',
        str(out_file_default),
        lambda x: int(x) >= 1 and int(x) <= 3))
    
    print('Generating images!')

    # locate all the subdirectories, the first alphabetically can have a background
    # all the rest of the images have to be alpha channel only
    im_dirs = sorted(['/'+x for x in os.listdir(root_dir)
                     if os.path.isdir(root_dir+'/'+x) and (x != out_dir[1:])])
    face_pts = dict.fromkeys(im_dirs)

    # load all the images, but skip directories with no .PNG files
    for d in im_dirs:
        face_pts[d] = FaceImage(
            kind=d[1:], common=get_ims(d), rare=get_ims(d+rare_dir))
        if face_pts[d].common == []:
            del face_pts[d]

    # if there's a rare directory off of root_dir, keep or delete it based on random number
    if (random.random() > rare_pct) and (face_pts[rare_dir] != []):
        del face_pts[rare_dir]

    # select rare or common images and then select random items from the cross product
    ims = [face_pts[i].rare if (random.random() < rare_pct and face_pts[i].rare != []) 
          else face_pts[i].common for i in face_pts]

    ims_size = last(accumulate([len(x) for x in ims], lambda x, y: x*y))
    face_ims = list(map(lambda x: nth_product(x, *ims),
                    random.sample(range(ims_size), min(ims_size, num_to_make))))

    # combine the images
    faces = [last(accumulate(
        f, lambda im1, im2: Image.alpha_composite(im1, im2))) for f in face_ims]

    for f in faces:
        if out_file in [1,3]:
            f.show()
        if out_file in [2,3]:
            os.chdir(root_dir+'/'+out_dir)
            for i, f in enumerate(faces):
                f.save(f'Face-{i:05}.png')


# ----------------------old code------------------

    # faces = []
    # for f in face_ims:
    #     faces.append(mit.last(it.accumulate(
    #         f, lambda im1, im2: Image.alpha_composite(im1, im2))))

    # ic(ims_size, num_to_make)
#         more_itertools.nth_product(index, *args)[source]
# Equivalent to list(product(*args))[index].

# The products of args can be ordered lexicographically. nth_product() computes the product at sort position index without computing the previous products.

# >>> nth_product(8, range(2), range(2), range(2), range(2))
# (1, 0, 0, 0)

# def random_product(*args, repeat=1):
#     "Random selection from itertools.product(*args, **kwds)"
#     pools = [tuple(pool) for pool in args] * repeat
#     return tuple(map(random.choice, pools))

    # for n in range(num_to_make):
    #     for d in im_dirs:
    #         o = random.choice(face_pts[d].common)
    #         if faces[n] == 0:
    #             faces[n] = o
    #         else:
    #             faces[n] = Image.alpha_composite(faces[n], o)

    # for f in faces:
    #     f.show()

    # faces =[]
    # for h in heads:
    #     for e in eyes:
    #         h_e = Image.alpha_composite(h, e)
    #         for ht in hats:
    #             h_e_ht = Image.alpha_composite(h_e, ht)
    #             for m in mouths:
    #                 new_face = Image.alpha_composite(h_e_ht, m)
    #                 faces.append(new_face)

    # os.chdir('./Faces')
    # for i, f in enumerate(faces):
    #     f.save('Face-'+str(i)+'.png')

    # f'The number is {n:02}'

   # print(face_pts[d].kind)
    # print(face_pts[d].common)
    # print(face_pts[d].rare)

    # all_faces = it.product(*ims)
    # all_faces = it.product(*[face_pts[d].common for d in im_dirs])
    # faces = it.islice(all_faces, num_to_make)

        # faces = it.islice(all_faces, num_to_make)

        # need to change this to use nth_product. make a list of random indexes to product set
    # faces = mit.random_product(*ims, repeat=num_to_make)
    # faces = mit.chunked(faces, len(im_dirs))

    # selection = [parts_list[x].common for x in parts_list]

        # selection = []
    # for i in parts_list:
    #     n = random.random()
    #     if (n < pct) and (parts_list[i].rare != []):
    #         selection.append(parts_list[i].rare)
    #     else:
    #         selection.append(parts_list[i].common)
    # ic(selection)

    # def bias_selection(parts_list: FaceImage, pct: float):
#     [parts_list[i].rare if ((random.random()<pct) and (parts_list[i].rare!=[])) else parts_list[i].common for i in parts_list]
#     return selection

# ims = [face_pts[i].rare if (random.random()<rare_pct and face_pts[i].rare!=[]) else face_pts[i].common for i in face_pts]

# def bias_selection(parts_list: FaceImage, pct: float):
#     selection = []
#     for i in parts_list:
#         n = random.random()
#         if (n < pct) and (parts_list[i].rare != []):
#             selection.append(parts_list[i].rare)
#         else:
#             selection.append(parts_list[i].common)
#     return selection

    # ims = bias_selection(face_pts, rare_pct)


#     [parts_list[i].rare if ((random.random()<pct) and (parts_list[i].rare!=[])) else parts_list[i].common for i in parts_list]
#     return selection
