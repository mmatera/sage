include(`sage_spkg_versions.m4')dnl' -*- conf-unix -*-
[metadata]
name = sagemath-standard
version = file: VERSION.txt
description = Sage: Open Source Mathematics Software: Standard Python Library
long_description = file: README.rst
long_description_content_type = text/x-rst
license_files = LICENSE.txt
include(`setup_cfg_metadata.m4')dnl'

[options]
python_requires = >=3.9, <3.12
install_requires =
    SPKG_INSTALL_REQUIRES_sagemath_standard_no_symbolics
    SPKG_INSTALL_REQUIRES_sagemath_symbolics

[options.extras_require]
R = SPKG_INSTALL_REQUIRES_rpy2
