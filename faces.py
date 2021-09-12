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

