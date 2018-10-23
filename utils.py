# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import numpy as np


def smooth(loss, cur_loss):
    return loss * 0.999 + cur_loss * 0.001


def print_sample(sample_ix, ix_to_char):
    txt = ''.join(ix_to_char[ix] for ix in sample_ix)
    txt = txt[0].upper() + txt[1:]
    print('%s' % (txt, ), end='')


def get_initial_loss(vocab_size, seq_length):
    return -np.log(1.0 / vocab_size) * seq_length


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)


def initialize_parameters(n_a, n_x, n_y):
    """
    初始化参数

    """
    np.random.seed(1)
    Wax = np.random.randn(n_a, n_x) * 0.01
    Waa = np.random.randn(n_a, n_a) * 0.01
    Wya = np.random.randn(n_y, n_a) * 0.01
    b = np.zeros((n_a, 1))
    by = np.zeros((n_y, 1))

    parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "b": b, "by": by}

    return parameters


def rnn_step_forward(parameters, a_prev, x):
    """
    执行单个时间步正向传播
    """
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters[
        'Wax'], parameters['Wya'], parameters['by'], parameters['b']
    a_next = np.tanh(np.dot(Wax, x) + np.dot(Waa, a_prev) + b)

    p_t = softmax(np.dot(Wya, a_next) + by)

    return a_next, p_t


def rnn_step_backward(dy, gradients, parameters, x, a, a_prev):
    """
    执行单个时间步反向传播
    """
    gradients['dWya'] += np.dot(dy, a.T)
    gradients['dby'] += dy
    da = np.dot(parameters['Wya'].T, dy) + \
        gradients['da_next']
    daraw = (1 - a * a) * da
    gradients['db'] += daraw
    gradients['dWax'] += np.dot(daraw, x.T)
    gradients['dWaa'] += np.dot(daraw, a_prev.T)
    gradients['da_next'] = np.dot(parameters['Waa'].T, daraw)
    return gradients


def update_parameters(parameters, gradients, lr):
    """
    执行参数更新
    """
    parameters['Wax'] += -lr * gradients['dWax']
    parameters['Waa'] += -lr * gradients['dWaa']
    parameters['Wya'] += -lr * gradients['dWya']
    parameters['b'] += -lr * gradients['db']
    parameters['by'] += -lr * gradients['dby']
    return parameters


def rnn_forward(X, Y, a0, parameters, vocab_size=5880):
    """
    RNN正向传播过程
    """
    x, a, y_hat = {}, {}, {}
    a[-1] = np.copy(a0)
    loss = 0
    for t in range(len(X)):
        x[t] = np.zeros((vocab_size, 1))
        if (X[t] != None):
            x[t][X[t]] = 1
        # 调用单个时间步的正向传播
        a[t], y_hat[t] = rnn_step_forward(parameters, a[t - 1], x[t])
        loss -= np.log(y_hat[t][Y[t], 0])
    cache = (y_hat, a, x)
    return loss, cache


def rnn_backward(X, Y, parameters, cache):
    """
    RNN反向传播
    """
    gradients = {}
    (y_hat, a, x) = cache
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters[
        'Wax'], parameters['Wya'], parameters['by'], parameters['b']

    gradients['dWax'], gradients['dWaa'], gradients[
        'dWya'] = np.zeros_like(Wax), np.zeros_like(Waa), np.zeros_like(Wya)
    gradients['db'], gradients['dby'] = np.zeros_like(b), np.zeros_like(by)
    gradients['da_next'] = np.zeros_like(a[0])

    for t in reversed(range(len(X))):
        dy = np.copy(y_hat[t])
        dy[Y[t]] -= 1
        # 执行单个反向传播时间步
        gradients = rnn_step_backward(
            dy, gradients, parameters, x[t], a[t], a[t - 1])
    return gradients, a
