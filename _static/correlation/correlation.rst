===========================
Correlation
===========================

Correlation (or more specifically `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`__) is one of the main tools used in DSP. Mathematically speaking, 
the (discrete) correlation between two signals :math:`x` and :math:`h` is given by:

.. math::

    x_{corr}[n] = \sum_{m=-\infty}^{m=+\infty} x[m] h[m-n]

where :math:`n` represents a time delay. It looks very similar to convolution,
but it's ultimately not the same thing. What correlation between two signals does
is essentially 'measuring' how much the signals are similar to each other. The more 
similarities, the higher the correlation output. This is very
useful for a number of things, and a few pratical examples are presented below.

Correlation can be done in python with a dedicated function from scipy:

.. code-block:: python
    :emphasize-lines: 1

    correlation_result = scipy.signal.correlate(signal_1, signal_2)

Matched filtering
===========================

Matched fitering is the process of correlating an unknown signal with a reference
waveform. The reference waveform should be chosen to match a typical pattern or pulse shape 
that we are expecting in the incoming signal. The matched filter acts as the optimal 
linear filter which 
allows maximizing the SNR in presence of AWGN noise.

Let's take the most simple example: if we consider a simple binary stream of data,
the reference waveform would be a pulse of width equal to a single bit.
This waveform is the famous rectangular function, defined by:

.. math::

    rect(t) = \Pi(t) = \Biggl\lbrace
    ^{{\displaystyle 1 \text{, if } \biggl\lvert\frac{t-t_{0}}{T}\biggl\rvert < \frac{1}{2}}}
    _{\displaystyle{0 \text{, elsewhere }}}

with :math:`t_{0}` the center position of the pulse (i.e. its delay) and :math:`T` the pulse width.
The autocorrelation of this function is a triangular pulse:

.. _figRect:
.. figure:: rectCorr.svg
    :align: center
    :scale: 100%

    Rectangular function and its autocorrelation

Now let's try with a real OOK-modulated signal recorded with the RTL-SDR to illustrate:

.. admonition:: The full python code for this example is available
    :class: pythonCode
    
    :download:`Download here <../Scripts/matchedFilter.zip>`

    Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

.. _figOOK1:
.. figure:: matchedFiltering1.svg
    :align: center
    :scale: 100%

    OOK signal

The blue trace represents our signal. While our trained human eye can easily distinguish the individual bits
we have to admit the trace looks awful. If we decided to slice the signal using 0.5 (amplitude level) 
as the decision threshold, it wouldn't work. There is too much noise, we would end up with 
a lot of glitches, which is what we see in the orange trace. So we define a reference pulse equivalent to one bit (in green), 
and we correlate it with the recorded signal. This gives us the match-filtered data.

.. _figOOK2:
.. figure:: matchedFiltering3.svg
    :align: center
    :scale: 100%

    Match-filtered OOK

The correlation gives us the expected triangular shape, and has gotten rid of most of the noise. On top of that,
each peak of a triangle indicates the middle of a bit, which will be very useful
when using timing error detection techniques. Slicing the output of the correlation now gives us a clean and faithful
representation of the intended bitstream.

To show the power of matched filtering, we can drown the signal in noise
to the point where it's barely recognisable:

.. _figOOK3:
.. figure:: matchedFiltering2.svg
    :align: center
    :scale: 100%

    Noisy signal

As we can see, the output of the correlation is very similar to the one obtained from the original signal.
It's a little bit more noisy and will require further processing to clean-up, but nothing insurmontable.

Pattern detection
====================

.. admonition:: The full python code for this example is available
    :class: pythonCode
   
    :download:`Download here <../Scripts/syncWordDetection.py>`

    Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

In simple protocols used in embedded wireless systems, radio frames are often built this way:

+------------------------------------------------------------------+-----------------------------------+-------------+-------------+-----------------------+
| **Preamble** (usually '101010...' type sequence, few bytes long) | **Sync Word** (Usually 2-4 bytes) | **Header**  | **Payload** | **CRC** (often CRC16) |
+------------------------------------------------------------------+-----------------------------------+-------------+-------------+-----------------------+

The preamble gives time to the receiver to adjust its mechanisms of 
Gain Control (AGC), Frequency Error Correction (FEC), etc. and also allows it to synchronize
its clock on the incoming signal. The problem is that the receiver can't know based on the preamble
alone when the 'useful' message actually starts.

That's where the synchronisation word come in: it's a specific binary sequence which marks
the beginning of the radio frame. So once the receiver has identified a preamble and locked onto it,
it will begin looking for the sync word so it knows where it needs to start decoding the message.
To do so we could scan for the sync word by doing a bit-by-bit comparison with the incoming binary
stream, but that wouldn't leave any room for errors. While this works in ideal conditions,
in the real world the signal will be noisy so some bits might be corrupted. 
By doing a correlation, we can instead estimate a likelyhood that we found the right sequence.

For example, let's say we have the binary sequence:

.. code-block:: python
    
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 
    1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 
    1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 
    1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 
    0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

and we're looking for the sync word **0xF9A8**. We correlate our bitstream with the binary sequence
corresponding to **0xF9A8** and we get:

.. _figSyncCorr:
.. figure:: syncDetection.svg
    :align: center
    :scale: 100%

    Sync word detection by correlation

The red dot indicates the (possible) location of the **center** of the sync word sequence, at
index 74. Our sync word is 16 bits long, so if we extract the bits from index 
(74-8) to (74+8), we get:

.. code-block:: python
    
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0] 

Which is 0xF9A8. In this simple example, we took the maximum correlation value as the point 
where the correlation is the most likely to have found the sync word; 
however please note this will not always
be the case and more complex methods of selection might be required.

.. |br| raw:: html

   <br />

Noise autocorrelation properties
=================================

(AWG or Additive White Gaussian) Noise has very interesting autocorrelation properties. Recall correlation is a measure of how much two signals are similar 
to each other. So if you correlate a signal with itself, what does it measure? It measures a signal's dependencies
within itself, in other words repeating patterns, regularities, specific frequency content.

But white noise is **supposed to be perfectly random**, i.e no repeating pattern. Therefore, at any point in time,
noise should produce a zero-output autocorrelation **except** when it's exactly aligned with itself. Below is an example
of noise measured with an RTL-SDR on the 868MHz ISM band.

.. admonition:: The full python code for this example is available
    :class: pythonCode
    
    :download:`Download here <../Scripts/noise.zip>`

    Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

.. _figNoise:
.. figure:: noise.svg
    :align: center
    :scale: 100%

    Noise recorded with RTL-SDR on 868MHz ISM band

.. _figNoiseCorr:
.. figure:: noiseAutoCorr.svg
    :align: center
    :scale: 100%

    Noise autocorrelation

As we can see on the left-hand side picture, the autocorrelation seems to be 0 except at the center, where the signal
perfectly aligns with itself during the correlation process. A zoom is performed and displayed on the right-hand side 
picture, along with each sample graphically represented by a dot. We can clearly that a **single** sample presents a 
high energy, while the others are pretty much at 0.

Interestingly, this also shows that when we do the assumption that noise is AWGN in order to simplify circuit or system
analysis, it's actually very close to reality. This practical example shows that background electromagnetic noise does in fact
behave like AWGN.

This particular behaviour is used in many cases, like sync word detection, where we will try to use codes that 
have strong autocorrelation properties (to produce a high-energy peak) and weak cross-correlation properties 
(to avoid being mistaken for other codes). Some examples are Barker codes used in WiFi or Zadoff-Chu sequences used in 
cellular (4G/5G).
