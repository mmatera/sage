def sage_setup(distributions, *,
               interpreters=(),
               required_modules=(), optional_modules=(),
               recurse_packages=(),
               package_data=None):
    r"""
    Replacement for :func:`setuptools.setup` for building distribution packages of the Sage library

    INPUT:

    - ``distributions`` -- (typically one-element) sequence of strings, the distribution names
      shipped with this distribution package.

    - ``interpreters`` -- sequence of strings, the interpreters to build with :mod:`sage_setup.autogen`.

    - ``required_modules`` -- sequence of strings, pkgconfig modules that are required for the build.

    - ``optional_modules`` -- sequence of strings, pkgconfig modules to checked for the build.

    - ``package_data`` -- ``None`` or a dictionary mapping package names to lists of filename
      glob patterns, the package data to install.

      * If ``None``, all of ``package_data`` is taken from ``pyproject.toml``.

      * If a dictionary, use it as package data and ignore ``package_data`` in ``pyproject.toml``.
    """
    import time

    from distutils import log
    from setuptools import setup, find_namespace_packages
    from sage_setup.command.sage_build_ext_minimal import sage_build_ext_minimal
    from sage_setup.cython_options import compiler_directives, compile_time_env_variables
    from sage_setup.extensions import create_extension
    from sage_setup.find import find_python_sources, find_extra_files

    # Work around a Cython problem in Python 3.8.x on macOS
    # https://github.com/cython/cython/issues/3262
    import os
    if os.uname().sysname == 'Darwin':
        import multiprocessing
        multiprocessing.set_start_method('fork', force=True)

    import sys

    from sage_setup.excepthook import excepthook
    sys.excepthook = excepthook

    from sage_setup.setenv import setenv
    setenv()

    import sage.env
    sage.env.default_required_modules = required_modules
    sage.env.default_optional_modules = optional_modules

    cmdclass = dict(build_ext=sage_build_ext_minimal)

    sdist = len(sys.argv) > 1 and (sys.argv[1] in ["sdist", "egg_info", "dist_info"])

    # ########################################################
    # ## Discovering Sources
    # ########################################################
    if sdist:
        extensions = []
        python_modules = []
        python_packages = []
    else:
        if interpreters:
            log.info("Generating auto-generated sources")
            # from sage_setup.autogen import autogen_all
            # autogen_all()
            from sage_setup.autogen.interpreters import rebuild
            rebuild(os.path.join("sage", "ext", "interpreters"),
                    interpreters=interpreters,
                    distribution=distributions[0], force=True)

        log.info("Discovering Python/Cython source code....")
        t = time.time()

        python_packages, python_modules, cython_modules = find_python_sources(
            '.', ['sage'], distributions=distributions)
        extra_files = find_extra_files(
            '.', ['sage'], '/doesnotexist', distributions=distributions)

        python_packages += find_namespace_packages(where='.', include=recurse_packages)

        if package_data is not None:
            package_data.update({"": [f
                                      for pkg, files in extra_files.items()
                                      for f in files]})
            python_packages += list(package_data)

        log.debug('python_packages = {0}'.format(sorted(python_packages)))
        log.debug('python_modules = {0}'.format(sorted(m if isinstance(m, str) else m.name for m in python_modules)))
        log.debug('cython_modules = {0}'.format(sorted(m if isinstance(m, str) else m.name for m in cython_modules)))
        log.debug('package_data = {0}'.format(package_data))

        log.info(f"Discovered Python/Cython sources, time: {(time.time() - t):.2f} seconds.")

        # from sage_build_cython:
        import Cython.Compiler.Options
        Cython.Compiler.Options.embed_pos_in_docstring = True
        gdb_debug = os.environ.get('SAGE_DEBUG', None) != 'no'

        try:
            from Cython.Build import cythonize
            from sage.env import cython_aliases, sage_include_directories
            from sage.misc.package_dir import cython_namespace_package_support
            with cython_namespace_package_support():
                extensions = cythonize(
                    cython_modules,
                    include_path=sage_include_directories(use_sources=True) + ['.'],
                    compile_time_env=compile_time_env_variables(),
                    compiler_directives=compiler_directives(False),
                    aliases=cython_aliases(),
                    create_extension=create_extension,
                    gdb_debug=gdb_debug,
                    nthreads=4)
        except Exception as exception:
            log.warn(f"Exception while cythonizing source files: {repr(exception)}")
            raise

    setup(cmdclass=cmdclass,
          packages=python_packages,
          py_modules=python_modules,
          ext_modules=extensions,
          package_data=package_data,
    )
