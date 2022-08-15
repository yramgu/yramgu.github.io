===========================
BPSK demodulation
===========================

This page will walk you through all the steps to demodulate a BPSK waveform using Python.

BPSK crash-course
===========================

The BPSK modulation is a very simple, yet very robust modulation. BPSK stands for "Binary Phase Shift Keying".
It simply consists of alternating a carrier phase between :math:`0` and :math:`\pi` radian depending on whether were are transmitting a '1' or a '0'.
Mathematically speaking, a bpsk-modulated carrier can be expressed by 

.. math::

    s(t) = Acos(2 \pi f_c t + \theta_0 + \theta_m)

where

- :math:`A =` signal amplitude
- :math:`fc =` carrier frequency
- :math:`\theta_0 =` initial phase offset
- :math:`\theta_m \in \{0, \pi\}` = phase modulation

The time-domain waveform is displayed below. Everytime we change bit, the carrier wave
is reversed, which is what a phase change from :math:`0` to :math:`\pi` (or vice-versa) does.

.. _bpsk_ideal_constellation:
.. figure:: bpsk_ideal_constellation.svg
    :align: center
    :scale: 100%

    BPSK representation

Since we have two phase states :math:`0` and :math:`\pi`, the :math:`I/Q` constellation has two symbols 
with amplitude +/-1 positionned on the :math:`I` (in-phase) axis. The :math:`Q` (quadrature) component
is null. When we transition from one symbol to the other, we travel **through the center** of the unit circle.
This produces nulls in the signal enveloppe at each transition. The example below shows a BPSK IQ waveform 
(filtered by a gaussian filter) and resulting enveloppe where we can see the nulls at each symbol transition:

.. _bpsk_ideal_iq:
.. figure:: bpsk-ideal-iq.svg
    :align: center
    :scale: 100%

    BPSK IQ exemple and resulting enveloppe

The BPSK Bit-Error-Rate (BER) is given by [1]_:

.. math::

    BER = \frac{1}{2}erfc\Biggl(\sqrt{\frac{E_b}{N_0}}\Biggl)

with

- :math:`E_b =` bit energy
- :math:`N_0 =` noise spectral density (Noise power in 1Hz bandwidth)

from this we can plot the BER as a function of SNR:

.. Attention::
    missing image

This plot shows us that for a typical BER value of :math:`10^{-3}` we need an SNR of ~6/7dB.

BPSK demodulation example
===========================

.. admonition:: The full python code for this example is available
   :class: pythonCode

   :download:`download here <../Scripts/bpsk-demod.zip>`

   Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

For this exercise, we will work with a BPSK waveform with the following characteristics:

+------------------+-------------------------------------+
| File name        |  bpsk_waveform.wav                  |
+------------------+-------------------------------------+
| Sampling rate    |  100 kHz                            |
+------------------+-------------------------------------+
| Baudrate         |  100 bps                            |
+------------------+-------------------------------------+
| Encoding         |  Differential ('1' = keep phase)    |
+------------------+-------------------------------------+
| CRC polynomial   |  :math:`X^{16} + X^{12} + X^5 + 1`  |
+------------------+-------------------------------------+

The message has the following structure:

+------------------------+-----------------------+----------------------+---------------------------------------+
| **Preamble**: 0xAAAAAA | **Sync Word**: 0xF9A8 | **Payload**: 8 bytes | **CRC**: CRC16 (computed from payload)|
+------------------------+-----------------------+----------------------+---------------------------------------+

The goal, of course, is to decode the payload.

Open the WAV file and inspect
==============================

We open the WAV file and plot the IQ data and FFT:

.. _bpsk_iq_fft:
.. figure:: bpsk_iq_fft.svg
    :align: center
    :scale: 100%

    IQ data and FFT

The IQ data looks very different to the one shown in the crash-course section: it looks much more "dense", and the quadrature
path is not zero. This is easily explained by the FFT: a baseband signal should be centered around DC. Here however, the signal is offset by +12kHz.
Therefore our bpsk signal is "riding" on a 12kHz carrier. That's why the quadrature path is not zero, and why the 
IQ data looks so dense: zooming in shows us the 12 kHz carrier with ~83ms period.

.. _bpsk_iq_12k_zoom:
.. figure:: bpsk_iq_12k_zoom.svg
    :align: center
    :scale: 100%

    IQ data zoom

Coarse frequency correction
==============================

First, we want to bring our signal back closer to DC. There are multiple ways of doing this, more or less complex,
but we'll choose an easy path. Since we have the FFT (and no visible interferer), we can just take the highest
peak in the FFT (which will be located in our signal of interest), call that our "Coarse frequency offset" and rotate the signal back to DC.

How do we rotate? That's very easy: we multiply by a complex exponential. Recall from trigonometry that 

.. math::

    A\Bigl[ cos(2 \pi f_c t) + jsin(2 \pi f_c t) \Bigl] = Ae^{2 \pi f_c t}

This is called a phasor, which is represented in the complex plane by a rotating vector of amplitude :math:`A`. 
Let's consider a phasor :math:`p` at frequency :math:`f_0` given by :math:`e^{2 \pi f_0 t}`. We want to translate it 
by another frequency :math:`f_1` to the left so we do

.. math::

    p(t) = e^{2 \pi (f_0 - f_1) t} = e^{(2 \pi f_0 t) - (2 \pi f_1 t)} = e^{2 \pi f_0 t} \times  e^{- 2 \pi f_1 t}

If we apply this to our BPSK waveform, we multiply it by an exponential with frequency -12kHz and we get our spectrum shifted near DC:

.. _bpsk_rotated_iq_fft:
.. figure:: bpsk_rotated_iq_fft.svg
    :align: center

    rotated waveform

The IQ waveforms look better, however still different from the ideal one shown in the crash-course section,
and we still have a quadrature component. This means two things:

- The constellation has a (static) phase offset
- There is a residual frequency Offset

.. Note::
    At this stage, any sane engineer would decimate. We are looking at a 100bps signal sampled at 100ksps, i.e. 1000 samples/symbol!
    We could easily decimate by 50 or 100 to get respectively 20 or 10 samples/symbols.
    For this article I thought the plots looked nicer with the original sampling rate so I didn't bother. Unfortunately it seems like this
    website is all about looks...

Fine frequency correction and demodulation: the Costas loop
===========================================================

The costas loop is the most central piece. A costas loop is a quadrature PLL designed for carrier phase recovery, invented by
John Costas in 1956 [2]_.
After coarse frequency offset correction, the Costas loop will take care of any remaining frequency offset, and will also eliminate any
static phase offset. It is often used to demodulate BPSKs or QPSKs, as the baseband data can be directly extracted from the loop.
The block diagram of a costas loop for BPSK demodulation is:

.. _bpsk_costas_diagram:
.. figure:: bpsk-costas-diagram.svg
    :align: center
    :scale: 100%

    Costas loop diagram

Let's do some basic math analysis:

Our input signal is the received signal :math:`r(t) = m_{bb}(t)cos(\omega_0t + \theta)`, with

- :math:`m_{bb}(t)` the BPSK symbols (+/-1)
- :math:`cos(\omega_0t + \theta)` the carrier wave of frequency :math:`\omega_0` and phase offset :math:`\theta`

The input signal goes into a quadrature mixer. On the :math:`I` arm we have:

.. tip::
    Use the trigonometric identity: :math:`cos(\alpha).cos(\beta) = 0.5\Bigl[cos(\alpha + \beta) + cos(\alpha - \beta)\Bigl]`

.. math::

    \begin{align}
        x_I(t)& = m_{bb}(t)cos(\omega_0t + \theta) \times 2cos(\omega_0t + \phi) \\
               &= m_{bb}(t)\Bigl[cos(\theta - \phi) + cos(2 \omega_0 t + \theta + \phi)\Bigl]
    \end{align}

The double frequency term is eliminated by the low-pass filter and we are left with 

.. math::

    x_{LPI}(t) = m_{bb}(t)cos(\theta - \phi)

Likewise on the :math:`Q` arm we have:

.. tip::
    Use the trigonometric identity: :math:`cos(\alpha).sin(\beta) = 0.5\Bigl[sin(\alpha + \beta) - sin(\alpha - \beta)\Bigl]`

.. math::

    \begin{align}
        x_Q(t)& = m_{bb}(t)cos(\omega_0t + \theta) \times -2sin(\omega_0t + \phi) \\
              & = m_{bb}(t)\Bigl[sin(\theta - \phi) - sin(2 \omega_0 t + \theta + \phi)\Bigl]
    \end{align}

The double frequency term is eliminated by the low-pass filter and we are left with 

.. math::

    x_{LPQ}(t) = m_{bb}(t)sin(\theta - \phi)

Then we multiply the I and Q branch together so we get:

.. math::

    \begin{align}
        x_{LF}(t) &= m_{bb}^2(t)cos(\theta - \phi)sin(\theta - \phi) \\ 
                  &= m_{bb}^2(t)sin\Bigl(2(\theta-\phi)\Bigl)
    \end{align}

For a BPSK, :math:`m_{bb}^2(t) = 1`, so we end up up with :math:`x_{LF}(t) = sin(2(\theta-\phi))`. The error
has a sinusoidal shape and the loop will settle (just like with a classic PLL) in the linear region around :math:`\theta-\phi \approx 0°`. For small angles
we know that :math:`sin(\theta) \approx \theta` therefore the error signal becomes :math:`2(\theta-\phi)`.

The loop filter is usually a proportional-integral (PI) structure. For dimensioning the PI and more generally the loop, we can consider
the loop to behave exactly like a classic PLL. The figure below represents a 2nd order complex PLL, in the digital domain:

.. _bpsk_pll:
.. figure:: bpsk-pll.svg
    :align: center
    :scale: 100%

    2nd order PLL

The digital PLL's behaviour depends on three parameters [3]_ [4]_:

- The damping factor :math:`\zeta`
    The typical value of 0.707 is suitable for the vast majority of cases 

- The sampling frequency :math:`F_s`
    Sampling frequency of the system in Hz

- The equivalent Noise bandwidth :math:`B_n`
    Loop bandwidth in Hz
    
    :math:`B_n` is related to :math:`\zeta` and the natural frequency of the loop :math:`\omega_n` by
    :math:`B_n = \frac{\omega_n}{2} \Bigl(\zeta + \frac{1}{4\zeta}\Bigl)`

    :math:`B_n` is however often simply chosen in function of :math:`F_s`, as a value between 1% and 5% of :math:`F_s`

The proportional and integral gains :math:`K_p` and :math:`K_I` of the loop filter are then approximated by:

.. math::

    \begin{align}
        K_p &\approx \frac{1}{K_D K_0}\times\frac{4\zeta}{\zeta + \frac{1}{4\zeta}}\times\frac{B_n}{F_s} \\
        K_I &\approx \frac{1}{K_D K_0}\times\Biggl(\frac{4}{\zeta + \frac{1}{4\zeta}}\Biggl)^2\times\Biggl(\frac{B_n}{F_s}\Biggl)^2 
    \end{align}

with

- :math:`K_0` the NCO gain, that can simply be set to 1

- :math:`K_D` the phase detector gain, that depends on the PLL structure (typically 0.5 or 1)

In our exemple, we set :math:`K_0 = K_D = 1`, :math:`\zeta=0.707`, :math:`B_n=1\%(F_s)`, and :math:`F_s=100ksps` (from our WAV file).
This gives us :math:`K_p = 0.026664` and :math:`K_I = 0.000355`. We run the loop and we extract :math:`x_{LPI}(t)`
and :math:`x_{LPQ}(t)`:

.. _bpsk_costas_output:
.. figure:: bpsk-costas-output.svg
    :align: center
    :scale: 100%

    Costas loop output

Now we're getting somewhere! The loop has locked very quickly and has eliminated any phase or frequency offset.
The in-phase branch now looks like a BPSK modulating signal, and the quadrature branch has been cancelled out.

This is good. We can visually see our bits; however we won't extract them manually, we want Python to do the work for us.
But how can the program know when to sample a bit? Remember our baseband signal has a bitrate of 100bps,
but our sampling frequency is 100kHz! That's 1000 samples per bit! Fortunately, algorithms exist that will
do this for us, and this is our next step.

Timing recovery
==============================

.. note:: 

    This step is usually done earlier, before the Costas loop; but for the purpose of this article and illustration 
    I thought it was more relevant to do it here

In order to know when to sample our symbols, we need a timing recovery mechanism. This is done with a Time Locked Loop (or TLL) 
using a Timing Error Detector (TED) algorithm:

.. _bpsk_tll:
.. figure:: bpsk-tll.svg
    :align: center
    :scale: 100%

    Time Locked Loop

The most interesting part here is the TED. There are plenty of different algorithms, and for this article I chose a very
simple one particularly suited to BPSK: the Gardner TED [5]_. The Gardner TED is part of a family of so-called 
"Early-Late" algorithms. The concept is fairly simple:

.. _bpsk_gardner:
.. figure:: bpsk-gardner.svg
    :align: center

    Gardner algorithm illustration

The Gardner equation giving the timing error is:

.. math::

    e[n] = \biggl(r\Bigl[nT_M + \varepsilon\Bigl] - r\Bigl[(n-1)T_M + \varepsilon\Bigl]\biggl) \times r\Bigl[nT_M - \frac{T_M}{2} + \varepsilon\Bigl]  

We note the symbol period :math:`T_M`. The algorithm will evaluate a symbol at time :math:`nT_M` and  
the preceding one at time :math:`(n-1)T_M` (the two red dots), take the difference and multiply by the middle point at 
time :math:`T_M\Bigl(n-\frac{1}{2}\Bigl)` (orange dot). 

In the illustration above, we have:

- :math:`(a) \quad e[n] = (-0.8-0.8) \times (+0.2) = -0.32`: A timing advance yields a negative error
- :math:`(b) \quad e[n] = (-0.8-0.8) \times (-0.2) = +0.32`: A timing delay yields a positive error
- :math:`(c) \quad e[n] = (-1-1) \times 0 = 0`: A perfect timing yields zero error

What we want is to sample the symbols at the right time, so we need to add an error term
:math:`\varepsilon` to the sampling instant. It becomes obvious that in order to do this the signal needs
to be interpolated/oversampled. This algorithm can't function if our input signal comes at a rate of 1 sample/symbol.
We need to oversample so that if we are sampling too early, we can adjust :math:`\varepsilon` to sample slightly
later at the next iteration (and vice-versa if we were sampling too late). In our example we have 1000 samples/symbol
which is way more than required (I would recommend 10 samples/symbol or more).

At each iteration the TED needs to go through a control loop in order to make the error converge to 0.
Similar to the PLL, the loop filter is quite a often a proportional-integral (PI) filter. In this example
I simplified it to a mere proportional (P) gain :math:`K_p`, which actually works quite well. 

The gain :math:`K_p` was deliberately set to a poor value in order to degrade the performance of the loop and 
see how it converges:

.. _bpsk_ted:
.. figure:: bpsk-ted.svg
    :align: center
    :scale: 100%

    Output of the TLL

The red dots indicate the sampling instants of the TLL. At the beginning the TLL is 
not sampling at the right time and is slowly converging to a lock state, which it reaches at about 200ms. The 
right-hand side picture shows us a zoom between 300ms and 450ms, where we can see that the symbols are sampled 
exactly where they should be. As an exercice you can modify the TLL :math:`K_p` in the code to improve the performance.

Now that we know where to sample our symbols, we can synchronise. The figure below shows us the constellation
before the TLL (left) and after the TLL (right). The few samples that are not located at +/1 on the :math:`I`
axis are the ones obtained during the convergence phase.

.. _bpsk_ted_constellations:
.. figure:: bpsk-ted_constellation.svg
    :align: center
    :scale: 100%

    Constellation before and after time synchronisation

We can also plot the EVM per symbol which also shows us the convergence of the TLL. When we are not synchronized
the EVM is really bad, then gradually improves to settle to its actual value around -25dB:

.. _bpsk_evm:
.. figure:: bpsk-evm.svg
    :align: center
    :scale: 100%

    EVM plot

Decoding the payload
==============================

We have retrieved our symbols, now we need to look for the synchronisation word in order to identify where the payload 
begins. 

As stated at the beginning of the example, the data is differentially encoded: A '1' is encoded by **not** changing
phase, and a '0' is encoded by changing phase. Applying the reverse encoding is trivial:

.. code-block:: python

    # apply reverse differential encoding, NRZ output format
    decoded_bits = []
    previous_bit = 0
    for bit in bits:
        if bit == previous_bit: decoded_bits.append(1)
        else:
            previous_bit = bit
            decoded_bits.append(-1)

.. code-block:: python

    decoded_bit = [-1, 1, 1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 
                    1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1, 1, 1, -1, 1, -1, 1, -1, 
                    1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 
                    1, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, 1, -1, 1,
                    -1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1]

After removing the differential encoding, we correlate the resulting  bit stream with the binary representation of the 
sync word:

.. code-block:: python

    0xF9A8 = [1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1]

.. _bpsk_syncWord:
.. figure:: bpsk-syncWord.svg
    :align: center
    :scale: 100%

    Correlation of data with sync word

We detect a clear maximum at index 27. Since the word is 16-bit long, the payload starts at index 27+16/2=35.
Our payload is 8 bytes long so we extract 64 bits starting at index 35 and we get (going back to unipolar format):

.. code-block:: python

    Payload: [1 1 0 1 1 1 1 0 1 0 1 0 1 1 0 1 1 0 1 1 1 1 1 0 1 1 1 0 1 1 1 1 1 1 0 0 1 0 1 0 1 1 1 1 1 1 1 0 1 0 1 1 1 0 1 0 1 1 0 1 0 0 0 0]

Which in hexadecimal is: 

.. code-block:: python

    [0xDE 0xAD 0xBE 0xEF 0xCA 0xFE 0xBA 0xD0] 

But we still need to make sure this data is valid, by checking the CRC.

Checking the CRC
==============================

The CRC (Cyclic Redundancy Check) is a mechanism that allows us to verify the integrity of our message [6]_.
Acccording to our frame structure, the CRC  is 16-bits long, placed right after the payload. 
If we extract those bits from the decoded bits array previously obtained, we get our received CRC:

.. code-block:: python

    CRC received: [0 1 0 1 0 1 1 0 0 0 0 0 1 1 0]

Since the CRC was originally computed from the payload data, we recalculate the CRC from the payload data we received in order 
to check if we get the same value as the CRC we received. 

A CRC is based on polynomial division with modulo-2 arithmetic and can be obtained from 
a linear shift register (LFSR) [6]_. With a polynomial of :math:`X^{16} + X^{12} + X^5 + 1`, its diagram representation is:

.. _bpsk_crc:
.. figure:: bpsk-crc.svg
    :align: center
    :scale: 100%

    CRC diagram

We calculate the CRC and we get:

.. code-block:: python

    CRC calculated: [0 1 0 1 0 1 1 0 0 0 0 0 1 1 0]

Success! The calculated CRC matches the one contained in the message, so we have verified our message integrity.

Now it's your turn to explore the code and learn from it.


References
==============================

.. [1] https://www.gaussianwaves.com/2012/07/intuitive-derivation-of-performance-of-an-optimum-bpsk-receiver-in-awgn-channel/
.. [2] J.Costas, "Synchronous communications", Proceedings of the IRE. 44(12): 1713–1718, 1956
.. [3] https://wirelesspi.com/phase-locked-loop-pll-in-a-software-defined-radio-sdr/
.. [4] M.Rice, Digital Communications – A Discrete-Time Approach, Prentice Hall, 2009
.. [5] F.Gardner, "A BPSK/QPSK Timing-Error Detector for Sampled Receivers", IEEE Transactions on Communications, Volume 34 Issue 4, p423-429, 1986
.. [6] W.W. Peterson, "Cyclic codes for error detection", Proceedings of the IRE. 49(1): 228-235, 1961