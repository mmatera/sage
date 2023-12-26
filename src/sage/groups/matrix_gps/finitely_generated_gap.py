# sage_setup: distribution = sagemath-gap

"""
Finitely Generated Matrix Groups with GAP
"""

# #############################################################################
#       Copyright (C) 2006      William Stein <wstein@gmail.com>
#                     2006-2008 David Joyner
#                     2008-2010 Simon King
#                     2009      Mike Hansen
#                     2011-2013 Volker Braun <vbraun.name@gmail.com>
#                     2013-2023 Travis Scrimshaw
#                     2015      Pierre Guillot
#                     2017      Ben Hutz
#                     2017      Rebecca Lauren Miller
#                     2018      Dima Pasechnik
#                     2018-2019 Sebastian Oehms
#                     2018-2020 Frédéric Chapoton
#                     2019      Vincent Delecroix
#                     2023      Matthias Koeppe
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  https://www.gnu.org/licenses/
# #############################################################################

from sage.combinat.integer_vector import IntegerVectors
from sage.groups.matrix_gps.finitely_generated import MatrixGroup
from sage.groups.matrix_gps.matrix_group_gap import MatrixGroup_gap
from sage.matrix.matrix_space import MatrixSpace
from sage.misc.cachefunc import cached_method
from sage.misc.functional import cyclotomic_polynomial
from sage.modules.free_module_element import vector
from sage.rings.fraction_field import FractionField
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.multi_polynomial_sequence import PolynomialSequence
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.rings.power_series_ring import PowerSeriesRing


class FinitelyGeneratedMatrixGroup_gap(MatrixGroup_gap):
    """
    Matrix group generated by a finite number of matrices.

    EXAMPLES::

        sage: m1 = matrix(GF(11), [[1,2],[3,4]])
        sage: m2 = matrix(GF(11), [[1,3],[10,0]])
        sage: G = MatrixGroup(m1, m2);  G
        Matrix group over Finite Field of size 11 with 2 generators (
        [1 2]  [ 1  3]
        [3 4], [10  0]
        )
        sage: type(G)
        <class 'sage.groups.matrix_gps.finitely_generated_gap.FinitelyGeneratedMatrixGroup_gap_with_category'>
        sage: TestSuite(G).run()
    """

    def __reduce__(self):
        """
        Implement pickling.

        EXAMPLES::

            sage: m1 = matrix(QQ, [[1,2],[3,4]])
            sage: m2 = matrix(QQ, [[1,3],[-1,0]])
            sage: loads(MatrixGroup(m1, m2).dumps())
            Matrix group over Rational Field with 2 generators (
            [1 2]  [ 1  3]
            [3 4], [-1  0]
            )
        """
        return (MatrixGroup,
                tuple(g.matrix() for g in self.gens()) + ({'check':False},))

    def as_permutation_group(self, algorithm=None, seed=None):
        r"""
        Return a permutation group representation for the group.

        In most cases occurring in practice, this is a permutation
        group of minimal degree (the degree being determined from
        orbits under the group action). When these orbits are hard to
        compute, the procedure can be time-consuming and the degree
        may not be minimal.

        INPUT:

        - ``algorithm`` -- ``None`` or ``'smaller'``. In the latter
          case, try harder to find a permutation representation of
          small degree.
        - ``seed`` -- ``None`` or an integer specifying the seed
          to fix results depending on pseudo-random-numbers. Here
          it makes sense to be used with respect to the ``'smaller'``
          option, since GAP produces random output in that context.

        OUTPUT:

        A permutation group isomorphic to ``self``. The
        ``algorithm='smaller'`` option tries to return an isomorphic
        group of low degree, but is not guaranteed to find the
        smallest one and must not even differ from the one obtained
        without the option. In that case repeating the invocation
        may help (see the example below).

        EXAMPLES::

            sage: MS = MatrixSpace(GF(2), 5, 5)
            sage: A = MS([[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0]])
            sage: G = MatrixGroup([A])
            sage: G.as_permutation_group().order()
            2

        A finite subgroup of `GL(12,\ZZ)` as a permutation group::

            sage: imf = libgap.function_factory('ImfMatrixGroup')
            sage: GG = imf( 12, 3 )
            sage: G = MatrixGroup(GG.GeneratorsOfGroup())
            sage: G.cardinality()
            21499084800
            sage: P = G.as_permutation_group()
            sage: Psmaller = G.as_permutation_group(algorithm="smaller", seed=6)
            sage: P.cardinality()
            21499084800
            sage: P.degree()
            144
            sage: Psmaller.cardinality()
            21499084800
            sage: Psmaller.degree() <= P.degree()
            True

        .. NOTE::

            In this case, the "smaller" option returned an isomorphic
            group of lower degree. The above example used GAP's library
            of irreducible maximal finite ("imf") integer matrix groups
            to construct the :class:`MatrixGroup` `G` over `\GF{7}`. The section
            "Irreducible Maximal Finite Integral Matrix Groups" in the
            GAP reference manual has more details.

        .. NOTE::

            Concerning the option ``algorithm='smaller'`` you should note
            the following from GAP documentation: "The methods used might
            involve the use of random elements and the permutation
            representation (or even the degree of the representation) is
            not guaranteed to be the same for different calls of
            ``SmallerDegreePermutationRepresentation``."

            To obtain a reproducible result the optional argument ``seed``
            may be used as in the example above.

        TESTS::

            sage: A = matrix(QQ, 2, [0, 1, 1, 0])
            sage: B = matrix(QQ, 2, [1, 0, 0, 1])
            sage: a, b = MatrixGroup([A, B]).as_permutation_group().gens()
            sage: a.order(), b.order()
            (2, 1)

        The above example in `GL(12,\ZZ)`, reduced modulo 7::

            sage: MS = MatrixSpace(GF(7), 12, 12)
            sage: G = MatrixGroup([MS(g) for g in GG.GeneratorsOfGroup()])
            sage: G.cardinality()
            21499084800
            sage: P = G.as_permutation_group()
            sage: P.cardinality()
            21499084800

        Check that large degree is still working::

            sage: Sp(6,3).as_permutation_group().cardinality()
            9170703360

        Check that :trac:`25706` still works after :trac:`26903`::

            sage: # needs sage.libs.pari
            sage: MG = GU(3,2).as_matrix_group()
            sage: PG = MG.as_permutation_group()
            sage: mg = MG.an_element()
            sage: PG(mg).order()  # particular element depends on the set of GAP packages installed
            6
        """
        # Note that the output of IsomorphismPermGroup() depends on
        # memory locations and will change if you change the order of
        # doctests and/or architecture
        from sage.groups.perm_gps.permgroup import PermutationGroup
        if not self.is_finite():
            raise NotImplementedError("group must be finite")
        if seed is not None:
            from sage.libs.gap.libgap import libgap
            libgap.set_seed(ZZ(seed))
        iso = self._libgap_().IsomorphismPermGroup()
        if algorithm == "smaller":
            iso = iso.Image().SmallerDegreePermutationRepresentation()
        return PermutationGroup(iso.Image().GeneratorsOfGroup().sage(),
                                canonicalize=False)

    def module_composition_factors(self, algorithm=None):
        r"""
        Return a list of triples consisting of [base field, dimension,
        irreducibility], for each of the Meataxe composition factors
        modules. The ``algorithm="verbose"`` option returns more information,
        but in Meataxe notation.

        EXAMPLES::

            sage: F = GF(3); MS = MatrixSpace(F,4,4)
            sage: M = MS(0)
            sage: M[0,1] = 1; M[1,2] = 1; M[2,3] = 1; M[3,0] = 1
            sage: G = MatrixGroup([M])
            sage: G.module_composition_factors()
            [(Finite Field of size 3, 1, True),
             (Finite Field of size 3, 1, True),
             (Finite Field of size 3, 2, True)]
            sage: F = GF(7); MS = MatrixSpace(F,2,2)
            sage: gens = [MS([[0,1],[-1,0]]), MS([[1,1],[2,3]])]
            sage: G = MatrixGroup(gens)
            sage: G.module_composition_factors()
            [(Finite Field of size 7, 2, True)]

        Type ``G.module_composition_factors(algorithm='verbose')`` to get a
        more verbose version.

        For more on MeatAxe notation, see
        https://www.gap-system.org/Manuals/doc/ref/chap69.html
        """
        from sage.libs.gap.libgap import libgap
        F = self.base_ring()
        if not F.is_finite():
            raise NotImplementedError("base ring must be finite")
        n = self.degree()
        MS = MatrixSpace(F, n, n)
        mats = [MS(g.matrix()) for g in self.gens()]
        # initializing list of mats by which the gens act on self
        mats_gap = libgap(mats)
        M = mats_gap.GModuleByMats(F)
        compo = libgap.function_factory('MTX.CompositionFactors')
        MCFs = compo(M)
        if algorithm == "verbose":
            print(str(MCFs) + "\n")
        return sorted((MCF['field'].sage(),
                       MCF['dimension'].sage(),
                       MCF['IsIrreducible'].sage()) for MCF in MCFs)

    def invariant_generators(self):
        r"""
        Return invariant ring generators.

        Computes generators for the polynomial ring
        `F[x_1,\ldots,x_n]^G`, where `G` in `GL(n,F)` is a finite matrix
        group.

        In the "good characteristic" case the polynomials returned
        form a minimal generating set for the algebra of `G`-invariant
        polynomials.  In the "bad" case, the polynomials returned
        are primary and secondary invariants, forming a not
        necessarily minimal generating set for the algebra of
        `G`-invariant polynomials.

        ALGORITHM:

        Wraps Singular's ``invariant_algebra_reynolds`` and ``invariant_ring``
        in ``finvar.lib``.

        EXAMPLES::

            sage: F = GF(7); MS = MatrixSpace(F,2,2)
            sage: gens = [MS([[0,1],[-1,0]]),MS([[1,1],[2,3]])]
            sage: G = MatrixGroup(gens)
            sage: G.invariant_generators()                                              # needs sage.libs.singular
            [x1^7*x2 - x1*x2^7,
             x1^12 - 2*x1^9*x2^3 - x1^6*x2^6 + 2*x1^3*x2^9 + x2^12,
             x1^18 + 2*x1^15*x2^3 + 3*x1^12*x2^6 + 3*x1^6*x2^12 - 2*x1^3*x2^15 + x2^18]

            sage: q = 4; a = 2
            sage: MS = MatrixSpace(QQ, 2, 2)
            sage: gen1 = [[1/a, (q-1)/a], [1/a, -1/a]]
            sage: gen2 = [[1,0], [0,-1]]; gen3 = [[-1,0], [0,1]]
            sage: G = MatrixGroup([MS(gen1), MS(gen2), MS(gen3)])
            sage: G.cardinality()
            12
            sage: G.invariant_generators()                                              # needs sage.libs.singular
            [x1^2 + 3*x2^2, x1^6 + 15*x1^4*x2^2 + 15*x1^2*x2^4 + 33*x2^6]

            sage: # needs sage.rings.number_field
            sage: F = CyclotomicField(8)
            sage: z = F.gen()
            sage: a = z+1/z
            sage: b = z^2
            sage: MS = MatrixSpace(F,2,2)
            sage: g1 = MS([[1/a, 1/a], [1/a, -1/a]])
            sage: g2 = MS([[-b, 0], [0, b]])
            sage: G = MatrixGroup([g1,g2])
            sage: G.invariant_generators()                                              # needs sage.libs.singular
            [x1^4 + 2*x1^2*x2^2 + x2^4,
             x1^5*x2 - x1*x2^5,
             x1^8 + 28/9*x1^6*x2^2 + 70/9*x1^4*x2^4 + 28/9*x1^2*x2^6 + x2^8]

        AUTHORS:

        - David Joyner, Simon King and Martin Albrecht.

        REFERENCES:

        - Singular reference manual

        - [Stu1993]_

        - S. King, "Minimal Generating Sets of non-modular invariant
          rings of finite groups", :arxiv:`math/0703035`.
        """
        from sage.interfaces.singular import singular
        from sage.rings.polynomial.polynomial_ring_constructor import \
            PolynomialRing
        gens = self.gens()
        singular.LIB("finvar.lib")
        n = self.degree()  # len((gens[0].matrix()).rows())
        F = self.base_ring()
        q = F.characteristic()
        # test if the field is admissible
        if F.gen() == 1:  # we got the rationals or GF(prime)
            FieldStr = str(F.characteristic())
        elif hasattr(F,'polynomial'):  # we got an algebraic extension
            if len(F.gens()) > 1:
                raise NotImplementedError("can only deal with finite fields and (simple algebraic extensions of) the rationals")
            FieldStr = '(%d,%s)' % (F.characteristic(), str(F.gen()))
        else:  # we have a transcendental extension
            FieldStr = '(%d,%s)' % (F.characteristic(),
                                    ','.join(str(p) for p in F.gens()))

        # Setting Singular's variable names
        # We need to make sure that field generator and variables get different names.
        if str(F.gen())[0] == 'x':
            VarStr = 'y'
        else:
            VarStr = 'x'
        VarNames = '(' + ','.join((VarStr+str(i) for i in range(1, n+1)))+')'
        # The function call and affectation below have side-effects. Do not remove!
        # (even if pyflakes say so)
        R = singular.ring(FieldStr, VarNames, 'dp')
        if hasattr(F, 'polynomial') and F.gen() != 1:
            # we have to define minpoly
            singular.eval('minpoly = '+str(F.polynomial()).replace('x',str(F.gen())))
        A = [singular.matrix(n,n,str((x.matrix()).list())) for x in gens]
        Lgens = ','.join((x.name() for x in A))
        PR = PolynomialRing(F, n, [VarStr+str(i) for i in range(1,n+1)])

        if q == 0 or (q > 0 and self.cardinality() % q):
            from sage.matrix.constructor import Matrix
            try:
                elements = [g.matrix() for g in self.list()]
            except (TypeError, ValueError):
                elements
            if elements is not None:
                ReyName = 't'+singular._next_var_name()
                singular.eval('matrix %s[%d][%d]' % (ReyName,
                                                     self.cardinality(), n))
                for i in range(1,self.cardinality()+1):
                    M = Matrix(F, elements[i-1])
                    D = [{} for foobar in range(self.degree())]
                    for x,y in M.dict().items():
                        D[x[0]][x[1]] = y
                    for row in range(self.degree()):
                        for t in D[row].items():
                            singular.eval('%s[%d,%d]=%s[%d,%d]+(%s)*var(%d)'
                                          % (ReyName,i,row+1,ReyName,i,row+1, repr(t[1]),t[0]+1))
                IRName = 't'+singular._next_var_name()
                singular.eval('matrix %s = invariant_algebra_reynolds(%s)' % (IRName,ReyName))
            else:
                ReyName = 't'+singular._next_var_name()
                singular.eval('list %s=group_reynolds((%s))' % (ReyName, Lgens))
                IRName = 't'+singular._next_var_name()
                singular.eval('matrix %s = invariant_algebra_reynolds(%s[1])' % (IRName, ReyName))

            OUT = [singular.eval(IRName+'[1,%d]' % (j))
                   for j in range(1, 1+int(singular('ncols('+IRName+')')))]
            return [PR(gen) for gen in OUT]
        if self.cardinality() % q == 0:
            PName = 't' + singular._next_var_name()
            SName = 't' + singular._next_var_name()
            singular.eval('matrix %s,%s=invariant_ring(%s)' % (PName, SName, Lgens))
            OUT = [singular.eval(PName+'[1,%d]' % (j))
                   for j in range(1,1+singular('ncols('+PName+')'))]
            OUT += [singular.eval(SName+'[1,%d]' % (j))
                    for j in range(2,1+singular('ncols('+SName+')'))]
            return [PR(gen) for gen in OUT]

    def molien_series(self, chi=None, return_series=True, prec=20, variable='t'):
        r"""
        Compute the Molien series of this finite group with respect to the
        character ``chi``.

        It can be returned either as a rational function in one variable
        or a power series in one variable. The base field must be a
        finite field, the rationals, or a cyclotomic field.

        Note that the base field characteristic cannot divide the group
        order (i.e., the non-modular case).

        ALGORITHM:

        For a finite group `G` in characteristic zero we construct
        the Molien series as

        .. MATH::

            \frac{1}{|G|}\sum_{g \in G} \frac{\chi(g)}{\text{det}(I-tg)},

        where `I` is the identity matrix and `t` an indeterminate.

        For characteristic `p` not dividing the order of `G`, let `k` be
        the base field and `N` the order of `G`. Define `\lambda` as a
        primitive `N`-th root of unity over `k` and `\omega` as a
        primitive `N`-th root of unity over `\QQ`. For each `g \in G`
        define `k_i(g)` to be the positive integer such that
        `e_i = \lambda^{k_i(g)}` for each eigenvalue `e_i` of `g`.
        Then the Molien series is computed as

        .. MATH::

            \frac{1}{|G|}\sum_{g \in G} \frac{\chi(g)}{\prod_{i=1}^n
                (1 - t\omega^{k_i(g)})},

        where `t` is an indeterminant. [Dec1998]_

        INPUT:

        - ``chi`` -- (default: trivial character) a linear group character of this group
        - ``return_series`` -- boolean (default: ``True``) if ``True``, then returns
          the Molien series as a power series, ``False`` as a rational function
        - ``prec`` -- integer (default: 20); power series default precision
          (possibly infinite, in which case it is computed lazily)
        - ``variable`` -- string (default: ``'t'``); variable name for the Molien series

        OUTPUT: single variable rational function or power series with integer coefficients

        EXAMPLES::

            sage: MatrixGroup(matrix(QQ,2,2,[1,1,0,1])).molien_series()
            Traceback (most recent call last):
            ...
            NotImplementedError: only implemented for finite groups
            sage: MatrixGroup(matrix(GF(3),2,2,[1,1,0,1])).molien_series()              # needs sage.rings.number_field
            Traceback (most recent call last):
            ...
            NotImplementedError: characteristic cannot divide group order

        Tetrahedral Group::

            sage: # needs sage.rings.number_field
            sage: K.<i> = CyclotomicField(4)
            sage: Tetra =  MatrixGroup([(-1+i)/2,(-1+i)/2, (1+i)/2,(-1-i)/2], [0,i, -i,0])
            sage: Tetra.molien_series(prec=30)
            1 + t^8 + 2*t^12 + t^16 + 2*t^20 + 3*t^24 + 2*t^28 + O(t^30)
            sage: mol = Tetra.molien_series(return_series=False); mol
            (t^8 - t^4 + 1)/(t^16 - t^12 - t^4 + 1)
            sage: mol.parent()
            Fraction Field of Univariate Polynomial Ring in t over Integer Ring
            sage: chi = Tetra.character(Tetra.character_table()[1])
            sage: Tetra.molien_series(chi, prec=30, variable='u')
            u^6 + u^14 + 2*u^18 + u^22 + 2*u^26 + 3*u^30 + 2*u^34 + O(u^36)
            sage: chi = Tetra.character(Tetra.character_table()[2])
            sage: Tetra.molien_series(chi)
            t^10 + t^14 + t^18 + 2*t^22 + 2*t^26 + O(t^30)

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: S3 = MatrixGroup(SymmetricGroup(3))
            sage: mol = S3.molien_series(prec=10); mol
            1 + t + 2*t^2 + 3*t^3 + 4*t^4 + 5*t^5 + 7*t^6 + 8*t^7 + 10*t^8 + 12*t^9 + O(t^10)
            sage: mol.parent()
            Power Series Ring in t over Integer Ring
            sage: mol = S3.molien_series(prec=oo); mol
            1 + t + 2*t^2 + 3*t^3 + 4*t^4 + 5*t^5 + 7*t^6 + O(t^7)
            sage: mol.parent()
            Lazy Taylor Series Ring in t over Integer Ring

        Octahedral Group::

            sage: # needs sage.rings.number_field
            sage: K.<v> = CyclotomicField(8)
            sage: a = v - v^3  # sqrt(2)
            sage: i = v^2
            sage: Octa = MatrixGroup([(-1+i)/2, (-1+i)/2,  (1+i)/2, (-1-i)/2],          # needs sage.symbolic
            ....:                    [(1+i)/a, 0,  0, (1-i)/a])
            sage: Octa.molien_series(prec=30)                                           # needs sage.symbolic
            1 + t^8 + t^12 + t^16 + t^18 + t^20 + 2*t^24 + t^26 + t^28 + O(t^30)

        Icosahedral Group::

            sage: # needs sage.rings.number_field
            sage: K.<v> = CyclotomicField(10)
            sage: z5 = v^2
            sage: i = z5^5
            sage: a = 2*z5^3 + 2*z5^2 + 1  #sqrt(5)
            sage: Ico = MatrixGroup([[z5^3,0, 0,z5^2],
            ....:                    [0,1, -1,0],
            ....:                    [(z5^4-z5)/a, (z5^2-z5^3)/a,
            ....:                     (z5^2-z5^3)/a, -(z5^4-z5)/a]])
            sage: Ico.molien_series(prec=40)
            1 + t^12 + t^20 + t^24 + t^30 + t^32 + t^36 + O(t^40)

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: G = MatrixGroup(CyclicPermutationGroup(3))
            sage: chi = G.character(G.character_table()[1])
            sage: G.molien_series(chi, prec=10)
            t + 2*t^2 + 3*t^3 + 5*t^4 + 7*t^5 + 9*t^6
             + 12*t^7 + 15*t^8 + 18*t^9 + 22*t^10 + O(t^11)

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: K = GF(5)
            sage: S = MatrixGroup(SymmetricGroup(4))
            sage: G = MatrixGroup([matrix(K, 4, 4,
            ....:                         [K(y) for u in m.list() for y in u])
            ....:                  for m in S.gens()])
            sage: G.molien_series(return_series=False)
            1/(t^10 - t^9 - t^8 + 2*t^5 - t^2 - t + 1)

        ::

            sage: # needs sage.rings.number_field
            sage: i = GF(7)(3)
            sage: G = MatrixGroup([[i^3,0, 0,-i^3], [i^2,0, 0,-i^2]])
            sage: chi = G.character(G.character_table()[4])
            sage: G.molien_series(chi)
            3*t^5 + 6*t^11 + 9*t^17 + 12*t^23 + O(t^25)
        """
        if not self.is_finite():
            raise NotImplementedError("only implemented for finite groups")
        if chi is None:
            chi = self.trivial_character()
        M = self.matrix_space()
        R = FractionField(self.base_ring())
        N = self.order()
        if R.characteristic() == 0:
            P = PolynomialRing(R, variable)
            t = P.gen()
            # it is possible the character is over a larger cyclotomic field
            K = chi.values()[0].parent()
            if K.degree() != 1:
                if R.degree() != 1:
                    L = K.composite_fields(R)[0]
                else:
                    L = K
            else:
                L = R
            mol = P(0)
            for g in self:
                mol += L(chi(g)) / (M.identity_matrix()-t*g.matrix()).det().change_ring(L)
        elif R.characteristic().divides(N):
            raise NotImplementedError("characteristic cannot divide group order")
        else:  # char p>0
            # find primitive Nth roots of unity over base ring and QQ
            F = cyclotomic_polynomial(N).change_ring(R)
            w = F.roots(ring=R.algebraic_closure(), multiplicities=False)[0]
            # don't need to extend further in this case since the order of
            # the roots of unity in the character divide the order of the group
            from sage.rings.number_field.number_field import CyclotomicField
            L = CyclotomicField(N, 'v')
            v = L.gen()
            # construct Molien series
            P = PolynomialRing(L, variable)
            t = P.gen()
            mol = P(0)
            for g in self:
                # construct Phi
                phi = L(chi(g))
                for e in g.matrix().eigenvalues():
                    # find power such that w**n  = e
                    n = 1
                    while w**n != e and n < N+1:
                        n += 1
                    # raise v to that power
                    phi *= (1-t*v**n)
                mol += P(1)/phi
        # We know the coefficients will be integers
        mol = mol.numerator().change_ring(ZZ) / mol.denominator().change_ring(ZZ)
        # divide by group order
        mol /= N
        if return_series:
            if prec == float('inf'):
                from sage.rings.lazy_series_ring import LazyPowerSeriesRing
                PS = LazyPowerSeriesRing(ZZ, names=(variable,), sparse=P.is_sparse())
            else:
                PS = PowerSeriesRing(ZZ, variable, default_prec=prec)
            return PS(mol)
        return mol

    def reynolds_operator(self, poly, chi=None):
        r"""
        Compute the Reynolds operator of this finite group `G`.

        This is the projection from a polynomial ring to the ring of
        relative invariants [Stu1993]_. If possible, the invariant is
        returned defined over the base field of the given polynomial
        ``poly``, otherwise, it is returned over the compositum of the
        fields involved in the computation.
        Only implemented for absolute fields.

        ALGORITHM:

        Let `K[x]` be a polynomial ring and `\chi` a linear character for `G`. Let

        .. MATH:

            K[x]^G_{\chi} = \{f \in K[x] | \pi f = \chi(\pi) f \forall \pi\in G\}

        be the ring of invariants of `G` relative to `\chi`. Then the Reynolds operator
        is a map `R` from `K[x]` into `K[x]^G_{\chi}` defined by

        .. MATH:

            f \mapsto \frac{1}{|G|} \sum_{ \pi \in G} \chi(\pi) f.

        INPUT:

        - ``poly`` -- a polynomial

        - ``chi`` -- (default: trivial character) a linear group character of this group

        OUTPUT: an invariant polynomial relative to `\chi`

        AUTHORS:

        Rebecca Lauren Miller and Ben Hutz

        EXAMPLES::

            sage: S3 = MatrixGroup(SymmetricGroup(3))
            sage: R.<x,y,z> = QQ[]
            sage: f = x*y*z^3
            sage: S3.reynolds_operator(f)                                               # needs sage.rings.number_field
            1/3*x^3*y*z + 1/3*x*y^3*z + 1/3*x*y*z^3

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: G = MatrixGroup(CyclicPermutationGroup(4))
            sage: chi = G.character(G.character_table()[3])
            sage: K.<v> = CyclotomicField(4)
            sage: R.<x,y,z,w> = K[]
            sage: G.reynolds_operator(x, chi)
            1/4*x + (1/4*v)*y - 1/4*z + (-1/4*v)*w
            sage: chi = G.character(G.character_table()[2])
            sage: R.<x,y,z,w> = QQ[]
            sage: G.reynolds_operator(x*y, chi)
            1/4*x*y + (-1/4*zeta4)*y*z + (1/4*zeta4)*x*w - 1/4*z*w

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: K.<i> = CyclotomicField(4)
            sage: G =  MatrixGroup(CyclicPermutationGroup(3))
            sage: chi = G.character(G.character_table()[1])
            sage: R.<x,y,z> = K[]
            sage: G.reynolds_operator(x*y^5, chi)
            1/3*x*y^5 + (-2/3*izeta3^3 - izeta3^2 - 8/3*izeta3 - 4/3)*x^5*z
                      + (2/3*izeta3^3 + izeta3^2 + 8/3*izeta3 + 1)*y*z^5
            sage: R.<x,y,z> = QQbar[]
            sage: G.reynolds_operator(x*y^5, chi)
             1/3*x*y^5 + (-0.1666666666666667? + 0.2886751345948129?*I)*x^5*z
                       + (-0.1666666666666667? - 0.2886751345948129?*I)*y*z^5

        ::

            sage: # needs sage.rings.number_field
            sage: K.<i> = CyclotomicField(4)
            sage: Tetra =  MatrixGroup([(-1+i)/2,(-1+i)/2, (1+i)/2,(-1-i)/2], [0,i, -i,0])
            sage: chi = Tetra.character(Tetra.character_table()[4])
            sage: L.<v> = QuadraticField(-3)
            sage: R.<x,y> = L[]
            sage: Tetra.reynolds_operator(x^4)
            0
            sage: Tetra.reynolds_operator(x^4, chi)
            1/4*x^4 + (1/2*v)*x^2*y^2 + 1/4*y^4
            sage: R.<x>=L[]
            sage: LL.<w> = L.extension(x^2 + v)
            sage: R.<x,y> = LL[]
            sage: Tetra.reynolds_operator(x^4, chi)
            Traceback (most recent call last):
            ...
            NotImplementedError: only implemented for absolute fields

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: G =  MatrixGroup(DihedralGroup(4))
            sage: chi = G.character(G.character_table()[1])
            sage: R.<x,y> = QQ[]
            sage: f = x^4
            sage: G.reynolds_operator(f, chi)
            Traceback (most recent call last):
            ...
            TypeError: number of variables in polynomial must match size of matrices
            sage: R.<x,y,z,w> = QQ[]
            sage: f = x^3*y
            sage: G.reynolds_operator(f, chi)
            1/8*x^3*y - 1/8*x*y^3 + 1/8*y^3*z - 1/8*y*z^3 - 1/8*x^3*w + 1/8*z^3*w +
            1/8*x*w^3 - 1/8*z*w^3

        Characteristic `p>0` examples::

            sage: G = MatrixGroup([[0,1, 1,0]])
            sage: R.<w,x> = GF(2)[]
            sage: G.reynolds_operator(x)
            Traceback (most recent call last):
            ...
            NotImplementedError: not implemented when characteristic divides group order

        ::

            sage: i = GF(7)(3)
            sage: G = MatrixGroup([[i^3,0, 0,-i^3], [i^2,0, 0,-i^2]])
            sage: chi = G.character(G.character_table()[4])                             # needs sage.rings.number_field
            sage: R.<w,x> = GF(7)[]
            sage: f = w^5*x + x^6
            sage: G.reynolds_operator(f, chi)                                           # needs sage.rings.number_field
            Traceback (most recent call last):
            ...
            NotImplementedError: nontrivial characters not implemented for characteristic > 0
            sage: G.reynolds_operator(f)
            x^6

        ::

            sage: # needs sage.rings.finite_rings
            sage: K = GF(3^2,'t')
            sage: G = MatrixGroup([matrix(K, 2, 2, [0,K.gen(), 1,0])])
            sage: R.<x,y> = GF(3)[]
            sage: G.reynolds_operator(x^8)
            -x^8 - y^8

        ::

            sage: # needs sage.rings.finite_rings
            sage: K = GF(3^2,'t')
            sage: G = MatrixGroup([matrix(GF(3), 2, 2, [0,1, 1,0])])
            sage: R.<x,y> = K[]
            sage: f = -K.gen()*x
            sage: G.reynolds_operator(f)
            t*x + t*y
        """
        if poly.parent().ngens() != self.degree():
            raise TypeError("number of variables in polynomial must match size of matrices")
        R = FractionField(poly.base_ring())
        C = FractionField(self.base_ring())
        if chi is None:  # then this is the trivial character
            if R.characteristic() == 0:
                from sage.rings.qqbar import QQbar

                # non-modular case
                if C == QQbar or R == QQbar:
                    L = QQbar
                elif not C.is_absolute() or not R.is_absolute():
                    raise NotImplementedError("only implemented for absolute fields")
                else:  # create the compositum
                    if C.absolute_degree() == 1:
                        L = R
                    elif R.absolute_degree() == 1:
                        L = C
                    else:
                        L = C.composite_fields(R)[0]
            elif not R.characteristic().divides(self.order()):
                if R.characteristic() != C.characteristic():
                    raise ValueError("base fields must have same characteristic")
                else:
                    if R.degree() >= C.degree():
                        L = R
                    else:
                        L = C
            else:
                raise NotImplementedError("not implemented when characteristic divides group order")
            poly = poly.change_ring(L)
            poly_gens = vector(poly.parent().gens())
            F = L.zero()
            for g in self:
                F += poly(*g.matrix()*vector(poly.parent().gens()))
            F /= self.order()
            return F
        # non-trivial character case
        K = chi.values()[0].parent()
        if R.characteristic() == 0:
            from sage.rings.qqbar import QQbar

            # extend base_ring to compositum
            if C == QQbar or K == QQbar or R == QQbar:
                L = QQbar
            elif not C.is_absolute() or not K.is_absolute() or not R.is_absolute():
                raise NotImplementedError("only implemented for absolute fields")
            else:
                fields = []
                for M in [R,K,C]:
                    if M.absolute_degree() != 1:
                        fields.append(M)
                l = len(fields)
                if l == 0:
                    # all are QQ
                    L = R
                elif l == 1:
                    # only one is an extension
                    L = fields[0]
                elif l == 2:
                    # only two are extensions
                    L = fields[0].composite_fields(fields[1])[0]
                else:
                    # all three are extensions
                    L1 = fields[0].composite_fields(fields[1])[0]
                    L = L1.composite_fields(fields[2])[0]
        else:
            raise NotImplementedError("nontrivial characters not implemented for characteristic > 0")
        poly = poly.change_ring(L)
        poly_gens = vector(poly.parent().gens())
        F = L.zero()
        for g in self:
            F += L(chi(g)) * poly(*g.matrix().change_ring(L)*poly_gens)
        F /= self.order()
        try:  # attempt to move F to base_ring of polynomial
            F = F.change_ring(R)
        except (TypeError, ValueError):
            pass
        return F

    def invariants_of_degree(self, deg, chi=None, R=None):
        r"""
        Return the (relative) invariants of given degree for this group.

        For this group, compute the invariants of degree ``deg``
        with respect to the group character ``chi``. The method
        is to project each possible monomial of degree ``deg`` via
        the Reynolds operator. Note that if the polynomial ring ``R``
        is specified it's base ring may be extended if the resulting
        invariant is defined over a bigger field.

        INPUT:

        - ``degree`` -- a positive integer

        - ``chi`` -- (default: trivial character) a linear group character of this group

        - ``R`` -- (optional) a polynomial ring

        OUTPUT: list of polynomials

        EXAMPLES::

            sage: # needs sage.groups sage.rings.number_field
            sage: Gr = MatrixGroup(SymmetricGroup(2))
            sage: sorted(Gr.invariants_of_degree(3))
            [x0^2*x1 + x0*x1^2, x0^3 + x1^3]
            sage: R.<x,y> = QQ[]
            sage: sorted(Gr.invariants_of_degree(4, R=R))
            [x^2*y^2, x^3*y + x*y^3, x^4 + y^4]

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: R.<x,y,z> = QQ[]
            sage: Gr = MatrixGroup(DihedralGroup(3))
            sage: ct = Gr.character_table()
            sage: chi = Gr.character(ct[0])
            sage: all(f(*(g.matrix()*vector(R.gens()))) == chi(g)*f
            ....: for f in Gr.invariants_of_degree(3, R=R, chi=chi) for g in Gr)
            True

        ::

            sage: i = GF(7)(3)
            sage: G = MatrixGroup([[i^3,0,0,-i^3],[i^2,0,0,-i^2]])
            sage: G.invariants_of_degree(25)                                            # needs sage.rings.number_field
            []

        ::

            sage: # needs sage.groups
            sage: G = MatrixGroup(SymmetricGroup(5))
            sage: R = QQ['x,y']
            sage: G.invariants_of_degree(3, R=R)
            Traceback (most recent call last):
            ...
            TypeError: number of variables in polynomial ring must match size of matrices

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: K.<i> = CyclotomicField(4)
            sage: G =  MatrixGroup(CyclicPermutationGroup(3))
            sage: chi = G.character(G.character_table()[1])
            sage: R.<x,y,z> = K[]
            sage: sorted(G.invariants_of_degree(2, R=R, chi=chi))
            [x*y + (-2*izeta3^3 - 3*izeta3^2 - 8*izeta3 - 4)*x*z
                 + (2*izeta3^3 + 3*izeta3^2 + 8*izeta3 + 3)*y*z,
             x^2 + (2*izeta3^3 + 3*izeta3^2 + 8*izeta3 + 3)*y^2
                 + (-2*izeta3^3 - 3*izeta3^2 - 8*izeta3 - 4)*z^2]

        ::

            sage: # needs sage.groups sage.rings.number_field
            sage: S3 = MatrixGroup(SymmetricGroup(3))
            sage: chi = S3.character(S3.character_table()[0])
            sage: sorted(S3.invariants_of_degree(5, chi=chi))
            [x0^3*x1^2 - x0^2*x1^3 - x0^3*x2^2 + x1^3*x2^2 + x0^2*x2^3 - x1^2*x2^3,
             x0^4*x1 - x0*x1^4 - x0^4*x2 + x1^4*x2 + x0*x2^4 - x1*x2^4]
        """
        D = self.degree()
        deg = int(deg)
        if deg <= 0:
            raise ValueError("degree must be a positive integer")
        if R is None:
            R = PolynomialRing(self.base_ring(), 'x', D)
        elif R.ngens() != D:
            raise TypeError("number of variables in polynomial ring must match size of matrices")

        ms = self.molien_series(prec=deg+1,chi=chi)
        if ms[deg].is_zero():
            return []
        inv = set()
        for e in IntegerVectors(deg, D):
            F = self.reynolds_operator(R.monomial(*e), chi=chi)
            if not F.is_zero() and _new_invariant_is_linearly_independent((F := F/F.lc()), inv):
                inv.add(F)
                if len(inv) == ms[deg]:
                    break
        return list(inv)

def _new_invariant_is_linearly_independent(F, invariants):
    """
    EXAMPLES::

        sage: gens = [matrix(QQ, [[-1,1],[-1,0]]), matrix(QQ, [[0,1],[1,0]])]
        sage: G = MatrixGroup(gens)
        sage: s = Sequence(G.invariants_of_degree(14))                                  # needs sage.rings.number_field
        sage: s.coefficient_matrix()[0].rank()                                          # needs sage.rings.number_field
        3
        sage: len(s)                                                                    # needs sage.rings.number_field
        3
    """
    if len(invariants) == 0:
        return True
    return PolynomialSequence(invariants).coefficient_matrix()[0].rank() != PolynomialSequence(list(invariants)+[F]).coefficient_matrix()[0].rank()
