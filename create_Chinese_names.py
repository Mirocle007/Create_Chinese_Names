# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 导入相关模块
import numpy as np
import random
from random import shuffle
from scipy import io
import scipy.io as iso
from utils import *

# 全局变量，名字库的文件名
DataSet = "name.txt"


def preprocess(data_set=DataSet):
    """
    对名字库进行预处理. 

    参数:
    dataset:文字库的文件名，默认为全局变量

    返回值：
    char_to_ix：一个字典，字典的键为名字库中所有的字，值为其编码，实现由字得到编码
    ix_to_char：一个字典，字典的键为名字库中字的编码，值为其对应的字，实现从编码得到字
    """
    with open(data_set, 'r', encoding="gbk") as f:
        data = f.read()
    chars = list(set(data))  # 取出名字库中所有的字，包括换行符
    data_size, vocab_size = len(data), len(chars)  # 计算总的字数和不重复的字数（包括换行符）
    # print('名字库中总共有%d个字（含换行符），不重复的字一共有%d个' %
    #       (data_size, vocab_size))
    char_to_ix = {ch: i for i, ch in enumerate(sorted(chars))}
    ix_to_char = {i: ch for i, ch in enumerate(sorted(chars))}
    return char_to_ix, ix_to_char


def clip(gradients, maximum):
    '''
    防止出现梯度爆炸的情况，使梯度处于-maximum到maximum.

    参数:
    gradients：一个包括网络中所有相关偏导数的字典（梯度字典）,键分别为："dWaa", "dWax", "dWya", "db", "dby"
    maximum：大于此值则被设置为此值，小于此值则被设置为-maximum

    返回值: 
    gradients：修改了的梯度字典
    '''
    for gradient in gradients:
        gradients[gradient] = gradients[
            gradient].clip(min=-maximum, max=maximum)
    return gradients


def sample(parameters, char_to_ix, first_name, seed):
    """
    对网络的输出根据输出的概率分布来进行采样，采集一组名字，直到名字超过两个字或者以换行符结尾

    参数:
    parameters：一个包括网络中相关权重参数的字典，包括Waa, Wax, Wya, by, and b. 
    char_to_ix：一个字典，字典的键为名字库中所有的字，值为其编码，实现由字得到编码
    first_name:用户输入的姓氏
    seed：固定随机数生成器的种子

    Returns:
    indices：一个包括了得到的名字序列的编码的列表
    """

    # 将网络的权重和偏置参数解析出来
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters[
        'Wax'], parameters['Wya'], parameters['by'], parameters['b']
    vocab_size = by.shape[0]
    n_a = Waa.shape[1]

    # 初始化第一个时间步的x输入为(vocab_size, 1)的0数组
    x = np.zeros((vocab_size, 1))

    # 初始化网络的初始激活值为(n_a, 1)的0数组
    a_prev = np.zeros((n_a, 1))

    indices = []  # 创建空列表，用于存放序列的编码（索引）

    idx = -1  # 初始化索引为-1，每次检测到新的字符时更新

    counter = 0  # 对indices中的字符进行计数
    newline_character = char_to_ix['\n']  # 获取换行符的编码

    # 固定姓氏，但是也第一个时间步也运行了一次
    a = np.tanh(np.dot(Wax, x) + np.dot(Waa, a_prev) + b)  # 用于下一个时间步的输入激活值
    idx = char_to_ix[first_name[0]]
    indices.append(idx)  # 获取姓氏的编码，并添加到indices中
    x = np.zeros((vocab_size, 1))
    x[idx] = 1  # 将姓氏作为独热编码，作为第二个时间步的输入
    a_prev = a
    # 考虑到有可能有复姓的情况，如果是复姓，则再运行一次时间步，并将输出设置为复姓的第二个字
    if len(first_name) == 2:
        a = np.tanh(np.dot(Wax, x) + np.dot(Waa, a_prev) + b)
        idx = char_to_ix[first_name[1]]
        indices.append(idx)
        x = np.zeros((vocab_size, 1))
        x[idx] = 1
        a_prev = a

    # 继续运行后面的时间步，直到遇到换行符或者输出两个字
    while (idx != newline_character and counter != 2):

        a = np.tanh(np.dot(Wax, x) + np.dot(Waa, a_prev) + b)
        z = np.dot(Wya, a) + by
        y = softmax(z)
        np.random.seed(counter + seed)

        # 根据该时间步输出中各个文字的概率来进行采样，采集到对应的编码
        idx = np.random.choice(list(range(len(y))), p=y.ravel())
        indices.append(idx)
        x = np.zeros((vocab_size, 1))
        x[idx] = 1
        a_prev = a
        seed += 1
        counter += 1

    if counter == 2:
        indices.append(char_to_ix['\n'])
    return indices


def optimize(X, Y, a_prev, parameters, learning_rate=0.01):
    """
    优化训练模型.

    参数:
    X：输入，名字库中的姓名对应的编码列表
    Y：输出，名字库中的姓名对应列表，比X早一个时间步
    a_prev：第一个时间步输入的激活值
    parameters：网络的参数字典，包括：
                        Wax:输入的权重矩阵，尺寸为(n_a, n_x)
                        Waa：输入激活值的权重矩阵，尺寸为(n_a, n_a)
                        Wya：输出的权重矩阵，尺寸为(n_y, n_a)
                        b：输入的偏置，尺寸为(n_a, 1)
                        by：输出的偏置，尺寸为(n_y, 1)
    learning_rate：学习速率

    返回值:
    loss：损失函数的值
    gradients：包含梯度的字典（与parameters对应），包括：dWax，dWaa，dWya，db，dby
    a[len(X)-1]：最后一个时间步的输入激活值
    """

    # 正向传播
    loss, cache = rnn_forward(X, Y, a_prev, parameters)

    # 反向传播
    gradients, a = rnn_backward(X, Y, parameters, cache)

    # 防止梯度爆炸
    gradients = clip(gradients, 5)

    # 更新参数
    parameters = update_parameters(parameters, gradients, learning_rate)

    return loss, gradients, a[len(X) - 1], parameters


def model(examples, ix_to_char, char_to_ix, num_iterations=1500000, n_a=4, names=7, vocab_size=5880):
    """
    总模型，训练模型，训练过程中也产生部分名字. 

    参数:
    examples：名字库中名字形成的列表
    char_to_ix：一个字典，字典的键为名字库中所有的字，值为其编码，实现由字得到编码
    ix_to_char：一个字典，字典的键为名字库中字的编码，值为其对应的字，实现从编码得到字
    num_iterations:迭代次数
    n_a：激活值的尺寸
    names:迭代过程中，每次打印名字时打印名字的数量
    vocab_size:名字库中字符的数量

    Returns:
    parameters：训练后得到的参数
    """

    # 进行时为了训练过程也能看到，实际对网络的参数训练没有影响
    while True:
        first_name = input("请输入姓：").strip()
        if len(first_name) == 1 or len(first_name) == 2:
            break
        else:
            print("姓氏只能一个字或者两个字，请重新输入！！")

    n_x, n_y = vocab_size, vocab_size

    # 初始化参数
    parameters = initialize_parameters(n_a, n_x, n_y)

    # 初始化损失函数
    loss = get_initial_loss(vocab_size, names)

    # 初始化输入激活值
    a_prev = np.zeros((n_a, 1))

    # 循环迭代
    for j in range(num_iterations):
        # 迭代一次，训练一个样本，防止，迭代次数过多，超出了examples的索引
        index = j % len(examples)
        X = [None] + [char_to_ix[ch]
                      for ch in examples[index]]
        Y = X[1:] + [char_to_ix["\n"]]

        # 调用上面写的optimize函数
        curr_loss, gradients, a_prev, parameters = optimize(
            X, Y, a_prev, parameters, learning_rate=0.1)

        # 移动平均，加速迭代的过程
        loss = smooth(loss, curr_loss)

        # 每2000次迭代，打印一次名字（names个）
        if j % 2000 == 0:

            print('Iteration: %d, Loss: %f' % (j, loss) + '\n')
            seed = 0
            for name in range(names):
                sampled_indices = sample(
                    parameters, char_to_ix, first_name, seed)
                print_sample(sampled_indices, ix_to_char)
                seed += 1
            print('\n')
    return parameters


if __name__ == "__main__":
    char_to_ix, ix_to_char = preprocess(data_set=DataSet)
    with open(DataSet) as f:
        examples = f.readlines()
    examples = [x.lower().strip() for x in examples]
    shuffle(examples)
    parameters = model(examples, ix_to_char, char_to_ix)
    io.savemat("parameters.mat", parameters)


# 下载参数并使用模型
# 使用use_the_model.py
