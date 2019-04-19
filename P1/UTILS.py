# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:37:41 2019

@author: Padamban
"""
import numpy as np
import scipy.signal as sg


class Coding:
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
            # Last coefficient is 0 and not returned
            all_lpc[i] = lpc[:-1]
        return np.squeeze(all_lpc)
    
    
    
    
    
    vd = [
    [0.0169,    0.0247,    0.0297,    0.0331,    0.0387,    0.0475 ,   0.0575],
    [0.0278 ,   0.0313 ,   0.0350,    0.0387 ,   0.0428  ,  0.0475  ,  0.0525  ,  0.0575  ,  0.0625 ,0.0675 ,   0.0731 ,   0.0800 ,   0.0881  ,  0.0969 ,   0.1056],
    [0.0550 ,   0.0600 ,   0.0650 ,   0.0703  ,  0.0766 ,   0.0841,    0.0925  ,  0.1016 ,   0.1125, 0.1250  ,  0.1375 ,   0.1500 ,   0.1625 ,   0.1750  ,  0.1875],
    [0.0800 ,   0.0863 ,   0.0947,    0.1047 ,   0.1156 ,   0.1281 ,   0.1406  ,  0.1525 ,   0.1650, 0.1775  ,  0.1900 ,   0.2025 ,   0.2150 ,   0.2275 ,   0.2400],
    [0.1281  ,  0.1363 ,   0.1463 ,   0.1559  ,  0.1647 ,   0.1737 ,   0.1837  ,  0.1937  ,  0.2037, 0.2138  ,  0.2250 ,   0.2375 ,   0.2500 ,   0.2625  ,  0.2750],
    [0.1900 ,   0.2037  ,  0.2200  ,  0.2394  ,  0.2625 ,   0.2875 ,   0.3125],
    [0.2300 ,   0.2400  ,  0.2537 ,   0.2750  ,  0.2987 ,   0.3237 ,   0.3500],
    [0.2891  ,  0.3078 ,   0.3234  ,  0.3406  ,  0.3594 ,   0.3813 ,   0.4062],
    [0.3525  ,  0.3675  ,  0.3812  ,  0.3937  ,  0.4069 ,   0.4213 ,   0.4362],
    [0.4037 ,   0.4138 ,   0.4231  ,  0.4319 ,   0.4425 ,   0.4562 ,   0.4712]      
          ]

    vq = [
    [0.0125 ,   0.0213 ,   0.0281 ,   0.0313 ,   0.0350 ,   0.0425,    0.0525  ,  0.0625],
    [0.0263 ,   0.0294 ,   0.0331 ,   0.0369 ,   0.0406  ,  0.0450 ,   0.0500 ,   0.0550,    0.0600, 0.0650  ,  0.0700  ,  0.0763  ,  0.0838   , 0.0925 ,   0.1013 ,   0.1100],
    [0.0525 ,  0.0575 ,   0.0625 ,   0.0675 ,   0.0731 ,   0.0800 ,   0.0881  ,  0.0969,    0.1062 ,0.1187 ,   0.1312  ,  0.1438 ,   0.1563,    0.1687  ,  0.1812  ,  0.1937],
    [0.0775 ,  0.0825  ,  0.0900 ,   0.0994 ,   0.1100 ,   0.1212,    0.1350  ,  0.1463 ,   0.1588,    0.1712  ,  0.1837  ,  0.1962 ,   0.2088 ,   0.2213  ,  0.2338  ,  0.246],
    [0.1250 ,   0.1312 ,  0.1413  ,  0.1513  ,  0.1606,    0.1687 ,   0.1787  ,  0.1887, 0.1987,    0.2088 ,   0.2188  ,  0.2313  ,  0.2437 ,   0.2562  ,  0.2687  ,  0.2813],
    [0.1837 ,   0.1962 ,   0.2113 ,   0.2288 ,   0.2500 ,   0.2750  ,  0.3000  ,  0.3250],
    [0.2250 ,   0.2350  ,  0.2450 ,   0.2625 ,   0.2875 ,   0.3100 ,   0.3375 ,   0.3625],
    [0.2781 ,  0.3000  ,  0.3156 ,   0.3312  ,  0.3500 ,   0.3688  ,  0.3937  ,  0.4188],
    [0.3450 ,  0.3600  ,  0.3750  ,  0.3875  ,  0.4000 ,   0.4138  ,  0.4288  ,  0.4437],
    [0.3987 ,  0.4088 ,   0.4188  ,  0.4275  ,  0.4363  ,  0.4487  ,  0.4637  ,  0.4788]     
          ]

    indexFormat = ['03b', '04b', '04b', '04b', '04b', '03b', '03b', '03b', '03b', '03b']
    
    def quantize(self, signal, partitions, codebook):
        indices = []
        quanta = []
        signal=[signal]

        for datum in signal:
            index = 0     
            while index < len(partitions) and datum > partitions[index]:
                index += 1
            indices.append(index)
            quanta.append(codebook[index])

        return indices[0], quanta

    
    def encodeLSP(self, lsp):
        
        bitsLSP = []
        lspq    = []
        
        vd = self.vd
        vq = self.vq
        
        index, lspqAux = self.quantize(lsp[0], vd[0], vq[0])

        lspq.append(lspqAux)
        
        binary=format(index, self.indexFormat[0])
        bitsLSP.append(binary)
        
        index, lspqAux = self.quantize(lsp[1], vd[1], vq[1])
        lspq.append(lspqAux)
        
        binary=format(index, self.indexFormat[1])
        bitsLSP.append(binary)
        
        for i in range(1, 10):
            
            index, lspqAux = self.quantize(lsp[i], vd[i], vq[i])
            lspq.append(lspqAux)
            
            while(lspq[i][0] < lspq[i-1][0]):
                index = index + 1
                lspq[i] = [vq[i][index]]
                
            binary = format(index, self.indexFormat[i] )
            bitsLSP.append(binary)
            
        return bitsLSP, lspq
       
    
        
        
    
    def decodeLSP(self, bits):
        vq = self.vq
        lspq=[]
        
        index=int(bits[0:3],2)
        lspq.append(vq[0][index])
        index=int(bits[3:7],2)
        lspq.append(vq[1][index])
    
        index=int(bits[7:11],2)
        lspq.append(vq[2][index])
    
        index=int(bits[11:15],2)
        lspq.append(vq[3][index])
    
    
        index=int(bits[15:19],2)
        lspq.append(vq[4][index])
    
    
        index=int(bits[19:22],2)
        lspq.append(vq[5][index])
        
        index=int(bits[22:25],2)
        lspq.append(vq[6][index])
    
        index=int(bits[25:28],2)
        lspq.append(vq[7][index])
    
        index=int(bits[28:31],2)
        lspq.append(vq[8][index])
        index=int(bits[31:34],2)
        lspq.append(vq[9][index])
    
        return lspq
    
    
    