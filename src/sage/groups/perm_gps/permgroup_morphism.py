# sage_setup: distribution = sagemath-gap
r"""
Permutation group homomorphisms

AUTHORS:

- David Joyner (2006-03-21): first version

- David Joyner (2008-06): fixed kernel and image to return a group,
  instead of a string.

EXAMPLES::

    sage: G = CyclicPermutationGroup(4)
    sage: H = DihedralGroup(4)
    sage: g = G([(1,2,3,4)])
    sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
    sage: phi.image(G)
    Subgroup generated by [(1,2,3,4)] of
     (Dihedral group of order 8 as a permutation group)
    sage: phi.kernel()
    Subgroup generated by [()] of (Cyclic group of order 4 as a permutation group)
    sage: phi.image(g)
    (1,2,3,4)
    sage: phi(g)
    (1,2,3,4)
    sage: phi.codomain()
    Dihedral group of order 8 as a permutation group
    sage: phi.codomain()
    Dihedral group of order 8 as a permutation group
    sage: phi.domain()
    Cyclic group of order 4 as a permutation group
"""

# ****************************************************************************
#       Copyright (C) 2006 David Joyner and William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from sage.categories.morphism import Morphism
from sage.groups.perm_gps.permgroup import PermutationGroup, PermutationGroup_generic


class PermutationGroupMorphism(Morphism):
    r"""
    A set-theoretic map between PermutationGroups.
    """
    def _repr_type(self):
        r"""
        Return the type of this morphism.

        This is used for printing the morphism.

        EXAMPLES::

            sage: G = PSL(2,7)
            sage: D, iota1, iota2, pr1, pr2 = G.direct_product(G)
            sage: pr1._repr_type()
            'Permutation group'
        """
        return "Permutation group"

    def kernel(self):
        r"""
        Return the kernel of this homomorphism as a permutation group.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: g = G([(1,2,3,4)])
            sage: phi = PermutationGroupMorphism_im_gens(G, H, [1])
            sage: phi.kernel()
            Subgroup generated by [(1,2,3,4)] of
             (Cyclic group of order 4 as a permutation group)

        ::

            sage: G = PSL(2,7)
            sage: D = G.direct_product(G)
            sage: H = D[0]
            sage: pr1 = D[3]
            sage: G.is_isomorphic(pr1.kernel())
            True
        """
        return self.domain().subgroup(gap_group=self._gap_().Kernel())

    def image(self, J):
        r"""
        Compute the subgroup of the codomain `H` which is the image of `J`.

        `J` must be a subgroup of the domain `G`.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: g = G([(1,2,3,4)])
            sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
            sage: phi.image(G)
            Subgroup generated by [(1,2,3,4)] of
             (Dihedral group of order 8 as a permutation group)
            sage: phi.image(g)
            (1,2,3,4)

        ::

            sage: G = PSL(2,7)
            sage: D = G.direct_product(G)
            sage: H = D[0]
            sage: pr1 = D[3]
            sage: pr1.image(G)
            Subgroup generated by [(3,7,5)(4,8,6), (1,2,6)(3,4,8)] of
             (The projective special linear group of degree 2 over Finite Field of size 7)
            sage: G.is_isomorphic(pr1.image(G))
            True

        Check that :trac:`28324` is fixed::

            sage: # needs sage.rings.number_field
            sage: R.<x> = QQ[]
            sage: f = x^4 + x^2 - 3
            sage: L.<a> = f.splitting_field()
            sage: G = L.galois_group()
            sage: D4 = DihedralGroup(4)
            sage: h = D4.isomorphism_to(G)
            sage: h.image(D4).is_isomorphic(G)
            True
            sage: all(h.image(g) in G for g in D4.gens())
            True
        """
        H = self.codomain()
        if J in self.domain():
            J = PermutationGroup([J])
            G = self._gap_().Image(J)
            return H.subgroup(gap_group=G).gens()[0]
        else:
            G = self._gap_().Image(J)
            return H.subgroup(gap_group=G)

    def __call__(self, g):
        r"""
        Some python code for wrapping GAP's ``Images`` function but only for
        permutation groups. This raises an error if g is not in G.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
            sage: g = G([(1,3),(2,4)]); g
            (1,3)(2,4)
            sage: phi(g)
            (1,3)(2,4)
        """
        return self.image(g)


class PermutationGroupMorphism_id(PermutationGroupMorphism):
    pass


class PermutationGroupMorphism_from_gap(PermutationGroupMorphism):
    def __init__(self, G, H, gap_hom):
        r"""
        This is a Python trick to allow Sage programmers to create a group
        homomorphism using GAP using very general constructions. An example
        of its usage is in the direct_product instance method of the
        :class:`PermutationGroup_generic` class in permgroup.py.

        Basic syntax:

        ``PermutationGroupMorphism_from_gap(domain_group,
        range_group, 'phi:=gap_hom_command;', 'phi')``. And don't forget the
        line: ``from sage.groups.perm_gps.permgroup_morphism import
        PermutationGroupMorphism_from_gap`` in your program.

        EXAMPLES::

            sage: from sage.groups.perm_gps.permgroup_morphism import PermutationGroupMorphism_from_gap
            sage: G = PermutationGroup([[(1,2),(3,4)], [(1,2,3,4)]])
            sage: H = G.subgroup([G([(1,2,3,4)])])
            sage: PermutationGroupMorphism_from_gap(H, G, gap.Identity)
            Permutation group morphism:
              From: Subgroup generated by [(1,2,3,4)] of
                    (Permutation Group with generators [(1,2)(3,4), (1,2,3,4)])
              To:   Permutation Group with generators [(1,2)(3,4), (1,2,3,4)]
              Defn: Identity
        """
        if not all(isinstance(X, PermutationGroup_generic) for X in [G, H]):
            raise TypeError("the groups must be permutation groups")
        PermutationGroupMorphism.__init__(self, G, H)
        self._gap_hom = gap_hom

    def _repr_defn(self):
        r"""
        Return the definition of this morphism.

        This is used when printing the morphism.

        EXAMPLES::

            sage: from sage.groups.perm_gps.permgroup_morphism import PermutationGroupMorphism_from_gap
            sage: G = PermutationGroup([[(1,2),(3,4)], [(1,2,3,4)]])
            sage: H = G.subgroup([G([(1,2,3,4)])])
            sage: phi = PermutationGroupMorphism_from_gap(H, G, gap.Identity)
            sage: phi._repr_defn()
            'Identity'
        """
        return str(self._gap_hom).replace('\n', '')

    def _gap_(self, gap=None):
        r"""
        Return a GAP version of this morphism.

        EXAMPLES::

            sage: from sage.groups.perm_gps.permgroup_morphism import PermutationGroupMorphism_from_gap
            sage: G = PermutationGroup([[(1,2),(3,4)], [(1,2,3,4)]])
            sage: H = G.subgroup([G([(1,2,3,4)])])
            sage: phi = PermutationGroupMorphism_from_gap(H, G, gap.Identity)
            sage: phi._gap_()
            Identity
        """
        return self._gap_hom

    def __call__(self, g):
        r"""
        Some python code for wrapping GAP's Images function but only for
        permutation groups. This returns an error if g is not in G.

        EXAMPLES::

            sage: G = PSL(2,7)
            sage: D = G.direct_product(G)
            sage: H = D[0]
            sage: pr1 = D[3]
            sage: [pr1(g) for g in G.gens()]
            [(3,7,5)(4,8,6), (1,2,6)(3,4,8)]
        """
        return self.codomain()(self._gap_().Image(g))


class PermutationGroupMorphism_im_gens(PermutationGroupMorphism):
    def __init__(self, G, H, gens=None):
        r"""
        Some python code for wrapping GAP's ``GroupHomomorphismByImages``
        function but only for permutation groups. Can be expensive if G is
        large. This returns "fail" if gens does not generate self or if the map
        does not extend to a group homomorphism, self - other.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens())); phi
            Permutation group morphism:
              From: Cyclic group of order 4 as a permutation group
              To:   Dihedral group of order 8 as a permutation group
              Defn: [(1,2,3,4)] -> [(1,2,3,4)]
            sage: g = G([(1,3),(2,4)]); g
            (1,3)(2,4)
            sage: phi(g)
            (1,3)(2,4)
            sage: images = ((4,3,2,1),)
            sage: phi = PermutationGroupMorphism_im_gens(G, G, images)
            sage: g = G([(1,2,3,4)]); g
            (1,2,3,4)
            sage: phi(g)
            (1,4,3,2)

        AUTHORS:

        - David Joyner (2006-02)
        """
        if not all(isinstance(X, PermutationGroup_generic) for X in [G, H]):
            raise TypeError("the groups must be permutation groups")
        PermutationGroupMorphism.__init__(self, G, H)
        self._images = [H(img) for img in gens]

    def _repr_defn(self):
        r"""
        Return the definition of this morphism.

        This is used when printing the morphism.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
            sage: phi._repr_defn()
            '[(1,2,3,4)] -> [(1,2,3,4)]'
        """
        return "%s -> %s" % (list(self.domain().gens()), self._images)

    def _gap_(self):
        r"""
        Return a GAP representation of this morphism.

        EXAMPLES::

            sage: G = CyclicPermutationGroup(4)
            sage: H = DihedralGroup(4)
            sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
            sage: phi._gap_()
            GroupHomomorphismByImages( Group( [ (1,2,3,4) ] ), Group(
            [ (1,2,3,4), (1,4)(2,3) ] ), [ (1,2,3,4) ], [ (1,2,3,4) ] )
        """
        return self.domain()._gap_().GroupHomomorphismByImages(self.codomain(), self.domain().gens(), self._images)


def is_PermutationGroupMorphism(f) -> bool:
    r"""
    Return ``True`` if the argument ``f`` is a :class:`PermutationGroupMorphism`.

    EXAMPLES::

        sage: from sage.groups.perm_gps.permgroup_morphism import is_PermutationGroupMorphism
        sage: G = CyclicPermutationGroup(4)
        sage: H = DihedralGroup(4)
        sage: phi = PermutationGroupMorphism_im_gens(G, H, map(H, G.gens()))
        sage: is_PermutationGroupMorphism(phi)
        True
    """
    return isinstance(f, PermutationGroupMorphism)
