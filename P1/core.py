# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 23:46:19 2019

@author: Padamban
"""

import os
import matplotlib.pyplot as plt
import simpleaudio as sa
import numpy as np
import scipy
from scipy import signal
from mpl_toolkits import mplot3d
import scipy.io.wavfile as wav
import random
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import pickle
import scipy.signal as sg


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
            span = range(d[3],d[3]+len(d[0]))  if len(d) == 4 else d[4]
            ax.plot(span, d[0], d[2], label=d[1])   
        plt.legend()
        plt.show() 
        
        
        
class Pickle:
    def __init__(self, folder, sTag='', lTag=''):
        self.folder = folder
        self.saveTag = sTag
        self.loadTag = lTag

    def path(self, name, tag=''):
      return self.folder + '/' + tag + str(name) +'.pkl'
    
    def save(self, name, data, oTag=None):
        tag = self.saveTag if  oTag==None else oTag
        pickle_out = open( self.path(name, tag) ,"wb")
        pickle.dump(data, pickle_out)
        pickle_out.close()

    def load(self, name, oTag=None):
        tag = self.loadTag if  oTag==None else oTag
        pickle_in = open(self.path(name, tag), 'rb')
        data = pickle.load(pickle_in)
        pickle_in.close()
        return data      
    
    def SaveData(self, data, oTag=None):
        self.save('raw', data.raw, oTag)
        self.save('gain', data.gain, oTag)
        self.save('pitch', data.pitch, oTag)
        self.save('power', data.power, oTag)
        self.save('lpc', data.lpc, oTag)


    def LoadData(self, oTag=None):
        data = SpeachData();        
        data.raw = self.load('raw', oTag)
        data.gain = self.load('gain', oTag)
        data.power = self.load('power', oTag)
        data.pitch = self.load('pitch', oTag)     
        data.lpc = self.load('lpc', oTag)     
        return data

    
    def SaveEncoded(self, data, oTag=None):
        self.save('binaries', data.binaries, oTag)
        self.save('maxgain', data.maxGain, oTag)


    def LoadEncoded(self, oTag=None):
        data = EncodedData();        
        data.binaries = self.load('binaries', oTag)
        data.maxGain = self.load('maxgain', oTag)   
        return data
    
    def SaveDecoded(self, data, oTag=None):
        self.save('qlpc', data.lpc, oTag)
        self.save('qpitch', data.pitch, oTag)
        self.save('qgain', data.gain, oTag)


    def LoadDecoded(self, oTag=None):
        data = DecodedData();        
        data.lpc = self.load('qlpc', oTag)
        data.gain = self.load('qgain', oTag)   
        data.pitch = self.load('qpitch', oTag)  
        return data

    def getFileSize(self, file):
        return os.path.getsize(file)



class Math:
    
    def autocorrelation(self, x) : 
        xp = x-np.mean(x)
        f = np.fft.fft(xp)
        p = np.array([np.real(v)**2+np.imag(v)**2 for v in f])        
        pi = np.fft.ifft(p)
        c = np.real(pi)[:int(x.size/2)]/np.sum(xp**2)
        return c
       
    def normalize(self, d):
        return 2*(d - np.min(d))/np.ptp(d)-1
   
     
class SpeachData:
    raw=[]
    pitch=[]
    power=[]
    lpc=[]
    gain=[]     
    

     
class EncodedData:
    binaries = ''
    maxGain = 0

class DecodedData:
    lpc  = []
    gain = []
    pitch = []



    