[![Build Status](https://travis-ci.com/steelelab-delft/stlab.svg?branch=ci)](https://travis-ci.com/steelelab-delft/stlab)
[![GitHub Issues](https://img.shields.io/github/issues/steelelab-delft/stlab.svg)](https://github.com/steelelab-delft/stlab/issues)
[![DOCS](https://img.shields.io/badge/read%20-thedocs-ff66b4.svg)](https://steelelab-delft.github.io/stlab/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1299278.svg)](https://doi.org/10.5281/zenodo.1299278)

# stlab

Environment for measurement and analysis scripts developed in the [SteeleLab at TU Delft](http://steelelab.tudelft.nl/open-science/).

The documentation can be found [here](https://steelelab-delft.github.io/stlab/) and on [the TUDelft server](http://nsweb.tn.tudelft.nl/~steelelab/stlab/).

Due to regular changes of the code (`stlab` is work in progress), it is recommended to `git clone` this repository to your local working directory (preferably `C:\libs\stlab` on windows) and add a link to the `PYTHONPATH` instead of directly placing it in `\site-packages`.

## Requirements

- [Python3](https://www.python.org/downloads/) or [Anaconda](https://www.anaconda.org/downloads)
- [SciPy](https://www.scipy.org/)
- [lmfit](https://pypi.org/project/lmfit/) (for fitting routines)
- [pyVISA](https://pypi.org/project/PyVISA-py/) (for measurements)

## Changelog

All notable changes to the master branch of this project will be documented below.

- [`74891f7`](https://github.com/steelelabgit/stlab/commit/74891f7e12057a18cd64b9e88492cf197438cc45) - 2019-04-09
  - pop-up windows when not resetting instrument
  - automatic recording of stlab git version
- [`d963325`](https://github.com/steelelabgit/stlab/commit/d963325aa98c72f713589200506a5edb609c3c8c) - 2019-03-29
  - enabled reverse sweeps for PNA5221A
- [`e05e9fb`](https://github.com/steelelabgit/stlab/commit/e05e9fb8d633c56612809d57e663505cb9e11c47) - 2019-02-26
  - added `**kwargs` to Keithley DMM6500
  - added `SetSweepTime` to PNA5221A
- [`a0b2d17`](https://github.com/steelelabgit/stlab/commit/a0b2d175df05ee5ab460816a65d8a8ee445e4e82) - 2019-02-25
  - FSV ready for frequency sweeps, syntax modernized
  - Reference for SMB enabled
  - Reference for Rigol AWG disabled because it breaks the system. Why?
- [`5ab0df2`](https://github.com/steelelabgit/stlab/commit/5ab0df2c88997ca4a513349b36b68e76b1dda514) - 2019-02-24
  - added capabilities for FSV signal analyzer
  - massive cleanup of old unused code and docstrings
- [`0393898`](https://github.com/steelelabgit/stlab/commit/0393898cfe9d575ff1bf3abcbba1579c4094abd7) - 2019-02-19
  - Reformatting for better readability
  - Docstrings for every device
  - Major updates for Keithley DMM6500 to handle loops and capture traces
