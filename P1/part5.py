# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 22:38:27 2019

@author: Padamban
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:09:00 2019

@author: Padamban
"""


from core import np, scipy
from core import Printer, SpeachData, AudioManager, Math, Pickle, EncodedData, DecodedData
from config import PrintConfig, Params, Paths, CodeConfig
from coder import CodeFrame, CodingUtils
 


class Decoder:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.p = Printer(1);
        self.am = AudioManager();
        self.m = Math();
        self.pickle = Pickle(self.paths.pickle, lTag=self.paths.tag4, sTag=self.paths.tag5);
        self.cc = CodeConfig()
        self.cu = CodingUtils()        
        self.encoded = self.pickle.LoadEncoded() 

    def separateBins(self):
        binary = self.encoded.binaries
        innerL = [5, 7, 34]
        gain = []
        pitch = []
        lsp = []
        for i, s in enumerate(range(0, len(binary), sum(innerL))):
            separated = []
            eLast = s
            for e in innerL:                
                separated.append(binary[eLast:eLast+e])
                eLast = eLast+e
            gain.append(separated[0])
            pitch.append(separated[1])
            lsp.append(separated[2])
        return gain, pitch, lsp
    
    
    
    def debinariseLsp(self, bLsp):
        frames = self.setupLspFrames()
        qLsp = []
        bcLsp = []
        for i, b in enumerate(bLsp):
            idx = 0
            qlsp = []
            bclsp = []
            for j, f in enumerate(frames) :
                bc = b[idx:idx+f.bits]
                qb = self.cu.debinarise([bc], f)[0]/0.5*np.pi
                idx = idx+f.bits
                qlsp.append(qb)
                bclsp.append(bc)

            qLsp.append(qlsp)
            bcLsp.append(bclsp)

        return qLsp, bcLsp
    
    def debinariseGain(self, bGain, maxGain):        
        gainFrame = CodeFrame(self.cc.gainSegments)
        gainFrame.scale(maxGain)
        qGain = self.cu.debinarise(bGain, gainFrame)
        return qGain
     
    def debinarisePitch(self, bPitch):
        qPitch = []
        for i, b in enumerate(bPitch):
            q = int(b,2)
            q = q + (0 if q==0 else 19)
            qPitch.append(q)  
        return qPitch


    def lspToLpc(self, lsp):
        lsp = np.array(lsp)
        return self.cu.lsf_to_lpc(lsp) 
  
  
    def setupLspFrames(self):
        frames = []
        for s in self.cc.lspSegments :
            frames.append(CodeFrame(s))       
        return frames

        
    def lspToLpc(self, lsp):
        lsp = np.array(lsp)
        return self.cu.lsf_to_lpc(lsp) 
    
    
    def Save(self, qlpc, qpitch, qgain):
        self.decoded = DecodedData()
        self.decoded.gain = qgain
        self.decoded.pitch = qpitch
        self.decoded.lpc = qlpc
        self.pickle.SaveDecoded(self.decoded)    
    
    
    def run(self, save=1):
        maxGain = self.encoded.maxGain
        bGain, bPitch, bLsp = self.separateBins()
        qGain = self.debinariseGain(bGain, maxGain)
        qPitch = self.debinarisePitch(bPitch)
        qLsp, bcLsp = self.debinariseLsp(bLsp)
        
        qLpc = self.lspToLpc(qLsp)
        qLpc = self.cu.removeLpcPrefix(qLpc)
        self.Save(qLpc, qPitch, qGain)
        
        for step in range(len(bGain)):

            if (step in self.pc.stepInto5 or step in self.pc.stepIntoAll):

       
                self.p.prnt(2, ' ',1)
                self.p.prnt(2, '    bitcount  -> ' + str(len(self.encoded.binaries)), 1)

                self.p.prnt(2, '    gain  -> ' + str(bGain[step]) + "    -  " + str(qGain[step]), 1)

                self.p.prnt(2, '    pitch -> ' + str(bPitch[step]) + "  -  " + str(qPitch[step]), 1)
                self.p.prnt(2, '    lsp   -> ' + str(bLsp[step]) , 1)
                self.p.prnt(2, ' ',1)
                for i, lspCoef in enumerate(qLsp[step]):  
                    self.p.prnt(2, '       lsp '+str(i)+' -> ' + str(bcLsp[step][i]) + "  -  " + str(lspCoef), 1)
                self.p.prnt(2, ' ',1)
                for i, lpcCoef in enumerate(qLpc[step]):  
                    self.p.prnt(2, '       lpc '+str(i)+' -> ' + str(lpcCoef) , 1)
     
#Decoder().run()