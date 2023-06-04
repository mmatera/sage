[build-system]
# Minimum requirements for the build system to execute.
requires = [
    esyscmd(`sage-get-system-packages install-requires-toml \
        setuptools     \
        wheel          \
        sage_setup     \
        pkgconfig      \
        sagemath_environment \
        sagemath_modules \
        scipy            \
        cython         \
        gmpy2          \
        cysignals      \
        memory_allocator   \
                    ')]
build-backend = "setuptools.build_meta"
