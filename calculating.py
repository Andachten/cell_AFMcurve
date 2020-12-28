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


def ppdistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    d = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    return d


def linearfunc(x, k, b):
    return k * x + b


class cell_processing():
    def __init__(self, filedir):
        self.filedir = filedir
        self.data = []
        self.filename_lst = []
        self.couple = []
        self.couple_arg = []
        self.fitrange = [0, 400]
        self.spring_constant = 0

    def GetFileName(self, suffix='txt'):
        for a, b, c in os.walk(self.filedir):
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

    def lrfitting(self):
        data = self.data
        couple_arg = []
        for i0, i1 in enumerate(self.couple):
            i, ii = i1
            peakrange = np.array([x for x in range(i - 60, i + 1)])
            bottrange = np.array([x for x in range(ii, ii + self.fitrange[1])])
            if ii + self.fitrange[1] > len(self.data[:, 0]):
                bottrange = np.array([x for x in range(ii, len(self.data[:, 0]))])
            if i0 + 1 < len(self.couple) and ii + self.fitrange[1] > self.couple[i0 + 1][0]:
                bottrange = np.array([x for x in range(ii, self.couple[i0 + 1][0])])
            try:
                popt_p, _ = curve_fit(linearfunc, data[:, 1][peakrange], data[:, 0][peakrange])
                popt_b, _ = curve_fit(linearfunc, data[:, 1][bottrange], data[:, 0][bottrange])
            except:
                popt_p = [0, 0]
                popt_b = [0, 0]
            couple_arg.append((popt_p, popt_b))
        self.couple_arg = couple_arg

    def curve_rotate(self, point, sita):
        x0, y0 = point
        self.data[:, 0] = (self.data[:, 0] - y0) * np.cos(sita) + (self.data[:, 1] - x0) * np.sin(sita)
        return self.data

    def findkneed(self, index, pkrange=[10, 70]):
        self.GetFileName()
        data = self.GetData(index)[1]
        self.data = data
        dataAftersmooth = smoothing(data)
        bott, _ = signal.find_peaks(np.gradient(np.gradient(dataAftersmooth)), height=0.012, distance=80,
                                    prominence=0.015)
        peak, _ = signal.find_peaks(np.gradient(np.gradient(dataAftersmooth)) * -1, height=0.008, distance=80,
                                    prominence=0.01)
        couple = []
        for i in peak:
            if len(np.abs(data[:, 1][i] - data[:, 1][bott])) == 0:
                continue
            ii = bott[np.argmin(np.abs(data[:, 1][i] - data[:, 1][bott]))]
            if ii - i < 50 and data[:, 0][i] > data[:, 0][ii] + 15 and ii > i:
                couple.append((i, ii))
        self.couple = couple
        self.lrfitting()

        fig = plt.figure()
        bx = fig.add_subplot(211)
        bx.plot(data[:, 1], data[:, 0])
        for i, ii in enumerate(couple):
            bx.plot(data[:, 1][ii[0]], data[:, 0][ii[0]], 'ro')
            x_ = np.arange(data[:, 1][ii[0]] - 200, data[:, 1][ii[0]], 0.1)
            y_ = linearfunc(x_, *self.couple_arg[i][0])
            bx.plot(x_, y_, '-.', color='r', linewidth=2)
            bx.plot(data[:, 1][ii[1]], data[:, 0][ii[1]], 'o', color='purple')
            x_ = np.arange(data[:, 1][ii[1]], data[:, 1][ii[1]] + 400, 0.1)
            y_ = linearfunc(x_, *self.couple_arg[i][1])
            bx.plot(x_, y_, '-.', color='purple', linewidth=2)

        if len(self.couple) == 0:
            return False
        sita = np.arctan(self.couple_arg[0][1][0])
        data = self.curve_rotate(point=(data[:, 1][self.couple[0][1]], data[:, 0][self.couple[0][1]]), sita=sita * -1)
        self.lrfitting()

        ax = fig.add_subplot(212)
        ax.plot(data[:, 1], data[:, 0])
        for i, ii in enumerate(couple):
            ax.plot(data[:, 1][ii[0]], data[:, 0][ii[0]], 'ro')
            x_ = np.arange(data[:, 1][ii[0]] - 200, data[:, 1][ii[0]], 0.1)
            y_ = linearfunc(x_, *self.couple_arg[i][0])
            ax.plot(x_, y_, '-.', color='r', linewidth=2)
            ax.plot(data[:, 1][ii[1]], data[:, 0][ii[1]], 'o', color='purple')
            x_ = np.arange(data[:, 1][ii[1]], data[:, 1][ii[1]] + 400, 0.1)
            y_ = linearfunc(x_, *self.couple_arg[i][1])
            ax.plot(x_, y_, '-.', color='purple', linewidth=2)
        fig.savefig(str(time.time()) + str(random.randint(1, 9)) + '.jpg', dpi=100)
        plt.show()
        plt.close()

