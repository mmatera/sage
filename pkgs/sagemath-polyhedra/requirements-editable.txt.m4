include(`sage_spkg_versions.m4')dnl
dnl Same as setup.cfg.m4 install_requires (+ their install-requires)
dnl FIXME: should pin to built wheels.
SPKG_INSTALL_REQUIRES_gmpy2
SPKG_INSTALL_REQUIRES_cysignals
SPKG_INSTALL_REQUIRES_memory_allocator
SPKG_INSTALL_REQUIRES_ipython
SPKG_INSTALL_REQUIRES_ipywidgets
-e ../sagemath-environment
-e ../sagemath-categories
-e ../sagemath-glpk
-e ../sagemath-modules
-e ../sagemath-mpmath
dnl To be added when ready for editable:
dnl -e ../sagemath-objects
