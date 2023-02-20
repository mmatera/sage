r"""
Base class for old-style parent objects with generators

.. NOTE::

   This class is being deprecated, see
   ``sage.structure.parent.Parent`` and
   ``sage.structure.category_object.CategoryObject`` for the new
   model.

Many parent objects in Sage are equipped with generators, which are
special elements of the object.  For example, the polynomial ring
`\ZZ[x,y,z]` is generated by `x`, `y`, and `z`.  In Sage the `i^{th}`
generator of an object ``X`` is obtained using the notation
``X.gen(i)``.  From the Sage interactive prompt, the shorthand
notation ``X.i`` is also allowed.

REQUIRED: A class that derives from ParentWithGens *must* define
the ngens() and gen(i) methods.

OPTIONAL: It is also good if they define gens() to return all gens,
but this is not necessary.

The ``gens`` function returns a tuple of all generators, the
``ngens`` function returns the number of generators.

The ``_assign_names`` functions is for internal use only, and is
called when objects are created to set the generator names.  It can
only be called once.

The following examples illustrate these functions in the context of
multivariate polynomial rings and free modules.

EXAMPLES::

    sage: R = PolynomialRing(ZZ, 3, 'x')
    sage: R.ngens()
    3
    sage: R.gen(0)
    x0
    sage: R.gens()
    (x0, x1, x2)
    sage: R.variable_names()
    ('x0', 'x1', 'x2')

This example illustrates generators for a free module over `\ZZ`.

::

    sage: M = FreeModule(ZZ, 4)
    sage: M
    Ambient free module of rank 4 over the principal ideal domain Integer Ring
    sage: M.ngens()
    4
    sage: M.gen(0)
    (1, 0, 0, 0)
    sage: M.gens()
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
"""

# ****************************************************************************
#       Copyright (C) 2005, 2006 William Stein <wstein@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ****************************************************************************

from . import gens_py
cimport sage.structure.parent as parent
from sage.structure.coerce_dict cimport MonoDict
cimport sage.structure.category_object as category_object


cdef inline check_old_coerce(parent.Parent p):
    if p._element_constructor is not None:
        raise RuntimeError("%s still using old coercion framework" % p)


cdef class ParentWithGens(ParentWithBase):
    # Derived class *must* call __init__ and set the base!
    def __init__(self, base, names=None, normalize=True, category=None):
        """
        EXAMPLES::

            sage: from sage.structure.parent_gens import ParentWithGens
            sage: class MyParent(ParentWithGens):
            ....:     def ngens(self): return 3
            sage: P = MyParent(base=QQ, names='a,b,c', normalize=True, category=Groups())
            sage: P.category()
            Category of groups
            sage: P._names
            ('a', 'b', 'c')
        """
        self._base = base
        self._assign_names(names=names, normalize=normalize)

        ParentWithBase.__init__(self, base, category=category)

    # Derived class *must* define ngens method.
    def ngens(self):
        check_old_coerce(self)
        raise NotImplementedError("Number of generators not known.")

    # Derived class *must* define gen method.
    def gen(self, i=0):
        check_old_coerce(self)
        raise NotImplementedError("i-th generator not known.")

    def gens(self):
        """
        Return a tuple whose entries are the generators for this
        object, in order.
        """
        cdef int i
        if self._gens is not None:
            return self._gens
        self._gens = tuple(self.gen(i) for i in range(self.ngens()))
        return self._gens

    def _assign_names(self, names=None, normalize=True):
        """
        Set the names of the generator of this object.

        This can only be done once because objects with generators
        are immutable, and is typically done during creation of the object.


        EXAMPLES:

        When we create this polynomial ring, self._assign_names is called by the constructor:

        ::

            sage: R = QQ['x,y,abc']; R
            Multivariate Polynomial Ring in x, y, abc over Rational Field
            sage: R.2
            abc

        We can't rename the variables::

            sage: R._assign_names(['a','b','c'])
            Traceback (most recent call last):
            ...
            ValueError: variable names cannot be changed after object creation.
        """
        if self._element_constructor is not None:
            return parent.Parent._assign_names(self, names=names, normalize=normalize)
        if names is None: return
        if normalize:
            names = category_object.normalize_names(self.ngens(), names)
        if self._names is not None and names != self._names:
            raise ValueError('variable names cannot be changed after object creation.')
        if isinstance(names, str):
            names = (names, )  # make it a tuple
        elif not isinstance(names, tuple):
            raise TypeError("names must be a tuple of strings")
        self._names = names

    #################################################################################
    # Give all objects with generators a dictionary, so that attribute setting
    # works.   It would be nice if this functionality were standard in Pyrex,
    # i.e., just define __dict__ as an attribute and all this code gets generated.
    #################################################################################
    def __getstate__(self):
        if self._element_constructor is not None:
            return parent.Parent.__getstate__(self)
        d = []
        try:
            d = list(self.__dict__.copy().iteritems()) # so we can add elements
        except AttributeError:
            pass
        d = dict(d)
        d['_base'] = self._base
        d['_gens'] = self._gens
        d['_list'] = self._list
        d['_names'] = self._names
        d['_latex_names'] = self._latex_names

        return d

    def __setstate__(self, d):
        if '_element_constructor' in d:
            return parent.Parent.__setstate__(self, d)
        try:
            self.__dict__.update(d)
        except (AttributeError,KeyError):
            pass
        self._base = d['_base']
        self._gens = d['_gens']
        self._list = d['_list']
        self._names = d['_names']
        self._latex_names = d['_latex_names']


    #################################################################################
    # Morphisms of objects with generators
    #################################################################################

    def hom(self, im_gens, codomain=None, base_map=None, category=None, check=True):
        r"""
        Return the unique homomorphism from self to codomain that
        sends ``self.gens()`` to the entries of ``im_gens``
        and induces the map ``base_map`` on the base ring.
        Raises a TypeError if there is no such homomorphism.

        INPUT:

        - ``im_gens`` -- the images in the codomain of the generators of
          this object under the homomorphism

        - ``codomain`` -- the codomain of the homomorphism

        - ``base_map`` -- a map from the base ring of the domain into something
          that coerces into the codomain

        - ``category`` -- the category of the resulting morphism

        - ``check`` -- whether to verify that the images of generators extend
          to define a map (using only canonical coercions)

        OUTPUT:

        - a homomorphism self --> codomain

        .. NOTE::

           As a shortcut, one can also give an object X instead of
           ``im_gens``, in which case return the (if it exists)
           natural map to X.

        EXAMPLES: Polynomial Ring
        We first illustrate construction of a few homomorphisms
        involving a polynomial ring.

        ::

            sage: R.<x> = PolynomialRing(ZZ)
            sage: f = R.hom([5], QQ)
            sage: f(x^2 - 19)
            6

            sage: R.<x> = PolynomialRing(QQ)
            sage: f = R.hom([5], GF(7))                                                 # optional - sage.libs.pari
            Traceback (most recent call last):
            ...
            ValueError: relations do not all (canonically) map to 0 under map determined by images of generators

            sage: R.<x> = PolynomialRing(GF(7))                                         # optional - sage.libs.pari
            sage: f = R.hom([3], GF(49, 'a'))                                           # optional - sage.libs.pari
            sage: f                                                                     # optional - sage.libs.pari
            Ring morphism:
              From: Univariate Polynomial Ring in x over Finite Field of size 7
              To:   Finite Field in a of size 7^2
              Defn: x |--> 3
            sage: f(x + 6)                                                              # optional - sage.libs.pari
            2
            sage: f(x^2 + 1)                                                            # optional - sage.libs.pari
            3

        EXAMPLES: Natural morphism

        ::

            sage: f = ZZ.hom(GF(5))                                                     # optional - sage.libs.pari
            sage: f(7)                                                                  # optional - sage.libs.pari
            2
            sage: f                                                                     # optional - sage.libs.pari
            Natural morphism:
              From: Integer Ring
              To:   Finite Field of size 5

        There might not be a natural morphism, in which case a TypeError exception is raised.

        ::

            sage: QQ.hom(ZZ)
            Traceback (most recent call last):
            ...
            TypeError: natural coercion morphism from Rational Field to Integer Ring not defined

        You can specify a map on the base ring::

            sage: k = GF(2)                                                             # optional - sage.libs.pari
            sage: R.<a> = k[]                                                           # optional - sage.libs.pari
            sage: l.<a> = k.extension(a^3 + a^2 + 1)                                    # optional - sage.libs.pari
            sage: R.<b> = l[]                                                           # optional - sage.libs.pari
            sage: m.<b> = l.extension(b^2 + b + a)                                      # optional - sage.libs.pari
            sage: n.<z> = GF(2^6)                                                       # optional - sage.libs.pari
            sage: m.hom([z^4 + z^3 + 1], base_map=l.hom([z^5 + z^4 + z^2]))             # optional - sage.libs.pari
            Ring morphism:
              From: Univariate Quotient Polynomial Ring in b over Finite Field in a of size 2^3 with modulus b^2 + b + a
              To:   Finite Field in z of size 2^6
              Defn: b |--> z^4 + z^3 + 1
                    with map of base ring
        """
        if self._element_constructor is not None:
            return parent.Parent.hom(self, im_gens, codomain, base_map=base_map, category=category, check=check)
        if isinstance(im_gens, parent.Parent):
            return self.Hom(im_gens).natural_map()
        if codomain is None:
            from sage.structure.all import Sequence
            im_gens = Sequence(im_gens)
            codomain = im_gens.universe()
        kwds = {}
        if check is not None:
            kwds['check'] = check
        if base_map is not None:
            kwds['base_map'] = base_map
        Hom_kwds = {} if category is None else {'category': category}
        return self.Hom(codomain, **Hom_kwds)(im_gens, **kwds)


cdef class localvars:
    r"""
    Context manager for safely temporarily changing the variables
    names of an object with generators.

    Objects with named generators are globally unique in Sage.
    Sometimes, though, it is very useful to be able to temporarily
    display the generators differently.   The new Python ``with``
    statement and the localvars context manager make this easy and
    safe (and fun!)

    Suppose X is any object with generators.  Write

    ::

        with localvars(X, names[, latex_names] [,normalize=False]):
             some code
             ...

    and the indented code will be run as if the names in X are changed
    to the new names.  If you give normalize=True, then the names are
    assumed to be a tuple of the correct number of strings.

    EXAMPLES::

        sage: R.<x,y> = PolynomialRing(QQ,2)
        sage: with localvars(R, 'z,w'):
        ....:     print(x^3 + y^3 - x*y)
        z^3 + w^3 - z*w

    .. NOTE::

       I wrote this because it was needed to print elements of the
       quotient of a ring R by an ideal I using the print function for
       elements of R.  See the code in
       ``quotient_ring_element.pyx``.

    AUTHOR:

    - William Stein (2006-10-31)
    """
    cdef object _obj
    cdef object _names
    cdef object _latex_names
    cdef object _orig

    def __init__(self, obj, names, latex_names=None, normalize=True):
        self._obj = obj
        if normalize:
            self._names = category_object.normalize_names(obj.ngens(), names)
            self._latex_names = latex_names
        else:
            self._names = names
            self._latex_names = latex_names

    def __enter__(self):
        self._orig = self._obj.__temporarily_change_names(self._names, self._latex_names)

    def __exit__(self, type, value, traceback):
        self._obj.__temporarily_change_names(self._orig[0], self._orig[1])
