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
        self.pfN = 146       # Fundamental frequency of human speach.
        self.pf = self.pfN*2
        self.speachMinMs = 150*10
     
#        self.pi = 20
#        self.u = 0.95
#        self.p = 11
#        self.threshold = 0.4
        