.. Test documentation master file, created by
   sphinx-quickstart on Mon Sep 10 12:04:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for STLab
=======================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   utils/*
   drivers/*

Introduction
============

STLab is a collection of drivers and scripts used for equipment control and measurement
automation.  For the most part it is built upon pyvisa and is inteded to avoid the complications
of low level communication with measurement instruments without including an inconvenient level
of additional complexity (see `KISS principle <https://en.wikipedia.org/wiki/KISS_principle>`_).

The instrument drivers should in general only contain basic commonly used commands and not
sophisticated setup and measurement schemes.  While things like "Get power" or "Get Trace" are
acceptable, methods like "Perform 2 tone measurement" should not be included in basic device drivers.
The latter kind of method should reside on a higher level of abstration since its use is likely
to be very specific and would only clutter the driver for others.

The basic structure of the package is as follows:

| stlab
| ├── __init__.py
| ├── LICENCE.md
| ├── README.md
| ├── devices
| │   ├── ...
| │   └── ...
| ├── utils
| │   ├── instrument.py
| │   └── ...
| ├── examples
| │   ├── ...
| │   └── ...
| ├── docs
| │   ├── ...
| │   └── ...
| ├── doc_gen
| │   ├── ...
| │   └── ...

* The "devices" folder contains all the implemented drivers as well as the basic instrument class.
* The "utils" folder contains modules for reading and writing files, resonance fitting, data structure management (stlabmtx for example).  Basically, everything not directly related to instrument communication.
* "examples" contains a collection of basic script examples suchs as VNA power sweeps or quick Q factor measurements and fits.
* "docs" contains this documentation and "doc_gen" contains the sphynx scripts for generating it.
* The __init__.py file contains the modules and names imported when running "import stlab".  Note that some modules and functions are renamed for convenience.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

