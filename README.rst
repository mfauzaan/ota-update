========
Examples
========

Setting up a virtual serial bus
===============================

To make the two code examples of each pair work together, you need a serial bus of communication. The easiest way to set up a serial bus is to use a virtual one. `socat <http://nc110.sourceforge.net/>`_ is a great tool for carrying out this task:

::

    socat -d -d socat -d -d pty,raw,echo=0 pty,raw,echo=0

This command will create two virtual devices such as ``/dev/pts/5`` and ``/dev/pts/6``. Everything you write in ``/dev/pts/5`` will be echoed in ``/dev/pts/6`` and vice versa.

``send_data_frame.py`` and ``receive_data_frame.py``
====================================================

These two code examples need ``pyserial`` as dependency:

::

    pip3 install pyserial
