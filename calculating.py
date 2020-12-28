# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 09:05:59 2020

@author: Administrator
"""

import numpy as np
import os
from scipy import signal
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time
import random


def smoothing(data):
    _, ys = data[:, 1], data[:, 0]
    smoothed = gaussian_filter(ys, 17.)
    return smoothed


def curve_rotate(data, point, sita):
    x0, y0 = point
    data[:, 0] = (data[:, 0] - y0) * np.cos(sita) + (data[:, 1] - x0) * np.sin(sita)
    return data


def linearfunc(x, k, b):
    return k * x + b
def lrfitting(data,peakcouple,fitrange):
    couple_arg = []
    for i0, i1 in enumerate(peakcouple):
        i, ii = i1
        peakrange = np.array([x for x in range(i - fitrange[0], i + 1)])
        bottrange = np.array([x for x in range(ii, ii + fitrange[1])])
        if ii + fitrange[1] > len(data[:, 0]):
            bottrange = np.array([x for x in range(ii, len(data[:, 0]))])
        if i0 + 1 < len(peakcouple) and ii + fitrange[1] > peakcouple[i0 + 1][0]:
            bottrange = np.array([x for x in range(ii, peakcouple[i0 + 1][0])])
        try:
            popt_p, _ = curve_fit(linearfunc, data[:, 1][peakrange], data[:, 0][peakrange])
            popt_b, _ = curve_fit(linearfunc, data[:, 1][bottrange], data[:, 0][bottrange])
        except:
            popt_p = [0, 0]
            popt_b = [0, 0]
        couple_arg.append((popt_p, popt_b))
    return couple_arg

class cell_processing():
    def __init__(self):
        self.data = []
        self.filename_lst = []
        self.couple = []
        self.couple_arg = []
        self.spring_constant = 0
        self.log={'methods':{'src':r'E:\ZB\cell\20200929-ACE2-RBD\map-data-2020.09.29-18.14.05.322_processed-2020.12.28-16.42.19\processed_curves-2020.12.28-16.42.19',
                             'fitrange':[60,400]},
                  'result':{
                      'keep':{},
                      'discard':[],
                  }}

    def GetFileName(self, suffix='txt'):
        for a, b, c in os.walk(self.log['methods']['src']):
            for i in c:
                if i.endswith(suffix):
                    self.filename_lst.append(os.path.join(a, i))
            break

    def GetData(self, index):
        if len(self.filename_lst) > index:
            name = self.filename_lst[index]
            with open(name, 'r') as f:
                x = f.read()
            lst = x.split('\n')
            lst1 = np.array([0., 0.])
            data = np.array([0., 0.])
            j = False
            for i in lst:
                if 'springConstant' in i:
                    self.spring_constant = float(i.split()[-1]) * 1e12 / 1e9
                if 'retract' in i:
                    j = True
                if 'extend' in i:
                    j = False
                if '#' in i or not i:
                    continue
                elif j:
                    lst1[0], lst1[1] = float(i.split(' ')[1]) * -1 * 1e12, float(i.split(' ')[0]) * 1e9
                    data = np.vstack((data, np.array(lst1)))
            data[:, 1] = data[:, 1] - np.abs(data[:, 0] / self.spring_constant)
            return True, data[1:]
        else:
            return False, 'index out of range'



    def findkneed(self, index):
        data = self.GetData(index)[1]
        dataAftersmooth = smoothing(data)
        bott, _ = signal.find_peaks(np.gradient(np.gradient(dataAftersmooth)), height=0.012, distance=80,
                                    prominence=0.015)
        peak, _ = signal.find_peaks(np.gradient(np.gradient(dataAftersmooth)) * -1, height=0.008, distance=80,
                                    prominence=0.01)
        couple = []
        for _,i in enumerate(peak):
            try:
                peak[_]=np.arange(i-10,i+11)[np.argmax(data[:,0][np.arange(i-10,i+11)])]
            except:
                pass

        for i in peak:
            if len(np.abs(data[:, 1][i] - data[:, 1][bott])) == 0:
                continue
            ii = bott[np.argmin(np.abs(data[:, 1][i] - data[:, 1][bott]))]
            if ii - i < 50 and data[:, 0][i] > data[:, 0][ii] + 15 and ii > i:
                couple.append((i, ii))
        if len(couple) == 0:
            self.log['result']['discard'].append(self.filename_lst[index])
            return False
        couple_arg = lrfitting(data,couple,self.log['methods']['fitrange'])
        theta = np.arctan(couple_arg[0][1][0]) * -1
        point = (data[:, 1][couple[0][1]], data[:, 0][couple[0][1]])
        data = curve_rotate(data, point, theta)
        couple_arg = lrfitting(data, couple, self.log['methods']['fitrange'])
        self.log['result']['keep'][self.filename_lst[index]]={}
        self.log['result']['keep'][self.filename_lst[index]]['index']=index
        for i,arg in enumerate(couple_arg):
            self.log['result']['keep'][self.filename_lst[index]]['theta'] = theta
            self.log['result']['keep'][self.filename_lst[index]]['peakindex']=couple[i][0]
            self.log['result']['keep'][self.filename_lst[index]]['peak_k'] = couple_arg[i][0][0]
            self.log['result']['keep'][self.filename_lst[index]]['peak_b'] = couple_arg[i][0][1]
            self.log['result']['keep'][self.filename_lst[index]]['bottindex'] = couple[i][1]
            self.log['result']['keep'][self.filename_lst[index]]['bott_k'] = couple_arg[i][1][0]
            self.log['result']['keep'][self.filename_lst[index]]['bott_b'] = couple_arg[i][1][1]
            break
        return True
    def run(self):
        import time
        self.GetFileName()
        t1 = time.time()
        for i,_ in enumerate(self.filename_lst):
            if self.findkneed(i):
                print('success')
            else:
                print('failed')
            print('Num.{}/Total.{}'.format(i,len(self.filename_lst)))
        t2=time.time()
        print('Average time.{}s\nTotal time.{}s'.format((t2-t1)/(i+1),t2-t1))
    def graph(self,filename):
        index = self.filename_lst.index(filename)
        data = self.GetData(index)[1]
        dic = self.log['result']['keep'][filename]
        peak_index = dic['peakindex']
        peak_k = dic['peak_k']
        peak_b = dic['peak_b']
        bott_index = dic['bottindex']
        bott_k = dic['bott_k']
        bott_b = dic['bott_b']
        theta = dic['theta']
        point = data[:,1][bott_index],data[:,0][bott_index]
        data = curve_rotate(data, point, theta)
        data[:,0] = data[:,0]-bott_b
        peak_b = peak_b - bott_b
        bott_b = 0
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(data[:,1],data[:,0])
        print(peak_index)
        ax.plot(data[:,1][peak_index],data[:,0][peak_index],'ro')
        ax.plot(data[:, 1][bott_index], data[:, 0][bott_index], 'o',color='purple')
        x_ = np.arange(data[:, 1][peak_index] - 200, data[:, 1][peak_index], 0.1)
        y_ = linearfunc(x_, peak_k,peak_b)
        ax.plot(x_,y_,'-.')
        x_ = np.arange(data[:, 1][bott_index], data[:, 1][bott_index]+200, 0.1)
        y_ = linearfunc(x_, bott_k, bott_b)
        ax.plot(x_, y_, '-.')
        plt.close()
        return fig
'''
if __name__=='__main__':
    cp = cell_processing()
    cp.run()
    '''
