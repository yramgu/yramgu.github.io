===========================
Decimation
===========================

The concept
===========================

Decimation is a process very often used in radio dsp, and consists in 
reducing the bandwidth of a signal. Decimating by a factor D is performed by 
dropping one out of every D sample of a signal. If a signal is sampled at a rate :math:`Fs`,
then the resulting decimated signal is sampled at a rate :math:`\frac{Fs}{D}`. 
In reality, it's a bit trickier than that: the process of simply reducing the sample rate is actually called
downsampling. But if we stop there we might have aliasing issues, so we always low-pass filter 
the signal prior to downsampling and that whole operation is called decimation. It is often
represented in block diagrams as shown below:

.. _decBloc:
.. figure:: decimBlock.svg
    :align: center
    :scale: 40%

    Decimation block

In Python the decimation
operation can be done automatically using a dedicated function from Scipy:

.. code-block:: python
    :emphasize-lines: 1

    y = scipy.signal.decimate(x, decimation_factor, ftype='fir')

The aliasing problem
===========================

Say we are sampling at Frequency :math:`Fs`: the Nyquist bandwidth will extend from DC to :math:`\frac{Fs}{2}`, 
this is known as the **Nyquist-Shannon sampling theorem**. 
This theorem states that in order to sample a signal correctly, the sampling
frequency must be superior to twice that signal's bandwidth.
In our example, there are two signals in the Nyquist bandwidth: our wanted :math:`W` and an interferer :math:`I`.

.. _figAliasing:
.. figure:: aliasing.svg
    :align: center
    :scale: 40%

    Aliasing

 
If we reduce our sampling rate to :math:`\frac{Fs}{D}`, our new Nyquist bandwidth now extends from DC to :math:`\frac{Fs}{2D}`. 
The Wanted :math:`W` is in that bandwidth, so it's fine. The Interferer :math:`I`, however, is now `undersampled`; but it might still be within
the physical bandwidth of the receiver. Because of that, its spectrum could be folded back inside
our new Nyquist bandwidth (Alias :math:`A`), which is what we call Aliasing.
In order to get rid of potential aliases, we must first implement a low-pass filter (otherwise known as anti-aliasing
filter) prior to the downsampling operation. 

Aliasing example
===========================

As an example, we generate two tones sampled at a rate of 10 kHz:
One tone at 100 Hz and another tone at 700 Hz. The time-domain representation of that signal is given in Plot 1
and its power spectrum is given in Plot 2. In this case, the Nyquist bandwidth extends from 0 to 5 kHz.

.. admonition:: The full python code for this example is available
    :class: pythonCode
    
    :download:`Download here <../Scripts/aliasing.py>`

    Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

.. _figAliasExperiment:
.. figure:: aliasing_python.svg
    :align: center
    :scale: 40%

    Aliasing python experiment

Then we downsample that signal by dropping 1 out of 10 samples. The new sampling rate becomes 1 kHz
and the nyquist bandwidth is reduced to 500 Hz, which should leave us only with the 100 Hz tone. 
The resulting power spectrum is shown on plot 3.

We can see our 100 Hz tone, but we now have an **uninvited guest showing up at 300 Hz**, and that tone shouldn't exist.
Now that our Nyquist bandwidth ranges from 0 to 500 Hz (1st Nyquist zone), the 2nd Nyquist zone ranges
from 500 Hz to 1000 Hz and so on. The 700 Hz tone is in the 2nd Nyquist zone; and every even Nyquist zone will fold back
flipped onto the 1st one. Thus our 700Hz tone is now showing up on 1000-700 = 300 Hz:

.. _figAliasFolding:
.. figure:: aliasFold.svg
    :align: center
    :scale: 40%

    Folding mechanism

So we implement a low-pass filter first to eliminate the unwanted tone at 700 Hz, then we downsample and the
result can be seen in Plot 4, where the 300 Hz alias has disappeared. 

SNR improvement
===========================

.. admonition:: The full python code for this example is available
    :class: pythonCode
    
    :download:`Download here <../Scripts/ook.zip>`

    Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3


Decimation will also improve the Signal-to-Noise Ratio (SNR): indeed, as we are reducing
the bandwidth, we are reducing the noise. This type of improvement is called a processing gain, 
and its value in dB can be calculated by the formula:

.. math::

    G_{dB} = 10log_{10} \left(\frac{Fs_{old}}{Fs_{new}}\right)

We can see below an example of decimation on a signal acquired with the RTL: the 
signal was sampled at 2 MHz then decimated by 10 to 200 kHz. The noise reduction is visible 
on the IQ traces, and the spectrum is displayed as well to show the reduced bandwidth.

.. _figDecIQ:
.. figure:: IQ_decimated.svg
    :align: center
    :scale: 100%

    RTL-SDR decimated IQ

The SNR improvement is :math:`10log_{10} \left(\frac{2M}{200k}\right) = 10dB`. So just like that, we've reduced our noise 
by 10dB. Additionally, since we now have 10x less samples, the next processing steps will run with reduced computing power needs.   

.. admonition:: But then we might ask ourselves...

   **Why go through all this trouble**? 

- Since we're using an SDR, why don't we just set the SDR to sample at 200ksps directly instead of oversampling at 2Msps then decimating? 
- Wouldn't sampling at a higher frequency bring in more noise anyway since the bandwidth is higher?

For starters, a trivial advantage to oversampling followed by decimation is the ability to get
rid of close-range interferers (assuming the ones that are further away are being filtered by the hardware).
Another less obvious advantage concerns the ADC inside the RTL2832 that samples our incoming signal.
As it turns out, **sampling at a higher frequency doesn't mean bringing in more noise**.

Let's consider a perfect ADC/system, which is only affected by quantization noise. If :math:`q` is the ADC's LSB, 
then the total noise power due to quantization noise for a perfect ADC is 

.. math::

    N_{q} = \frac{q^2}{12}

A mathematical proof for this number can be found `here <https://www.analog.com/media/en/training-seminars/tutorials/MT-001.pdf>`__.
The total noise power is **constant, and independant the sampling frequency**. Now if we consider noise
to have flat spectrum, and knowing that spectrum is band-limited by the sampling frequency, we can 
represent it as:

.. _figAdcNoise:
.. figure:: PSDnoise.svg
    :align: center
    :scale: 100%

    Perfect ADC quantization noise Power Spectral Density

The Power Spectral Density (PSD) of that quantization noise can then be expressed as

.. math::

    PSD_{noise} = \frac{q^2}{12} \frac{1}{Fs} 

Since the total noise power is constant it becomes clear that **increasing the sampling frequency 
spreads the noise**, so given the chance
it's quite often (but not always) better to oversample first and then decimate.

.. |br| raw:: html

   <br />



