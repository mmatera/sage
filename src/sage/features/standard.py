r"""
Check for various standard packages (for modularized distributions)

These features are provided by standard packages in the Sage distribution.
"""

# *****************************************************************************
#       Copyright (C) 2023 Matthias Koeppe
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  https://www.gnu.org/licenses/
# *****************************************************************************

from . import PythonModule
from .join_feature import JoinFeature


def all_features():
    return [PythonModule('cvxopt', spkg='pypi:cvxopt', type='standard'),
            PythonModule('fpylll', spkg='pypi:fpylll', type='standard'),
            JoinFeature('ipython', (PythonModule('IPython'),), spkg='pypi:ipython', type='standard'),
            JoinFeature('lrcalc_python', (PythonModule('lrcalc'),), spkg='pypi:lrcalc', type='standard'),
            PythonModule('mpmath', spkg='pypi:mpmath', type='standard'),
            PythonModule('networkx', spkg='pypi:networkx', type='standard'),
            PythonModule('numpy', spkg='pypi:numpy', type='standard'),
            PythonModule('pexpect', spkg='pypi:pexpect', type='standard'),
            JoinFeature('pillow', (PythonModule('PIL'),), spkg='pypi:pillow', type='standard'),
            JoinFeature('pplpy', (PythonModule('ppl'),), spkg='pypi:pplpy', type='standard'),
            PythonModule('primecountpy', spkg='pypi:primecountpy', type='standard'),
            PythonModule('ptyprocess', spkg='pypi:ptyprocess', type='standard'),
            PythonModule('pyparsing', spkg='pypi:pyparsing', type='standard'),
            PythonModule('requests', spkg='pypi:requests', type='standard'),
            PythonModule('scipy', spkg='pypi:scipy', type='standard'),
            PythonModule('sympy', spkg='pypi:sympy', type='standard')]
