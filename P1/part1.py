# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 00:13:53 2019

@author: Padamban
"""

from core import np
from core import Printer, SpeachData, AudioManager, Math, Pickle
from config import PrintConfig, Params, Paths


class PreProcessing:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.data = SpeachData();
        self.p = Printer(1);
        self.am = AudioManager();
        self.m = Math();
        self.pickle = Pickle(self.paths.pickle, sTag=self.paths.tag1);

        self.data.raw = self.am.readAudio(self.paths.file);
        

    
    def filterPitch(self,p):
        for i, v in enumerate(p):
            if i==0 or i==len(p)-1:
                continue
            if p[i-1]==0 and v!=0 and p[i+1]==0:
                p[i]=0
            elif p[i-1]!=0 and v==0 and p[i+1]!=0:
                p[i] = np.mean([p[i-1], p[i+1]])
        return p        
    
    
    def run(self, save=1):

        stp =  self.param.step
        for step, idx in enumerate(range(0,len(self.data.raw),stp)):
            
            trama  = self.data.raw[idx:idx+self.param.pf]
            tramaAC = self.m.autocorrelation(trama) 
            power = np.sum(self.data.raw[idx:idx+stp]**2)/self.param.step
            pitch = 0
            if(max(tramaAC[self.param.pi:self.param.pfN])>self.param.threshold):
                pitch = np.argmax(tramaAC[self.param.pi:self.param.pfN])+self.param.pi
                        
            self.data.pitch.append(pitch)
            self.data.power.append(power)

            if (step in self.pc.stepInto1 or step in self.pc.stepIntoAll):
                self.p.prnt(2, str(step)+"------------------ start", 1)
                self.p.prnt(4, str("In First Cycle"), 1)
                self.p.plot([(self.data.raw, 'speech', 'c', 0),(trama, 'trama', 'r',  idx)])
                self.p.plot([(trama, 'trama', 'c',  0)])
                self.p.plot([(tramaAC, 'tramaAC','c', 0)])
                self.p.plot([(tramaAC, 'tramaAC','c', 0)])

                self.p.prnt(2, str(step)+"------------------ end", 1)
                if self.pc.stop1:
                    input("   ...")
                    
        self.data.pitch = self.filterPitch(self.data.pitch)

    
        if save:
            self.pickle.SaveData(self.data)
        


PreProcessing().run()