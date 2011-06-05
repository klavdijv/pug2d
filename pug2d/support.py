# -*- coding: utf-8 -*-

class AttrDict(dict):
    '''A dictionary with attribute access to its items'''
    
    def __getattr__(self, name):
        return self.__getitem__(name)
    
    def __setattr__(self, name, value):
        super(AttrDict, self).__setattr__(name, value)
        self.__setitem__(name ,value)
    
    def __delattr__(self, name):
        self.__delitem__(name)
