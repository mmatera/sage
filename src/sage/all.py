"""
all.py -- much of sage is imported into this module, so you don't
          have to import everything individually.

TESTS:

This is to test :trac:`10570`. If the number of stackframes at startup
changes due to a patch you made, please check that this was an
intended effect of your patch.

::

    sage: import gc
    sage: import inspect
    sage: from sage import *
    sage: frames = [x for x in gc.get_objects() if inspect.isframe(x)]

We exclude the dependencies and check to see that there are no others
except for the known bad apples::

    sage: allowed = [
    ....:     'IPython', 'prompt_toolkit', 'jedi',     # sage dependencies
    ....:     'threading', 'multiprocessing',  # doctest dependencies
    ....:     'pytz', 'importlib.resources',   # doctest dependencies
    ....:     '__main__', 'sage.doctest',      # doctesting
    ....:     'signal', 'enum', 'types'        # may appear in Python 3
    ....: ]
    sage: def is_not_allowed(frame):
    ....:     module = inspect.getmodule(frame)
    ....:     if module is None: return False
    ....:     return not any(module.__name__.startswith(name) for name in allowed)
    sage: [inspect.getmodule(f).__name__ for f in frames if is_not_allowed(f)]
    []

Check lazy import of ``interacts``::

    sage: type(interacts)
    <class 'sage.misc.lazy_import.LazyImport'>
    sage: interacts
    <module 'sage.interacts.all' from '...'>
"""
# ****************************************************************************
#       Copyright (C) 2005-2012 William Stein <wstein@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

import os
import sys
import operator
import math

############ setup warning filters before importing Sage stuff ####
import warnings

__with_pydebug = hasattr(sys, 'gettotalrefcount')   # This is a Python debug build (--with-pydebug)
if __with_pydebug:
    # a debug build does not install the default warning filters. Sadly, this breaks doctests so we
    # have to re-add them:
    warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
    warnings.filterwarnings('ignore', category=ImportWarning)
    warnings.filterwarnings('ignore', category=ResourceWarning)
else:
    deprecationWarning = ('ignore', None, DeprecationWarning, None, 0)
    if deprecationWarning in warnings.filters:
        warnings.filters.remove(deprecationWarning)

# Ignore all deprecations from IPython etc.
warnings.filterwarnings('ignore', category=DeprecationWarning,
    module='(IPython|ipykernel|jupyter_client|jupyter_core|nbformat|notebook|ipywidgets|storemagic|jedi)')

# scipy 1.18 introduced reprecation warnings on a number of things they are moving to
# numpy, e.g. DeprecationWarning: scipy.array is deprecated
#             and will be removed in SciPy 2.0.0, use numpy.array instead
# This affects networkx 2.2 up and including 2.4 (cf. :trac:29766)
warnings.filterwarnings('ignore', category=DeprecationWarning,
    module='(scipy|networkx)')

# However, be sure to keep OUR deprecation warnings
warnings.filterwarnings('default', category=DeprecationWarning,
    message=r'[\s\S]*See https?://trac\.sagemath\.org/[0-9]* for details.')

# Ignore Python 3.9 deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning,
    module='ast')

# Ignore packaging 20.5 deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning,
    module='(.*[.]_vendor[.])?packaging')

# Ignore numpy warnings triggered by pythran
warnings.filterwarnings('ignore', category=DeprecationWarning,
                        module='pythran')

warnings.filterwarnings('ignore', category=DeprecationWarning,
                        message='The distutils(.sysconfig module| package) is deprecated',
                        module='Cython|distutils|numpy|sage.env|sage.features')

################ end setup warnings ###############################


from .all__sagemath_environment import *


###################################################################

# This import also sets up the interrupt handler
from cysignals.signals import (AlarmInterrupt, SignalError,
        sig_on_reset as sig_on_count)

from time                import sleep
from functools import reduce  # in order to keep reduce in python3

import sage.misc.lazy_import

from sage.misc.all       import *         # takes a while
from sage.typeset.all    import *
from sage.repl.all       import *

from sage.misc.sh import sh

from sage.libs.all       import *
from sage.data_structures.all import *
from sage.doctest.all    import *

from sage.structure.all  import *
from sage.rings.all      import *
from sage.arith.all      import *
from sage.matrix.all     import *

from sage.modules.all    import *
from sage.monoids.all    import *
from sage.algebras.all   import *
from sage.modular.all    import *
from sage.sat.all        import *
from sage.schemes.all    import *
from sage.graphs.all     import *
from sage.groups.all     import *
from sage.arith.power    import generic_power as power
from sage.databases.all  import *
from sage.categories.all import *
from sage.sets.all       import *
from sage.probability.all import *
from sage.interfaces.all import *

lazy_import('sage.tests', 'all', as_='tests', deprecation=27337)
from sage.cpython.all    import *

from sage.crypto.all     import *
import sage.crypto.mq as mq

from sage.plot.all       import *
from sage.plot.plot3d.all     import *

from sage.coding.all     import *
from sage.combinat.all   import *

from sage.geometry.all   import *
from sage.geometry.triangulation.all   import *

from sage.dynamics.all   import *

from sage.homology.all   import *

from sage.topology.all   import *

from sage.quadratic_forms.all import *

from sage.games.all      import *

lazy_import('sage.media.wav', 'Wave', as_='wave', deprecation=12673)

from sage.logic.all      import *

from sage.numerical.all  import *

from sage.stats.all      import *
import sage.stats.all as stats

lazy_import("sage.finance", "all", as_="finance", deprecation=32427)

from sage.parallel.all   import *

from sage.ext.fast_callable  import fast_callable
from sage.ext.fast_eval      import fast_float

from sage.sandpiles.all import *

from sage.tensor.all     import *

from sage.matroids.all   import *

from sage.game_theory.all import *

from sage.knots.all import *

from cysignals.alarm import alarm, cancel_alarm

# Lazily import interacts (#15335)
lazy_import('sage.interacts', 'all', 'interacts')

from copy import copy, deepcopy

# The code executed here uses a large amount of Sage components
from sage.rings.qqbar import _init_qqbar
_init_qqbar()

try:
    from sage.symbolic.all   import *
    from sage.functions.all  import *
    from sage.calculus.all   import *
    from sage.manifolds.all import *
    from sage.lfunctions.all import *
    from sage.geometry.riemannian_manifolds.all   import *
except ImportError:
    pass

###########################################################
#### WARNING:
# DO *not* import numpy / matplotlib / networkx here!!
# Each takes a surprisingly long time to initialize,
# and that initialization should be done more on-the-fly
# when they are first needed.
###########################################################

CC = ComplexField()
QQ = RationalField()
RR = RealField()  # default real field
ZZ = IntegerRing()

true = True
false = False
oo = infinity
from sage.rings.imaginary_unit import I
i = I

from sage.misc.copying import license
copying = license
copyright = license

_cpu_time_ = cputime()
_wall_time_ = walltime()


def quit_sage(verbose=True):
    """
    Does nothing. Code that needs cleanup should register its own
    handler using the atexit module.
    """
    from sage.misc.superseded import deprecation
    deprecation(8784, 'quit_sage is deprecated and now does nothing; please simply delete it')


from sage.misc.persist import register_unpickle_override
register_unpickle_override('sage.categories.category', 'Sets', Sets)
register_unpickle_override('sage.categories.category_types', 'HeckeModules', HeckeModules)
register_unpickle_override('sage.categories.category_types', 'Objects', Objects)
register_unpickle_override('sage.categories.category_types', 'Rings', Rings)
register_unpickle_override('sage.categories.category_types', 'Fields', Fields)
register_unpickle_override('sage.categories.category_types', 'VectorSpaces', VectorSpaces)
register_unpickle_override('sage.categories.category_types', 'Schemes_over_base', sage.categories.schemes.Schemes_over_base)
register_unpickle_override('sage.categories.category_types', 'ModularAbelianVarieties', ModularAbelianVarieties)
register_unpickle_override('sage.libs.pari.gen_py', 'pari', pari)

# Cache the contents of star imports.
sage.misc.lazy_import.save_cache_file()


### Debugging for Singular, see trac #10903
# from sage.libs.singular.ring import poison_currRing
# sys.settrace(poison_currRing)


# Set a new random number seed as the very last thing
# (so that printing initial_seed() and using that seed
# in set_random_seed() will result in the same sequence you got at
# Sage startup).
set_random_seed()


# From now on it is ok to resolve lazy imports
sage.misc.lazy_import.finish_startup()


def sage_globals():
    r"""
    Return the Sage namespace.

    EXAMPLES::

        sage: 'log' in sage_globals()
        True
        sage: 'MatrixSpace' in sage_globals()
        True
        sage: 'Permutations' in sage_globals()
        True
        sage: 'TheWholeUniverse' in sage_globals()
        False
    """
    return globals()
