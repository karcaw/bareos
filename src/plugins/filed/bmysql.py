#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bareosfd import *
from bareos_fd_consts import *
from io import open
from os import O_WRONLY, O_CREAT

from BareosFdMySQLclass import *
from BareosFdWrapper import *

def load_bareos_plugin(context, plugindef):
    DebugMessage(context, 100, "------ Plugin loader called with " + plugindef + "\n");
    BareosFdWrapper.bareos_fd_plugin_object = BareosFdMySQLclass (context, plugindef);
    return bRCs['bRC_OK'];

# the rest is done in the Plugin module
