r"""
Solve S-unit equation x + y = 1

Inspired by work of Tzanakis--de Weger, Baker--W{\"{u}}stholz and Smart, we use the LLL methods in Sage to implement an algorithm that returns all S-unit solutions to the equation x + y = 1.

REFERENCES:

- [MR2016]_

- [Sma1995]_

- [Sma1998]_

AUTHORS:

- Alejandra Alvarado, Angelos Koutsianas, Beth Malmskog, Christopher Rasmussen, Christelle Vincent, Mckenzie West (2017-01-10): original version

EXAMPLE::

    sage: K.<xi> = NumberField(x^2+x+1)
    sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
    sage: S=SUK.primes()
    sage: solve_S_unit_equation(K, S, 200)
    [[(2, 1), (4, 0), xi + 2, -xi - 1],
     [(5, -1), (4, -1), 1/3*xi + 2/3, -1/3*xi + 1/3],
     [(5, 0), (1, 0), -xi, xi + 1],
     [(1, 1), (2, 0), -xi + 1, xi]]
"""


#*****************************************************************************
#       Copyright (C) 2017 Alejandra Alvarado <aalvarado2 at eiu.edu>
#                          Angelos Koutsianas <koutsis.jr at gmail.com>
#                          Beth Malmskog <beth.malmskog at gmail.com>
#                          Christopher Rasmussen <crasmussen at wesleyan.edu>
#                          Christelle Vincent <christelle.vincent at uvm.edu>
#                          Mckenzie West <mckenzierwest at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from __future__ import absolute_import

import numpy
from math import pi
from sage.misc.prandom import random

from sage.rings.ring import Field
from sage.rings.all import Infinity
from sage.rings.number_field.number_field import NumberField
from sage.rings.number_field.unit_group import UnitGroup
from sage.rings.number_field.number_field_ideal import NumberFieldIdeal
from sage.rings.number_field.number_field_element import NumberFieldElement
from sage.rings.polynomial.polynomial_ring import polygen
from sage.rings.polynomial.polynomial_element import Polynomial
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.number_field.number_field import NumberField_absolute
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.finite_rings.integer_mod_ring import Integers
from sage.rings.finite_rings.integer_mod import mod
from sage.rings.integer_ring import ZZ
from sage.rings.integer import Integer
from sage.rings.rational_field import QQ
from sage.rings.real_mpfr import RealField, RR
from sage.rings.padics.factory import Qp
from sage.rings.fast_arith import prime_range
from sage.modules.free_module_element import zero_vector
from sage.groups.abelian_gps.values import AbelianGroupWithValues_class
from sage.combinat.multichoose_nk import MultichooseNK
from sage.combinat.combination import Combinations
from sage.misc.all import prod
from sage.arith.all import gcd, factor, lcm, CRT
from sage.arith.all import factorial
from copy import copy

def set_R(prec = None):
    r"""
    Return a real field of precision ``prec``

    INPUT:

    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    - The real field ``RealField(prec)``, with precision 106 by default

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import set_R
        sage: set_R()
        Real Field with 106 bits of precision

    ::

        sage: set_R(53)
        Real Field with 53 bits of precision
    """
    if prec is None:
        return RealField(106)
    else:
        return RealField(prec)

def is_real(v, prec = None):
    r"""
    Return ``True`` if ``v`` is real, ``False`` if ``v`` is complex

    INPUT:

    - ``v`` -- an infinite place of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    A boolean indicating whether a place is real (``True``) or complex (``False``).

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import is_real
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: is_real(phi_real)
        True

        sage: is_real(phi_complex)
        False

    It is an error to put in a finite place

    ::

        sage: is_real(v_fin)
        Traceback (most recent call last):
        ...
        AttributeError: 'NumberFieldFractionalIdeal' object has no attribute 'im_gens'

    """
    R = set_R(prec)

    try:
        R(v.im_gens()[0])
        return True
    except TypeError:
        return False

def abs_val(SUK, v, iota, prec = None):
    r"""
    Return the value `|\iota|_{v}`.

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a place of ``K``, finite (a fractional ideal) or infinite (element of ``SUK.number_field().places(prec)``)
    - ``iota`` -- an element of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The absolute value as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import abs_val
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: abs_val(SUK,phi_real,xi^2)
        2.080083823051904114530056824358

        sage: abs_val(SUK,phi_complex,xi^2)
        4.326748710922225349406744498992

        sage: abs_val(SUK,v_fin,xi^2)
        0.1111111111111111111111111111111
    """
    R = set_R(prec)
    K = SUK.number_field()
    primes = SUK.primes()
    num_primes = len(primes)
    rank = SUK.rank()
    try:
        p = v.smallest_integer()
        iota_ideal = K.ideal(K(iota))
        exponent = - v.residue_class_degree() * iota_ideal.valuation(v)
        return R(p**exponent)
    except AttributeError:
        if is_real(v):
            return R(v(iota).abs())
        else:
            return R(v(iota).abs()**2)

def column_Log(SUK, iota, U, prec = None):
    r"""
    Return the log vector of ``iota``; i.e., the logs of all the valuations

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``iota`` -- an element of ``K``
    - ``U`` -- a list of places (finite or infinite) of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The log vector as a list of real numbers

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import column_Log
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_complex = K.places()[1]
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: U = [phi_complex, v_fin]
        sage: column_Log(SUK, xi^2, U)
        [1.464816384890812968648768625966, -2.197224577336219382790490473845]

    REFERENCE:

    - [Sma1995]_ p. 823
    """
    R = set_R(prec)
    from sage.functions.log import log
    return [ R(log(abs_val(SUK,v,iota,prec))) for v in U]

def c1_func(SUK, prec = None):
    r"""
    Return the constant `c_1` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c1``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c1_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))

        sage: c1_func(SUK)
        1.174298947359884381924644003448

    REFERENCE:

    - [Sma1995]_ p. 823
    """
    R = set_R(prec)
    all_places = list(SUK.primes()) + SUK.number_field().places(prec)
    Possible_U = Combinations(all_places, SUK.rank())
    c1 = 0
    for U in Possible_U:
        # first, build the matrix C_{i,U}
        columns_of_C = []
        for unit in SUK.fundamental_units():
            columns_of_C.append( column_Log(SUK, unit, U, prec) )
        from sage.matrix.constructor import Matrix
        C = Matrix(SUK.rank(), SUK.rank(), columns_of_C)
        # Is it invertible?
        if abs(C.determinant()) > 10**(-10):
            poss_c1 = C.inverse().apply_map(abs).norm(Infinity)
            c1 = max(poss_c1,c1)
    return R(c1)

def c3_func(SUK, prec = None):
    r"""
    Return the constant `c_3` from Smart's 1995 TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c3``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c3_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))

        sage: c3_func(SUK)
        0.4257859134798034746197327286726

    .. NOTE::

        The numerator should be as close to 1 as possible, especially as the rank of the `S`-units grows large

    REFERENCE:

    - [Sma1995]_ p. 823

    """

    R = set_R(prec)
    return R(R(0.9999999)/(c1_func(SUK,prec)*SUK.rank()))

def c4_func(SUK,v, A, prec = None):
    r"""
    Return the constant `c_4` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a place of ``K``, finite (a fractional ideal) or infinite (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- the set of the product of the coefficients of the ``S``-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c4``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c4_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: A = K.roots_of_unity()

        sage: c4_func(SUK,phi_real,A)
        1.000000000000000000000000000000

        sage: c4_func(SUK,phi_complex,A)
        1.000000000000000000000000000000

        sage: c4_func(SUK,v_fin,A)
        1.000000000000000000000000000000

    REFERENCE:

    - [Sma1995]_ p. 824
    """
    R = set_R(prec)
    return max( [abs_val(SUK, v, alpha, prec) for alpha in A])

def c5_func(SUK, v, prec = None):
    r"""
    Return the constant `c_5` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c5``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c5_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: c5_func(SUK,v_fin)
        0.1291890135314859378711048471736

    REFERENCE:

    - [Sma1995]_ p. 824
    """
    R = set_R(prec)
    from sage.functions.log import log
    return R(c3_func(SUK, prec)/(v.residue_class_degree()*log(v.smallest_integer())*v.ramification_index()))

def c6_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_6` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``
    - ``A`` -- the set of the product of the coefficients of the ``S``-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c6``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c6_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: A = K.roots_of_unity()

        sage: c6_func(SUK,v_fin,A)
        0.0000000000000000000000000000000

    REFERENCE:

    - [Sma1995]_ p. 824

    """
    R = set_R(prec)
    from sage.functions.log import log
    return R(log(c4_func(SUK, v, A, prec))/(v.residue_class_degree()*log(v.smallest_integer())*v.ramification_index()))

def c7_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_7` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``
    - ``A`` -- the set of the product of the coefficients of the ``S``-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c7``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c7_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: A = K.roots_of_unity()

        sage: c7_func(SUK,v_fin,A)
        0.0000000000000000000000000000000

    REFERENCE:

    - [Sma1995]_ p. 824
    """
    R = set_R(prec)
    from sage.functions.log import log
    return R(log(c4_func(SUK, v, A, prec))/c3_func(SUK, prec))

def beta_ns(SUK,v):
    r"""
    Return a list of pairs `[\beta,|\beta|_v]`, for `\beta` in the fundamental units of SUK

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``

    OUTPUT:

    The list of pairs ``[beta,val_v(beta)]``, for ``beta`` in the fundamental units of ``SUK`` (elements of ``K``), ``val_v(beta)`` is an integer

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import beta_ns
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: beta_ns(SUK,v_fin)
        [[xi^2 - 2, 0], [xi, 1]]

    .. NOTE::

        `n_0` is the valuation of the coefficient `\alpha_d` of the `S`-unit equation such that `|\alpha_d \tau_d|_v = 0`
        We have set `n_0 = 0` here since the coefficients are roots of unity

    REFERENCE:

    - [Sma1995]_ pp. 824-825
    """
    betas = SUK.fundamental_units()
    # n_0 = valuation_v of one of the coefficients of the equation = 0 for x + y = 1 p. 824
    return [[beta,beta.valuation(v)] for beta in betas]

def beta_k(betas_and_ns):
    r"""
    Return a pair `[\beta_k,|beta_k|_v]`, where `\beta_k` has the smallest nonzero valuation in absolute value of the list ``betas_and_ns``

    INPUT:

    - ``betas_and_ns`` -- a list of pairs ``[beta,val_v(beta)]`` outputted from the function ``beta_ns``

    OUTPUT:

    The pair ``[beta_k,v(beta_k)]``, where ``beta_k`` is an element of ``K`` and ``val_v(beta_k)`` is a integer

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import beta_k, beta_ns
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: betas = beta_ns(SUK,v_fin)
        sage: beta_k(betas)
        [xi, 1]

    REFERENCE:

    - [Sma1995]_ pp. 824-825
    """
    for pair in betas_and_ns:
        if pair[1].abs() != 0:
            good_pair = pair
            break
    for pair in betas_and_ns:
        if (pair[1].abs() != 0 and pair[1].abs() < good_pair[1].abs()):
            good_pair = pair
    return good_pair

def mus(SUK,v):
    r"""
    Return a list `[\mu]`, for `\mu` defined on pp. 824-825 of TCDF, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``

    OUTPUT:

    A list ``[mus]`` where each ``mu`` is an element of ``K``

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import mus
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: mus(SUK,v_fin)
        [xi^2 - 2]

    REFERENCE:

    - [Sma1995]_ pp. 824-825

    """
    beta_and_ns = beta_ns(SUK,v)
    if all(pair[1]==0 for pair in beta_and_ns):
        return SUK.fundamental_units()
    else:
        good_pair = beta_k(beta_and_ns)
        temp = [(beta[0]**good_pair[1])*(good_pair[0]**(-beta[1])) for beta in beta_and_ns]
        temp.remove(1)
        return temp

def possible_mu0s(SUK,v):
    r"""
    Return a list `[\mu_0]` of all possible `\mu_0`s defined on pp. 824-825 of TCDF, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K``

    OUTPUT:

    A list ``[mu0s]`` where each ``mu0`` is an element of ``K``

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import possible_mu0s
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: possible_mu0s(SUK,v_fin)
        [-1, 1]

    .. NOTE::

        `n_0` is the valuation of the coefficient `\alpha_d` of the `S`-unit equation such that `|\alpha_d \tau_d|_v = 0`
        We have set `n_0 = 0` here since the coefficients are roots of unity
        `\alpha_0` is not defined in the paper, we set it to be 1

    REFERENCE:

    - [Sma1995]_ pp. 824-825, but we modify the definition of ``sigma`` (``sigma_tilde``) to make it easier to code

    """
    beta_and_ns = beta_ns(SUK,v)
    betak, nk = beta_k(beta_and_ns)
    ns = [beta[1] for beta in beta_and_ns if beta[0] != betak]
    betas = [beta[0] for beta in beta_and_ns if beta[0] != betak]
    mu0s = []
    for rs in MultichooseNK(nk.abs(),len(betas)):
        # n_0 = valuation_v of one of the coefficients of the equation = 0 for x + y = 1 p. 824
        n_rs = zip(ns,rs)
        sigma_tilde = -(sum([n_r[0]*n_r[1] for n_r in n_rs]))
        if sigma_tilde % nk == 0:
            beta_rs = zip(betas,rs)
            temp_prod = prod([beta_r[0]**beta_r[1] for beta_r in beta_rs])*betak**(sigma_tilde/nk)
            for alpha0 in SUK.roots_of_unity():
                if alpha0*temp_prod not in mu0s:
                    mu0s.append(alpha0*temp_prod)
    return mu0s

def modified_height(SUK,v,D,b, prec = None):
    r"""
    Return the modified height at the finite place ``v``

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an finite place of ``K``
    - ``D`` -- an auxiliary quantity (an integer)
    - ``b`` -- an element of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The modified height at the place ``v``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import modified_height
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: modified_height(SUK,v_fin,2*K.degree(),xi^2)
        0.7324081924454063363683076204325

    REFERENCES:

    - [Sma1998]_ p. 226

    """
    R = set_R(prec)
    d = SUK.number_field().degree()
    f_p = v.residue_class_degree()
    p = v.smallest_integer()
    from sage.functions.log import log
    max_log_b = max([log(phi(b)).abs() for phi in SUK.number_field().places(prec)])
    return R(max([b.global_height(),max_log_b/(2*pi*D),f_p*log(p)/d]))

def local_c3(SUK,v,D, prec = None):
    r"""
    Return a factor of the constant `c_3` defined on p. 226 of [Sma1998]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an finite place of ``K``
    - ``D`` -- an auxiliary quantity (an integer)
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    A factor of the constant ``c3``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import local_c3
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]

        sage: local_c3(SUK,v_fin,2*K.degree())
        0.3081828906869137495462570381080

    REFERENCE:

    - [Sma1998]_ p. 226

    """
    R = set_R(prec)
    mus_prod = prod([modified_height(SUK,v,D,b,prec) for b in mus(SUK,v)])
    return R(max([mus_prod*modified_height(SUK,v,D,mu0,prec) for mu0 in possible_mu0s(SUK,v)]))

def c8_c9_func(SUK, v, A, prec = None):
    r"""
    Return the constants `c_8` and `c_9` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K`` (a fractional ideal)
    - ``A`` -- the set of the product of the coefficients of the $S$-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constants ``c8`` and ``c9``, as real numbers

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c8_c9_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: A = K.roots_of_unity()

        sage: c8_c9_func(SUK,v_fin,A)
        (4.524941291354698258804956696127e15, 1.621521281297160786545580368612e16)

    REFERENCES:

    - [Sma1995]_ p. 825
    - [Sma1998]_ p. 226, Theorem A.2 for the local constants

    """
    R = set_R(prec)
    num_mus = len(mus(SUK,v))+1
    p = v.smallest_integer()
    f_p = v.residue_class_degree()
    d = SUK.number_field().degree()
    if p == 2:
        local_c2 = 197142*36**num_mus
    elif p%4 == 1:
        local_c2 = 35009*(45/2)**num_mus
    else:
        local_c2 = 30760*25**num_mus
    x = polygen(SUK.number_field())
    if ( p > 2 and not ((x**2+1).is_irreducible()) ) or ( p==2 and not ((x**2+3).is_irreducible()) ):
        D = d
    else:
        D = 2*d
    from sage.functions.log import log
    l_c3 = (num_mus+1)**(2*num_mus+4)*p**(D * f_p/d)*(f_p*log(p))**(-num_mus-1)*D**(num_mus+2)
    l_c3 *= local_c3(SUK,v,D, prec)
    H = max([modified_height(SUK,v,D,alpha, prec) for alpha in mus(SUK,v)+possible_mu0s(SUK,v)])
    if p == 2:
        local_c4 = log(3*2**10*(num_mus+1)**2*D**2*H)
    else:
        local_c4 = log(2**11*(num_mus+1)**2*D**2*H)
    local_c5 = 2*log(D)
    return R(local_c2*l_c3*local_c4), R(local_c2*l_c3*local_c4*local_c5)

def c10_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_{10}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K`` (a fractional ideal)
    - ``A`` -- the set of the product of the coefficients of the $S$-unit equation with each root of unity of ``K``
   - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c10``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import c10_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v_fin = tuple(K.primes_above(3))[0]
        sage: A = K.roots_of_unity()

        sage: c10_func(SUK,v_fin,A)
        9.475576673109275443280257946930e17

    REFERENCE:

    - [Sma1995]_ p. 824
    """
    R = set_R(prec)
    e_h = v.ramification_index()
    c_8, c_9 = c8_c9_func(SUK, v, A, prec)
    from sage.functions.log import log
    return R((2/(e_h*c5_func(SUK,v,prec)))*(e_h*c6_func(SUK, v, A, prec) + c_9 + c_8 * log( c_8/(e_h*c5_func(SUK,v, prec)))))

def c11_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_{11}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a place of ``K``, finite (a fractional ideal) or infinite (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- the set of the product of the coefficients of the $S$-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c11``, a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c11_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: c11_func(SUK,phi_real,A)
        3.255848343572896153455615423662

        sage: c11_func(SUK,phi_complex,A)
        6.511696687145792306911230847323

    REFERENCE:

    - [Sma1995]_ p. 825
    """
    R = set_R(prec)
    from sage.functions.log import log
    if is_real(v,prec):
        return R(log(4*c4_func(SUK, v, A, prec))/(c3_func(SUK, prec)))
    else:
        from sage.functions.other import sqrt
        return R(2*(log(4*sqrt(c4_func(SUK,v, A, prec))))/(c3_func(SUK, prec)))

def c12_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_{12}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of ``S``-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- the set of the product of the coefficients of the ``S``-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c12``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c12_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: c12_func(SUK,phi_real,A)
        2.000000000000000000000000000000

        sage: c12_func(SUK,phi_complex,A)
        2.000000000000000000000000000000

    REFERENCES:

    - [Sma1995]_ p. 825
    """
    R = set_R(prec)
    if is_real(v,prec):
        return R(2*c4_func(SUK, v, A, prec))
    else:
        from sage.functions.other import sqrt
        return R(2*sqrt(c4_func(SUK,v, A, prec)))

def c13_func(SUK, v, prec = None):
    r"""
    Return the constant `c_{13}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c13``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c13_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]

        sage: c13_func(SUK,phi_real)
        0.4257859134798034746197327286726

        sage: c13_func(SUK,phi_complex)
        0.2128929567399017373098663643363

    REFERENCE:

    - [Sma1995]_ p. 825
    """
    R = set_R(prec)
    if is_real(v,prec):
        return c3_func(SUK,prec)
    else:
        return c3_func(SUK,prec)/2

def Baker_C(t,d,prec = None):
    r"""
    Return `C(t,d)` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``t`` -- the rank of the $S$-unit group (an integer)
    - ``d`` -- the degree of ``K`` (an integer)
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``C(t,d)`` as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import Baker_C
        sage: Baker_C(3,4)
        3.371389974809293972795830360284e19

    REFERENCE:

    - [Sma1998]_ p. 225, Theorem A.1

    """
    R = set_R(prec)
    from sage.functions.log import log
    return R( 18 * factorial(t+2) * (t+1)**(t+2) * (32*d)**(t + 3) * log( 2*(t+1) * d) )

def hprime(SUK, alpha, v, prec = None):
    r"""
    Return the modified height at the infinite place `v`

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``alpha`` -- an element of ``K``
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The modified height at the place `v`, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import hprime
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]

        sage: hprime(SUK,xi^2,phi_real)
        0.7324081924454063363683076204325

        sage: hprime(SUK,xi^2,phi_complex)
        0.7395879186929970039443560381187

    REFERENCES:

    - [Sma1998]_ p. 225

    """
    R = set_R(prec)
    from sage.functions.log import log
    return R(max(alpha.global_height(), 1/SUK.number_field().degree(), log(v(alpha)).abs()/SUK.number_field().degree()))

def c14_func(SUK,v,A,prec = None):
    r"""
    Return the constant `c_{14}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- the set of the product of the coefficients of the ``S``-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c14``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c14_func, set_R, Baker_C, hprime
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: c14_func(SUK,phi_real,A)
        2.661434475699529175064652896133e14

        sage: c14_func(SUK,phi_complex,A)
        5.908765797306433904563179346367e14

    REFERENCES:

    - [Sma1995]_ p. 825
    - [Sma1998]_ p. 225, Theorem A.1

    """
    R = set_R(prec)
    c_1 = Baker_C(SUK.rank(),SUK.number_field().degree(),prec)
    hproduct = c_1 * prod([hprime(SUK, alpha, v, prec) for alpha in SUK.gens_values()])
    return hproduct

def c15_func(SUK, v, A, prec = None):
    r"""
    Return the constant `c_{15}` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- the set of the product of the coefficients of the $S$-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``c15``, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import c15_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: c15_func(SUK,phi_real,A)
        4.396386097852707394927181864635e16

        sage: c15_func(SUK,phi_complex,A)
        2.034870098399844430207420286581e17

    REFERENCE:

    - [Sma1995]_ p. 825

    """
    R = set_R(prec)
    from sage.functions.log import log
    return R(2*(log(c12_func(SUK,v,A,prec))+c14_func(SUK,v,A,prec)*log((SUK.rank()+1)*c14_func(SUK,v,A,prec)/c13_func(SUK,v,prec)))/c13_func(SUK,v,prec))

def K0_func(SUK, A, prec = None):
    r"""
    Return the constant `K_0` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- a finite place of ``K`` (a fractional ideal)
    - ``A`` -- the set of the product of the coefficients of the $S$-unit equation with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``K0``, a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import K0_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: A = K.roots_of_unity()

        sage: K0_func(SUK,A)
        9.475576673109275443280257946930e17

    REFERENCE:

    - [Sma1995]_ p. 824
    """
    R = set_R(prec)
    return R(max([c10_func(SUK,v, A, prec) for v in SUK.primes()] + [c7_func(SUK,v,A, prec) for v in SUK.primes()]))

def K1_func(SUK, v, A, prec = None):
    r"""
    Return the constant `K_1` from Smart's TCDF paper, [Sma1995]_

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``A`` -- a list of all products of each potential ``a``, ``b`` in the S-unit equation ``ax + by + 1 = 0`` with each root of unity of ``K``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    The constant ``K1,`` a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import K1_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: K1_func(SUK,phi_real,A)
        4.396386097852707394927181864635e16

        sage: K1_func(SUK,phi_complex,A)
        2.034870098399844430207420286581e17

    REFERENCES:

    - [Sma1995]_ p. 825

    """
    R = set_R(prec)
    return max([c11_func(SUK,v, A, prec), c15_func(SUK,v,A,prec)])

def cx_LLL_bound_one_embed(SUK, v, c11_LLL, c12_LLL, c13_LLL, old_K1, gens=None, prec = None):
    r"""
    Return a lower value for the constant `K_1`, obtained using LLL at an infinite place of `K`

    INPUT:

    - ``SUK`` -- a group of $S$-units
    - ``v`` -- an infinite place of ``K`` (element of ``SUK.number_field().places(prec)``)
    - ``c11_LLL`` -- the constant ``c11`` value obtained
    - ``c12_LLL`` -- the constant ``c12`` value obtained
    - ``c13_LLL`` -- the constant ``c13`` value obtained
    - ``old_K1`` -- the constant ``K1`` value obtained, either from ``K1_func`` or from a previous iteration of LLL
    - ``gens`` -- (default: None) fundamental units of ``SUK``
    - ``prec`` -- (default: None) the precision of the real field

    OUTPUT:

    A lower value for ``K1``, as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import cx_LLL_bound_one_embed, c11_func, c12_func, c13_func, K1_func
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: phi_real = K.places()[0]
        sage: phi_complex = K.places()[1]
        sage: A = K.roots_of_unity()

        sage: cx_LLL_bound_one_embed(SUK, phi_real, c11_func(SUK,phi_real, A), c12_func(SUK,phi_real,A), c13_func(SUK,phi_real),K1_func(SUK, phi_real, A)) #random
        99.00000000000000000000000000000

    .. NOTE::

        The constant `C_0` used has an element of randomness, which should improve the algorithm.
        For easily replicable results, one may double `C_0` instead
        The new value of `K_1` cannot fall below `c_{11}`, a constant computed earlier.

    REFERENCE:

    - [MR2016]_
    """
    R = set_R(prec)
    if prec is None:
        prec = 106

    if gens == None:
        gens = SUK.gens_values()

    kappa = []
    from sage.functions.log import log
    for gen in gens:
        kappa.append(log(v(gen)))

    Lemma6 = False
    t = SUK.rank()
    C0 = R(1.0)
    C = C0 * old_K1**( (t + 1)/2 )
    from sage.matrix.constructor import Matrix
    while not Lemma6 and C0 < 2**100:
        C = C0 * old_K1**( (t + 1)/2 )
        B = Matrix(ZZ, t + 1, t + 1)
        for i in xrange(0, t):
            B[i,i] = 1
            B[t - 1, i] = round(C * kappa[i].real())
            B[t , i] = round(C * kappa[i].imag())
        B[t, t] = round( C * 2.0 * pi / SUK.zeta_order() )

        if B[t - 1, t - 1] == 0: # if there is a zero in this position, LLL will struggle, so we swap out with a different kappa_i
            kk = t - 1
            while B[t - 1, kk] == 0: # find a nonzero entry
                kk -= 1
            # swap
            temp = B[t - 1, t - 1]
            B[t - 1, t - 1] = B[t - 1, kk]
            B[t - 1, kk] = temp
            temp = B[t, t - 1]
            B[t, t - 1] = B[t, kk]
            B[t, kk] = temp

        B_LLL = B.transpose().LLL().transpose()

        K2 = R( 2**(-t/2) * B_LLL.column(0).norm(2) ) # K2 is a lower bound for the length of the smallest non-zero vector in the lattice generated by the columns of B

        from sage.functions.other import sqrt
        T_L = R( (t * old_K1/2) * (SUK.zeta_order()/2 + 2 + sqrt(2)) )

        if K2**2 >= T_L**2 + (t - 1)*old_K1**2:
            Lemma6 = True

        C0 = R(C0 * (R(1.0) + random()))
        #C0 = R(2* C0)

    if not Lemma6:
        return old_K1
    else:
        from sage.functions.log import log
        S_LLL = R(sqrt(K2**2 - (t - 1)*old_K1**2))
        K1_new = R((1/c13_LLL) * ( log(C*c12_LLL) - log(S_LLL - T_L) ))
        from sage.functions.other import ceil
        return R(ceil(max([K1_new, c11_LLL])))

def round(a):
    r"""
    round any real number to the nearest integer, including integers

    INPUT:

    - ``a`` : a real number

    OUTPUT:

    The closest integer to ``a``

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import round
        sage: round(1.2)
        1

    ::

        sage: round(-9.5)
        -10

    ::

        sage: round(7)
        7

    .. NOTE::

        Integers do not have an implicit round function.
    """
    if a in ZZ:
        return a
    else:
        return a.round()

def minimal_vector(A,y):
    r"""

    INPUT:

    - ``A`` : a square n by n non-singular integer matrix whose rows generate a lattice `\mathcal L`
    - ``y`` : a row (1 by n) vector with integer coordinates

    OUTPUT:

    A low bound for the square of

    .. MATH::

        \ell (\mathcal L,\vec y) =
        \begin{cases}
        \displaystyle\min_{\vec x\in\mathcal L}\Vert\vec x-\vec y\Vert &, \vec y\not\in\mathcal L. \\
        \displaystyle\min_{0\neq\vec x\in\mathcal L}\Vert\vec x\Vert &,\vec y\in\mathcal L.
        \end{cases}`

    ALGORITHM:

    The algorithm is based on V.9 and V.10 of [Sma1998]_

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import minimal_vector
        sage: B = matrix(ZZ,2,[1,1,1,0])
        sage: y = vector(ZZ,[2,1])
        sage: minimal_vector(B,y)
        1/2

    ::

        sage: B = random_matrix(ZZ,3)
        sage: B #random
            [-2 -1 -1]
            [ 1  1 -2]
            [ 6  1 -1]
        sage: y = vector([1,2,100])
        sage: minimal_vector(B,y) #random
        15/28
    """
    if A.is_singular():
        raise ValueError('The matrix A is singular')

    n = len(y)
    c1 = 2**(n-1)
    ALLL = A.LLL()
    ALLLinv = ALLL.inverse()
    ybrace = [(a-round(a)).abs() for a in y * ALLLinv if (a-round(a)) != 0]

    if len(ybrace) == 0:
        return (ALLL.rows()[0].norm())**2 / c1
    else:
        sigma = ybrace[len(ybrace)-1]
        return ((ALLL.rows()[0].norm())**2 * sigma) / c1

def higher_precision(place,new_prec):
    r"""

    Allow for a higher precision when numbers get large

    INPUT:

    - ``place`` -- (ring morphism) an infinite place of a number field `K`
    - ``new_prec`` -- the new precision

    OUTPUT:

    The ``place`` but with precision equal with ``new_prec``

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import higher_precision
        sage: K.<a> = NumberField(x^2-2)
        sage: place = K.places()[0]
        sage: place
        Ring morphism:
          From: Number Field in a with defining polynomial x^2 - 2
          To:   Real Field with 106 bits of precision
          Defn: a |--> -1.414213562373095048801688724210
        sage: higher_precision(place,50)
        Ring morphism:
          From: Number Field in a with defining polynomial x^2 - 2
          To:   Real Field with 50 bits of precision
          Defn: a |--> -1.4142135623731

    ::

        sage: K.<a> = NumberField(x^4-2)
        sage: place = K.places()[0]
        sage: place
        Ring morphism:
          From: Number Field in a with defining polynomial x^4 - 2
          To:   Real Field with 106 bits of precision
          Defn: a |--> -1.189207115002721066717492233629
        sage: higher_precision(place,150)
        Ring morphism:
          From: Number Field in a with defining polynomial x^4 - 2
          To:   Real Field with 150 bits of precision
          Defn: a |--> -1.1892071150027210667174999705604759152929721
    """
    K = place.domain()
    old_prec = place.codomain().precision()
    Kplaces = K.places(prec = new_prec)
    gens = K.gens()

    #Below we check which of the candidates in Kplaces has values quite close to the initial place.

    i = 1
    while i <= old_prec:
        Q = [q for q in Kplaces if len([0 for a in gens if (q(a)-place(a)).abs() <= 2**(-i)]) == len(gens)]
        if len(Q) == 1:
            return Q[0]
        else:
            i += 1
    if i > old_prec:
        raise ValueError('I cannot find the place')

def e_s_real(a,place):
    r"""

    INPUT:

    - ``a`` -- an element of a number field ``K``
    - ``place`` -- (ring morphism) an real place of ``K``

    OUTPUT:

    Return ``a`` if ``place(a)>=0``, otherwise ``-a``

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import e_s_real
        sage: K.<a> = NumberField(x^4-7)
        sage: place = K.places()[0]
        sage: e_s_real(a,place)
        -a
        sage: e_s_real(-a,place)
        -a
        sage: place(a)
        -1.626576561697785743211232345494
    """

    if place(a) < 0:
        return (-1)*a
    else:
        return a

def reduction_step_real_case(place,B0,G,c7):
    r"""

    INPUT:

    - ``place`` -- (ring morphism) an infinite place of a number field `K`
    - ``B0`` -- the initial bound
    - ``G`` -- a set of generators of the free part of the group
    - ``c7`` -- a positive real number

    OUTPUT:

    A tuple consisting of:

    1. a new upper bound, an integer
    2. a boolean value, ``True`` if we have to increase precision, otherwise ``False``

    .. NOTE::

        The constant ``c7`` in the reference page 137

    REFERENCE:

    - [Sma1998]_

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import reduction_step_real_case
        sage: K.<a> = NumberField(x^3-2)
        sage: SK = sum([K.primes_above(p) for p in [2,3,5]],[])
        sage: G = [g for g in K.S_unit_group(S = SK).gens_values() if g.multiplicative_order() == Infinity]
        sage: p1 = K.real_places(prec = 200)[0]
        sage: reduction_step_real_case(p1,10**10,G,2)
        (58, False)
    """
    n = len(G)
    from sage.functions.log import log
    from sage.functions.other import sqrt
    Glog = [log(place(e_s_real(g,place))) for g in G]
    if len([1 for g in G if place(e_s_real(g,place)).is_zero()]) > 0:
        return 0,True

    #We choose the initial value of C such that the vector v not to have 0 everywhere
    C = round(max([1/l.abs() for l in Glog if l != 0])+1)

    #if the precision we have is not high enough we have to increase it and evaluate c7 again
    if place.codomain().precision() < log(C)/log(2):
        return 0,True

    S = (n-1) * (B0)**2
    T = (1 + n * B0)/2
    finish = False
    from sage.matrix.constructor import identity_matrix, vector
    while  not finish:
        A = copy(identity_matrix(ZZ,n))
        v = vector([round(g*C) for g in Glog])

        if v[n-1] == 0: #we replace the last element of v with an other non zero
            k = [i for i,a in enumerate(v) if not a.is_zero()][0]
            v[n-1] = v[k]
            v[k] = 0
        A[n-1] = v

        #We have to work with rows because of the .LLL() function

        A = A.transpose()
        y = copy(zero_vector(ZZ,n))
        l = minimal_vector(A,y)

        #On the following lines I apply Lemma VI.1 from Smart's book page 83

        if l < T**2 + S:
            C = 2 * C
            #Again if our precision is not high enough
            if place.codomain().precision() < log(C)/log(2):
                return 0,True
        else:
            if sqrt(l-S) - T > 0:
                return round((log(C * 2)-log(sqrt(l-S) - T))/c7),False
            else:
                return B0,False

def reduction_step_complex_case(place,B0,G,g0,c7):
    r"""

    INPUT:

    - ``place`` -- (ring morphism) an infinite place of a number field `K`
    - ``B0`` -- the initial bound
    - ``G`` -- a set of generators of the free part of the group
    - ``g0`` -- an element of the torsion part of the group
    - ``c7`` -- a positive real number

    OUTPUT:

    A tuple consisting of:

    1. a new upper bound, an integer
    2. a boolean value, ``True`` if we have to increase precision, otherwise ``False``

    .. NOTE::

        The constant ``c7`` in the reference page 138

    REFERENCE:

    See [Sma1998]_.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import reduction_step_complex_case
        sage: K.<a> = NumberField([x^3-2])
        sage: SK = sum([K.primes_above(p) for p in [2,3,5]],[])
        sage: G = [g for g in K.S_unit_group(S = SK).gens_values() if g.multiplicative_order() == Infinity]
        sage: p1 = K.places(prec = 100)[1]
        sage: reduction_step_complex_case(p1,10^5,G,-1,2)
        (17, False)
    """
    precision = place.codomain().precision()
    R = set_R(precision)
    n = len(G)
    from sage.functions.log import log
    Glog_imag = [R((log(place(g))).imag_part()) for g in G]
    Glog_real = [R((log(place(g))).real_part()) for g in G]
    Glog_imag = Glog_imag + [2 * R(pi)]
    Glog_real = Glog_real + [0]
    a0log_imag = (log(place(-g0))).imag_part()
    a0log_real = (log(place(-g0))).real_part()

    #the case when the real part is 0 for all log(a_i)

    pl = higher_precision(place,2 * place.codomain().precision())
    if len([g for g in G if (pl(g).abs()-1).abs() > 2**(-place.codomain().precision())]) == 0:

        #we have only imaginary numbers and we are in case 2 as Smart's book says on page 84

        C = ZZ(1) #round(min((B0**n/100),max([1/l.abs() for l in Glog_imag if l != 0]+[0])))+1
        S = n * B0**2

        #if the precision we have is not high enough we have to increase it and evaluate c7 again
        # if precision < log(C)/log(2):
        #     return 0,True

        T = ((n+1) * B0 + 1)/2
        finish = False
        from sage.matrix.constructor import identity_matrix, vector
        while not finish:
            A = copy(identity_matrix(ZZ,n+1))
            v = vector([round(g * C) for g in Glog_imag])

            if v[n] == 0:
                #we replace the last element of v with an other non zero

                k = [i for i,a in enumerate(v) if not a.is_zero()][0]
                v[n] = v[k]
                v[k] = 0
            A[n] = v

            if A.is_singular():
                C = ZZ(2 * C)
            else:
                #We have to work with rows because of the .LLL() function

                A = A.transpose()
                y = copy(zero_vector(ZZ,n+1))
                y[n] = (-1) * round(a0log_imag * C)
                l = minimal_vector(A,y)

                #On the following lines I apply Lemma VI.1 of the reference page 83

                if l < T**2 + S:
                    C = ZZ(2 * C)

                    #The same as above if for the new C the precision is low
                    if precision < log(C)/log(2):
                        return 0,True
                else:
                    Bnew = round((log(C * 2)-log(sqrt(l-S)-T))/c7)
                    finish = True
                    if mod(y[n],A[n,n]) == 0:
                        return max(Bnew,(y[n]/A[n,n]).abs()),False
                    else:
                        return Bnew,False

    else:

        #the case when the real part is not 0 for all log(a_i)
        C = 1
        S = (n-1) * B0**2
        from sage.functions.other import sqrt
        T = ((n+1)*B0+1)/sqrt(2)
        finish = False

        #we are relabeling the Glog_real and Glog_imag s.t. the condition Real(a_n)*Im(a_(n-1))-Real(a_(n-1))*Im(a_n)!=0 to be satisfied. See page 84 of the reference.

        k = [i for i in range(len(Glog_real)) if Glog_real[i] != 0][0]
        a = Glog_real[k]
        Glog_real[k] = Glog_real[n-1]
        Glog_real[n-1] = a

        a = Glog_imag[k]
        Glog_imag[k] = Glog_imag[n-1]
        Glog_imag[n-1] = a

        from sage.matrix.constructor import identity_matrix, vector, matrix
        while not finish:

            A = copy(identity_matrix(ZZ,n+1))
            #return [g * C for g in Glog_imag]
            A[n-1] = vector([round(g * C) for g in Glog_real])
            A[n] = vector([round(g * C) for g in Glog_imag])

            if A.is_singular():
                C *= 2
            else:
                #On the following lines I apply Lemma VI.2 of the reference page 85

                A = A.transpose()
                y = copy(zero_vector(ZZ,n+1))
                y[n] = (-1) * round(a0log_imag * C)
                y[n-1] = (-1) * round(a0log_real*C)
                l = minimal_vector(A,y)


                if l <= T**2 + S:
                    C *= 2
                    #The same as above if for the new C the precision is low
                    if precision < log(C)/log(2):
                        return 0,True
                else:
                    Bnew = round((log(C * 2)-log(sqrt(l-S)-T))/c7)

                    #we take into account the second case of the theorem VI.2 of the reference page 85

                    M = matrix(ZZ,2,[A[n-1,n-1],A[n-1,n],A[n,n-1],A[n,n]])
                    b = vector(ZZ,2,[-y[n-1],-y[n]])
                    if M.determinant() == 1 or M.determinant() == -1:
                        x = M.inverse() * b
                        return max(Bnew,x[0].abs(),x[1].abs()),False
                    else:
                        return Bnew,False

def cx_LLL_bound(SUK,A, prec = None):
    r"""
    Return the maximum of all of the `K_1`'s as they are LLL-optimized for each infinite place `v`

    INPUT:

    - ``SUK`` -- a group of `S`-units
    - ``A`` -- a list of all products of each potential ``a``, ``b`` in the `S`-unit equation ``ax + by + 1 = 0`` with each root of unity of ``K``

    OUTPUT:

    A bound for the exponents at the infinite place, as a real number

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import cx_LLL_bound
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: A = K.roots_of_unity()

        sage: cx_LLL_bound(SUK,A)
        22
    """
    #R = set_R(prec)
    if prec is None:
        prec = 106
    cx_LLL = 0
    #initialize a bound, a bad guess, as we iterate over the places of the number field, we will replace its value with the largest complex LLL bound we've found across the places
    for v in SUK.number_field().places(prec = prec):
        prec_v = prec
        #c11_LLL = c11_func(SUK,v,A)
        #c12_LLL = c12_func(SUK,v,A)
        c13_LLL = c13_func(SUK,v,prec_v)
        cx_bound = K1_func(SUK,v,A,prec_v)
        #cx_bound is the LLL bound according to this place, it will be replaced as LLL gives us smaller bounds
        if is_real(v):
            new_bound,inc_prec = reduction_step_real_case(v, cx_bound, SUK.fundamental_units(), c13_LLL)
            while inc_prec:
                prec_v = 2*prec_v
                v = higher_precision(v,prec_v)
                c13_LLL = c13_func(SUK,v,prec_v)
                cx_bound = K1_func(SUK,v,A,prec_v)
                new_bound, inc_prec = reduction_step_real_case(v, cx_bound, SUK.fundamental_units(), c13_LLL)
            counter = 0
            while (cx_bound - new_bound).abs() > .01*cx_bound and counter < 15:
                #We fear a loop that is not convergent, this is the purpose of the counter
                #Repeat complex LLL until we get essentially no change from it
                cx_bound = min(cx_bound,new_bound)
                new_bound, inc_prec = reduction_step_real_case(v, cx_bound, SUK.fundamental_units(),c13_LLL)
                while inc_prec:
                    prec_v = 2*prec_v
                    v = higher_precision(v,prec_v)
                    c13_LLL = c13_func(SUK,v,prec_v)
                    new_bound, inc_prec = reduction_step_real_case(v, cx_bound, SUK.fundamental_units(), c13_LLL)
                counter += 1
        else:
            prec_v = prec
            new_bound, inc_prec = reduction_step_complex_case(v, cx_bound, SUK.fundamental_units(), SUK.zeta(), c13_LLL)
            while inc_prec:
                prec_v = 2*prec_v
                v = higher_precision(v,prec_v)
                c13_LLL = c13_func(SUK,v,prec_v)
                cx_bound = K1_func(SUK,v,A,prec_v)
                new_bound, inc_prec = reduction_step_complex_case(v, cx_bound, SUK.fundamental_units(),SUK.zeta(), c13_LLL)
            counter = 0
            while (cx_bound - new_bound).abs() > .01*cx_bound and counter < 15:
                #We fear a loop that is not convergent, this is the purpose of the counter
                #Repeat complex LLL until we get essentially no change from it
                cx_bound = min(cx_bound,new_bound)
                new_bound, inc_prec = reduction_step_complex_case(v, cx_bound, SUK.fundamental_units(),SUK.zeta(), c13_LLL)
                while inc_prec:
                    prec_v = 2*prec_v
                    v = higher_precision(v,prec_v)
                    c13_LLL = c13_func(SUK,v,prec_v)
                    new_bound, inc_prec = reduction_step_complex_case(v, cx_bound, SUK.fundamental_units(),SUK.zeta(), c13_LLL)
                counter += 1

        cx_bound = min(cx_bound,new_bound)
        #for this place the complex LLL bound is cx_bound
        cx_LLL = max(cx_bound,cx_LLL)
        #compare this value with the complex LLL bounds we have found for the previous places, if it is bigger, replace that bound
    return cx_LLL

def log_p_of_a_list(L,prime,prec):
    r"""

    INPUT:

    - ``L`` -- a list of elements of a number field `K`
    - ``prime`` -- a prime ideal of `K`
    - ``prec`` -- a positive natural number, the precision

    OUTPUT:

    A list with the ``prime``-adic logarithms of ``L``

    .. NOTE::

        `K` has to be an absolute extension

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import log_p_of_a_list
        sage: K.<a> = QuadraticField(17)
        sage: p = K.prime_above(13); p
        Fractional ideal (-a + 2)
        sage: log_p_of_a_list([3*a^3+1,2*a^2+a+7],p,20)
        [90957756839706500805798/13*a + 800239096845092924869910/13,
         2062304673797573083577432/13*a + 1425114372563713406518529/13]
    """
    K = prime.ring()
    if not K.is_absolute():
        raise ValueError('K has to be an absolute extension')

    return [log_p(a,prime,prec) for a in L]

def log_p(a,prime,prec):
    r"""

    INPUT:

    - ``a`` -- an element of a number field `K`
    - ``prime`` -- a prime ideal of the number field `K`
    - ``prec`` -- a positive integer

    OUPUT:

    An element of `K` which is congruent to the ``prime``-adic logarithm of ``a`` with respect to ``prime`` modulo ``p^prec``, where ``p`` is the rational prime below ``prime``

    .. NOTE::

        Here we take into account the other primes in `K` above `p` in order to get coefficients with small values

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import log_p
        sage: K.<a> = NumberField(x^2+14)
        sage: p1 = K.primes_above(3)[0]
        sage: p1
        Fractional ideal (3, a + 1)
        sage: log_p(a+2,p1,20)
        8255385638/3*a + 15567609440/3

    ::

        sage: K.<a> = NumberField(x^4+14)
        sage: p1 = K.primes_above(5)[0]
        sage: p1
        Fractional ideal (5, a + 1)
        sage: log_p(1/(a^2-4),p1,30)
        -42392683853751591352946/25*a^3 - 113099841599709611260219/25*a^2 -
        8496494127064033599196/5*a - 18774052619501226990432/25
    """
    if a == 0:
        raise ValueError('a is the zero element')

    if a.valuation(prime) != 0:
        raise ValueError('The valuation of a with respect to prime is not zero')

    K = prime.ring()
    p = prime.smallest_integer()

    #In order to get an approximation with small coefficients we have to take into account the other primes above p
    #with negative valuation.  For example, say prime2 is another (principal ideal) prime above p, and a=(unit)(prime2)^(-k) for some unit and k
    #a postive integer, and let tilde(a):=a(prime2)^k.  Then log_p(a)=log_p(tilde(a))-k(log_p(prime2)), where the series representations
    #of these two logs will have smaller coeffiecients.

    primes = [(-(a.valuation(pr)),pr) for pr in K.primes_above(p) if a.valuation(pr) < 0]
    list = []

    for (val,pr) in primes:
        #for its pair in primes we find an element in K such that it is divisible only by pr and not by any other ideal above p. Then we take this element in the correct exponent

        if pr.is_principal():
            list.append(pr.gens_reduced()[0]**val)
        else:
            list.append(pr.gens()[1]**val)

    return log_p_series_part(a * prod(list),prime,prec) - sum([log_p_series_part(b,prime,prec) for b in list])

def log_p_series_part(a,prime,prec):
    r"""

    INPUT:

    - ``a`` -- an element of a number field `K`
    - ``prime`` -- a prime ideal of the number field `K`
    - ``precision`` -- a positive integer

    OUPUT:

    The ``prime``-adic logarithm of ``a`` and accuracy ``p^prec``, where ``p`` is the rational prime below ``prime``

    ALGORITHM:

    The algorithm is based on the algorithm on page 30 of [Sma1998]_

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import log_p_series_part
        sage: K.<a> = NumberField(x^2-5)
        sage: p1 = K.primes_above(3)[0]
        sage: p1
        Fractional ideal (3)
        sage: log_p_series_part(a^2-a+1,p1,30)
        120042736778562*a + 263389019530092

    ::

        sage: K.<a> = NumberField(x^4+14)
        sage: p1 = K.primes_above(5)[0]
        sage: p1
        Fractional ideal (5, a + 1)
        sage: log_p_series_part(1/(a^2-4),p1,30)
        5628940883264585369224688048459896543498793204839654215019548600621221950915106576555819252366183605504671859902129729380543157757424169844382836287443485157589362653561119898762509175000557196963413830027960725069496503331353532893643983455103456070939403472988282153160667807627271637196608813155377280943180966078/1846595723557147156151786152499366687569722744011302407020455809280594038056223852568951718462474153951672335866715654153523843955513167531739386582686114545823305161128297234887329119860255600972561534713008376312342295724191173957260256352612807316114669486939448006523889489471912384033203125*a^2 + 2351432413692022254066438266577100183514828004415905040437326602004946930635942233146528817325416948515797296867947688356616798913401046136899081536181084767344346480810627200495531180794326634382675252631839139904967037478184840941275812058242995052383261849064340050686841429735092777331963400618255005895650200107/1846595723557147156151786152499366687569722744011302407020455809280594038056223852568951718462474153951672335866715654153523843955513167531739386582686114545823305161128297234887329119860255600972561534713008376312342295724191173957260256352612807316114669486939448006523889489471912384033203125
    """
    if prec is None:
        prec = 106
    if a.valuation(prime) != 0:
        raise ValueError('The valuation of a with respect to prime is not zero')
    K = prime.ring()
    g = K.gen()
    p = prime.smallest_integer()
    f = prime.residue_class_degree()
    e = prime.absolute_ramification_index()
    q = p**f - 1

    divisor = q.divisors()
    order = min([d for d in divisor if (a**d - 1).valuation(prime) > 0])
    gamma= a**order
    t = 0
    from sage.functions.log import log
    while (gamma-1).valuation(prime) <= e:
        t += 1
        gamma = gamma**p
    prec += t
    #since later we divide by p^t, we must increase the precision by t at this point.
    m = (gamma - 1).valuation(prime)/e
    n = Integer(1)
    step = 10 **(RR(log(prec)/log(10))).floor()
    while n < (log(n)/log(p) + prec)/m:
        n += step
    #could use smaller stepsize to get actual smallest integer n, however this seems to run faster.
    w = RR((log(prec)/log(p))).floor()
    gamma = sum([ZZ(gi%(p**(prec+w)))* g**i if gi.valuation(p) >= 0 else ZZ((gi * p**(-gi.valuation(p)))%(p**(prec+w-gi.valuation(p)))) * p**(gi.valuation(p)) * g**i for i,gi in enumerate(gamma) if gi != 0])


    beta = 0
    delta = 1-gamma
    for i in range(1,n+1):
        beta -= delta/i
        delta *= (1-gamma)
        delta = sum([ZZ(di%(p**(prec+w)))* g**e if di.valuation(p) >= 0 else ZZ((di * p**(-di.valuation(p)))%(p**(prec+w-di.valuation(p)))) * p**(di.valuation(p)) * g**e for e,di in enumerate(delta) if di != 0],0)
    beta = beta/(order*p**t)

    #we try to make the coefficients small

    logp = 0
    for i,b in enumerate(beta.list()):
        val = b.valuation(p)
        if val < 0:
            t = b * p**(-val)
            t = ZZ(mod(t,p**(prec-val)))
            t = t * p**val
        else:
            t = ZZ(mod(b,p**prec))
        logp = logp + t * g**i

    return logp

def defining_polynomial_for_Kp(prime,precision):
    r"""

    INPUT:

    - ``prime`` -- a prime ideal of a number field `K`
    - ``precision`` -- a positive natural number

    OUTPUT:

    A polynomial with integer coefficients that is equivalent ``mod p^precision`` to the defining polynomial of the completion of `K` associate to the definig polynomial of `K`

    .. NOTE::

        `K` has to be an absolute extension

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import defining_polynomial_for_Kp
        sage: K.<a> = QuadraticField(2)
        sage: p2 = K.prime_above(7); p2
        Fractional ideal (-2*a + 1)
        sage: defining_polynomial_for_Kp(p2,10)
        x + 266983762

    ::

        sage: K.<a> = QuadraticField(-6)
        sage: p2 = K.prime_above(2); p2
        Fractional ideal (2, a)
        sage: defining_polynomial_for_Kp(p2,100)
        x^2 + 6
        sage: p5 = K.prime_above(5); p5
        Fractional ideal (5, a + 2)
        sage: defining_polynomial_for_Kp(p5,100)
        x + 3408332191958133385114942613351834100964285496304040728906961917542037
    """
    if precision == None:
        precision = 106
    K = prime.ring()
    if not K.is_absolute():
        raise ValueError('The number field is not an absolute extension')

    theta = K.gen()
    f = K.defining_polynomial()
    p = prime.smallest_integer()
    e = prime.absolute_ramification_index()

    find = False
    N = precision
    while find == False:
        RQp = Qp(p,prec = N,type = 'capped-rel', print_mode = 'series')

        #We factorize f in Integers(p**(precision)) using the factorization in Qp

        g = f.change_ring(RQp)
        factors = g.factor();

        #We are going to find which factor of f is related to the prime ideal 'prime'

        L = [factors[i][0].change_ring(ZZ) for i in range(len(factors))]
        A = [g for g in L if (g(theta)).valuation(prime) >= e*N/2];

        if len(A) == 1:
            return A[0].change_ring(Integers(p**precision)).change_ring(ZZ)
        else:
            N += 1

def embedding_to_Kp(a,prime,precision):
    r"""

    INPUT:

    - ``a`` -- an element of a number field `K`
    - ``prime`` -- a prime ideal of `K`
    - ``precision`` -- a positive natural number

    OUTPUT:

    An element of `K` that is equivalent to ``a`` modulo ``p^(precision)`` and the generator of `K` appears with exponent less than `e\cdot f`, where ``p`` is the rational prime below ``prime`` and `e,f` are the ramification index and residue degree, respectively.

    .. NOTE::

        `K` has to be an absolute extension

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import embedding_to_Kp
        sage: K.<a> = QuadraticField(17)
        sage: p = K.prime_above(13); p
        Fractional ideal (-a + 2)
        sage: embedding_to_Kp(a-3,p,15)
        -20542890112375827

    ::

        sage: K.<a> = NumberField(x^4-2)
        sage: p = K.prime_above(7); p
        Fractional ideal (-a^2 + a - 1)
        sage: embedding_to_Kp(a^3-3,p,15)
        -1261985118949117459462968282807202378
    """
    K = prime.ring()
    if not K.is_absolute():
        raise ValueError('K has to be an absolute extension')

    g = defining_polynomial_for_Kp(prime,precision)
    p = prime.smallest_integer()
    gen = K.gen()
    n = g.degree()
    g = g.change_ring(QQ)
    f = K(a).lift()

    return K(sum([b*gen**j for j,b in enumerate(f.mod(g))]))

def p_adic_LLL_bound_one_prime(prime,B0,M,M_logp,m0,c3,precision):
    r"""

    INPUT:

    - ``prime`` -- a prime ideal of a number field `K`
    - ``B0`` -- the initial bound
    - ``M`` -- a list of elements of `K`, the `\mu_i`'s from Lemma IX.3 of [Sma1998]_
    - ``M_logp`` -- the p-adic logarithm of elements in `M`
    - ``m0`` -- an element of `K`, this is `\mu_0` from Lemma IX.3 of [Sma1998]_
    - ``c3`` -- a positive real constant
    - ``precision`` -- the precision of the calculations

    OUTPUT:

    A pair consisting of:

    1. a new upper bound, an integer
    2. a boolean value, ``True`` if we have to increase precision, otherwise ``False``

    .. NOTE::

        The constant `c_5` is the constant `c_5` at the page 89 of [Sma1998]_ which is equal to the constant `c_{10}` at the page 139 of [Sma1995]_.
        In this function, the `c_i` constants are in line with [Sma1998]_, but generally differ from the constants in [Sma1995]_ and other parts of this code.

    EXAMPLES:

    This example indictes a case where we must increase precision

    ::

        sage: from sage.rings.number_field.S_unit_solver import K0_func, possible_mu0s, mus, log_p_of_a_list, p_adic_LLL_bound_one_prime, c3_func
        sage: prec = 50
        sage: K.<a> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v = tuple(K.primes_above(3))[0]
        sage: A = SUK.roots_of_unity()
        sage: K0_old = K0_func(SUK, A, prec)
        sage: Mus0 = possible_mu0s(SUK, v)
        sage: m0 = Mus0[0]
        sage: Mus = mus(SUK,v)
        sage: Log_p_Mus = log_p_of_a_list(Mus, v, prec)
        sage: m0_Kv_new, increase_precision = p_adic_LLL_bound_one_prime( v, K0_old, Mus, Log_p_Mus, m0, c3_func(SUK, prec), prec)
        sage: m0_Kv_new
        0
        sage: increase_precision
        True

    And now we increase the precision to make it all work

    ::

        sage: prec = 106
        sage: K.<a> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: v = tuple(K.primes_above(3))[0]
        sage: A = SUK.roots_of_unity()
        sage: K0_old = K0_func(SUK, A,prec)
        sage: Mus0 = possible_mu0s(SUK, v)
        sage: m0 = Mus0[0]
        sage: Mus = mus(SUK,v)
        sage: Log_p_Mus = log_p_of_a_list(Mus, v, prec)
        sage: m0_Kv_new, increase_precision = p_adic_LLL_bound_one_prime( v, K0_old, Mus, Log_p_Mus, m0, c3_func(SUK, prec), prec)
        sage: m0_Kv_new
        476
        sage: increase_precision
        False
    """
    if precision == None:
        precision = 106
    if len([g for g in M+[m0] if g.valuation(prime) != 0]) > 0:
        raise ValueError('There is an element with non zero valuation at prime')

    K = prime.ring()
    p = prime.smallest_integer()
    f = prime.residue_class_degree()
    e = prime.absolute_ramification_index()
    from sage.functions.log import log
    c5 = c3/(f * e * log(p))
    theta = K.gen()

    #if M is empty then it is easy to give an upper bound
    if len(M) == 0:
        if m0 != 1:
            return RR(max(log(p) * f * (m0-1).valuation(prime)/c3,0)).floor(),False
        else:
            return 0,False
    #we evaluate the p-adic logarithms of m0 and we embed it in the completion of K with respect to prime

    m0_logp = log_p(m0,prime,precision)
    m0_logp = embedding_to_Kp(m0_logp,prime,precision)
    n = len(M_logp)
    #Below we implement paragraph VI.4.2 of [Smart], pages 89-93

    #we evaluate the order of discriminant of theta

    Theta = [theta**i for i in range(K.absolute_degree())]
    ordp_Disc = (K.disc(Theta)).valuation(p)
    #Let's check the mathematics here
    #We evaluate lambda

    c8 = min([min([a.valuation(p) for a in g]) for g in M_logp])
    lam = p**c8

    #we apply lemma VI.5 of [Smart] page 90
    #c6 is 0 here because we seek to solve the equation x+y=1, so our set A
    #is contained in the roots of unity of K

    low_bound = round(1/c5)
    for a in m0_logp:
        if a != 0:
            if c8 > a.valuation(p):
                B1 = (c8 + ordp_Disc/2)/c5
                if B1 > low_bound:
                    return RR(B1).floor(),False
                else:
                    return low_bound,False

    c8 = min([a.valuation(p) for a in m0_logp]+[c8])
    B = [g/lam for g in M_logp]
    b0 = m0_logp/lam
    c9 = c8 + ordp_Disc/2

    #We evaluate 'u' and we construct the matrix A

    m = e * f
    u = 1
    finish = False
    from sage.matrix.constructor import identity_matrix, zero_matrix, vector, block_matrix
    while not finish:
        if u > (precision * log(2))/log(p):
            return 0,True

        #We construct the matrix A as a block matrix

        A11 = copy(identity_matrix(ZZ,n))
        A12 = copy(zero_matrix(ZZ,n,m))
        A21 = copy(zero_matrix(ZZ,n,m))
        A22 = p**u * copy(identity_matrix(ZZ,m))
        for i,b in enumerate(B):
            A21[i] = vector([mod(b[j],p**u) for j in range(m)])
        A = block_matrix([[A11,A12],[A21.transpose(),A22]])

        y = copy(zero_vector(ZZ,n+m))
        for i in range(m):
            y[i+n] = -mod(b0[i],p**u)
        #This refers to c10 from Smart
        c10squared = minimal_vector(A.transpose(),y)
        if c10squared > n * B0**2:
            B2 = (u + c9)/c5
            if B2 > low_bound:
                return RR(B2).floor(),False
            else:
                return low_bound,False
        else:
            u += 1

def p_adic_LLL_bound(SUK,A, prec = None):
    r"""
    Return the maximum of all of the `K_0`'s as they are LLL-optimized for each finite place `v`

    INPUT:

    - ``SUK`` -- a group of `S`-units
    - ``A`` -- a list of all products of each potential ``a``, ``b`` in the `S`-unit equation ``ax + by + 1 = 0`` with each root of unity of ``K``
    - ``prec``-- precision for p-adic LLL calculations

    OUTPUT:

    A bound for the max of exponents in the case that extremal place is finite (see [Sma1995]_) as a real number

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import p_adic_LLL_bound
        sage: K.<xi> = NumberField(x^3-3)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: A = SUK.roots_of_unity()
        sage: prec = 100
        sage: p_adic_LLL_bound(SUK,A, prec)
        89
    """
    if prec is None:
        prec = 106
    S = SUK.primes()
    K0_old = K0_func(SUK, A, prec)
    LLL_K0_by_finite_place = []
    for i,v in enumerate(S):
        #Kv_old = K0_by_finite_place[0]
        Mus0 = possible_mu0s(SUK, v)
        Mus = mus(SUK,v)
        Log_p_Mus = log_p_of_a_list(Mus, v, prec)
        local_prec = prec
        val = 0
        for m0 in Mus0:
            m0_Kv_old = K0_old
            m0_Kv_new, increase_precision = p_adic_LLL_bound_one_prime( v, m0_Kv_old, Mus, Log_p_Mus, m0, c3_func(SUK,local_prec), local_prec)
            while increase_precision:
                local_prec *= 2
                Log_p_Mus = log_p_of_a_list(Mus,v,local_prec)
                m0_Kv_new, increase_precision = p_adic_LLL_bound_one_prime( v, m0_Kv_old, Mus, Log_p_Mus, m0, c3_func(SUK,local_prec), local_prec)

            while m0_Kv_new < m0_Kv_old:
                m0_Kv_old = m0_Kv_new
                m0_Kv_new , increase_precision = p_adic_LLL_bound_one_prime(v, m0_Kv_old, Mus, Log_p_Mus, m0, c3_func(SUK,local_prec), local_prec)
                while increase_precision:
                    local_prec *= 2
                    Log_p_Mus = log_p_of_a_list(Mus,v,local_prec)
                    m0_Kv_new,increase_precision = p_adic_LLL_bound_one_prime( v, m0_Kv_old, Mus, Log_p_Mus, m0, c3_func(SUK,local_prec), local_prec)

            if m0_Kv_old > val:
                val = m0_Kv_old

        LLL_K0_by_finite_place.append(val)
    return max(LLL_K0_by_finite_place)

def completely_split_primes(K, Bound = 200):
    r"""
    Returns a list of rational primes which split completely in the number field `K`.

    INPUT:

    - ``K`` -- a number field
    - Bound -- a positive integer bound (default: 200)

    OUTPUT:

    A list of all primes ``p < Bound`` which split completely in ``K``.

    NOTE:

    This function does not screen against primes in S, specified for determining S-Unit equation solutions.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import completely_split_primes
        sage: K.<xi> = NumberField(x^3 - 3*x + 1)
        sage: completely_split_primes(K, 100)
        [17, 19, 37, 53, 71, 73, 89]

    """

    f = K.defining_polynomial()
    split_primes = []
    for p in prime_range(Bound):
        Fp = GF(p)
        FpT = PolynomialRing(Fp,'T')
        g = FpT(K.defining_polynomial())
        if len(factor(g)) == K.degree():
            split_primes.append(p)
    return split_primes

def split_primes_large_lcm(SUK, Bound):
    r"""
    Return a list ``L`` of rational primes `q` which split completely in `K` and which have desirable properties (see NOTE).

    INPUT:

    - ``SUK`` -- the `S`-unit group of an absolute number field `K`.
    - ``Bound`` -- a positive integer

    OUTPUT:

    A list `L` of rational primes `q`, with the following properties:

    - each prime `q` in `L` splits completely in `K`
    - if `Q` is a prime in `S` and `q` is the rational
      prime below `Q`, then `q` is **not** in `L`
    - the value ``lcm { q - 1 : q in L }`` is greater than or equal
       to ``2 * Bound + 1`.

    .. NOTE::

        - A series of compatible exponent vectors for the primes in `L` will
          lift to **at most** one integer exponent vector whose entries
          `a_i` satisfy `|a_i|` is less than or equal to ``Bound``.

        - The ordering of this set is not very intelligent for the purposes
          of the later sieving processes.

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import split_primes_large_lcm
        sage: K.<xi> = NumberField(x^3 - 3*x + 1)
        sage: S = K.primes_above(3)
        sage: SUK = UnitGroup(K,S=tuple(S))
        sage: split_primes_large_lcm(SUK, 200)
        [17, 19, 37, 53]

    With a tiny bound, SAGE may ask you to increase the bound.

    ::

        sage: from sage.rings.number_field.S_unit_solver import split_primes_large_lcm
        sage: K.<xi> = NumberField(x^2 + 163)
        sage: S = K.primes_above(23)
        sage: SUK = UnitGroup(K,S=tuple(S))
        sage: split_primes_large_lcm(SUK, 8)
        Traceback (most recent call last):
        ...
        ValueError: Not enough split primes found. Increase bound.

    """

    K = SUK.number_field()
    S0 = []
    # we recover the rational primes below S:
    for prime_ideal in SUK.primes():
        q0 = prime_ideal.residue_field().characteristic()
        if q0 not in S0:
            S0.append( q0 )

    split_prime_list = completely_split_primes(K, 4*Bound + 4)
    lcm_list = []
    L = 1
    while L < 2*Bound + 1:
        if split_prime_list == []:
            # Need More Primes!
            raise ValueError('Not enough split primes found. Increase bound.')
        q = split_prime_list.pop(0)
        # only use q if it is *not* below a prime in S -- that is,
        # only if q does *not* appear in S0.
        if q not in S0:
            L = lcm(L, q-1)
            lcm_list.append(q)
    return lcm_list

def sieve_ordering(SUK, q):
    r"""
    Returns ordered data for running sieve on the primes in `SUK` over the rational prime `q`.

    INPUT:

    - ``SUK`` -- the `S`-unit group of a number field `K`
    - ``q``   -- a rational prime number which splits completely in `K`

    OUTPUT:

    A list of lists, ``[ideals_over_q, residue_fields, rho_images, product_rho_orders]``, where

    1. ``ideals_over_q`` is a list of the `d = [K:\mathbb{Q}]` ideals in `K` over `q`
    2. ``residue_fields[i]`` is the residue field of ``ideals_over_q[i]``
    3. ``rho_images[i]`` is a list of the generators in `rho`, ``modulo ideals_over_q[i]``
    4. ``product_rho_orders[i]`` is the product of the multiplicative orders of the elements in ``rho_images[i]``

    .. NOTE::

        - The list ``Q_ideal`` is sorted so that the product of orders is smallest for ``Q_ideal[0]``, as this will make the later sieving steps more efficient.
        - The primes of ``S`` may not lie over over ``q``.

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import sieve_ordering
        sage: K.<xi> = NumberField(x^3 - 3*x + 1)
        sage: SUK = K.S_unit_group(S=3)
        sage: sieve_data = sieve_ordering(SUK, 19)
        sage: sieve_data[0]
        [Fractional ideal (-2*xi^2 + 3),
        Fractional ideal (xi - 3),
        Fractional ideal (2*xi + 1)]

        sage: sieve_data[1]
        [Residue field of Fractional ideal (-2*xi^2 + 3),
        Residue field of Fractional ideal (xi - 3),
        Residue field of Fractional ideal (2*xi + 1)]

        sage: sieve_data[2]
        [[18, 17, 6, 8], [18, 11, 2, 4], [18, 13, 8, 10]]

        sage: sieve_data[3]
        [972, 972, 3888]
    """

    K = SUK.number_field()
    rho = SUK.gens_values()
    d = K.absolute_degree()
    primes_over_q = K.primes_above(q)
    # q must split completely.
    if len(primes_over_q) != d:
        raise ValueError('The prime q is not completely split.')

    for P in SUK.primes():
        if P in K.primes_above(q):
            raise ValueError('There is a prime in S over q.')

    # We initialize some unsorted lists:

    ideals_over_q_unsorted = []
    # will contain the d ideals over q. In the comments, we use Q[i] as shorthand for ideals_over_q_unsorted[i]

    residue_fields_unsorted = []
    # ith entry is the residue field of Q[i].
    # Note that these are all isomorphic to GF(q), but each has a different reduction map from OK.

    rho_images_unsorted = []
    # The ith entry is a list of the images of the generators in rho under the natural reduction map
    #     OK ---> residue_fields_unsorted[i] == OK / Q[i]

    product_rho_orders_unsorted = []
    # Viewed as elements in the multiplicative group GF(p)^\times, each generator has some multiplicative order.
    # product_rho_orders_Q_unsorted[i] records the product of these multiplicative orders.

    # We will sort the ideals so that the 0th ideal has the minimum value for this product.

    for Qi in primes_over_q:
        ideals_over_q_unsorted.append( Qi )
        residue_fields_unsorted.append( Qi.residue_field() )
        rho_mod_Qi = [ Qi.residue_field()( rho_j) for rho_j in rho ]
        rho_images_unsorted.append( rho_mod_Qi )
        product_of_orders_of_images = prod( rho_ij.multiplicative_order() for rho_ij in rho_mod_Qi )
        product_rho_orders_unsorted.append( product_of_orders_of_images )

    # zip() will turn the four separate lists into one list of 4-tuples.
    # the sort command will sort in the first entry -- i.e., the product of rho orders.

    q_data_zip = zip( product_rho_orders_unsorted, ideals_over_q_unsorted, residue_fields_unsorted, rho_images_unsorted )
    q_data_zip.sort()

    # The remaining code simply regurgitates the data into four separate lists.

    ideals_over_q = []
    residue_fields = []
    rho_images = []
    product_rho_orders = []

    for qdata_item in q_data_zip:
        product_rho_orders.append( qdata_item[0] )
        ideals_over_q.append( qdata_item[1] )
        residue_fields.append( qdata_item[2] )
        rho_images.append( qdata_item[3] )

    return ideals_over_q, residue_fields, rho_images, product_rho_orders

def bounded_integer_lifts(r, m, bound):
    r"""
    Returns all integers up to a given bound which are equivalent to ``r`` modulo ``m``.

    INPUT:

    - ``r`` -- an integer, representing a residue class modulo ``m``
    - ``m`` -- an integer; the modulus under consideration
    - ``bound`` -- a positive integer

    OUTPUT:

    A list of integers ``x`` satisfying both ``x = r % m`` and ``abs(x) <= bound``.

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import bounded_integer_lifts
        sage: bounded_integer_lifts(2, 7, 13)
        [2, 9, -5, -12]

    ::

        sage: bounded_integer_lifts(4, 12, 1)
        []

    """

    r0 = r % m
    lifts = []
    r_plus = r0
    # first find the lifts in the range [0, bound]
    while r_plus <= bound:
        lifts.append(r_plus)
        r_plus += m

    r_minus = r0 - m
    # now, find the lifts in the range [-bound, 0)
    while r_minus >= -bound:
        lifts.append(r_minus)
        r_minus -= m

    return lifts

def bounded_vector_lifts( exponent_vector, m, bound ):
    r"""
    Given an exponent vector modulo ``m``, construct the possible lifts which agree modulo ``m`` and with no entry exceeding ``bound`` in absolute value.

    INPUT:

    - ``exponent_vector`` -- an exponent vector (to be viewed as an exponent vector modulo ``m``)
    - ``m`` -- a positive integer > 1
    - ``bound`` -- a positive integer, bounding the absolute value of entries in lifts

    OUTPUT:

    A list of all exponent vectors with integer entries which satisfy the following criteria:

    1. the 0th entry matches the 0th entry of ``exponent_vector``
    2. for each ``j > 0``, the ``j``th entry is congruent to the ``j``th entry of ``exponent_vector`` modulo ``m``
    3. all entries, except possibly the first, are bounded in absolute value by ``bound``.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import bounded_vector_lifts
        sage: bounded_vector_lifts((2,7), 16, 44)
        [(2, 7), (2, 23), (2, 39), (2, -9), (2, -25), (2, -41)]

    """

    length = len(exponent_vector)
    if length == 0:
        return [ () ]
    elif length == 1:
        return [(exponent_vector[0],)]
    elif length > 1:
        # We work recursively. First, lift the final entry of the vector.
        final_entry_lifts = bounded_integer_lifts( exponent_vector[-1], m, bound )
        # Second, get the lifts of the shorter vector:
        start_of_exponent_vector = exponent_vector[:-1]
        lifted_vectors = []
        for start_of_lift in bounded_vector_lifts( start_of_exponent_vector, m, bound ):
            for final_entry in final_entry_lifts:
                new_vector = start_of_lift + (final_entry,)
                lifted_vectors.append( new_vector )
        return lifted_vectors

def clean_rfv_dict( rfv_dictionary ):
    r"""
    Given a residue field vector dictionary, removes some impossible keys and entries.

    INPUT:

    - ``rfv_dictionary`` -- a dictionary whose keys are exponent vectors and whose values are residue field vectors

    OUTPUT:

    None. But it removes some keys from the input dictionary.

    .. NOTE::

        - The keys of a residue field vector dictionary are exponent vectors modulo ``(q-1)`` for some prime ``q``.
        - The values are residue field vectors. It is known that the entries of a residue field vector
          which comes from a solution to the S-unit equation cannot have 1 in any entry.

    EXAMPLE:

    In this example, we use a truncated list generated when solving the `S`-unit equation in the case that `K` is defined by the
    polynomial `x^2+x+1` and `S` consists of the primes above 3

    ::

        sage: from sage.rings.number_field.S_unit_solver import clean_rfv_dict
        sage: rfv_dict = {(1, 3): [3, 2], (3, 0): [6, 6], (5, 4): [3, 6], (2, 1): [4, 6], (5, 1): [3, 1], (2, 5): [1, 5], (0, 3): [1, 6]}
        sage: len(rfv_dict)
        7
        sage: clean_rfv_dict(rfv_dict)
        sage: len(rfv_dict)
        4
        sage: rfv_dict
        {(1, 3): [3, 2], (2, 1): [4, 6], (3, 0): [6, 6], (5, 4): [3, 6]}
    """

    garbage = []
    for a in rfv_dictionary:
        if 1 in rfv_dictionary[a]:
            garbage.append(a)
    for a in garbage:
        trash = rfv_dictionary.pop(a,0)

def construct_rfv_to_ev( rfv_dictionary, q, d, verbose_flag = False ):
    r"""
    Returns a reverse lookup dictionary, to find the exponent vectors associated to a given residue field vector.

    INPUTS:

    - ``rfv_dictionary`` -- a dictionary whose keys are exponent vectors and whose values are the associated residue field vectors
    - ``q`` -- a prime (assumed to split completely in the relevant number field)
    - ``d`` -- the number of primes in `K` above the rational prime ``q``
    - ``verbose_flag`` -- a boolean flag to indicate more detailed output is desired

    OUTPUT:

    A dictionary ``P`` whose keys are residue field vectors and whose values are lists of all exponent vectors
    which correspond to the given residue field vector.

    .. NOTE::

        - For example, if ``rfv_dictionary[ e0 ] = r0``, then ``P[ r0 ]`` is a list which contains ``e0``.
        - During construction, some residue field vectors can be eliminated as coming from
          solutions to the `S`-unit equation. Such vectors are dropped from the keys of the dictionary ``P``.

    EXAMPLES:

    In this example, we use a truncated list generated when solving the `S`-unit equation in the case that `K` is defined by the
    polynomial `x^2+x+1` and `S` consists of the primes above 3

    ::

        sage: from sage.rings.number_field.S_unit_solver import construct_rfv_to_ev
        sage: rfv_dict = {(1, 3): [3, 2], (3, 0): [6, 6], (5, 4): [3, 6], (2, 1): [4, 6], (4, 0): [4, 2], (1, 2): [5, 6]}
        sage: construct_rfv_to_ev(rfv_dict,7,2,False)
        {(3, 2): [(1, 3)], (4, 2): [(4, 0)], (4, 6): [(2, 1)], (5, 6): [(1, 2)]}
    """

    # Step 0. Initialize P:
    # The keys in P are just the possible first entries of a residue field vector.
    # The values (all empty lists now) will be added in the next step.

    P = {}
    P = { (v,) : [] for v in xrange(2, q) }

    # Step 1. Populate the empty lists in P[ (v,) ].
    # Loop through the keys in rfv_dictionary. For each, look at the output rf_vector.
    # Find the key in P which matches the first entry of the rf_vector.
    # Dump the **rest** of the rf_vector into a pair [exp_vec, rf_vec[1:]],
    # and append this pair into the dictionary P at the key (rf_vec[0], ).

    # Now, P[ (v,) ] = [ [a_0, e_0], [a_1, e_1], ...]
    #
    # The relationship between v, a_i, and e_i is as follows:
    #
    # a_i is an exponent vector, whose associated residue field vector is the
    # concatenation of v with e_i.

    for exponent_vector in rfv_dictionary:
        residue_field_vector = rfv_dictionary[exponent_vector]
        rf_vector_start = (residue_field_vector[0], )
        rf_vector_end = residue_field_vector[1:]
        P[rf_vector_start].append( [exponent_vector, rf_vector_end] )

    if verbose_flag:
        print "Populated P. Currently it has ", len(P), "keys."

    # Step 2: We build a new dictionary, P_new, from P.
    #
    # This is a step that will be repeated, once for each of the d primes over q.
    #
    # P is a dictionary whose keys are tuples of length m, representing the beginning of known residue field vectors.
    #
    # For any such beginning `s`,
    #
    # P[s] = [ [a_0, e_0], [a_1, e_1], ...]
    #
    # where for any exponent vector a_i, the associated residue field vector is the concatenation s + e_i.
    #
    # The dictionary P_new is constructed from the dictionary P. The new keys will be tuples of length m + 1.
    #
    # During the construction, we look for impossible entries for S-unit solutions, and drop them from the dictionary as needed.

    for j in xrange( d-1 ):
        if verbose_flag:
            print "Constructing ", j, " th place of the residue field vectors, out of ", d-1, " total."
        P_new = {}
        garbage = {}

        # we loop over each key of P.
        for rf_vector_start in P:

            # each key of P provides q-2 possible keys for P_new, which we introduce and assign an empty list.
            for w in xrange(2, q):
                new_rf_vector_start = tuple( list( rf_vector_start ) + [w] )
                P_new[ new_rf_vector_start ] = []

            # we populate P_new[ new_rf_vector_start ] using P[rf_vector_start]
            for exponent_vector, rf_vector_end in P[ rf_vector_start ]:
                new_rf_vector_end = rf_vector_end[1:]
                w = rf_vector_end[0]
                new_rf_vector_start = tuple( list( rf_vector_start ) + [w] )
                P_new[ new_rf_vector_start ].append( [exponent_vector, new_rf_vector_end] )

        if verbose_flag:
            print "P_new is populated with ", len(P_new), " keys."

        # we now loop over the keys of P_new, looking for incompatible entries.

        for rf_vector_start in P_new:
            # the final entry of rf_vector_start or rf_vector_complement_start must be < (q+3)/2.
            # No loss to insist that it is rf_vector_start.
            if rf_vector_start[-1] < (q+3)/2:
                # we find the complement to rf_vector_start:
                rf_vector_complement_start = tuple( [ q+1-j for j in rf_vector_start] )
                if P_new[ rf_vector_start ] == [] or P_new[ rf_vector_complement_start ] == []:
                    # these can't be solutions. Mark them for deletion.
                    garbage[ rf_vector_start ] = True
                    garbage[ rf_vector_complement_start ] = True

        # garbage removal
        for rf_vector_start in garbage:
            trash = P_new.pop(rf_vector_start, 0)

        if verbose_flag:
            print "After removing incompatible entries, P_new is down to ", len(P_new), " keys."

        # Time to move on to the next dictionary.
        P = P_new.copy()

    # Now, we just clean up P.
    for residue_field_vector in P:
        # at this instant, P[ residue_field_vector ] is a list of pairs: [ [a0,e0], ... ]
        # We only care about the exponent vectors a0,...
        P[residue_field_vector] = [ a[0] for a in P[residue_field_vector] ]

    if verbose_flag:
        print "Returning dictionary P with ", len(P), " keys."

    return P.copy()

def construct_comp_exp_vec( rfv_to_ev_dict, q ):
    r"""
    Constructs a dictionary associating complement vectors to residue field vectors.

    INPUT:

    - ``rfv_to_ev_dict`` -- a dictionary whose keys are residue field vectors and whose values are lists of exponent vectors with the associated residue field vector.
    - ``q`` -- the characteristic of the residue field

    OUTPUT:

    A dictionary whose typical key is an exponent vector ``a``, and whose associated value is a list of complementary exponent vectors to ``a``.

    EXAMPLE:

    In this example, we use the list generated when solving the `S`-unit equation in the case that `K` is defined by the
    polynomial `x^2+x+1` and `S` consists of the primes above 3

    ::

        sage: from sage.rings.number_field.S_unit_solver import construct_comp_exp_vec
        sage: rfv_to_ev_dict = {(6, 6): [(3, 0)], (5, 6): [(1, 2)], (5, 4): [(5, 3)], (6, 2): [(5, 5)], (2, 5): [(0, 1)], (5, 5): [(3, 4)], (4, 4): [(0, 2)], (6, 3): [(1, 4)], (3, 6): [(5, 4)], (2, 2): [(0, 4)], (3, 5): [(1, 0)], (6, 4): [(1, 1)], (3, 2): [(1, 3)], (2, 6): [(4, 5)], (4, 5): [(4, 3)], (2, 3): [(2, 3)], (4, 2): [(4, 0)], (6, 5): [(5, 2)], (3, 3): [(3, 2)], (5, 3): [(5, 0)], (4, 6): [(2, 1)], (3, 4): [(3, 5)], (4, 3): [(0, 5)], (5, 2): [(3, 1)], (2, 4): [(2, 0)]}
        sage: construct_comp_exp_vec( rfv_to_ev_dict, 7 )
        {(0, 1): [(1, 4)],
         (0, 2): [(0, 2)],
         (0, 4): [(3, 0)],
         (0, 5): [(4, 3)],
         (1, 0): [(5, 0)],
         (1, 1): [(2, 0)],
         (1, 2): [(1, 3)],
         (1, 3): [(1, 2)],
         (1, 4): [(0, 1)],
         (2, 0): [(1, 1)],
         (2, 1): [(4, 0)],
         (2, 3): [(5, 2)],
         (3, 0): [(0, 4)],
         (3, 1): [(5, 4)],
         (3, 2): [(3, 4)],
         (3, 4): [(3, 2)],
         (3, 5): [(5, 3)],
         (4, 0): [(2, 1)],
         (4, 3): [(0, 5)],
         (4, 5): [(5, 5)],
         (5, 0): [(1, 0)],
         (5, 2): [(2, 3)],
         (5, 3): [(3, 5)],
         (5, 4): [(3, 1)],
         (5, 5): [(4, 5)]}

    """

    comp_exp_vec_dict = {}
    for residue_field_vector in rfv_to_ev_dict:
        rf_vector_complement = tuple( [q + 1 - j for j in residue_field_vector] )
        exponent_vector_list = rfv_to_ev_dict[ residue_field_vector ][:]
        exponent_vector_complement_list = rfv_to_ev_dict[ rf_vector_complement ][:]
        for exponent_vector in exponent_vector_list:
            comp_exp_vec_dict[ exponent_vector ] = exponent_vector_complement_list
    return comp_exp_vec_dict

def drop_vector(ev, p, q, complement_ev_dict):
    r"""
    Determines if the exponent vector, ``ev``, may be removed from the complement dictionary during construction.
    This will occur if ``ev`` is not compatible with an exponent vector mod ``q-1``.

    INPUT:

    - ``ev`` -- an exponent vector modulo ``p - 1``
    - ``p`` -- the prime such that ev is an exponent vector modulo ``p-1``
    - ``q`` -- a prime, distinct from ``p``, that is a key in the ``complement_ev_dict``
    - ``complement_ev_dict`` -- a dictionary of dictionaries, whose keys are primes
      ``complement_ev_dict[q]`` is a dictionary whose keys are exponent vectors modulo ``q-1``
      and whose values are lists of complementary exponent vectors modulo ``q-1``

    OUTPUT:

    Returns ``True`` if ``ev`` may be dropped from the complement exponent vector dictionary, and ``False`` if not.

    .. NOTE::

        - If ``ev`` is not compatible with any of the vectors modulo ``q-1``, then it can no longer correspond to a solution
          of the `S`-unit equation. It returns ``True`` to indicate that it should be removed.

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import drop_vector
        sage: drop_vector((1, 2, 5), 7, 11, {11: {(1, 1, 3): [(1, 1, 3),(2, 3, 4)]}})
        True

    ::

        sage: P={3: {(1, 0, 0): [(1, 0, 0), (0, 1, 0)], (0, 1, 0): [(1, 0, 0), (0, 1, 0)]}, 7: {(0, 3, 4): [(0, 1, 2), (0, 3, 4), (0, 5, 0)], (1, 2, 4): [(1, 0, 4), (1, 4, 2), (1, 2, 0)], (0, 1, 2): [(0, 1, 2), (0, 3, 4), (0, 5, 0)], (0, 5, 4): [(1, 0, 0), (1, 4, 4), (1, 2, 2)], (1, 4, 2): [(1, 2, 4), (1, 4, 0), (1, 0, 2)], (1, 0, 4): [(1, 2, 4), (1, 4, 0), (1, 0, 2)], (0, 3, 2): [(1, 0, 0), (1, 4, 4), (1, 2, 2)], (1, 0, 0): [(0, 5, 4), (0, 3, 2), (0, 1, 0)], (1, 2, 0): [(1, 2, 4), (1, 4, 0), (1, 0, 2)], (0, 1, 0): [(1, 0, 0), (1, 4, 4), (1, 2, 2)], (0, 5, 0): [(0, 1, 2), (0, 3, 4), (0, 5, 0)], (1, 2, 2): [(0, 5, 4), (0, 3, 2), (0, 1, 0)], (1, 4, 0): [(1, 0, 4), (1, 4, 2), (1, 2, 0)], (1, 0, 2): [(1, 0, 4), (1, 4, 2), (1, 2, 0)], (1, 4, 4): [(0, 5, 4), (0, 3, 2), (0, 1, 0)]}}
        sage: drop_vector((0,1,0),3,7,P)
        False
    """
    # returns True if it is OK to drop exp_vec given the current comp_exp_vec dictionary associated to some q.
    # returns False otherwise
    # loop over the possible compatible vectors in the other modulus
    for compatible_exp_vec in compatible_vectors(ev, p-1, q-1):
        # do they appear in the other dictionary?
        if compatible_exp_vec in complement_ev_dict[q]:
            # OK, but the complements need to be compatible, too!
            ev_complement_list = complement_ev_dict[p][ ev ]
            for ev_comp in ev_complement_list:
                for compatible_cv in compatible_vectors( ev_comp, p-1, q-1 ):
                    if compatible_cv in complement_ev_dict[q][compatible_exp_vec]:
                        return False
    return True

def construct_complement_dictionaries(split_primes_list, SUK, verbose_flag = False):
    r"""
    A function to construct the complement exponent vector dictionaries.

    INPUT:

    - ``split_primes_list`` -- a list of rational primes which split completely in the number field `K`
    - ``SUK`` -- the `S`-unit group for a number field `K`
    - ``verbose_flag`` -- (default: False) a boolean to provide additional feedback

    OUTPUT:

    A dictionary of dictionaries. The keys coincide with the primes in ``split_primes_list``
    For each ``q``, ``comp_exp_vec[q]`` is a dictionary whose keys are exponent vectors modulo ``q-1``,
    and whose values are lists of exponent vectors modulo ``q-1``

    If ``w`` is an exponent vector in ``comp_exp_vec[q][v]``, then the residue field vectors modulo ``q`` for
    ``v`` and ``w`` sum to ``[1,1,...,1]``

    .. NOTE::

        - The data of ``comp_exp_vec`` will later be lifted to `\mathbb{Z}` to look for true `S`-Unit equation solutions.
        - During construction, the various dictionaries are compared to each other several times to
          eliminate as many mod `q` solutions as possible.
        - The authors acknowledge a helpful discussion with Norman Danner which helped formulate this code.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import construct_complement_dictionaries
        sage: f = x^2 + 5
        sage: H = 10
        sage: K.<xi> = NumberField(f)
        sage: SUK = K.S_unit_group( S = K.primes_above(H) )
        sage: split_primes_list = [3, 7]
        sage: construct_complement_dictionaries( split_primes_list, SUK )
        {3: {(0, 1, 0): [(1, 0, 0), (0, 1, 0)], (1, 0, 0): [(1, 0, 0), (0, 1, 0)]},
        7: {(0, 1, 0): [(1, 0, 0), (1, 4, 4), (1, 2, 2)],
        (0, 1, 2): [(0, 1, 2), (0, 3, 4), (0, 5, 0)],
        (0, 3, 2): [(1, 0, 0), (1, 4, 4), (1, 2, 2)],
        (0, 3, 4): [(0, 1, 2), (0, 3, 4), (0, 5, 0)],
        (0, 5, 0): [(0, 1, 2), (0, 3, 4), (0, 5, 0)],
        (0, 5, 4): [(1, 0, 0), (1, 4, 4), (1, 2, 2)],
        (1, 0, 0): [(0, 5, 4), (0, 3, 2), (0, 1, 0)],
        (1, 0, 2): [(1, 0, 4), (1, 4, 2), (1, 2, 0)],
        (1, 0, 4): [(1, 2, 4), (1, 4, 0), (1, 0, 2)],
        (1, 2, 0): [(1, 2, 4), (1, 4, 0), (1, 0, 2)],
        (1, 2, 2): [(0, 5, 4), (0, 3, 2), (0, 1, 0)],
        (1, 2, 4): [(1, 0, 4), (1, 4, 2), (1, 2, 0)],
        (1, 4, 0): [(1, 0, 4), (1, 4, 2), (1, 2, 0)],
        (1, 4, 2): [(1, 2, 4), (1, 4, 0), (1, 0, 2)],
        (1, 4, 4): [(0, 5, 4), (0, 3, 2), (0, 1, 0)]}}


    """

    # we define a custom function to flatten tuples for use in a later step.
    # see the definition of ev_iterator, below.

    def ev_flatten(vec):
        # turns (a, (b1,...,bn)) to (a, b1, ..., bn)
        return tuple([vec[0]] + list(vec[1]))

    # We initialize some dictionaries.

    rho = SUK.gens_values()
    rho_length = len(rho)
    rho_images_dict = {}
    rho_orders_dict = {}

    K = SUK.number_field()
    for q in split_primes_list:
        ideals_over_q, residue_fields, rho_images, product_rho_orders = sieve_ordering(SUK, q)
        rho_images_dict[q] = rho_images
        rho_orders_dict[q] = product_rho_orders

    nK = K.absolute_degree()
    w0 = rho[0].multiplicative_order()

    # We build a dictionary of dictionaries.
    # rfv_to_ev[q] is the 'mod q' residue field vector to exponent vector dictionary.

    rfv_to_ev = {}

    # We build a second dictionary of dictiories.
    # comp_exp_vec[q] is the dictionary mod q which assigns to each exponent vector
    # a list of 'complementary' exponent vectors.

    comp_exp_vec = {}

    q0 = split_primes_list[0]

    if verbose_flag:
        print "Using the following primes: ", split_primes_list
        sys.stdout.flush()
    import itertools
    for q in split_primes_list:
        rho_images = rho_images_dict[q]
        if verbose_flag:
            print "q = ", q
            sys.stdout.flush()
        def epsilon_q(a, i):
            # a is an exponent vector
            # i is an index for one of the primes over q
            # returns the value of rho_j^a_j inside the
            # residue field of Qi. (Necessarily isomorphic to F_q.)
            # rho_images[i][j] == rho[j] modulo Q[i]
            eps_value = rho_images[i][0]**a[0] % q
            for j in xrange(1, rho_length):
                eps_value = eps_value * rho_images[i][j]**a[j] % q
            return eps_value

        if verbose_flag:
            print "The evaluation function epsilon has beend defined using rho_images = ", rho_images
            sys.stdout.flush()
        # Now, we run through the vectors in the iterator, but only keep the ones
        # which are compatible with the previously constructed dictionaries. That is,
        # in order to keep an exp_vec mod q, there must exist a compatible exp_vec mod p
        # in the keys of the rfv_to_ev[p] dictionary for each completely split prime
        # p appearing prior to q in split_primes_list.

        if q == q0:
            # for the first prime, there is no filtering possible, and we just build the exponent vector
            # iterator.

            # This should consist of all vectors (a0,...,a_{t-1}), where
            # a0 is in the range 0 .. w_0 - 1 and
            # aj is in the range 0 .. q - 2   (for j > 0)

            lumpy_ev_iterator = itertools.product( xrange(w0), itertools.product( xrange(q-1), repeat = rho_length - 1))
            ev_iterator = itertools.imap(ev_flatten, lumpy_ev_iterator)

            # With the iterator built, we construct the exponent vector to residue field dictionary.

            ev_to_rfv_dict = { ev : [epsilon_q(ev, i) for i in xrange(nK) ] for ev in ev_iterator }

            if verbose_flag:
                print "The residue field dictionary currently has ", len(ev_to_rfv_dict), " exponent vector keys."
                sys.stdout.flush()
        else:
            ev_to_rfv_dict = {}
            # We use compatibility requirements to keep the size of the dictionary down.
            # Later on, we'll compare all dictionaries pairwise. But for now, we just
            # check against the first.

            # That is, rather than loop over every possible exponent vector mod q-1,
            # we only consider those evs which are compatible with the mod q0 - 1 vectors.

            # Loop over exponent vectors modulo q0 - 1
            for exp_vec_mod_q0 in comp_exp_vec[q0]:
                # Loop only over exponent vectors modulo q-1 which are compatible with exp_vec_mod_q0
                for exp_vec in compatible_vectors(exp_vec_mod_q0, q0-1, q-1):
                    # fill the dictionary with the residue field vectors using the evaluation function.
                    ev_to_rfv_dict[exp_vec] = [epsilon_q(exp_vec, i) for i in xrange(nK) ]

        if verbose_flag:
            print "The residue field dictionary currently has ", len(ev_to_rfv_dict), " exponent vector keys."
            sys.stdout.flush()
        # At this point, we now have a dictionary ev_to_rfv_dict, which attaches
        # to each exponent vector a 'residue field vector,' which is a tuple of the
        # nK values epsilon_q(a,0),...,epsilon_q(a,nK-1).

        clean_rfv_dict( ev_to_rfv_dict )

        if verbose_flag:
            print "clean_rfv_dict executed."
            print "The residue field dictionary currently has ", len(ev_to_rfv_dict), " exponent vector keys."
            sys.stdout.flush()
        # We essentially construct an inverse dictionary: one whose keys are residue field vectors,
        # and whose values are the exponent vectors that yield each key

        rfv_to_ev[q] = construct_rfv_to_ev( ev_to_rfv_dict, q, nK, verbose_flag )

        if verbose_flag:
            print "construct_rfv_to_ev executed."
            print "The rfv_to_ev dictionary currently has ", len(rfv_to_ev[q]), "rfv keys."
            sys.stdout.flush()

        comp_exp_vec[q] = construct_comp_exp_vec( rfv_to_ev[q], q )

        if verbose_flag:
            print "construct_comp_exp_vec executed."

        if verbose_flag:
            print "Size of comp_exp_vec[q]: ", len(comp_exp_vec[q])
            sys.stdout.flush()

        # Now that we have a new dictionary, we compare all the dictionaries pairwise,
        # looking for opportunities to remove 'impossible' solutions.

        for p in [qi for qi in comp_exp_vec.keys() if qi != q]:

            if verbose_flag:
                print "Comparing dictionaries for p = ", p, "and q = ", q, "."
                sys.stdout.flush()

            old_size_p = len(comp_exp_vec[p])

            if verbose_flag:
                print "Size of comp_exp_vec[p] is: ", old_size_p, "."
                cv_size = ( (q-1)/gcd(p-1, q-1) )**( rho_length - 1 )
                print "Length of compatible_vectors: ", cv_size, "."
                print "Product: ", old_size_p * cv_size
                sys.stdout.flush()

            for exp_vec in comp_exp_vec[p].copy():
                if drop_vector(exp_vec, p, q, comp_exp_vec):
                    trash = comp_exp_vec[p].pop(exp_vec)

            if verbose_flag:
                print "Shrunk dictionary p from ", old_size_p, " to ", len(comp_exp_vec[p])
                sys.stdout.flush()

            # Now, repeat, but swap p and q.

            old_size_q = len(comp_exp_vec[q])

            if verbose_flag:
                print "Size of comp_exp_vec[q] is: ", old_size_q, "."
                cv_size = ( (p-1)/gcd(p-1, q-1) )**( rho_length - 1 )
                print "Length of compatible_vectors: ", cv_size, "."
                print "Product: ", old_size_q * cv_size
                sys.stdout.flush()

            for exp_vec in comp_exp_vec[q].copy():
                if drop_vector(exp_vec, q, p, comp_exp_vec):
                    trash = comp_exp_vec[q].pop(exp_vec)

            if verbose_flag:
                print "Shrunk dictionary q from ", old_size_q, " to ", len(comp_exp_vec[q])
                sys.stdout.flush()

    return comp_exp_vec

def compatible_classes(a, m0, m1):
    r"""
    Given a congruence class a modulo `m_0`, returns those `b` modulo `m_1` such that `x = a \mod m_0`, `x = b \mod m_1` has a solution

    INPUT:

    - ``a`` -- an integer
    - ``m0`` -- a positive integer
    - ``m1`` -- a positive integer

    OUTPUT:

    A list of integers ``b`` in the range ``0..(m1-1)`` such that the Chinese Remainder Theorem problem

    .. MATH::

        \begin{aligned}
        x & = a \mod m_0\\
        x & = b \mod m_1
        \end{aligned}

    has a solution.

    .. NOTE::

        - For efficiency, the solutions are not computed.
        - A necessary and sufficient condition is that ``a`` and ``b`` are congruent modulo ``g = gcd(m0, m1)``

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import compatible_classes
        sage: compatible_classes(2, 18, 27)
        [2, 11, 20]

    Use CRT to check the output

    ::

        sage: CRT(2, 2, 18, 27)
        2
        sage: CRT(2, 11, 18, 27)
        38
        sage: CRT(2, 20, 18, 27)
        20

    """

    g = gcd(m0, m1)
    a0 = a % g
    return [a0 + b0*g for b0 in xrange(m1/g) ]

def compatible_vectors_check( a0, a1, m0, m1):
    r"""
    Given exponent vectors with respect to two moduli, determines if they are compatible.

    INPUT:

    - ``a0`` -- an exponent vector modulo ``m0``
    - ``a1`` -- an exponent vector modulo ``m1``
    - ``m0`` -- a positive integer giving the modulus of ``a0``
    - ``m1`` -- a positive integer giving the modulus of ``a1``

    OUTPUT:

    True if there is an integer exponent vector a satisfying

    .. MATH::

        \begin{aligned}
        a[0] &== a0[0] == a1[0]\\
        a[1:] &== a0[1:] \mod m_0\\
        a[1:] &== a1[1:] \mod m_1
        \end{aligned}

    and False otherwise.

    .. NOTE::

        - Exponent vectors must agree exactly in the first coordinate.
        - If exponent vectors are different lengths, an error is raised.

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import compatible_vectors_check
        sage: a0 = (3, 1, 8, 11)
        sage: a1 = (3, 5, 6, 13)
        sage: a2 = (5, 5, 6, 13)
        sage: a3 = (3, 1, 8)
        sage: compatible_vectors_check(a0, a1, 12, 22)
        True
        sage: compatible_vectors_check(a0, a2, 12, 22)
        False
        sage: compatible_vectors_check(a3, a0, 12, 22)
        Traceback (most recent call last):
        ...
        ValueError: Exponent vectors a0 and a1 are not the same length.
    """

    g = gcd(m0, m1)
    a0_mod_g = (x % g for x in a0)

    length = len( a0 )
    if length != len( a1 ):
        raise ValueError("Exponent vectors a0 and a1 are not the same length.")

    if a0[0] != a1[0]:
        # exponent vectors must agree exactly in the 0th coordinate.
        return False
    else:
        for j in xrange(1, length):
            if ( a0[j]-a1[j] ) % g != 0:
                return False

    # all conditions hold
    return True

def compatible_vectors(a, m0, m1):
    r"""
    Given an exponent vector ``a`` modulo ``m0``, returns a list of exponent vectors for the modulus ``m1``, such that a lift to the lcm modulus exists.

    INPUT:

    - ``a``  -- an exponent vector for the modulus ``m0``
    - ``m0`` -- a positive integer (specifying the modulus for ``a``)
    - ``m1`` -- a positive integer (specifying the alternate modulus)

    OUTPUT:

    A list of exponent vectors modulo ``m1`` which are compatible with ``a``.

    .. NOTE::

        - Exponent vectors must agree exactly in the 0th position in order to be compatible.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import compatible_vectors
        sage: a = (3, 1, 8, 1)
        sage: compatible_vectors(a, 18, 12)
        [(3, 1, 2, 1),
        (3, 1, 2, 7),
        (3, 1, 8, 1),
        (3, 1, 8, 7),
        (3, 7, 2, 1),
        (3, 7, 2, 7),
        (3, 7, 8, 1),
        (3, 7, 8, 7)]

    The order of the moduli matters.

    ::

        sage: len(compatible_vectors(a, 18, 12))
        8
        sage: len(compatible_vectors(a, 12, 18))
        27

    """

    # to start, recall that the 0th entry must be an exact match.
    compatible_list = [ ( a[0], ) ]

    # we now build a new list, extending the length of the compatible vectors.
    compatible_list_new = []

    for entry in a[1:]:
        compatible_entries = compatible_classes( entry, m0, m1 )
        for compatible_vector in compatible_list:
            for new_entry in compatible_entries:
                compatible_list_new.append( tuple(list(compatible_vector) + [new_entry]) )
        compatible_list = compatible_list_new
        compatible_list_new = []

    return compatible_list

def compatible_systems( split_prime_list, complement_exp_vec_dict ):
    r"""
    Given dictionaries of complement exponent vectors for various primes that split in K, compute all possible compatible systems.

    INPUT:

    - ``split_prime_list`` -- a list of rational primes that split completely in `K`
    - ``complement_exp_vec_dict`` -- a dictionary of dictionaries. The keys are primes from ``split_prime_list``.

    OUTPUT:

    A list of compatible systems of exponent vectors.

    .. NOTE::

        - For any ``q`` in ``split_prime_list``, ``complement_exp_vec_dict[q]`` is a dictionary whose keys are exponent vectors modulo ``q-1``
          and whose values are lists of exponent vectors modulo ``q-1`` which are complementary to the key.

        - an item in system_list has the form ``[ [v0, w0], [v1, w1], ..., [vk, wk] ]``, where::

            - ``qj = split_prime_list[j]``
            - ``vj`` and ``wj`` are complementary exponent vectors modulo ``qj - 1``
            - the pairs are all simultaneously compatible.

        - Let ``H = lcm( qj - 1 : qj in split_primes_list )``. Then for any compatible system, there is at most one pair of integer
          exponent vectors ``[v, w]`` such that::

            - every entry of ``v`` and ``w`` is bounded in absolute value by ``H``
            - for any ``qj``, ``v`` and ``vj`` agree modulo ``(qj - 1)``
            - for any ``qj``, ``w`` and ``wj`` agree modulo ``(qj - 1)``

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import construct_complement_dictionaries, compatible_systems
        sage: f = x^2 + 5
        sage: H = 10
        sage: K.<xi> = NumberField(f)
        sage: SUK = K.S_unit_group( S=K.primes_above(10) )
        sage: split_primes_list = [3, 7]
        sage: comp_exp_vec = construct_complement_dictionaries( split_primes_list, SUK, False )
        sage: compatible_systems( split_primes_list, comp_exp_vec )
        [[[(0, 1, 0), (0, 1, 0)], [(0, 3, 4), (0, 1, 2)]], [[(0, 1, 0), (0, 1, 0)], [(0, 3, 4), (0, 3, 4)]], [[(0, 1, 0), (0, 1, 0)], [(0, 3, 4), (0, 5, 0)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 2, 4), (1, 0, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 2, 4), (1, 4, 2)]], [[(1, 0, 0), (1, 0, 0)], [(1, 2, 4), (1, 2, 0)]],
         [[(0, 1, 0), (0, 1, 0)], [(0, 1, 2), (0, 1, 2)]], [[(0, 1, 0), (0, 1, 0)], [(0, 1, 2), (0, 3, 4)]], [[(0, 1, 0), (0, 1, 0)], [(0, 1, 2), (0, 5, 0)]],
         [[(0, 1, 0), (1, 0, 0)], [(0, 5, 4), (1, 0, 0)]], [[(0, 1, 0), (1, 0, 0)], [(0, 5, 4), (1, 4, 4)]], [[(0, 1, 0), (1, 0, 0)], [(0, 5, 4), (1, 2, 2)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 4, 2), (1, 2, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 4, 2), (1, 4, 0)]], [[(1, 0, 0), (1, 0, 0)], [(1, 4, 2), (1, 0, 2)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 0, 4), (1, 2, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 0, 4), (1, 4, 0)]], [[(1, 0, 0), (1, 0, 0)], [(1, 0, 4), (1, 0, 2)]],
         [[(0, 1, 0), (1, 0, 0)], [(0, 3, 2), (1, 0, 0)]], [[(0, 1, 0), (1, 0, 0)], [(0, 3, 2), (1, 4, 4)]], [[(0, 1, 0), (1, 0, 0)], [(0, 3, 2), (1, 2, 2)]],
         [[(1, 0, 0), (0, 1, 0)], [(1, 0, 0), (0, 5, 4)]], [[(1, 0, 0), (0, 1, 0)], [(1, 0, 0), (0, 3, 2)]], [[(1, 0, 0), (0, 1, 0)], [(1, 0, 0), (0, 1, 0)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 2, 0), (1, 2, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 2, 0), (1, 4, 0)]], [[(1, 0, 0), (1, 0, 0)], [(1, 2, 0), (1, 0, 2)]],
         [[(0, 1, 0), (1, 0, 0)], [(0, 1, 0), (1, 0, 0)]], [[(0, 1, 0), (1, 0, 0)], [(0, 1, 0), (1, 4, 4)]], [[(0, 1, 0), (1, 0, 0)], [(0, 1, 0), (1, 2, 2)]],
         [[(0, 1, 0), (0, 1, 0)], [(0, 5, 0), (0, 1, 2)]], [[(0, 1, 0), (0, 1, 0)], [(0, 5, 0), (0, 3, 4)]], [[(0, 1, 0), (0, 1, 0)], [(0, 5, 0), (0, 5, 0)]],
         [[(1, 0, 0), (0, 1, 0)], [(1, 2, 2), (0, 5, 4)]], [[(1, 0, 0), (0, 1, 0)], [(1, 2, 2), (0, 3, 2)]], [[(1, 0, 0), (0, 1, 0)], [(1, 2, 2), (0, 1, 0)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 4, 0), (1, 0, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 4, 0), (1, 4, 2)]], [[(1, 0, 0), (1, 0, 0)], [(1, 4, 0), (1, 2, 0)]],
         [[(1, 0, 0), (1, 0, 0)], [(1, 0, 2), (1, 0, 4)]], [[(1, 0, 0), (1, 0, 0)], [(1, 0, 2), (1, 4, 2)]], [[(1, 0, 0), (1, 0, 0)], [(1, 0, 2), (1, 2, 0)]],
         [[(1, 0, 0), (0, 1, 0)], [(1, 4, 4), (0, 5, 4)]], [[(1, 0, 0), (0, 1, 0)], [(1, 4, 4), (0, 3, 2)]], [[(1, 0, 0), (0, 1, 0)], [(1, 4, 4), (0, 1, 0)]]]
    """

    S0 = split_prime_list[:]

    if len(S0) == 0:
        return []
    if len(S0) == 1:
        system_list = []
        q = S0[0]
        for exponent_vector in complement_exp_vec_dict[q]:
            for complementary_vector in complement_exp_vec_dict[q][ exponent_vector ]:
                pair = [ [exponent_vector, complementary_vector] ]
                system_list.append( pair )
        return system_list
    if len(S0) > 1:
        system_list = []
        S1 = S0[:-1]
        num_primes = len(S1)
        old_systems = compatible_systems( S1, complement_exp_vec_dict )
        q = S0[-1]
        for exp_vec in complement_exp_vec_dict[q]:
            for comp_vec in complement_exp_vec_dict[q][ exp_vec ]:
                CompatibleSystem = True
                for old_system in old_systems:
                    for j in xrange(num_primes):
                        qj = S1[j]
                        exp_vec_qj = old_system[j][0]
                        comp_vec_qj = old_system[j][1]
                        CompatibleSystem = compatible_vectors_check( exp_vec, exp_vec_qj, q-1, qj-1 )
                        if CompatibleSystem:
                            CompatibleSystem = compatible_vectors_check( comp_vec, comp_vec_qj, q-1, qj-1 )
                        if not CompatibleSystem:
                            # no reason to finish the j loop.
                            break
                    if CompatibleSystem:
                        # build the new system and append it to the list.
                        new_system = old_system + [ [exp_vec, comp_vec] ]
                        system_list.append( new_system )
        return system_list

def compatible_system_lift( compatible_system, split_primes_list ):
    r"""
    Given a compatible system of exponent vectors and complementary exponent vectors, return a lift to the integers.

    INPUT:

    - ``compatible_system`` -- a list of pairs ``[ [v0, w0], [v1, w1], .., [vk, wk] ]``
      where [vi, wi] is a pair of complementary exponent vectors modulo ``qi - 1``, and all pairs are compatible.
    - ``split_primes_list`` -- a list of primes ``[ q0, q1, .., qk ]``

    OUTPUT:

    A pair of vectors ``[v, w]`` satisfying:

    1. ``v[0] == vi[0]`` for all ``i``
    2. ``w[0] == wi[0]`` for all ``i``
    3. ``v[j] == vi[j]`` modulo ``qi - 1`` for all ``i`` and all ``j > 0``
    4. ``w[j] == wi[j]`` modulo ``qi - 1`` for all ``i`` and all `j > 0``
    5. every entry of ``v`` and ``w`` is bounded by ``L/2`` in absolute value, where ``L`` is the
      least common multiple of ``{qi - 1 : qi in split_primes_list }``

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import construct_complement_dictionaries, compatible_systems, compatible_system_lift
        sage: f = x^2 + 5
        sage: H = 10
        sage: K.<xi> = NumberField(f)
        sage: S = K.primes_above(10)
        sage: SUK = K.S_unit_group(S=S)
        sage: split_primes_list = [3, 7]
        sage: comp_exp_vec = construct_complement_dictionaries( split_primes_list, SUK, False )
        sage: comp_sys = compatible_systems( split_primes_list, comp_exp_vec )[0]

    compatible_systems returns a long list of compatible systems; we just grab the first

    ::

        sage: compatible_system_lift( comp_sys, split_primes_list )
        [(0, 3, -2), (0, 1, 2)]
    """

    if len(split_primes_list) != len( compatible_system ):
        raise ValueError("The number of primes does not match the length of the given exponent vectors.")

    m = len( split_primes_list )
    t = len( compatible_system[0][0] )

    # the first entries are already determined.
    exponent_vector_lift = ( ZZ(compatible_system[0][0][0]), )
    complement_vector_lift = ( ZZ(compatible_system[0][1][0]), )

    # fill in exponent_vector_lift
    moduli_list = [q-1 for q in split_primes_list]
    L = lcm( moduli_list )

    for i in xrange(1,t):
        exp_coord_residues = [ compatible_system[j][0][i] for j in xrange(m) ]
        comp_coord_residues = [ compatible_system[j][1][i] for j in xrange(m) ]

        ev_lift_coordinate = CRT( exp_coord_residues, moduli_list)
        cv_lift_coordinate = CRT( comp_coord_residues, moduli_list)

        # these values lie in the range [0, L-1], so we must shift them if they are bigger than L/2.

        if ev_lift_coordinate > L/2:
            ev_lift_coordinate -= L
        if cv_lift_coordinate > L/2:
            cv_lift_coordinate -= L

        exponent_vector_lift = exponent_vector_lift + ( ev_lift_coordinate, )
        complement_vector_lift = complement_vector_lift + (cv_lift_coordinate, )

    return [ exponent_vector_lift, complement_vector_lift ]

def solutions_from_systems( SUK, bound, cs_list, split_primes_list ):
    r"""
    Lifts compatible systems to the integers and returns the S-unit equation solutions the lifts yield.

    INPUT:

    - ``SUK`` -- the group of `S`-units where we search for solutions
    - ``bound`` -- a bound for the entries of all entries of all lifts
    - ``cs_list`` -- a list of compatible systems of exponent vectors modulo `q-1` for
                 various primes `q`
    - ``split_primes_list`` -- a list of primes giving the moduli of the exponent vectors in ``cs_list``

    OUTPUT:

    A list of solutions to the S-unit equation. Each solution is a list:

    1. an exponent vector over the integers, ``ev``
    2. an exponent vector over the integers, ``cv``
    3. the S-unit corresponding to ``ev``, ``iota_exp``
    4. the S-unit corresponding to ``cv``, ``iota_comp``

    .. NOTE::

        - Every entry of ``ev`` is less than or equal to bound in absolute value
        - every entry of ``cv`` is less than or equal to bound in absolute value
        - ``iota_exp + iota_comp == 1``

    EXAMPLES::

        sage: from sage.rings.number_field.S_unit_solver import construct_complement_dictionaries, compatible_systems, solutions_from_systems
        sage: f = x^2 - 15
        sage: K.<xi> = NumberField(f)
        sage: S = K.primes_above(2)
        sage: SUK = K.S_unit_group(S=S)
        sage: split_primes_list = [7, 17]
        sage: comp_exp_vec = construct_complement_dictionaries( split_primes_list, SUK )
        sage: compatible_systems_list = compatible_systems( split_primes_list, comp_exp_vec )
        sage: solutions_from_systems( SUK, 20, compatible_systems_list, split_primes_list )
        [[(1, 0, 0), (0, 0, 1), -1, 2], [(1, 2, 0), (0, 1, 3), -8*xi - 31, 8*xi + 32],
         [(1, -2, 0), (0, -1, 3), 8*xi - 31, -8*xi + 32], [(0, -1, 3), (1, -2, 0), -8*xi + 32, 8*xi - 31],
         [(0, 0, 1), (1, 0, 0), 2, -1], [(0, -1, -3), (0, 1, -3), -1/8*xi + 1/2, 1/8*xi + 1/2],
         [(0, 0, -1), (0, 0, -1), 1/2, 1/2], [(0, 1, 3), (1, 2, 0), 8*xi + 32, -8*xi - 31],
         [(0, 1, -3), (0, -1, -3), 1/8*xi + 1/2, -1/8*xi + 1/2]]
    """

    solutions = []

    for system in cs_list:
        lift = compatible_system_lift( system, split_primes_list )
        ev = lift[0]
        cv = lift[1]
        t = len( ev )
        ValidLift = True
        for x in ev[1:]:
        # coordinates must be less than or equal to H in absolute value
            if abs(x) > bound:
                ValidLift = False
                break
        for x in cv[1:]:
            if abs(x) > bound:
                ValidLift = False
                break
        if ValidLift:
            # the entries are all below the bound, so there is nothing left to do
            # except construct the elements and see if they are solutions to
            # the S-unit equation
            iota_exp = SUK.exp( ev )
            iota_comp = SUK.exp( cv )
            if iota_exp + iota_comp == 1:
                sol = [ ev, cv, iota_exp, iota_comp ]
                solutions.append( sol )

    return solutions

def clean_sfs( sfs_list ):
    r"""
    Given a list of S-unit equation solutions, remove trivial redundancies.

    INPUT:

    - ``sfs_list`` -- a list of solutions to the S-unit equation

    OUTPUT:

    A list of solutions to the S-unit equation

    .. NOTE::

        The function looks for cases where ``x + y = 1`` and ``y + x = 1`` appear\
        as separate solutions, and removes one.

    EXAMPLE::

        sage: from sage.rings.number_field.S_unit_solver import construct_complement_dictionaries, compatible_systems, solutions_from_systems, clean_sfs
        sage: f = x^2 - 15
        sage: K.<xi> = NumberField(f)
        sage: S = K.primes_above(2)
        sage: SUK = K.S_unit_group(S=S)
        sage: split_primes_list = [7, 17]
        sage: comp_exp_vec = construct_complement_dictionaries( split_primes_list, SUK )
        sage: compatible_systems_list = compatible_systems( split_primes_list, comp_exp_vec )
        sage: suniteq_sols = solutions_from_systems( SUK, 20, compatible_systems_list, split_primes_list )
        sage: clean_sfs( suniteq_sols )
        [[(1, 0, 0), (0, 0, 1), -1, 2], [(1, 2, 0), (0, 1, 3), -8*xi - 31, 8*xi + 32],
         [(1, -2, 0), (0, -1, 3), 8*xi - 31, -8*xi + 32],
         [(0, -1, -3), (0, 1, -3), -1/8*xi + 1/2, 1/8*xi + 1/2],
         [(0, 0, -1), (0, 0, -1), 1/2, 1/2]]
    """
    # given the output from solutions_from_systems,
    # look for trivial redundancies: swapping exp_vec, comp_vec, particularly.
    new_sfs = []
    for entry in sfs_list:
        swapped_entry = [entry[1], entry[0], entry[3], entry[2]]
        repeat = False
        if entry in new_sfs or swapped_entry in new_sfs:
            repeat = True
        if not repeat:
            new_sfs.append( entry )
    return new_sfs

def solve_S_unit_equation(K, S, prec = None):
    r"""
    Return all solutions to the S-unit equation ``x + y = 1`` over K.

    INPUT:

    - ``K`` -- a number field (an absolute extension of the rationals)
    - ``S`` -- a list of finite primes of ``K``
    - ``prec`` -- (default: None) precision used for computations in real field, complex field, and p-adic field.

    OUTPUT:

    A list of lists ``[[ A_1, B_1, x_1, y_1], [A_2, B_2, x_2, y_2], ... [ A_n, B_n, x_n, y_n]]`` such that:

    1. The first two entries are tuples ``A_i = (a_0, a_1, ... , a_t)`` and ``B_i = (b_0, b_1, ... , b_t)`` of exponents.
    2. The last two entries are ``S``-units ``x_i`` and ``y_i`` in ``K`` with ``x_i + y_i = 1``.
    3. If the default generators for the ``S``-units of ``K`` are ``(rho_0, rho_1, ... , rho_t)``, then these satisfy ``x_i = \prod(rho_i)^(a_i)`` and ``y_i = \prod(rho_i)^(bx_i)``.

    EXAMPLE::

        sage: K.<xi> = NumberField(x^2+x+1)
        sage: SUK = UnitGroup(K,S=tuple(K.primes_above(3)))
        sage: S=SUK.primes()
        sage: solve_S_unit_equation(K, S, 200)
        [[(2, 1), (4, 0), xi + 2, -xi - 1], [(5, -1), (4, -1), 1/3*xi + 2/3, -1/3*xi + 1/3], [(5, 0), (1, 0), -xi, xi + 1], [(1, 1), (2, 0), -xi + 1, xi]]
    """

    if not K.is_absolute():
        raise ValueError("K must be an absolute extension.")

    S=list(S)
    xi = K.gen()
    nK = K.absolute_degree()
    SUK = UnitGroup(K, S=tuple(S))
    t = SUK.rank()
    rho = SUK.gens_values()
    A = K.roots_of_unity()

    all_LLL_bounds = [p_adic_LLL_bound(SUK, A, prec)] + [cx_LLL_bound(SUK,A, prec)]

    final_LLL_bound = max(all_LLL_bounds)

    split_primes_list = split_primes_large_lcm(SUK, final_LLL_bound)

    complement_exp_vec_dict = construct_complement_dictionaries(split_primes_list, SUK)

    cs_list = compatible_systems(split_primes_list, complement_exp_vec_dict)

    sfs_list = solutions_from_systems(SUK, final_LLL_bound, cs_list, split_primes_list)

    s_unit_solutions = clean_sfs(sfs_list)

    return s_unit_solutions
