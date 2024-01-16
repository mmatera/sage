# sage_setup: distribution = sagemath-combinat
"""
Hecke Monoids
"""
#*****************************************************************************
#  Copyright (C) 2015 Nicolas M. Thiéry <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.misc.cachefunc import cached_function
from sage.sets.finite_set_maps import FiniteSetMaps

@cached_function
def HeckeMonoid(W):
    r"""
    Return the `0`-Hecke monoid of the Coxeter group `W`.

    INPUT:

    - `W` -- a finite Coxeter group

    Let `s_1,\ldots,s_n` be the simple reflections of `W`. The 0-Hecke
    monoid is the monoid generated by projections `\pi_1,\ldots,\pi_n`
    satisfying the same braid and commutation relations as the `s_i`.
    It is of same cardinality as `W`.

    .. NOTE::

        This is currently a very basic implementation as the submonoid
        of sorting maps on `W` generated by the simple projections of
        `W`. It's only functional for `W` finite.

    .. SEEALSO::

        - :class:`CoxeterGroups`
        - :class:`CoxeterGroups.ParentMethods.simple_projections`
        - :class:`IwahoriHeckeAlgebra`

    EXAMPLES::

        sage: from sage.monoids.hecke_monoid import HeckeMonoid
        sage: W = SymmetricGroup(4)
        sage: H = HeckeMonoid(W); H
        0-Hecke monoid of the Symmetric group of order 4! as a permutation group
        sage: pi = H.monoid_generators(); pi
        Finite family {1: ..., 2: ..., 3: ...}
        sage: all(pi[i]^2 == pi[i] for i in pi.keys())
        True
        sage: pi[1] * pi[2] * pi[1] == pi[2] * pi[1] * pi[2]
        True
        sage: pi[2] * pi[3] * pi[2] == pi[3] * pi[2] * pi[3]
        True
        sage: pi[1] * pi[3] == pi[3] * pi[1]
        True
        sage: H.cardinality()
        24
    """
    ambient_monoid = FiniteSetMaps(W, action="right")
    pi = W.simple_projections(length_increasing=True).map(ambient_monoid)
    H = ambient_monoid.submonoid(pi)
    H.rename("0-Hecke monoid of the %s" % W)
    return H
