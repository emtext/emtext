#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Prepare Artificial Neural Network functions.
"""

import pickle 
import os

import numpy as np
import neurolab as nl

ann_model = None

def _train(lines):
    """
    Inner function: Input lines of training data, and return trained Artificial Neural Network model.
    
    Param:
    * lines: ((density, text_len, code_len, density_pre_line, text_len_pre_line, code_len_pre_line, density_next_line, text_len_next_line, code_len_next_line, decision), (...), ...)
    """
    filter_too_large = lambda x: x if x <= 1000 else 1000
    input_data = [map(filter_too_large, line[:9]) for line in lines]
    target_data = [[line[9]] for line in lines]

    net = nl.net.newff([[0.0, 1.0], [0.0, 1000.0], [0.0, 1000.0], [0.0, 1.0], [0.0, 1000.0], [0.0, 1000.0], [0.0, 1.0], [0.0, 1000.0], [0.0, 1000.0]], [10, 1])
    err = net.train(input_data, target_data, show=15)

    return net
    
def train(lines):
    """
    Input lines of training data, and return trained Artificial Neural Network model.
    
    Param:
    * lines: ((density, text_len, code_len, density_pre_line, text_len_pre_line, code_len_pre_line, density_next_line, text_len_next_line, code_len_next_line, decision), (...), ...)
    """
    net_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ann.pickle')
    net = _train(lines)
    pickle.dump(net, open(net_path, 'wb'))
    return net

def _get_ann():
    """
    Prepare pickled ann model.
    """
    net_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'ann.pickle')
    if os.path.exists(net_path):
        net = pickle.load(open(net_path, 'rb'))
        global ann_model
        ann_model = net
    else:
        print 'You must train the model first!'

def check(line):
    """
    Check whether the line is part of main text.
    """
    if ann_model == None:
        _get_ann()
    if ann_model == None:
        return None
    guess = ann_model.sim([line])
    if guess >= 0.5:
        return True
    else:
        return False

