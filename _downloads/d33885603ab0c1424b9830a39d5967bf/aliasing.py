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

import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('tkAgg', force=True)
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == "__main__":
    # --- Constants
    Fs = 10000
    Fw = 100
    Fi = 700
    N = 1000
    Np = 1e-3
    t = np.arange(N)/Fs
    decimation_factor = 10

    # build signal x with Wanted + Interferer
    W = np.cos(2*np.pi*Fw*t)
    I = np.cos(2*np.pi*Fi*t)
    x = W+I

    # add some noise
    x += np.random.normal(scale=np.sqrt(Np), size=t.shape)

    # calculate spectrum of x
    f, Pxx = signal.welch(x, Fs, nperseg=N, return_onesided=True, scaling='spectrum', window='hanning')
    Pxx_dB = 10*np.log10(Pxx)

    # downsample by dropping one out of every 10 sample
    # and calculate spectrum
    x2 = x[::decimation_factor]
    f2, Pxx2 = signal.welch(x2, Fs/decimation_factor, nperseg=len(x2), return_onesided=True, scaling='spectrum', window='hanning')
    Pxx_dB2 = 10*np.log10(Pxx2)

    # Decimate properly (LPF + downsampling) by a factor of 10
    # and recalculate spectrum
    x3 = signal.decimate(x, decimation_factor, ftype='fir')
    f3, Pxx3 = signal.welch(x3, Fs/decimation_factor, nperseg=len(x3), return_onesided=True, scaling='spectrum', window='hanning')
    Pxx_dB3 = 10*np.log10(Pxx3)


    # ============================   Plot results   ======================================

    SMALL_SIZE = 6
    MEDIUM_SIZE = 8
    BIGGER_SIZE = 10

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.rc('lines', linewidth=1)             # fontsize of the figure title

    fig, (ax1, ax2) = plt.subplots(2, 2, sharex=False)

    ax1[0].plot(t, x)
    ax1[0].set_xlabel('time [s]')
    ax1[0].set_ylabel('Amplitude')
    ax1[0].set_title('Plot 1 - Signal', c='blue')

    ax1[1].plot(f/1000, Pxx_dB)
    ax1[1].set_xlabel('Frequency [kHz]')
    ax1[1].set_ylabel('Amplitude (dB)')
    ax1[1].set_title('Plot 2 - Signal FFT', c='blue')


    ax2[0].plot(f2/1000, Pxx_dB2)
    ax2[0].set_xlabel('Frequency [kHz]')
    ax2[0].set_ylabel('Amplitude (dB)')
    ax2[0].set_title('Plot 3 - Signal FFT after downsampling only', c='blue')

    ax2[1].plot(f3/1000, Pxx_dB3)
    ax2[1].set_xlabel('Frequency [kHz]')
    ax2[1].set_ylabel('Amplitude (dB)')
    ax2[1].set_title('Plot 4 - Signal FFT after LPF + downsampling', c='blue')

    #----

    fig.tight_layout()
    """
    fig.subplots_adjust(top=0.974,
    bottom=0.112,
    left=0.068,
    right=0.987,
    hspace=0.298,
    wspace=0.1)
    """
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()

    plt.show()


