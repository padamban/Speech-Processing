# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 23:05:01 2019

@author: Padamban
"""


# cmeneses@deetc.isel.ipl.pt


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


    def extractSpeech(self, desc, visu=False):
        raw = self.readAudioFile(desc)
        energy = self.getSignalEnergy(raw)
        speech, speechIdx = self.getSpeech(raw, energy) 
        if(visu):
            title = str( " content: " + desc[1][0]) + " | orator: " + str(desc[1][2])+ " |  version: " + str(desc[1][1])
            self.p.plotSpeech(raw, speech, speechIdx, title)
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
    
    
    
    def processSpeech(self, raw):
        stp = self.param.step;
        wndw = self.param.window;
        p = self.param.p;

        tramasAC = [];    
    
        for step, idx in enumerate(range(0,len(raw),stp)):
            trama  = raw[idx:idx+wndw];

            if len(trama)<wndw:
                expTrama = trama;
                for i in range(0, np.ceil((wndw/len(trama))-1).astype(int)):                    
                    expTrama =  np.hstack([expTrama, trama])
                expTrama = expTrama[0:wndw];
                trama = expTrama;
                                
            tAC = self.m.autocorrelation(trama);
            ptAC = tAC[:p]            
            tramasAC = np.vstack([ptAC] if step==0 else [tramasAC, ptAC])
#            if step == 20:
#                self.p.plot([ (tAC, 'all', 'b*-',  0), (ptAC, 'order p='+str(p), 'y',  0) ], 0, 'Autocorrelation of segment');
#                title = str( " trama: " + str(step))
#                self.p.plot([ (raw, 'speech', 'r',  0), (trama, 'segment ', 'b',  idx) ], 0, title)

        return tramasAC
        
 
    
    def getExpandedDistanceMap(self, D):
        eD = np.zeros(np.array(D.shape)+1)+np.Inf
        eD[1:,1:] = D
        eD[0,0] = 0
        return eD
                

    def getDistanceMapOfAc(self, sR, sT):
        R = len(sR)
        T = len(sT)
        D = np.zeros([R, T]);
        for r in range(R):
            for t in range(T):                
                tMin = (max(r*(T/(R*2)),(r-R*0.5)*(2*T/R)) )
                tMax = (min(r*(2*T/R),(r+R)*(T/2/R)) )
                if not (tMin <= t+1 and t-1 <= tMax) : 
                    D[r,t] = np.Inf
                else:
                    D[r,t] = (sum((sT[t]-sR[r])**2)**(0.5))
        return D 
    
    def stepOne(self, dist, position, arround):
        dim = arround.shape
        if 2<sum(dim):
            dirs = np.array([])
            if 1<dim[0] and 1<dim[1] :
                dirs = np.array([[1,0], [0,1], [1,1]]);
            elif 1<dim[0]:
                dirs = np.array([[1,0]]);
            elif 1<dim[1]:
                dirs = np.array([[0,1]]);    
                
            minDir = dirs[0];
            minVal = arround[minDir[0], minDir[1]];
    
            for d in dirs:
                thisVal = arround[d[0], d[1]];
                if thisVal <= minVal:
                    minDir =d;
                    minVal = thisVal;

            dist = dist + minVal;
            position = position + minDir;
            
        return position, dist, minVal
    
    
    
    def getDistanceRoute(self, expD):
        target = expD.shape;
        Route =  np.zeros(expD.shape);
        expDRoute =  np.array(expD);

        baseline = 0.5;
        pos = np.array([0,0]);
        dist = 0;
        Route[pos[0], pos[1]] = baseline; 
        step = 0;
        
        while ((target[0]-1)-pos[0] + (target[0]-1)-pos[0])!=0:
            around = expD[pos[0]:pos[0]+2, pos[1]:pos[1]+2];
            pos, dist, delta = self.stepOne(dist, pos, around);
            step = step + 1;            
            Route[pos[0], pos[1]] = baseline + delta; 
            expDRoute[pos[0], pos[1]] = expDRoute[pos[0], pos[1]] +3;
        globalDist = np.inf;
        if 0 < step:
            globalDist = dist / step;
        
        return globalDist, Route, expDRoute;
        
    
    def getDistance(self, sR, sT):
        D = self.getDistanceMapOfAc( sR, sT);
        expD = self.getExpandedDistanceMap(D);
        globalDist, route, expdRoute = self.getDistanceRoute(expD);
        return globalDist, expD, route, expdRoute;
    
    
    
    
    def processAll(self, descs):
        ACs = [] 
        for d in descs:
            speech = self.extractSpeech(d, False)[0]
            speechAC = self.processSpeech(speech)
            ACs.append(speechAC)
        return ACs
        
    def compareAC(self, speechA_AC, speechB_AC):
        globalDistance, expD, route, expdRoute = self.getDistance( speechA_AC, speechB_AC );
        return globalDistance, expD, route, expdRoute
    
    def compare(self, descA, descB, visu=False, speechAlreadyProcessed=False): 
        speechA = self.extractSpeech(descA, visu)[0]
        speechB = self.extractSpeech(descB, visu)[0]           
        speechA_AC = self.processSpeech(speechA)
        speechB_AC = self.processSpeech(speechB)
        globalDistance, expD, route, expdRoute = self.compareAC( speechA_AC, speechB_AC );
        return globalDistance, expD, route, expdRoute
    
    def compare1toN(self, one, many, visu=False):
        dA = one;
        for dK in many:
            globalDistance, expD, route, expdRoute = self.compare( dA, dK, visu);
            if(visu):
                self.p.imShow(expD, "expD of " + str(dA[1]) + " v " + str(dK[1]) + "      dist="+str(round(globalDistance,3)))

                self.p.imShow(expdRoute, "expdRoute of " + str(dA[1]) + " v " + str(dK[1]) + "      dist="+str(round(globalDistance,3)))

                self.p.imShow(route, "route of " + str(dA[1]) + " v " + str(dK[1]) + "      dist="+str(round(globalDistance,3)))

      
    def compareTestToTrain(self, test, train, visu=False):

        testACs = self.processAll(test)
        trainACs =  self.processAll(train)
        
        rows = len(test)
        cols = len(train)
        scoreMap = np.zeros([rows, cols])
        matchMap = np.zeros([rows, cols])
        matchScoreMap = np.zeros([rows*3, cols])-np.inf

#        print("compareTestToTrain 1 - ", testACs)
        
        matchCount = 0;
        testCount = 0;


        print("compareTestToTrain  - ", len(test[0]), len(train[0]))
        for i, iTest in enumerate(test):
            iexp = i*3
            
            iTestAC = testACs[i]
            scores = []
            for j, jTrain in enumerate(train):
                jTrainAC = trainACs[j]
                globalDistance, expD, route, expdRoute = self.compareAC(iTestAC, jTrainAC)            
                
                scoreMap[i,j] = globalDistance
                matchScoreMap[iexp,j] = globalDistance
                
                scores.append(globalDistance);
                isSame = iTest[1][0] == jTrain[1][0];
                matchScoreMap[iexp+1,j] = 1 if isSame else np.inf
                
                
#                print("   -> ", i, j, "   -  ", iTest[1][0]," v ", jTrain[1][0], "  \t",round(globalDistance, 3) )

            lowestScoreIdx = np.argmin(scores);
            
            isMatch = iTest[1][0] == train[lowestScoreIdx][1][0];
            
            matchCount = matchCount + (1 if isMatch else 0);
            testCount = testCount + 1;

            
            print("   -> ", i, lowestScoreIdx, "   -  ", iTest[1][0]," v ", train[lowestScoreIdx][1][0], "  \t",round( scores[lowestScoreIdx], 3), "  \t", isMatch )

            matchMap[i,lowestScoreIdx] = 1 * (1 if isMatch else -1);
            matchScoreMap[iexp+1,lowestScoreIdx] = 1 * (2 if isMatch else -0.5);
            
        matchRatio = (matchCount / testCount) if testCount != 0 else 0
            
        self.p.imShow(scoreMap, "scoreMap ")

        self.p.imShow(matchMap, "matchMap ")
        self.p.imShow(matchScoreMap, "matchScoreMap ")
        print(" matchRatio " , matchRatio,"    ", matchCount,  testCount)


    def compareAll(self, data):
                
        numOfSamples = len(data)
        
        confusionMap = np.ones([numOfSamples, numOfSamples])
#        matchMap = np.ones([numOfSamples, numOfSamples])
        matchMap = np.zeros([numOfSamples, numOfSamples])

        xMap = np.zeros([numOfSamples, numOfSamples])



        ACs = self.processAll(data)

        
        for i, di in enumerate(data):
            iAC = ACs[i]
            iValue = di[1][0]
            
            
            for j, dj in enumerate(data):
                if i > j-1:
                    jValue = dj[1][0]
                    jAC = ACs[j]
                    globalDistance, expD, route, expdRoute = self.compareAC(iAC, jAC)            
                    confusionMap[i,j] = globalDistance
                    confusionMap[j,i] = globalDistance
                    matchMap[i,j] = (jValue == iValue) and (globalDistance < 0.8)
                    xMap[i,j] = (globalDistance < 0.5)
                    print("   -> ", i, j, "   -  ", di[1][0]," v ", dj[1][0], "  \t",round(globalDistance, 3) )



        self.p.imShow(confusionMap, "confusionMap ")
        self.p.imShow(matchMap, "matchMap ")
        self.p.imShow(xMap, "xMap ")
        


    
    def run(self):
#        self.compare1toN(self.testingDesc[21], [self.trainingDesc[30]], True)
#        self.compare1toN(self.trainingDesc[1], [self.trainingDesc[0]], True)

#        self.compareAll(self.trainingDesc[:40])
        self.compareTestToTrain(self.testingDesc[:], self.trainingDesc[:])

        
 

Preprocess().run()
        