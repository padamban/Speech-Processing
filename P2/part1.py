# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 23:05:01 2019

@author: Padamban
"""


from config import Paths, Params
from core import AudioManager, Printer, Math
from core import np, pd


class Preprocess:
    
    def __init__(self):
        self.p = Printer(1)
        self.param = Params()
        self.m = Math()
        self.am = AudioManager()
        self.paths = Paths()
        self.trainingDesc, self.testingDesc = self.scanForAudioFiles()
        
        
    def scanForAudioFiles(self):
        trainPaths = self.am.scanDirectory(self.paths.folderTrain)
        testPaths = self.am.scanDirectory(self.paths.folderTest)
        return trainPaths, testPaths

    

    def readAudioFile(self, desc): 
        path = desc[2]
        raw = self.am.readAudio(path)
        return raw 
    
    def getSignalEnergy(self, raw):
        energy = []
        stp = self.param.step
        for step, idx in enumerate(range(0,len(raw),stp)):
            e = np.sum(raw[idx:idx+stp]**2)            
            energy.append(e)
        return energy
    
#   
    
    def getSpeech(self, raw, energy):
        rawAbs = abs(raw)
        stp = self.param.step
 
        whiteNoiseRef = 100;
        activationScale = [50, 1000, 100]
        dectivationScale = [100]
        
        activated = [0, 0, 0]

        lastActivated = 0
        spans = []
        span = []
        spanMaxRef= []
        maxRef = 0
        
        maxRaw = []
        for i, e in enumerate(energy):
            mx = max(rawAbs[:(i+1)*stp]) if i==0 else max(rawAbs[(i)*stp:(i+1)*stp]) 
            maxRaw.append(mx)


        for i, e in enumerate(energy):
            wait = 0     
            # passed the minimum activation            
            if e >= whiteNoiseRef*activationScale[0] and activated[0] == 0:
                activated[0] = 1
                lastActivated = i
            # bellow the deactivation value
            elif e < whiteNoiseRef*dectivationScale[0] and i-lastActivated>wait and activated[0] == 1:
                if activated[0]==1 and activated[1]==1:
                    span = [lastActivated*stp, i*stp]
                    spans.append(span)
                    spanMaxRef.append(maxRef)
                activated = [0, 0, 0]
                maxRef = maxRaw[i]
            # passed the second activation 
            if activated[0] == 1 and e >= whiteNoiseRef*activationScale[1]:
                activated[1] = 1
                maxRef = max([maxRef,maxRaw[i]])

        # join spans, which are close 
        joinedSpans = []
        joinedSpanMaxRef = []
        join = []
        jmaxRef = 0
        maxG = 1000
        for i, s in enumerate(spans):
            
            if i==0:
                join=[s[0], s[1]]
                jmaxRef = spanMaxRef[i] 
            elif s[0]-join[1]<maxG:
                join[1] = s[1]
                jmaxRef = max([jmaxRef,spanMaxRef[i]])
            else:
                joinedSpans.append(join)
                joinedSpanMaxRef.append(jmaxRef)
                jmaxRef = spanMaxRef[i] 
                join = s
            if i==len(spans)-1 and len(join)==2:
                joinedSpans.append(join)
                joinedSpanMaxRef.append(jmaxRef)

        # remove short spans
        minL = 1500
        longEnoughSpans = []
        longEnoughMaxRef = []
        for i, s in enumerate(joinedSpans):
            if s[1]-s[0]>minL : 
                longEnoughSpans.append(s)
                longEnoughMaxRef.append(joinedSpanMaxRef[i])

        # the most probable span
        bestSpan = [longEnoughSpans[np.argmax(longEnoughMaxRef)]]        
        speech = []
        speechIdx = []
        for s in bestSpan:
            speech.append(raw[s[0]:s[1]])
            speechIdx.append(s[0])    
        return speech, speechIdx


    def processOne(self, desc):
        raw = self.readAudioFile(desc)
        energy = self.getSignalEnergy(raw)
        speech, speechIdx = self.getSpeech(raw, energy)        
        self.p.plotSpeech(raw, speech, speechIdx)
        return speech
    

    def getDistanceMap(self, sR, sT):
        R = len(sR)
        T = len(sT)
        D = np.zeros([R, T])
        for r in range(R):
            for t in range(T):                
                tMin = (max(r*(T/(R*2)),(r-R*0.5)*(2*T/R)) )
                tMax = (min(r*(2*T/R),(r+R)*(T/2/R)) )
                if tMin <= t and t <= tMax : 
                    D[r,t] = np.sqrt((sR[r]-sT[t])**2)
                else:
                    D[r,t] = np.Inf
        return D 
    
    def getExpandedDistanceMap(self, D):
        eD = np.zeros(np.array(D.shape)+1)+np.Inf
        eD[1:,1:] = D
        eD[0,0] = 0
        return eD
                
    def getRouteMap(self, D):
        R = np.zeros(D.shape)
        size = R.shape
        print(size)
        g = np.array([1,1])
        dirs = np.array([[1, 0], [1,1], [0,1]])
        for step in range(sum(size)-1):
            
            
            print(step, "->", )
            vals = []
            for d in dirs:
                p = g-d
                v = D[p[0], p[1]]
                vals.append(v)
                print( "    ->", d, '\t', p, '\t', v)
 
            minVal = np.min(vals)
            minDir = dirs[np.argmin(vals)]

            g = g + minDir
            R[g[0],g[1]] = 1

#            if step == 0:
            dirs[np.argmin(vals)] 
#            g.    
            
            print("  -> ", vals, '\t',np.argmin(vals),  '\t', dirs[np.argmin(vals)] )
            print("  -> ", g)
#            R[g[0],g[1]] = np.inf
#            min([12,11,15])
            if(size[0]-g[0]-2<0 or size[1]-g[1]-2<0):
                break
        return R

    def getDistance(self, sR, sT):
#        r = len(sR)
#        t = len(sT)
        sR = range(0,15)
        sT = range(15,0,-1)

        D = self.getDistanceMap(sR,sT)
        self.p.imShow(D, "Distance Map " + str(D.shape))

        eD = self.getExpandedDistanceMap(D)
        
        self.p.imShow(eD, "exp Distance Map " + str(eD.shape))
        R = self.getRouteMap(D)
        self.p.imShow(R, "Route Map " + str(R.shape))

#        self.p.imShow(D)
#        print( r, t)

        
        
    def run(self):
        print("Tdesc ", self.trainingDesc[0])


        dA = self.trainingDesc[0]
        dB = self.trainingDesc[1]
        
        print(" -- dA",  dA[1])
        speechA = self.processOne(dA)[0]
        print(" -- dB",  dB[1])
        speechB = self.processOne(dB)[0]

        self.getDistance(speechA, speechB)

Preprocess().run()
        