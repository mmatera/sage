dnl MANIFEST.in is generated from this file by SAGE_ROOT/bootstrap via m4.
prune sage

include VERSION.txt

prune .tox
exclude *.m4
include requirements.txt

global-include all__sagemath_plot.py

graft sage/plot

include sage/ext_data/graphs/graph_plot_js.html
graft sage/ext_data/threejs


global-exclude *.py[co]
global-exclude *.so
global-exclude *.bak
