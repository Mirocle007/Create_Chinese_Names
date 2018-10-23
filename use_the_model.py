# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import scipy.io as iso
from utils import print_sample
from create_Chinese_names import sample, preprocess, DataSet

if __name__ == "__main__":
    char_to_ix, ix_to_char = preprocess(data_set=DataSet)
    # 下载参数并使用模型
    while True:
        first_name = input("请输入姓：").strip()
        if len(first_name) == 1 or len(first_name) == 2:
            break
        else:
            print("姓氏只能一个字或者两个字，请重新输入！！")
    data = iso.loadmat("parameters.mat")
    parameters = {}
    for x in data:
        if x[0] == "W" or x[0] == "b":
            parameters[x] = data[x]
    for _ in range(7):
        sampled_indices = sample(parameters, char_to_ix,
                                 first_name, seed=random.randint(1, 100))
        print_sample(sampled_indices, ix_to_char)
