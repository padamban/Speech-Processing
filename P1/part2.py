# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 12:41:29 2019

@author: Padamban
"""


from core import np, scipy
from core import Printer, SpeachData, AudioManager, Math, Pickle
from config import PrintConfig, Params, Paths



class LpcProcessing:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.p = Printer(1);
        self.am = AudioManager();
        self.m = Math();
        self.pickle = Pickle(self.paths.pickle, lTag=self.paths.tag1, sTag=self.paths.tag2);
        
        self.data = self.pickle.LoadData();
    
    
    def calculateLpcCoefs(self, data):
        toep = scipy.linalg.toeplitz(data[0:-1])
        a = np.linalg.inv(toep).dot(-data[1:])
        return a
    
    
    def calculateGain(self, s, Rs0, lpcCoef):
        Rs = self.m.autocorrelation(s)[1:self.param.p]
        G = np.sqrt((1 + lpcCoef.dot(Rs))*Rs0)        
        return G
    
    def voicedPreprocesing(self,data):
        # High pass filter
        dLen = len(data) 
        spp = data[1:dLen] - self.param.u * data[0:dLen-1] 
        spp = np.insert(spp, 0, spp[0] )
        return spp
 
    
    def run(self, save=1):
        stp =  self.param.step
 

        for step, idx in enumerate(range(0,len(self.data.raw),stp)):
            pitch = self.data.pitch[step]
            trama  = self.data.raw[idx:idx+self.param.pf]            
            h = np.zeros(self.param.pf)

            tramaHp = trama
            if pitch:
                tramaHp = self.voicedPreprocesing(trama)
            ham = np.hamming(len(tramaHp))
            tramaHpHam = tramaHp*ham
            tramaHpHamAc = self.m.autocorrelation(tramaHpHam)
            tramaHpHamAcP=tramaHpHamAc[0:self.param.p]
            lpcCoefs = self.calculateLpcCoefs(tramaHpHamAcP)
            energy = self.data.power[step]*self.param.step

            G = self.calculateGain(trama, energy, lpcCoefs)

            for it, t in enumerate(trama): 
                if it<self.param.p-1:
                    h[it] = 0
                elif it==self.param.p:
                    h[it] = G
                else:
                    for ic, c in enumerate(lpcCoefs):
                        h[it] -=  c*h[it-ic-1]
                        
            hShift = np.append( h[self.param.p-1:], np.zeros(self.param.p-1))
            hShiftFft = np.fft.fft(hShift)
            trFft = np.fft.fft(tramaHp)

            
            hShiftAc = self.m.autocorrelation(hShift)

            self.data.gain.append(G)    
            if step==0:
                self.data.lpc = lpcCoefs
            else:             
                self.data.lpc = np.vstack([self.data.lpc, lpcCoefs])
            
            
            if (step in self.pc.stepInto2 or step in self.pc.stepIntoAll):
                self.p.prnt(2, str(step)+"------------------ start", 1)
                self.p.prnt(4, str("In Second Cycle"), 1)
                self.p.prnt(6, "Current voice pitch: " +str(self.data.pitch[step]), 1)
                self.p.plot([(self.data.raw, 'speech', 'y', 0),(trama, 'trama', 'r',  idx)])

                ptrFft = 20*np.log10(trFft[0:int(len(trFft)/2)])
                phShiftFft = 20*np.log10(hShiftFft[0:int(len(hShiftFft)/2)])
                self.p.plot([(tramaHp, 'trama - high pass', 'b',  0)])
                self.p.plot([(tramaHpHam, 'trama - hamming', 'b',  0)])
                self.p.plot([(tramaHpHamAc, 'trama - auto correlation', 'b',  0),(tramaHpHamAc[0:self.param.p], 'trama - auto correlation (p='+str(self.param.p)+")", 'r',  0)])
                self.p.plot([(h, 'h', 'm',  0)])
                self.p.plot([(hShift, 'hShift', 'm',  0)])
                self.p.plot([(ptrFft, 'trFft dB', 'b',  0),(phShiftFft, 'phShiftFft dB', 'r',  0)],0)
                self.p.plot([(hShiftAc[:30], 'hShiftAc 30', 'r',  0),(tramaHpHamAc[:30], 'tramaHpHamAc 30', 'b',  0)],0)

                self.p.plot([(hShiftAc[:self.param.p], 'hShiftAc p', 'r',  0),(tramaHpHamAc[:self.param.p], 'tramaHpHamAc p', 'b',  0)],0)

                self.p.prnt(2, str(step)+"------------------ end", 1)

                if self.pc.stop2:
                    input("   ...")
                    
        self.data.pitch = np.mat(self.data.pitch).T
        self.data.gain = np.mat(self.data.gain).T
        
        if save:
            self.pickle.SaveData(self.data)
        

#LpcProcessing().run()