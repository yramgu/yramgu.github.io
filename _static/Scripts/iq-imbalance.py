#!/usr/bin/env python

"""
MIT License

Copyright (c) 2022 Yannish RAMGULAM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

import numpy as np
import copy

import matplotlib
matplotlib.use('tkAgg', force=True)
import matplotlib.pyplot as plt

import logging

class modulationClass:
  def __init__(self, name=""):
    self.name       = name
    self.I          = np.array([1, 1, 3, 3, 1, 1, 3, 3, -1, -1, -3, -3, -1, -1, -3, -3]) / np.sqrt(10)
    self.Q          = np.array([1, 3, 1, 3, -1, -3, -1, -3, 1, 3, 1, 3, -1, -3, -1, -3]) / np.sqrt(10)
    self.symbols    = np.array(['0000, 0001, 0010, 0011, 0100, 0101, 0110, 0111, 1000, 1001, 1010, 1011, 1100, 1101, 1110, 1111'])

if __name__ == "__main__":

    QAM = modulationClass('16-QAM')

    QAM_DC = copy.deepcopy(QAM)
    DC_offset = 0.25
    for i, (I, Q) in enumerate(zip(QAM_DC.I, QAM_DC.Q)):
        QAM_DC.Q[i] = Q + DC_offset
        QAM_DC.I[i] = I + DC_offset

    QAM_Gain = copy.deepcopy(QAM)
    gain_offset = 1.5
    for i,Q in enumerate(QAM_Gain.Q):
        QAM_Gain.Q[i] = Q * gain_offset
    
    QAM_Phase = copy.deepcopy(QAM)
    phase_offset = 20 # degrees
    for i, (I, Q) in enumerate(zip(QAM_Phase.I, QAM_Phase.Q)):
        QAM_Phase.Q[i] = Q * np.cos(phase_offset*2*np.pi/360) 
        QAM_Phase.I[i] = I + Q * np.sin(phase_offset*2*np.pi/360)

    # ============================   Plot results   ======================================
    
    SMALL_SIZE = 12
    MEDIUM_SIZE = 14
    BIGGER_SIZE = 16

    plt.rc('font', size=SMALL_SIZE)                 # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)           # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)           # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)           # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)           # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)           # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)         # fontsize of the figure title
    plt.rc('lines', linewidth=1.5, markersize=6)    # line parameters

    fig, (ax1, ax2) = plt.subplots(2, 2, sharex=False)
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    scale = 2

    # no impairment
    ax1[0].set_title('(a) ' + QAM.name+' / no impairment', color='b')
    ax1[0].scatter(QAM.I, QAM.Q, c='r')
    ax1[0].set_xlabel('I')
    ax1[0].set_ylabel('Q')
    ax1[0].axis('scaled')
    ax1[0].set_xlim(left=-scale, right = scale)
    ax1[0].set_ylim(top=scale, bottom = -scale)
    ax1[0].axvline(0, c='grey')
    ax1[0].axhline(0, c='grey')

    # dc offset
    ax1[1].set_title('(b) ' + QAM.name+' / DC offset', color='b')
    ax1[1].scatter(QAM_DC.I, QAM_DC.Q, c='r')
    ax1[1].set_xlabel('I')
    ax1[1].set_ylabel('Q')
    ax1[1].axis('scaled')
    ax1[1].set_xlim(left=-scale, right = scale)
    ax1[1].set_ylim(top=scale, bottom = -scale)
    ax1[1].axvline(0, c='grey')
    ax1[1].axhline(0, c='grey')

    # gain imbalance
    ax2[0].set_title('(c) ' + QAM.name+' / Gain imbalance', color='b')
    ax2[0].scatter(QAM_Gain.I, QAM_Gain.Q, c='r')
    ax2[0].set_xlabel('I')
    ax2[0].set_ylabel('Q')
    ax2[0].axis('scaled')
    ax2[0].set_xlim(left=-scale, right = scale)
    ax2[0].set_ylim(top=scale, bottom = -scale)
    ax2[0].axvline(0, c='grey')
    ax2[0].axhline(0, c='grey')

    # phase imbalance
    ax2[1].set_title('(d) ' + QAM.name+' / Phase imbalance', color='b')
    ax2[1].scatter(QAM_Phase.I, QAM_Phase.Q, c='r')
    ax2[1].set_xlabel('I')
    ax2[1].set_ylabel('Q')
    ax2[1].axis('scaled')
    ax2[1].set_xlim(left=-scale, right = scale)
    ax2[1].set_ylim(top=scale, bottom = -scale)
    ax2[1].axvline(0, c='grey')
    ax2[1].axhline(0, c='grey')

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.15, hspace=0.35, bottom=0.07, top=0.95, left=0.05, right=0.98)

    plt.show()
    


