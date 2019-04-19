# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 14:33:08 2019

@author: Padamban
"""


from core import np
from core import Printer, SpeachData, AudioManager, Math, Pickle
from config import PrintConfig, Params, Paths


class Synthesizer:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.data = SpeachData();
        self.p = Printer(1);
        self.am = AudioManager();
        self.m = Math();
        self.pickle = Pickle(self.paths.pickle, lTag=self.paths.tag2,  sTag=self.paths.tag3);
        self.data = self.pickle.LoadData();

    
    def gNoise(self, length, val=1  ):
        return np.array([np.random.normal() for i in range(int(length))])*val


    def linearPredictor(self, lpcCoefs, Sni, SniPrev  ):
        lpcLen = len(lpcCoefs)
        SniPrev =  SniPrev[len(SniPrev)-lpcLen:]
        SniPrefixed = np.append(SniPrev,Sni)
        for i, n in enumerate(range(lpcLen, len(SniPrefixed))):
            SniLastN = SniPrefixed[i:n]
            pred = -np.dot(lpcCoefs,SniLastN[::-1])
            SniPrefixed[n] += pred
        Sni = SniPrefixed[lpcLen:] 
        return Sni
    
    
    def glutealPulse(self, pitch, gain=1 ):
        N0 = np.int(pitch)
        Nop = np.int(N0*2/3)
        pulse = np.zeros(N0)
        for n in range(Nop):
            pulse[n] = ((2*Nop - 1)*n - 3*n**2)/(Nop**2 - 3*Nop + 2)       
        return pulse*gain
 
    
    def synth(self, LPC, Pitch, Gain ):
        stp =  self.param.step
        Sn = np.array([])

        SniPrev = np.zeros(stp)
        stepInset = 0
        for step, pitch in enumerate(Pitch[:]):
            
            lpcCoefs = LPC[step]      
            gain = float(Gain[step])            
            stepLeftover = stp - stepInset    
            Sni = np.array([])
            if pitch==0:
                G = float(np.sqrt(1/stp)*gain)
                Sni = np.append(Sni,self.gNoise(stepLeftover, G))
                stepInset = 0
            else:
                G = float(np.sqrt(pitch/stp)*gain)
                innerJumps = int(1 if pitch == 0 else np.ceil(stepLeftover/pitch))
                spannedStep = 0
                Snisub = np.array([])
                for ij in range(innerJumps):                    
                    Snisubi=self.glutealPulse(pitch, G)
                    Snisub = np.append(Snisub,Snisubi)
                    spannedStep += pitch
                Sni = np.append(Sni,Snisub)
                stepInset = spannedStep - stepLeftover

            Sni = self.linearPredictor(lpcCoefs, Sni, SniPrev)
            SniPrev = Sni
            Sn = np.append(Sn,np.array(Sni))         

      
        return Sn
        
     
    def run(self, save=1):
        stp =  self.param.step
        Sn = np.array([])

        SniPrev = np.zeros(self.param.step)
        stepInset = 0
        for step, pitch in enumerate(self.data.pitch[:]):
            
            lpcCoefs = self.data.lpc[step]      
            gain = float(self.data.gain[step])            
            stepLeftover = stp - stepInset    
            Sni = np.array([])
            if pitch==0:
                G = float(np.sqrt(1/self.param.step)*gain)
                Sni = np.append(Sni,self.gNoise(stepLeftover, G))
                stepInset = 0
            else:
                G = float(np.sqrt(pitch/self.param.step)*gain)
                innerJumps = int(1 if pitch == 0 else np.ceil(stepLeftover/pitch))
                spannedStep = 0
                Snisub = np.array([])
                for ij in range(innerJumps):                    
                    Snisubi=self.glutealPulse(pitch, G)
                    Snisub = np.append(Snisub,Snisubi)
                    spannedStep += pitch
                Sni = np.append(Sni,Snisub)
                stepInset = spannedStep - stepLeftover

            Sni = self.linearPredictor(lpcCoefs, Sni, SniPrev)

            SniPrev = Sni

            Sn = np.append(Sn,np.array(Sni))
            
            if (step in self.pc.stepInto3 or step in self.pc.stepIntoAll):
                self.p.prnt(2, str(step)+"------------------ start", 1)
                self.p.prnt(4, str("In Third Cycle"), 1)
                self.p.plot([ (Sn, 'Sn', 'b', 0), (Sni, 'Sni', 'r', len(Sn)-len(Sni)), (self.data.raw[:len(Sn)]*0.3, 'raw*0.3', 'c', 0)],0)
                prev = 3
                since =  len(Sn)-len(Sni)*prev
                since = 0 if since < 0 else since
                self.p.plot([(self.data.raw[since:len(Sn)]*2, 'raw*2', 'c', since), (Sn[since:len(Sn)-len(Sni)], 'Sn', 'b', since), (Sni, 'Sni', 'r', len(Sn)-len(Sni)) ],0)

                if self.pc.stop3:
                    input("   ...")
      
        self.syntesized = Sn
        
        if save:
            self.pickle.SaveData(self.data)
            self.pickle.save('syntesized', self.syntesized)
        
        
#Synthesizer().run()