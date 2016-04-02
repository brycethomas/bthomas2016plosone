# Overview

Herein lies the dataset and code used to produce the results presented in
*Diffusion in Colocation Contact Networks: the Impact of Nodal Spatiotemporal
Dynamics*.  To run all simulations and produce all results one can simply run
`main.sh`.

# Execution environment & dependencies

## Execution environment

The code was executed on Ubuntu Linux 12.04.  Note that in addition to the
dependencies outlined below, other unix-based environments may require
additional dependencies to be installed.

## Dependencies

Here is a list of the dependencies of the main script:

* [GNU Parallel](http://www.gnu.org/software/parallel/)
* [Go](https://golang.org/)
* [Matplotlib](http://matplotlib.org/)
* [Numpy](http://www.numpy.org/)
* [NetworkX](https://networkx.github.io/)

If you identify further dependencies please let us know.

# Code structure & documentation

## Structure

There is a single entry point script i.e. `main.sh` which when executed will
run all simulations and produce all numerical outputs and their derivatives
(figures, tables, scalar constants etcetera).  These outputs are written to the
`OUT_DIR` directory specified in `main.sh`.

The code relies heavily on the unix pipeline and standard unix commands to
manipulate the data.  Most of the more complex computations are written as
Python scripts or Go scripts which accept input from stdin and either write
output to stdout or directly to a file if the output is a figure.

## Documentation

Extensive comments can be found throughout the code base.

# Dataset 

There are two `.csv` files provided in this distribution: (i) `uq.csv` and (ii)
`st_lucia.csv`.  Both files consist of a set of lines of the form `<mac, start,
end, ap>` describing a `mac` having a session between `start` and `end` at `ap`.
`st_lucia.csv` is the dataset for only the
[UQ St Lucia campus](http://en.wikipedia.org/wiki/University_of_Queensland#St_Lucia_campus).
`uq.csv` is a superset dataset for all UQ-affiliated sites.  These two files
consitute the minimal dataset necessary to reproduce the results presented in
the paper.  Note that `mac` and `ap` have both been
[minified](http://en.wikipedia.org/wiki/Minification_%28programming%29) i.e. the
original identities have been remapped to a set of more compact identifiers.
