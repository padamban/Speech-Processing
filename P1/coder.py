# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:11:43 2019

@author: Padamban
"""


from core import np, scipy, sg
 


class CodeFrame:
 
    def __init__(self, seg, val = None):
        self.segments = np.array(seg)
        self.values = np.array(val) if val else CodingUtils().createSegmentValues(self.segments)
        self.segs = len(seg)
        self.bits = np.log2(self.segs+1).astype(np.uint8) 
        
    def scale(self, scl=1):
        self.segments = self.segments * scl
        self.values = self.values*scl


        
     

class CodingUtils:
    
    def binarise(self, data, frame):        
        binary = [] 
        quanta = [] 
        indice = []         
        for d in data:
            val = 0
            idx = frame.segs-1
            for i in range(0, frame.segs):
                seg = frame.segments[i]
                if(i < frame.segs):
                    val = frame.values[i-1]
                if(0 < i and d < seg):
                    idx = i-1
                    break
            bin = np.binary_repr(idx,width=frame.bits)            
            binary.append(bin)
            quanta.append(val)
            indice.append(idx)   

        return binary, quanta, indice 
    
    def debinarise(self, binaries, frame):        
        quanta = []
        for b in binaries:
            idx = int(b, 2)
            quanta.append(frame.values[idx])
        return quanta
    
    
    def createSegments(self, start, end, segments):        
        delta = (end-start)/segments
        return np.arange(start, end+delta, delta)
        
    
    def createSegmentValues(self, segments):
        quantas = [];
        lastS = 0;  
        putInCap = 0
        for i, S in enumerate(segments):
            if i == 0:
                lastS = S
            else:        
                quantas.append((S + lastS)*0.5)
                lastS = S
                putInCap = 1
        if putInCap == 1:
            quantas.append((quantas[-1]+ lastS)*0.5)
        return np.array(quantas)
    
            
    def prefixLpcWith1(self, lpc ):
        lpc1 = []
        for i, aks in enumerate(lpc):
            ak = np.insert(aks, 0, 1., axis=0)
            lpc1.append(ak.tolist())            
        lpc1 = np.array(lpc1)
        return lpc1   
    
    def removeLpcPrefix(self, lpc1 ):
        lpc = []
        for i, aks in enumerate(lpc1):
            lpc.append(aks[1:])            
        lpc = np.array(lpc)
        return lpc  
    
    
    def lpc_to_lsf(self, all_lpc):
        if len(all_lpc.shape) < 2:
            all_lpc = all_lpc[None]
        order = all_lpc.shape[1] - 1
        all_lsf = np.zeros((len(all_lpc), order))
        for i in range(len(all_lpc)):
            lpc = all_lpc[i]
            lpc1 = np.append(lpc, 0)
            lpc2 = lpc1[::-1]
            sum_filt = lpc1 + lpc2
            diff_filt = lpc1 - lpc2
    
            if order % 2 != 0:
                deconv_diff, _ = sg.deconvolve(diff_filt, [1, 0, -1])
                deconv_sum = sum_filt
            else:
                deconv_diff, _ = sg.deconvolve(diff_filt, [1, -1])
                deconv_sum, _ = sg.deconvolve(sum_filt, [1, 1])
    
            roots_diff = np.roots(deconv_diff)
            roots_sum = np.roots(deconv_sum)
            angle_diff = np.angle(roots_diff[::2])
            angle_sum = np.angle(roots_sum[::2])
            lsf = np.sort(np.hstack((angle_diff, angle_sum)))
            if len(lsf) != 0:
                all_lsf[i] = lsf
        return np.squeeze(all_lsf)
    
    
    def lsf_to_lpc(self, all_lsf):
        if len(all_lsf.shape) < 2:
            all_lsf = all_lsf[None]
        order = all_lsf.shape[1]
        all_lpc = np.zeros((len(all_lsf), order + 1))
        for i in range(len(all_lsf)):
            lsf = all_lsf[i]
            zeros = np.exp(1j * lsf)
            sum_zeros = zeros[::2]
            diff_zeros = zeros[1::2]
            sum_zeros = np.hstack((sum_zeros, np.conj(sum_zeros)))
            diff_zeros = np.hstack((diff_zeros, np.conj(diff_zeros)))
            sum_filt = np.poly(sum_zeros)
            diff_filt = np.poly(diff_zeros)
    
            if order % 2 != 0:
                deconv_diff = sg.convolve(diff_filt, [1, 0, -1])
                deconv_sum = sum_filt
            else:
                deconv_diff = sg.convolve(diff_filt, [1, -1])
                deconv_sum = sg.convolve(sum_filt, [1, 1])
    
            lpc = .5 * (deconv_sum + deconv_diff)
            all_lpc[i] = lpc[:-1]
        return np.squeeze(all_lpc)
    
