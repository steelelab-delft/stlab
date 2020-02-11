[![GitHub Issues](https://img.shields.io/github/issues/steelelab-delft/stlab.svg)](https://github.com/steelelab-delft/stlab/issues)
[![DOCS](https://img.shields.io/badge/read%20-thedocs-ff66b4.svg)](https://steelelab-delft.github.io/stlab/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1299278.svg)](https://doi.org/10.5281/zenodo.1299278)

# stlab

Environment for measurement and analysis scripts developed in the [SteeleLab at TU Delft](http://steelelab.tudelft.nl/open-science/).

The documentation can be found [here](https://steelelab-delft.github.io/stlab/) and on [the TUDelft server](http://nsweb.tn.tudelft.nl/~steelelab/stlab/).

Due to regular changes of the code (`stlab` is work in progress), we recommend to `git clone` this repository to your local working directory (preferably `C:\libs\stlab` on windows) and add a link to the `PYTHONPATH` instead of directly placing it in `\site-packages`.
For more on this, see [the installation instructions](#installation-instructions).

## Requirements

See [`requirements.txt`](https://github.com/steelelab-delft/stlab/blob/master/requirements.txt)

## Installation instructions

1. Clone the repository to your computer using, for example, the GitHub desktop client or git bash.
1. Then add the directory you cloned it to (or any upper folder in the folder tree it is stored in) to your ```PYTHONPATH```, using one of the following methods.

### Windows

1. After anaconda installation, there should be a ```PYTHONPATH``` variable in ```My Computer > Properties > Advanced System Settings > Environment Variables > ```
1. Add the directory in which the git repos are to this library, for example ```;C:\libs```

_Taken from [here](https://stackoverflow.com/questions/3701646/how-to-add-to-the-pythonpath-in-windows) and [here](https://stackoverflow.com/questions/7054424/python-not-recognized-as-a-command)._

### macOS

1. On a mac, the GitHub desktop client stores local repositories in `/Users/<user>/Documents/GitHub`
1. This means that one should add this directory to the ```PYTHONPATH ``` environment variable. You might for example add the following to your `.profile` file: `export PYTHONPATH="$PYTHONPATH:/Users/<user>/Documents/GitHub"`

### Linux

Same as for macOS (both are UNIX based).

For detailed instructions on setting the python path variable on different platforms, see [this stack exchange post](https://stackoverflow.com/questions/3402168/permanently-add-a-directory-to-pythonpath).

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
