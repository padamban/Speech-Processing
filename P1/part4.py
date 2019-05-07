# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:09:00 2019

@author: Padamban
"""


from core import np, scipy
from core import Printer, SpeachData, AudioManager, Math, Pickle, EncodedData
from config import PrintConfig, Params, Paths, CodeConfig
from coder import CodeFrame, CodingUtils
 


class Coder:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.p = Printer(1);
        self.am = AudioManager();
        self.m = Math();
        self.pickle = Pickle(self.paths.pickle, lTag=self.paths.tag3, sTag=self.paths.tag4);
        self.cc = CodeConfig()
        self.cu = CodingUtils()        
        self.data = self.pickle.LoadData();

        
    def binariseGain(self):
        gainFrame = CodeFrame(self.cc.gainSegments)
        maxGain = np.max(self.data.gain)
        gainFrame.scale(maxGain)
        binary, quanta, indice = self.cu.binarise(self.data.gain, gainFrame)
        return binary, maxGain
     
        
    def binarisePitch(self):
        bits = 7
        binary = []
        dig = []
        for i, p in enumerate(self.data.pitch):
            shifted = (p-self.param.pi+1 if p!=0 else p).astype(np.uint8)
            dig.append(shifted[0,0])
            binary.append(np.binary_repr(shifted[0, 0],width=bits))  
        return binary
        
            
    def lpcToLsp(self, lpc):
        return self.cu.lpc_to_lsf(lpc)
    
  
    def setupLspFrames(self):
        frames = []
        for s in self.cc.lspSegments :
            frames.append(CodeFrame(s))       
        return frames
    
    def binariseLsp(self,LSP):
        frames = self.setupLspFrames()     
        lspBinaries = []
        for j, lsp in enumerate(LSP):
            lspBin = []
            for i, coef in enumerate(lsp):                 
                c = [coef*0.5/np.pi]
                binary, quanta, indice = self.cu.binarise( c, frames[i])
                lspBin.append(binary[0])

            lspBinaries.append(lspBin)  
        return lspBinaries


    def comoposeBinaries(self, gain, pitch, lsp):
        allBins= []
        for i in range(len(gain)):
            blsp = ''
            for ls in lsp[i]:
                blsp = blsp + ls                
            oneBin = gain[i] + pitch[i]+ blsp
            allBins.append(oneBin)        
        return allBins
     
        
    def zipBinaries(self, coded, maxGain):
        encoded = EncodedData()
        encoded.maxGain = maxGain
        binary = ''
        for c in coded:
            binary = binary + c
        encoded.binaries = binary
        return encoded
    
      
    def run(self, save=1):
        bGain, maxGain = self.binariseGain()
        bPitch = self.binarisePitch()  
        LPC1 = self.cu.prefixLpcWith1(self.data.lpc)
        LSP = self.lpcToLsp(LPC1)
        bLSP = self.binariseLsp(LSP)        
        coded = self.comoposeBinaries(bGain,bPitch,bLSP)        
        encoded = self.zipBinaries(coded, maxGain)
        self.pickle.SaveEncoded(encoded)

        for step in range(len(bGain)):
            if (step in self.pc.stepInto4 or step in self.pc.stepIntoAll):

                self.p.prnt(2, str(step)+"------------------ start", 1)
                self.p.prnt(4, str("In Forth Cycle"), 1)
                self.p.prnt(2, ' '  , 1)
                self.p.prnt(2, '    gain max  -> ' + str(maxGain) , 1)
                self.p.prnt(2, '    gain  -> ' + str( self.data.gain[step, 0]) + "  ==  " + str( bGain[step]) , 1)
                self.p.prnt(2, '    pitch -> ' + str( self.data.pitch[step, 0])  + "  ==  " + str( bPitch[step]) , 1)
                self.p.prnt(2, ' '  , 1)
                for i, c in enumerate(self.data.lpc[step]):                    
                    self.p.prnt(2, '    lpc ' + str(i) + ' -> ' + str(round(c,4)) + "\t" + bLSP[step][i]  , 1)
                self.p.prnt(2, ' '  , 1)
                for i, c in enumerate(LSP[step]):                    
                    self.p.prnt(2, '    lsp ' + str(i) + ' -> ' + str(round(LSP[step][i],4)) + "\t" + bLSP[step][i]  , 1)
                self.p.prnt(2, ' '  , 1)
                self.p.prnt(2, '    lsp   -> ' + coded[step] , 1)

                self.p.prnt(2, ' '  , 1)



        
#Coder().run()









