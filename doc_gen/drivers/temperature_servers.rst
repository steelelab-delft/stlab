Temperature servers and Daemons for BlueFors and He7 fridges
============================================================

Temperature control and logging using the Lakeshore units can be difficult due to the fact that
the standard control programs provided by the companies (Entropy and BlueFors) generally
do not allow our scripts to remotely control or read out from the Lakeshore directly.
For example, the BF temperature monitor program blocks communication from any other process to the
temperature controller and does not provide any way to remotely give commands to the
monitoring program.  These programs run on separate computers (usually laptops that sit on the relevant
system) and do not usually run measurement scripts.

In order to get around this issue there a several scripts and daemons ( https://en.wikipedia.org/wiki/Daemon_(computing) )
that we have developed for the different systems.  Some of them directly communicate with the lakeshore units via
a program that simply forwards commands and responses to a from the measurement computer and the temperature controller.
This allows access to temperatures as well as to the pid loops and control systems.  However, the standard logging programs
have to be halted when these scripts are running.

Others take a more rudimentary approach of providing access to the last logged temperatures instead of directly
communication with the controller.  This has the advantage of being able to keep the standard logging provided running while
still being able to access the temperatures.  However, no temperature control is available.

MySocket.py -- Basic TCP socket
-------------------------------

This is the basic TCP socket used for the implementation of the temperature servers

.. automodule:: stlab.utils.MySocket
  :members:
  :special-members:
  :exclude-members: __weakref__

BFDaemon.py
-----------

File location: :code:`stlab/devices/BFDaemon/BFDaemon.py`

.. automodule:: stlab.devices.BFDaemon.BFDaemon
  :special-members:
  :members:


BFWrapper.py
------------

File location: :code:`stlab/devices/BFWrapper.py`.

Imported similar to an intrument::

  from stlab.devices.BFWrapper import BFWrapper
  dev = BFWrapper(addr)

.. automodule:: stlab.devices.BFWrapper
  :special-members:
  :members:

He7Daemon.py
------------

File location: :code:`stlab/devices/He7Daemon/He7Daemon.py`

.. automodule:: stlab.devices.He7Daemon.He7Daemon
  :special-members:
  :members:


He7Temperature.py
-----------------

File location: :code:`stlab/devices/He7Temperature.py`

Imported similar to an intrument::

  from stlab.devices.He7Temperature import He7Temperature
  dev = He7Temperature(addr)


.. automodule:: stlab.devices.He7Temperature
  :special-members:
  :members:

TritonDaemon.py
---------------

File location: :code:`stlab/devices/TritonDaemon/TritonDaemon.py`

.. automodule:: stlab.devices.TritonDaemon.TritonDaemon
  :special-members:
  :members:

TritonWrapper.py
----------------

File location: :code:`stlab/devices/TrtionWrapper.py`.

Imported similar to an intrument::

  from stlab.devices.TritonWrapper import TritonWrapper
  dev = TritonWrapper(addr)

.. automodule:: stlab.devices.TritonWrapper
  :special-members:
  :members:


