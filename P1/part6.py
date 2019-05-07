# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 16:53:33 2019

@author: Padamban
"""

from core import Printer, SpeachData, AudioManager, Math, Pickle, EncodedData, DecodedData
from config import PrintConfig, Params, Paths, CodeConfig
from part3 import Synthesizer



class ComaparedData:
    def __init__(self, original, decoded, error, raw=[]):
        self.o = original
        self.d = decoded
        self.e = error
        self.raw = raw
        


class Analysis:
    
    def __init__(self):
        self.paths = Paths();
        self.param = Params();
        self.pc = PrintConfig();
        self.am = AudioManager()

        self.p = Printer(1);
        self.S = Synthesizer()
        self.pickle = Pickle(self.paths.pickle);
        self.decoded, self.original, self.coded = self.loadAll()
        self.cP, self.cG, self.cLpc = self.organize()
        self.cSn = self.SynthAll()

    def loadAll(self):
        coded = self.pickle.LoadEncoded(self.paths.tag4);
        decoded = self.pickle.LoadDecoded(self.paths.tag5);
        data = self.pickle.LoadData(self.paths.tag3);
        return decoded, data, coded
    
    def SynthAll(self):
        snO = self.S.synth(self.cLpc.o, self.cP.o, self.cG.o)
        snD = self.S.synth(self.cLpc.d, self.cP.d, self.cG.d)
        snE = []
        for i, sno in enumerate(snO):
            snE.append(snO[i] - snD[i]) 
            
        rw = self.am.readAudio(self.paths.file)
        return ComaparedData(snO,snD,snE,rw)
        
    def organize(self):
        oPitch = []
        dPitch = []
        ePitch = []
        oGain = []
        dGain = []
        eGain = []         
        oLpc = self.original.lpc
        dLpc = self.decoded.lpc
        
        for i in range(len(self.original.lpc)):            
            op = int(self.original.pitch[i][0,0])
            dp = self.decoded.pitch[i]
            ep = op - dp            
            oPitch.append(op)
            dPitch.append(dp)
            ePitch.append(ep) 
            og = round(self.original.gain[i][0,0],3)
            dg = self.decoded.gain[i]
            eg = og - dg
            oGain.append(og)
            dGain.append(dg)
            eGain.append(eg)
            
        cP = ComaparedData(oPitch,dPitch,ePitch)
        cG = ComaparedData(oGain,dGain,eGain)
        cLpc = ComaparedData(oLpc,dLpc,None)
        return cP, cG, cLpc
        
    
    
    def compareVisu(self):


        for i in range(len(self.cP.o)):
            if (i in self.pc.stepInto6 or i in self.pc.stepIntoAll):
                self.p.prnt(2, str(i)+"------------------ start", 1)
                self.p.prnt(4, str("In Sixth Cycle"), 1)
                self.p.prnt(2, '  ',1)
                self.p.prnt(2, '    gain   ' +str(i)+"  "+" ->    " + str(round(self.cG.o[i], 0)) +"\t"+str(int(self.cG.d[i]))+"\t"+str(int(self.cG.e[i])),1)
                self.p.prnt(2, '    pitch  ' +str(i)+"  "+" ->    " + str(round(self.cP.o[i], 0)) +"\t"+str(int(self.cP.d[i]))+"\t"+str(int(self.cP.e[i])),1)

                for j in range(len(self.cLpc.o[i])):
                    self.p.prnt(2, '     lpc   ' +str(i)+" "+str(j)+" ->   " + str(round(self.cLpc.o[i][j], 3)) +"\t"+str(round(self.cLpc.d[i][j], 3)),1)

                start=i*self.param.step
                end = start +self.param.step
                tag = str(i)+"th "
                self.p.plot([(self.cSn.raw[start:end], ' raw audio', 'k',  0),(self.cSn.o[start:end], tag+' original synth', 'b',  0),(self.cSn.d[start:end], tag+'  decoded synth', 'g',  0), (self.cSn.e[start:end], tag+'    error synth', 'r',  0)])

        self.p.plot([(self.cSn.raw, ' raw audio', 'k',  0),(self.cSn.o, ' original synth', 'b',  0),(self.cSn.d, '  decoded synth', 'g',  0), (self.cSn.e, '    error synth', 'r',  0)])
        self.p.plot([(self.cP.o, ' original gain', 'b',  0), (self.cP.d, 'decoded gain', 'g*',  0), (self.cP.e, 'error', 'r--',  0)])
        self.p.plot([(self.cG.o, ' original gain', 'b',  0), (self.cG.d, 'decoded gain', 'g*',  0), (self.cG.e, 'error', 'r--',  0)])
        originalFileSize = self.pickle.getFileSize(self.paths.file)*8
        codedFileSize = len(self.coded.binaries)
        self.p.prnt(2, '  ---------------------------------------------------   ',1)
        self.p.prnt(2, '    original file size    ->    ' + str(originalFileSize) + ' bits',1)
        self.p.prnt(2, '       coded file size    ->    ' + str(codedFileSize) + ' bits',1)
        self.p.prnt(2, '           compression    ->    ' + str(round((codedFileSize/originalFileSize)*100, 3)) + ' %',1)

        
    def compareAudio(self):
        self.p.prnt(4, "", 1)       

        self.p.prnt(4, str("Listen"), 1)       
        self.p.prnt(4, "      1.  original file", 1)       
        self.p.prnt(4, "      2.  sytesized before coding", 1)       
        self.p.prnt(4, "      3.  sytesized after decoding", 1)       

      
        self.am.playOriginalAudio(self.paths.file)        
        self.am.playSyntesizedAudio(self.cSn.o)
        self.am.playSyntesizedAudio(self.cSn.d)

        
#Analysis().compareVisu()
#Analysis().compareAudio()





