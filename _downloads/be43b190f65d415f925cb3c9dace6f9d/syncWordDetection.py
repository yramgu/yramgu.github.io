#!/usr/bin/env python

import numpy as np
import scipy.signal
import matplotlib
matplotlib.use('tkAgg', force=True)
import matplotlib.pyplot as plt

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# ------------------------------------------------------------------ 
#                       MAIN CODE
# ------------------------------------------------------------------

if __name__ == "__main__":

    # bitstream
    recovered_bits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 
    1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 
    1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 
    1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 
    0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    # transform in NRZ
    recovered_bits = [-1 if x==0 else 1 for x in recovered_bits]

    # syncword we are looking for
    syncWord = 0xF9A8
    # autocorrelate sync word
    syncWord_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0] 
    # transform in NRZ
    syncWord_bits = [-1 if x==0 else 1 for x in syncWord_bits]

    # correlation
    correlated_data = scipy.signal.correlate(recovered_bits, syncWord_bits, mode='same')

    # Find the sync word position
    SynchroFrameIndex = np.argmax(correlated_data)
    print("index where synchro candidate was found: ",SynchroFrameIndex)
    print("synchro candidate: ",recovered_bits[int(SynchroFrameIndex-8):int(SynchroFrameIndex+8)])
    print("synchro wanted: ",syncWord_bits)

    # Sync word autocorrelation
    sync_autocorrelation = scipy.signal.correlate(syncWord_bits, syncWord_bits, mode='same')

    # ------------------------------------------------------------------ 
    #                       PLOT RESULTS
    # ------------------------------------------------------------------

    # --- Plot results

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

    #--------------------------- AX1 -----------------------------------
    ax1[0].plot(recovered_bits, label='')
    ax1[0].legend()
    ax1[0].set_title('Bitstream', c='blue')
    ax1[0].set_xlabel('Samples')
    ax1[0].set_ylabel('')

    ax1[1].plot(sync_autocorrelation, label='')
    ax1[1].legend()
    ax1[1].set_title('Sync word autocorrelationn', c='blue')
    ax1[1].set_xlabel('Samples')
    ax1[1].set_ylabel('Correlation level')

    #--------------------------- AX2 -----------------------------------

    ax2[0].plot(correlated_data, label='Sync Word correlation')
    ax2[0].plot(SynchroFrameIndex, correlated_data[SynchroFrameIndex], 'ro', label='Sync Word detected')
    ax2[0].legend()
    ax2[0].set_title('Sync word detection', c='blue')
    ax2[0].set_xlabel('Samples')
    ax2[0].set_ylabel('Correlation level')

    #-------------------------------------------------------------------

    fig.tight_layout()
    fig.subplots_adjust(wspace=0.1, hspace=0.35, bottom=0.08, top=0.92, left=0.06, right=0.95)

    plt.show()


