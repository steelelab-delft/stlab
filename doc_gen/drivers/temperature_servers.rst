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


BFDaemon
--------

.. automodule:: stlab.devices.BFDaemon.BFDaemon
  :special-members:
  :members:


BFWrapper
---------

.. automodule:: stlab.devices.BFWrapper
  :special-members:
  :members:

He7Daemon
---------

.. automodule:: stlab.devices.He7Daemon.He7Daemon
  :special-members:
  :members:


He7Temperature
--------------

.. automodule:: stlab.devices.He7Temperature
  :special-members:
  :members:
