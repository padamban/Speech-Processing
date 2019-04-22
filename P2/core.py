# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 23:04:41 2019

@author: Padamban
"""


import numpy as np
import pandas as pd

import scipy.io.wavfile as wav
import simpleaudio as sa
import matplotlib.pyplot as plt
import os
from scipy import signal


class AudioManager:
    
    def readAudio(self, file):
        fs, raw_audio = wav.read(file)       
        raw = np.array([raw_audio]).astype(float)[0]
        return raw       
        
    def playOriginalAudio(self,file):
        wave_obj = sa.WaveObject.from_wave_file(file)
        play_obj = wave_obj.play()
        play_obj.wait_done()
            
    def playSyntesizedAudio(self, syntesized):
        Sn = syntesized
        ply = Sn * 32767 / max(abs(Sn))
        ply = ply.astype(np.int16)
        play_obj = sa.play_buffer(ply, 1, 2, 8000)
        play_obj.wait_done()
    
    def processFileName(self, file):
        name = os.path.splitext(file)[0]
        return [name[4], name[5], name[0:3]]
        
    def scanDirectory(self, folder):
        paths = []
        i = 0
        for r, d, f in os.walk(folder):
            for file in f:
                label = self.processFileName(file)
                paths.append([i, label, os.path.join(r, file)])
                i = i + 1
        return paths
                

        

class Printer:
    
    def __init__(self, enable):
        self.enable = enable
        
    def prnt(self, tab, text, enable=0):
        indent = "|"+ " "*int(tab) 
        if self.enable or enable:
            print(indent+text)
            
    def plot(self, data, sep=False):
        fig, ax1 = plt.subplots()
        for i, d in enumerate(data):
            ax = ax1.twinx() if sep and i else ax1 
            span = range(d[3],d[3]+len(d[0]))  if len(d) == 4 else self.getSpan(d[0], d[4])
            ax.plot(span, d[0], d[2], label=d[1])   
        plt.legend()
        plt.show() 
    
    def getSpan(self, data, step):
        return np.arange(len(data))*step
    
    def plotSpeech(self, raw, speech, idx):
        for i, s in enumerate(speech):
            c = 'g' if i>0 else 'r'
            self.plot([ (raw, 'raw', 'y',  0), (s, 'speech ', c,  idx[i]) ], 1)
        
    def imShow(self, I, title=''):
        size = 7
        fig = plt.figure(figsize=(size,size))
        ax = fig.add_subplot(111)
        ax.set_title(title)
        plt.imshow(I)

    
        
class Math:
    
    def autocorrelation(self, x) : 
        xp = x-np.mean(x)
        f = np.fft.fft(xp)
        p = np.array([np.real(v)**2+np.imag(v)**2 for v in f])        
        pi = np.fft.ifft(p)
        c = np.real(pi)[:int(x.size/2)]/np.sum(xp**2)
        return c
       
    def normalize(self, d, span=[0, 1]):
        delta = span[1]-span[0]
        bottom = span[0]
        return delta*(d - np.min(d))/np.ptp(d)-bottom
      
    def dirac(self, length, val=1 ):
        return signal.unit_impulse(int(length))*val
    
    
    def movingAvg(self, data, N=5):
        dataMA = []
        for i, d in enumerate(data):
            if i < N:
                dataMA.append(data[i])
            else:    
                ma = np.sum(data[i-N:i])/N
                dataMA.append(ma)
                dataMA[i-int(2*N/3)] = ma
        return dataMA
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        