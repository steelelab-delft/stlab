# stlab

Environment for measurement and analysis scripts developed in the [SteeleLab at TU Delft](http://steelelab.tudelft.nl/open-science/).

The documentation can be found [here](http://nsweb.tn.tudelft.nl/~steelelab/stlab/).

Due to regular changes of the code (`stlab` is work in progress), it is recommended to `git clone` this repository to your local working directory and add a link to the `PYTHONPATH` instead of directly placing it in `/site-packages`.

## Requirements

- [Python3](https://www.python.org/downloads/) or [Anaconda](https://www.anaconda.org/downloads)
- [SciPy](https://www.scipy.org/)
- [lmfit](https://pypi.org/project/lmfit/) (for fitting routines)
- [pyVISA](https://pypi.org/project/PyVISA-py/) (for measurements)

## TODO

- `base` classes for
  - signal analyzer
  - Keithley DMM
- docstrings for all devices
- file with overview on all devices
- update example files

## Changelog

All notable changes to this project will be documented below.

### ['5ab0df2'](https://github.com/steelelabgit/stlab/commit/5ab0df2c88997ca4a513349b36b68e76b1dda514) - 2019-02-24

#### Changed

- added capabilities for FSV signal analyzer
- massive cleanup of old unused code and docstrings

### [`0393898`](https://github.com/steelelabgit/stlab/commit/0393898cfe9d575ff1bf3abcbba1579c4094abd7) - 2019-02-19

#### Changed

- Reformatting for better readability
- Docstrings for every device
- Major updates for Keithley DMM6500 to handle loops and capture traces
