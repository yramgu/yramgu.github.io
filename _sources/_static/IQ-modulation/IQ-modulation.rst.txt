===========================
I/Q modulation
===========================

Basics
===========================

The :math:`I/Q` representation is the universal way of representing a modulating (or baseband) signal. It consists of representing symbols
in a complex plane with an **In-phase** component :math:`X_I` and a **Quadrature** component :math:`X_Q`. A given symbol :math:`S`
will be represented as

.. _iq:
.. figure:: iq_constellation.svg
    :align: center
    :scale: 100%

    Symbol representation in the I/Q plane

The magnitude of :math:`S` is:

.. math::

    |S| = A = \sqrt{X_I^2 + X_Q^2}

The phase of :math:`S` is:

.. math::

    \angle{S} = \phi = \arctan{\frac{X_Q}{X_I}}

:math:`S` can be re-written as

.. math::

    S = A\cos(\phi) + jA\sin(\phi) = Ae^{j\phi}

The figure below shows a constellation for a QPSK. A QPSK has four symbols each representing two bits,
and those symbols are equally spaced by 90° :

.. _qpsk_iq:
.. figure:: QPSK_constellation.svg
    :align: center
    :scale: 100%

    QPSK constellation example

The symbols coordinates are:

+-------------+---------------------------------------------------+
| Symbol      |  Coordinates                                      |
+-------------+---------------------------------------------------+
| :math:`00`  | :math:`+\frac{\sqrt{2}}{2} + j\frac{\sqrt{2}}{2}` |
+-------------+---------------------------------------------------+
| :math:`01`  | :math:`-\frac{\sqrt{2}}{2} + j\frac{\sqrt{2}}{2}` |
+-------------+---------------------------------------------------+
| :math:`11`  | :math:`-\frac{\sqrt{2}}{2} - j\frac{\sqrt{2}}{2}` |
+-------------+---------------------------------------------------+
| :math:`10`  | :math:`+\frac{\sqrt{2}}{2} - j\frac{\sqrt{2}}{2}` |
+-------------+---------------------------------------------------+

.. admonition:: But

    Why do we perform quadrature modulation?

There are plenty of reasons, we'll explore two simple but fundamental ones

- 1) Easily perform arbitrary phase/frequency/amplitude modulation from a simple low frequency baseband signal  

- 2) Transmit *complex* baseband signals

Arbitrary modulation
=========================

Let's consider the simple case of a modulating signal :math:`x_{bb}(t)` and a carrier wave :math:`\cos{(\omega_0t + \phi)}`. 
These signals are mixed together using a simple modulator:

.. _real-mixing:
.. figure:: real_mixing.svg
    :align: center
    :scale: 100%

    Simple modulator

The output of the modulator will be 

.. math::

    x_{RF}(t) = x_{bb}(t)\cos{(\omega_0t+\phi)}

If we want to perform amplitude modulation, it's pretty straightforward. The amplitude of the carrier is directly :math:`x_{bb}(t)` which 
is easily generated with a DAC or other mean (filtered PWM, etc). However if we want to generate phase (or frequency) modulation, it becomes less straightforward. 
How can we easily modify the phase :math:`\phi` of the carrier? If that carrier has a frequency of say 1GHz, this would requires very fast 
circuits and/or processors!

This is where trigonometry comes to the rescue. Indeed, we know that:

.. math::

    cos(\theta+\phi) = \cos(\theta)\cos(\phi) - \sin(\theta)\sin(\phi)

An arbitrarily modulated carrier would be written as

.. math::

    x(t) =  a(t)\cos\Bigl(\omega_0t+\phi(t)\Bigl)

With 

- :math:`a(t)` the envelope
- :math:`\omega_0` the frequency
- :math:`\phi(t)` the phase

We apply the trigonometric identity which gives us:

.. math::

    \begin{align}
        a(t)\cos\Bigl(\omega_0t+\phi(t)\Bigl) &= \color{blue}a(t)\cos\Bigl(\phi(t)\Bigl)\color{black}\cos(\omega_0t) - \color{red}a(t)\sin\Bigl(\phi(t)\Bigl)\color{black}\sin(\omega_0t) \\
                                              &= \color{blue}X_I(t)\color{black}\cos(\omega_0t) - \color{red}X_Q(t)\color{black}\sin(\omega_0t)
    \end{align}

If we want to perform arbitrary amplitude and phase modulation we need two low-frequency terms :math:`a(t)\cos(\phi(t))` and :math:`a(t)\sin(\phi(t))`.
They are in fact respectively the :math:`X_I` and :math:`X_Q` components of the baseband signal represented in the :math:`I/Q` plane, as defined in the "Basics" section. 
Since they are low frequency signals, they would be fairly easy to generate with a DAC.

But now the carrier wave has been split into two terms :math:`\cos(\omega_0t)` and :math:`-\sin(\omega_0t)`, so we cannot use
the simple modulator circuit shown above. We need a new circuit: the quadrature modulator.

It becomes apparent that we can transmit two independant information, :math:`X_I` and :math:`X_Q`, on two different carriers
that have the same frequency but are orthogonal to each other. These two independant components can individually be 
recovered at the receiver by means of a quadrature demodulator.

So how do we perform the quadrature modulation in an actual circuit?

.. _complex-mixing:
.. figure:: complex_mixing.svg
    :align: center
    :scale: 100%

    Quadrature modulator

A baseband processor generates :math:`X_I` and :math:`X_Q` in the digital domain, and this is then translated into the analog domain
(voltages) with DACs. The local oscillator is assumed to produce :math:`cos(\omega_0t)` by default. In order to generate :math:`-sin(\omega_0t)`
we simply need to dephase the :math:`cos` by :math:`+\frac{\pi}{2}` following the trigonometric identity

.. math::

    \cos\Bigl(\theta+\frac{\pi}{2}\Bigl) = -\sin(\theta)

:math:`X_I` is mixed with :math:`cos(\omega_0)` and :math:`X_Q` is mixed with :math:`-sin(\omega_0)`.
The two resulting :math:`I` and :math:`Q` branches are then summed together to form the final modulated waveform at RF

.. math::

    x_{RF}(t) = X_I(t)\cos(\omega_0t) - X_Q(t)\sin(\omega_0t)


Complex baseband signals
=======================================

Let's begin by the case of a real modulation, as illustrated in the previous diagram of a simple modulator. We define :math:`x_{bb}(t)`
as a real baseband signal. A real baseband signal is centered on 0Hz, and the negative frequency content is the symmetrical
of the positive frequency content:

.. _real-bb:
.. figure:: iq_realBB.svg
    :align: center
    :scale: 100%

    Real baseband signal

If we perform simple mixing, we will end up with our wanted signal, but also with an (unwanted) image. Let's define for simplicity

.. math::

    x_{bb}(t) =  \cos(\omega_it)

After mixing we will have 

.. math::

    \begin{align}
        x_{RF}(t) &= \cos(\omega_it)\cos(\omega_0t) \\
                  &= 0.5\Bigl[\cos(\omega_0+\omega_i)t + \cos(\omega_0-\omega_i)t\Bigl]
    \end{align}

The resulting signal contains a component at frequency :math:`\omega_0+\omega_i` and another at :math:`\omega_0-\omega_i`. 
One of them is the wanted and the other is the image. The spectrum looks like this:

.. _real-rf:
.. figure:: iq_realRF.svg
    :align: center
    :scale: 100%

    Real RF signal

This is not really ideal as we do need to get rid of the image. This would be done by means of filtering which can be quite difficult to implement
if it has to be done in hardware.

What happens if we now define :math:`x_{bb}(t)` as a complex baseband signal? A complex baseband signal is centered on 0Hz, 
but is asymetrical:

.. _cpx-bb:
.. figure:: iq_cpxBB.svg
    :align: center
    :scale: 100%

    Complex baseband signal

We have seen that a complex baseband signal can be defined as 

.. math::

    \begin{align}
        x_{bb}(t) &= X_I(t) + jX_Q(t) \\
                  &= a(t)e^{j\phi(t)}
    \end{align}

Staying in the complex domain, we mix it with a complex sinusoid at frequency :math:`\omega_0`:

.. math::

    \begin{align}
        x_{RF}(t) &= x_{bb}(t)e^{j\omega_0t} \\
    \end{align}

However in the real world we can only transmit real signals, we cannot transmit imaginary ones. So what we can transmit is in fact

.. math::

    \begin{align}
        x_{RF}(t) &= \Re\Bigl(x_{bb}(t)e^{j\omega_0t}\Bigl) \\
                  &= \Re\Bigl[\Bigl(X_I(t)+jX_Q(t)\Bigl)\Bigl(\cos(\omega_0t)+j\sin(\omega_0t)\Bigl)\Bigl] \\
                  &= \Re\Bigl[X_I(t)\cos(\omega_0t) + jX_I(t)\sin(\omega_0t) + jX_Q(t)\cos(\omega_0t) + j^2X_Q(t)\sin(\omega_0t)\Bigl] \\
                  &= \Re\Bigl[\color{blue}X_I(t)\cos(\omega_0t)-X_Q(t)\sin(\omega_0t) \color{black}+ \color{red}j\Bigl(X_I(t)\sin(\omega_0t)+X_Q(t)\cos(\omega_0t)\Bigl)\color{black}\Bigl] \\
                  &= X_I(t)\cos(\omega_0t)-X_Q(t)\sin(\omega_0t) \\
                  &= a(t)\cos\Bigl(\omega_0t + \phi(t)\Bigl)
    \end{align}

We just found the expression of :math:`x_{RF}` when generated by a quadrature modulator (surprise surprise). 
The spectrum of such a modulated signal is unique (no image), centered on :math:`\omega_0`:

.. _cps-rf:
.. figure:: iq_cpxRF.svg
    :align: center
    :scale: 100%

    Complex RF signal


I/Q impairments
=======================================

.. admonition:: The full python code for this example is available
   :class: pythonCode

   :download:`download here <../Scripts/iq-imbalance.py>`

   Validated with: Python 3.6.7 - Numpy 1.19.4 - Scipy 1.5.4 - Matplotlib 3.3.3

The quadrature modulator circuit previously shown works on the asssumtion that the :math:`I` and :math:`Q` branches are perfectly balanced and contain no
DC offset.
Any electronics engineer knows this cannot be true: even within the same chip, we cannot have perfect alignment on two
supposedly identical channels, and we'll always have burden voltages. Any impairment will have an effect on the constellation, and 
it needs to be calibrated out. We illustrate :math:`I/Q` impairments with a 16-QAM:

.. _iq-imbalance:
.. figure:: iq_imbalance.svg
    :align: center
    :scale: 100%

    Types of IQ imbalance

DC Offset
----------------

The first type of impairment is the DC offset. If :math:`I` and/or :math:`Q` exhibit a DC offset, this will shift the whole constellation
in a certain direction (constellation (b) with an offset of 0.25). A DC offset will have another nasty consequence: LO leakage.

To show this let's define 

.. math::

    \begin{align}
        X_I' &= X_I + DC \\
        X_Q' &= X_Q + DC
    \end{align}

Then if we mix with our LO we get

.. math::

    \begin{align}
        x_{RF}'(t) &= (X_I + DC)\cos(\omega_0t) - (X_Q + DC)\sin(\omega_0t) \\
                  &= \color{blue}X_I\cos(\omega_0t) - X_Q\sin(\omega_0t) \color{black}- \color{red}DC\Bigl(\cos(\omega_0t) - \sin(\omega_0t)\Bigl) \\
                  &= \color{blue}x_{RF}(t) \color{black}- \color{red}DC\cos(\omega_0t)
    \end{align}

The output contains our modulated signal :math:`x_{RF}(t)`, but it also contains the LO (unmodulated carrier), scaled by the 
DC offset value! This is a big issue for the receiver as when the signal is received and converted back to baseband, that LO component
will be transformed back do a DC value which will then degrade the receiver performance (blocking). LO leakage can also cause the apparition
of images by intermodulating with the wanted. The picture below shows a real-life example of LO leakage:

.. _iq-LOleak:
.. figure:: LO-leakage.png
    :align: center
    :scale: 50%

    Example of LO leakage

Gain imbalance
----------------

Gain imbalance happens when one the paths exhibits a different gain than the other one.

.. math::

    \begin{align}
        X_I' &= X_I \\
        X_Q' &= (1+\alpha)X_Q 
    \end{align}

This will cause the constellation to *stretch* along an axis (constellation (c) with a gain of 1.5). For example, if we 
assume :math:`I` to have a gain of 1 and :math:`Q` to have a higher gain, the constellation will stretch along the 
:math:`Q` axis.This is easy to guess since the :math:`I` coordinate does not change but the :math:`Q` coordinate 
increases in value.

Phase imbalance
----------------

Phase imbalance happens when one the paths (after mixing) exhibits a different phase than the other one. This will cause
the constellation to *skew* (constellation (d) with a phase imbalance of 10 degrees). In that case both :math:`I` and :math:`Q` 
coordinates change. To understand why we need to do a little bit of math.

Let's define 

.. math::

    \begin{align}
        x_{RF}(t) &= X_I(t)\cos(\omega_0t) - X_Q(t)\sin(\omega_0t-\phi) \\
                  &= X_I(t)\cos\omega_0t - X_Q(t)\Bigl[\sin\omega_0t\cos\phi + cos\omega_0t\sin\phi\Bigl] \\
                  &= \cos\omega_0t\color{blue}\Bigl(X_I-X_Q\sin\phi\Bigl) \color{black} - \sin\omega_0t\color{red}\Bigl(X_Q\cos\phi\Bigl) \\
    \end{align}

We end up with an **In-phase** path which contains our original :math:`X_I` but now also contains a scaled version of :math:`X_Q`.
This is equivalent to an altered baseband signal where :math:`X_I' = X_I-X_Q\sin\phi`. Similarly for the **Quadrature** path
we have an equivalent :math:`X_Q' = X_Q\cos\phi`.

You can play with the provided python script to see the effect of :math:`I/Q` impairments on a constellation. 

EVM (Vector Error Magnitude)
=======================================

On top of potential :math:`I/Q` impairments that can occur at the transmitter or at the receiver, our symbols can also get distorted 
when they are transmitted over-the-air: from additional white noise to reflections/diffractions,
or interferers, the symbol we receive at the end will surely not be exactly where we expect it.

.. _channel:
.. figure:: iq_channel.svg
    :align: center
    :scale: 100%

    Transmission through a channel

In the :math:`I/Q` plane, we can plot a vector from the expected or wanted symbol, and another vector from the measured symbol.
A third vector connecting these two symbols is called the **Error Vector**.

.. _evm:
.. figure:: iq_evm.svg
    :align: center
    :scale: 100%

    EVM phasor diagram

The differences on the values of :math:`I` and :math:`Q` for the wanted and measured vectors allow us the calculate the length of 
the error vector called the **Error Vector Magnitude**, or EVM, defined as:

.. math::

    EVM = \sqrt{I_{err}^2+Q_{err}^2}

The EVM, a sort of SNR figure of merit, is often expressed in :math:`\%` or in :math:`dB`. Be careful the decibel value is computed using 20log(...) 
and not 10log(...).
