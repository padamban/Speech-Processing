# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 23:02:17 2019

@author: Padamban
"""

class Paths:
    folderTrain = 'X:\ISEL\PF\Speech-Processing\P2\CorpusDigitos\\training examples'
    folderTest = 'X:\ISEL\PF\Speech-Processing\P2\CorpusDigitos\\test examples'
    pickle = 'X:/ISEL/PF/Speech-Processing/P2/Pickle'



    
class Params: 
    
    def __init__(self):
        self.step = 80
        self.window = 190;
        self.p = 3; # order of the autocorelation

        