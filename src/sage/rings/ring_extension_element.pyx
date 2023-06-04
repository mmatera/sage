r"""
Elements lying in extension of rings

AUTHOR:

- Xavier Caruso (2019)
"""

# ###########################################################################
#    Copyright (C) 2019 Xavier Caruso <xavier.caruso@normalesup.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#                  https://www.gnu.org/licenses/
# ***************************************************************************


from sage.ext.stdsage cimport PY_NEW
from sage.cpython.getattr cimport AttributeErrorMessage
from sage.cpython.getattr import dir_with_other_class
from sage.misc.latex import latex

from sage.structure.category_object import normalize_names
from sage.structure.element cimport CommutativeAlgebraElement
from sage.rings.integer_ring import ZZ
from sage.categories.fields import Fields
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing

from sage.rings.ring_extension cimport RingExtension_generic, RingExtensionWithGen, RingExtensionFractionField
from sage.rings.ring_extension_morphism cimport MapRelativeRingToFreeModule
from sage.rings.ring_extension_conversion cimport backend_parent, backend_element
from sage.rings.ring_extension_conversion cimport to_backend, from_backend


# Classes
#########

cdef class RingExtensionElement(CommutativeAlgebraElement):
    r"""
    Generic class for elements lying in ring extensions.

    TESTS::

        sage: K = GF(5^4).over()                                                        # optional - sage.rings.finite_rings
        sage: x = K.random_element()                                                    # optional - sage.rings.finite_rings
        sage: TestSuite(x).run()                                                        # optional - sage.rings.finite_rings

    """
    def __init__(self, RingExtension_generic parent, x, *args, **kwds):
        r"""
        Initialize this element.

        INPUT:

        - ``parent`` -- the parent of this element

        - ``x`` -- some data to construct this element

        TESTS::

            sage: Q = QQ.over(ZZ)
            sage: x = Q(1/2)
            sage: x
            1/2
        """
        if not isinstance(parent, RingExtension_generic):
            raise TypeError("%s is not a ring extension" % parent)
        x = backend_element(x)
        try:
            parentx = x.parent()
            if parent._base.has_coerce_map_from(parentx):
                x = parent._base.coerce_map_from(parentx)(x)
                x = parent._backend_defining_morphism(x)
        except AttributeError:
            pass
        CommutativeAlgebraElement.__init__(self, parent)
        ring = parent._backend
        self._backend = ring(x, *args, **kwds)

    def __reduce__(self):
        """
        Return a tuple of a function and data that can be used to unpickle this
        element.

        TESTS::

            sage: K = GF(5^3).over()                                                    # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: type(x)                                                               # optional - sage.rings.finite_rings
            <class 'sage.rings.ring_extension_element.RingExtensionWithBasisElement'>
            sage: loads(dumps(x)) == x                                                  # optional - sage.rings.finite_rings
            True
        """
        return self._parent, (self._backend,)

    def __getattr__(self, name):
        """
        If the parent of this element was created with ``import_methods = True``,
        return a wrapper to the corresponding method of the backend element
        (if it exists).

        EXAMPLES::

            sage: x = polygen(ZZ, 'x')
            sage: A.<a> = QQ.extension(x^2 - 2)                                         # optional - sage.rings.number_field
            sage: K.<a> = A.over()  # over QQ                                           # optional - sage.rings.number_field

            sage: hasattr(a, 'continued_fraction')                                      # optional - sage.rings.number_field
            True
            sage: a.continued_fraction()                                                # optional - sage.rings.number_field
            [1; (2)*]
        """
        try:
            return self.getattr_from_category(name)
        except AttributeError:
            pass
        method = None
        if (<RingExtension_generic>self._parent)._import_methods and hasattr(self._backend, name):
            method = getattr(self._backend, name)
        if not callable(method):
            raise AttributeError(AttributeErrorMessage(self, name))

        def wrapper(*args, **kwargs):
            output = method(*to_backend(args), **to_backend(kwargs))
            return from_backend(output, self._parent)
        wrapper.__doc__ = method.__doc__
        return wrapper

    def __dir__(self):
        """
        Return the list of all the attributes of this element;
        if the parent of this element was created with ``import_methods = True``,
        concatenate this list with the list of all the methods of the backend
        element.

        EXAMPLES::

            sage: x = polygen(ZZ, 'x')
            sage: A.<a> = QQ.extension(x^2 - 2)                                         # optional - sage.rings.number_field
            sage: K.<a> = A.over()                                                      # optional - sage.rings.number_field

            sage: dir(a)                                                                # optional - sage.rings.number_field
            ['__abs__',
             '__add__',
             ...
             'complex_embeddings',
             'conjugate',
             'continued_fraction',
             'continued_fraction_list',
             ...
             'trace',
             'valuation',
             'vector',
             'xgcd']
        """
        d = dir_with_other_class(self, self._parent.category().element_class)
        if not (<RingExtension_generic>self._parent)._import_methods:
            return d
        for name in dir(self._backend):
            try:
                attribute = getattr(self._backend, name)
                if callable(attribute):
                    d.append(name)
            except AttributeError:
                pass
        return sorted(set(d))

    def __hash__(self):
        """
        Return a hash of this element.

        EXAMPLES:

            sage: E.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: hash(a)                                                               # optional - sage.rings.finite_rings
            5
        """
        return hash(self._backend)

    def _repr_(self, **options):
        r"""
        Return a string representation of this element.

        Do not override this method in subclasses;
        instead override the method :meth:`_repr_extension`.

        TESTS::

            sage: K.<a> = GF(5^2).over()                                                # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^4).over(K)                                               # optional - sage.rings.finite_rings
            sage: b._repr_()                                                            # optional - sage.rings.finite_rings
            'b'
        """
        cdef RingExtension_generic parent = self._parent
        if 'print_elements_as' in options:
            print_as = options.pop('print_elements_as')
        else:
            print_as = parent._print_options.get('print_elements_as')
        if print_as is not None:
            return print_as(self._backend)._repr_(**options)
        print_options = parent._print_options.copy()
        for (name, value) in options.items():
            method = None
            if hasattr(parent, '_print_option_' + name):
                method = getattr(parent, '_print_option_' + name)
            if not callable(method):
                raise ValueError("option '%s' does not exist" % name)
            print_options[name] = method(value)
        return self._repr_extension(**print_options)

    def _repr_extension(self, **options):
        r"""
        Return a string representation of this element.

        TESTS::

            sage: K = QQ.over(ZZ)
            sage: x = K(1/2)
            sage: x._repr_extension()
            '1/2'
        """
        return str(self._backend)

    def _latex_(self, **options):
        r"""
        Return a LaTeX representation of this element.

        Do not override this method in subclasses;
        instead override the method :meth:`_latex_extension`.

        TESTS::

            sage: K.<a> = GF(5^2).over()                                                # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^4).over(K)                                               # optional - sage.rings.finite_rings
            sage: b._latex_()                                                           # optional - sage.rings.finite_rings
            'b'
        """
        cdef RingExtension_generic parent = self._parent
        if 'print_elements_as' in options:
            print_as = options.pop('print_elements_as')
        else:
            print_as = parent._print_options.get('print_elements_as')
        if print_as is not None:
            return print_as(self._backend)._latex_(**options)
        print_options = parent._print_options.copy()
        for (name, value) in options.items():
            method = None
            if hasattr(parent, '_print_option_' + name):
                method = getattr(parent, '_print_option_' + name)
            if not callable(method):
                raise ValueError("option '%s' does not exist" % name)
            print_options[name] = method(value)
        return self._latex_extension(**print_options)

    def _latex_extension(self, **options):
        r"""
        Return a LaTeX representation of this element.

        TESTS::

            sage: K = QQ.over(ZZ)
            sage: x = K(1/2)
            sage: x._latex_extension()
            \frac{1}{2}
        """
        return latex(self._backend)

    cpdef _richcmp_(left, right, int op):
        r"""
        Compare this element with ``right`` according to
        the rich comparison operator ``op``.

        The comparison is performed by comparing the backend
        elements.

        INPUT:

        - ``right`` -- an element in the same parent

        - ``op`` -- the comparison operator

        EXAMPLES::

            sage: K.<a> = GF(5^2).over()                                                # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: x == x                                                                # optional - sage.rings.finite_rings
            True
            sage: x == x + 1                                                            # optional - sage.rings.finite_rings
            False
            sage: x == x^25                                                             # optional - sage.rings.finite_rings
            True
        """
        return left._backend._richcmp_(backend_element(right), op)

    cpdef _add_(self,other):
        r"""
        Return the sum of this element and ``other``.

        TESTS::

            sage: K = GF(5^4).over(GF(5^2))                                             # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: y = K.random_element()                                                # optional - sage.rings.finite_rings

            sage: (x+y).parent() is K                                                   # optional - sage.rings.finite_rings
            True
            sage: x + y == y + x                                                        # optional - sage.rings.finite_rings
            True
        """
        cdef RingExtensionElement ans = PY_NEW(type(self))
        ans._parent = self._parent
        ans._backend = self._backend + (<RingExtensionElement>other)._backend
        return ans

    cpdef _neg_(self):
        r"""
        Return the opposite of this element.

        TESTS::

            sage: K = GF(5^4).over(GF(5^2))                                             # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings

            sage: y = -x                                                                # optional - sage.rings.finite_rings
            sage: y.parent() is K                                                       # optional - sage.rings.finite_rings
            True
            sage: x + y == 0                                                            # optional - sage.rings.finite_rings
            True
        """
        cdef RingExtensionElement ans = PY_NEW(type(self))
        ans._parent = self._parent
        ans._backend = -self._backend
        return ans

    cpdef _sub_(self,other):
        r"""
        Return the difference of this element and ``other``.

        TESTS::

            sage: K = GF(5^4).over(GF(5^2))                                             # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: y = K.random_element()                                                # optional - sage.rings.finite_rings

            sage: (x-y).parent() is K                                                   # optional - sage.rings.finite_rings
            True
            sage: x - y == x + (-y)                                                     # optional - sage.rings.finite_rings
            True
        """
        cdef RingExtensionElement ans = PY_NEW(type(self))
        ans._parent = self._parent
        ans._backend = self._backend - (<RingExtensionElement>other)._backend
        return ans

    cpdef _mul_(self,other):
        r"""
        Return the product of this element and ``other``.

        TESTS::

            sage: K = GF(5^4).over(GF(5^2))                                             # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: y = K.random_element()                                                # optional - sage.rings.finite_rings

            sage: (x*y).parent() is K                                                   # optional - sage.rings.finite_rings
            True
            sage: x * y == y * x                                                        # optional - sage.rings.finite_rings
            True
        """
        cdef RingExtensionElement ans = PY_NEW(type(self))
        ans._parent = self._parent
        ans._backend = self._backend * (<RingExtensionElement>other)._backend
        return ans

    cpdef _div_(self,other):
        r"""
        Return the quotient of this element by ``other``,
        considered as an element of the fraction field.

        TESTS::

            sage: x = polygen(ZZ, 'x')
            sage: A.<a> = ZZ.extension(x^2 - 2)                                         # optional - sage.rings.number_field
            sage: OK = A.over()                                                         # optional - sage.rings.number_field
            sage: a = OK(a)                                                             # optional - sage.rings.number_field

            sage: b = 1/a; b                                                            # optional - sage.rings.number_field
            a/2
            sage: b.parent()                                                            # optional - sage.rings.number_field
            Fraction Field of
             Order in Number Field in a with defining polynomial x^2 - 2 over its base
            sage: a*b                                                                   # optional - sage.rings.number_field
            1
        """
        cdef RingExtensionElement ans
        cdef RingExtension_generic parent = self._parent
        if parent._fraction_field is None:
            parent._fraction_field = parent.fraction_field()
            parent._fraction_field_type = <type>parent._fraction_field.element_class
        ans = PY_NEW(parent._fraction_field_type)
        ans._parent = parent._fraction_field
        ans._backend = self._backend / (<RingExtensionElement>other)._backend
        return ans

    def additive_order(self):
        r"""
        Return the additive order of this element.

        EXAMPLES::

            sage: K.<a> = GF(5^4).over(GF(5^2))                                         # optional - sage.rings.finite_rings
            sage: a.additive_order()                                                    # optional - sage.rings.finite_rings
            5
        """
        return self._backend.additive_order()

    def multiplicative_order(self):
        r"""
        Return the multiplicite order of this element.

        EXAMPLES::

            sage: K.<a> = GF(5^4).over(GF(5^2))                                         # optional - sage.rings.finite_rings
            sage: a.multiplicative_order()                                              # optional - sage.rings.finite_rings
            624
        """
        return self._backend.multiplicative_order()

    def is_unit(self):
        r"""
        Return whether if this element is a unit in this ring.

        EXAMPLES::

            sage: A.<x> = PolynomialRing(QQ)
            sage: E = A.over(QQ)
            sage: E(4).is_unit()
            True
            sage: E(x).is_unit()
            False
        """
        return self._backend.is_unit()

    def is_nilpotent(self):
        r"""
        Return whether if this element is nilpotent in this ring.

        EXAMPLES::

            sage: A.<x> = PolynomialRing(QQ)
            sage: E = A.over(QQ)
            sage: E(0).is_nilpotent()
            True
            sage: E(x).is_nilpotent()
            False
        """
        return self._backend.is_nilpotent()

    def is_prime(self):
        r"""
        Return whether this element is a prime element in this ring.

        EXAMPLES::

            sage: A.<x> = PolynomialRing(QQ)
            sage: E = A.over(QQ)
            sage: E(x^2+1).is_prime()
            True
            sage: E(x^2-1).is_prime()
            False
        """
        return self._backend.is_prime()

    def is_square(self, root=False):
        r"""
        Return whether this element is a square in this ring.

        INPUT:

        - ``root`` -- a boolean (default: ``False``); if ``True``,
          return also a square root

        EXAMPLES::

            sage: K.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: a.is_square()                                                         # optional - sage.rings.finite_rings
            False
            sage: a.is_square(root=True)                                                # optional - sage.rings.finite_rings
            (False, None)

            sage: b = a + 1                                                             # optional - sage.rings.finite_rings
            sage: b.is_square()                                                         # optional - sage.rings.finite_rings
            True
            sage: b.is_square(root=True)                                                # optional - sage.rings.finite_rings
            (True, 2 + 3*a + a^2)
        """
        is_sq = self._backend.is_square()
        sq = None
        if root and is_sq:
            sq = self.sqrt(extend=False, all=False)
        if root:
            return is_sq, sq
        else:
            return is_sq

    def sqrt(self, extend=True, all=False, name=None):
        r"""
        Return a square root or all square roots of this element.

        INPUT:

        - ``extend`` -- a boolean (default: ``True``); if "True",
          return a square root in an extension ring, if necessary.
          Otherwise, raise a :class:`ValueError` if the root is not in
          the ring

        - ``all`` -- a boolean (default: ``False``); if ``True``,
          return all square roots of this element, instead of just one.

        - ``name`` -- Required when ``extend=True`` and ``self`` is not a
          square. This will be the name of the generator extension.

        .. NOTE::

            The option ``extend=True`` is often not implemented.

        EXAMPLES::

            sage: K.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: b = a + 1                                                             # optional - sage.rings.finite_rings
            sage: b.sqrt()                                                              # optional - sage.rings.finite_rings
            2 + 3*a + a^2
            sage: b.sqrt(all=True)                                                      # optional - sage.rings.finite_rings
            [2 + 3*a + a^2, 3 + 2*a - a^2]
        """
        sq = self._backend.sqrt(extend=extend, all=all)
        if all:
            gen = sq[0]
        else:
            gen = sq
        parent = self._parent
        backend_parent = gen.parent()
        if backend_parent is not (<RingExtension_generic>parent)._backend:
            from sage.rings.ring_extension import RingExtension
            if name is None:
                raise ValueError("you must specify a variable name")
            names = normalize_names(1, name)
            constructor = (RingExtensionWithGen,
                           {'gen': gen, 'name': names[0], 'is_backend_exposed': False})
            parent = RingExtension(backend_parent, parent, (gen,), names, constructors=[constructor])
        if all:
            return [ parent(s) for s in sq ]
        else:
            return parent(sq)


# Fraction fields
#################

cdef class RingExtensionFractionFieldElement(RingExtensionElement):
    r"""
    A class for elements lying in fraction fields of ring extensions.

    TESTS::

        sage: Z = ZZ.over()
        sage: Q = Z.fraction_field()
        sage: x = Q.random_element()
        sage: type(x)
        <class 'sage.rings.ring_extension_element.RingExtensionFractionFieldElement'>
        sage: TestSuite(x).run()
    """
    def __hash__(self):
        """
        Return a hash of this element.

        EXAMPLES:

            sage: E.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: hash(a)                                                               # optional - sage.rings.finite_rings
            5
        """
        return hash(self._backend)

    def _repr_extension(self, **options):
        r"""
        Return a string representation of this element.

        TESTS::

            sage: Z = ZZ.over()
            sage: Q = Z.fraction_field()
            sage: x = Q(1/2)
            sage: x._repr_extension()
            '1/2'
            sage: R = QQ['x'].over()
            sage: K = R.fraction_field()
            sage: x = R.gen()
            sage: (x^2 + 1) / (x^2 - 1)
            (x^2 + 1)/(x^2 - 1)
            sage: x / (x + 1)
            x/(x + 1)
            sage: (x + 1)/(-x)
            (-x - 1)/x
        """
        num = self.numerator()
        denom = self.denominator()
        if denom == 1:
            sd = ""
        elif denom == -1:
            num = -num
            sd = ""
        elif denom._is_atomic():
            sd = "/%s" % denom
        elif (-denom)._is_atomic():
            sd = "/%s" % (-denom)
            num = -num
        else:
            sd = "/(%s)" % denom
        if num._is_atomic():
            return "%s%s" % (num, sd)
        else:
            return "(%s)%s" % (num, sd)

    def _latex_extension(self, **options):
        r"""
        Return a LaTeX representation of this element.

        TESTS::

            sage: Z = ZZ.over()
            sage: Q = Z.fraction_field()
            sage: x = Q(1/2)
            sage: x._latex_extension()
            '\\frac{1}{2}'
        """
        num = self.numerator()
        denom = self.denominator()
        if denom == -1:
            denom = 1
            num = -num
        if isinstance((<RingExtensionFractionField>self._parent)._ring, RingExtension_generic):
            snum = num._latex_(**options)
            sdenom = denom._latex_(**options)
        else:
            snum = latex(num)
            sdenom = latex(denom)
        if denom == 1:
            return snum
        else:
            return "\\frac{%s}{%s}" % (snum, sdenom)

    def numerator(self):
        r"""
        Return the numerator of this element.

        EXAMPLES::

            sage: x = polygen(ZZ, 'x')
            sage: A.<a> = ZZ.extension(x^2 - 2)                                         # optional - sage.rings.number_field
            sage: OK = A.over()  # over ZZ                                              # optional - sage.rings.number_field
            sage: K = OK.fraction_field(); K                                            # optional - sage.rings.number_field
            Fraction Field of Order in Number Field in a
             with defining polynomial x^2 - 2 over its base

            sage: x = K(1/a); x                                                         # optional - sage.rings.number_field
            a/2
            sage: num = x.numerator(); num                                              # optional - sage.rings.number_field
            a

        The numerator is an element of the ring which was used
        to construct the fraction field::

            sage: num.parent()                                                          # optional - sage.rings.number_field
            Order in Number Field in a with defining polynomial x^2 - 2 over its base
            sage: num.parent() is OK                                                    # optional - sage.rings.number_field
            True

        TESTS::

            sage: x = K.random_element()                                                # optional - sage.rings.number_field
            sage: x == x.numerator() / x.denominator()                                  # optional - sage.rings.number_field
            True
        """
        ring = (<RingExtensionFractionField>self._parent)._ring
        num = self._backend.numerator()
        return ring(num)

    def denominator(self):
        r"""
        Return the denominator of this element.

        EXAMPLES::

            sage: R.<x> = ZZ[]
            sage: A.<a> = ZZ.extension(x^2 - 2)                                         # optional - sage.rings.number_field
            sage: OK = A.over()  # over ZZ                                              # optional - sage.rings.number_field
            sage: K = OK.fraction_field(); K                                            # optional - sage.rings.number_field
            Fraction Field of Order in Number Field in a
             with defining polynomial x^2 - 2 over its base

            sage: x = K(1/a); x                                                         # optional - sage.rings.number_field
            a/2
            sage: denom = x.denominator(); denom                                        # optional - sage.rings.number_field
            2

        The denominator is an element of the ring which was used
        to construct the fraction field::

            sage: denom.parent()                                                        # optional - sage.rings.number_field
            Order in Number Field in a with defining polynomial x^2 - 2 over its base
            sage: denom.parent() is OK                                                  # optional - sage.rings.number_field
            True

        TESTS::

            sage: x = K.random_element()                                                # optional - sage.rings.number_field
            sage: x == x.numerator() / x.denominator()                                  # optional - sage.rings.number_field
            True
        """
        ring = (<RingExtensionFractionField>self._parent)._ring
        denom = self._backend.denominator()
        return ring(denom)


# Finite free extensions
########################

cdef class RingExtensionWithBasisElement(RingExtensionElement):
    r"""
    A class for elements lying in finite free extensions.

    TESTS::

        sage: K.<a> = GF(5^3).over()                                                    # optional - sage.rings.finite_rings
        sage: L.<b> = GF(5^9).over(K)                                                   # optional - sage.rings.finite_rings
        sage: type(b)                                                                   # optional - sage.rings.finite_rings
        <class 'sage.rings.ring_extension_element.RingExtensionWithBasisElement'>
        sage: TestSuite(b).run()                                                        # optional - sage.rings.finite_rings
    """
    def __hash__(self):
        """
        Return a hash of this element.

        EXAMPLES:

            sage: E.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: hash(a)                                                               # optional - sage.rings.finite_rings
            5
        """
        return hash(self._backend)

    def _repr_extension(self, base, **options):
        r"""
        Return a string representation of this element written as
        a linear combination over ``base`` in the basis provided by
        the method :meth:`basis_over`.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: K.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^9).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = 1/(a+b)                                                           # optional - sage.rings.finite_rings

            sage: u._repr_extension(base=K)                                             # optional - sage.rings.finite_rings
            '(2 + 2*a) + (-1 + a - a^2)*b + (2 + 3*a + 3*a^2)*b^2'
            sage: u._repr_extension(base=GF(5))                                         # optional - sage.rings.finite_rings
            '2 + 2*a - b + a*b - a^2*b + 2*b^2 + 3*a*b^2 + 3*a^2*b^2'
        """
        cdef RingExtensionWithBasis parent = self._parent
        coeffs = self._vector(base)
        names = parent._basis_names
        b = parent._base
        while b is not base:
            new_names = [ ]
            for y in names:
                for x in (<RingExtensionWithBasis>b)._basis_names:
                    if x == "":
                        new_names.append(y)
                    elif y == "":
                        new_names.append(x)
                    else:
                        new_names.append(x + "*" + y)
            names = new_names
            b = (<RingExtensionWithBasis>b)._base
        s = ""
        for i in range(len(names)):
            c = coeffs[i]
            if c.is_zero():
                continue
            sign = 1
            ss = ""
            if c == -1:
                sign = -1
            elif c != 1:
                atomic = c._is_atomic()
                if not atomic and (-c)._is_atomic():
                    c = -c
                    sign = -sign
                    atomic = True
                sc = str(c)
                if atomic:
                    ss += sc
                else:
                    ss += "(" + sc + ")"
                if names[i] != "":
                    ss += "*"
            if ss and ss[0] == "-":
                ss = ss[1:]
                sign *= -1
            if s == "":
                if sign == -1:
                    s = "-"
            else:
                s += " + " if sign == 1 else " - "
            ss += names[i]
            if ss == "":
                ss += "1"
            s += ss
        if s == "":
            return "0"
        if s[0] == "(" and s[-1] == ")":
            s = s[1:-1]
        return s

    def _latex_extension(self, base, **options):
        r"""
        Return a LaTeX representation of this element written as
        a linear combination over ``base`` in the basis provided by
        the method :meth:`basis_over`.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: K.<a> = GF(5^3).over()                                                # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^9).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = 1/(a+b)                                                           # optional - sage.rings.finite_rings

            sage: u._latex_extension(base=K)                                            # optional - sage.rings.finite_rings
            \left( 2 + 2 a \right) + \left( -1 + a - a^{2} \right) b + \left( 2 + 3 a + 3 a^{2} \right) b^{2}
            sage: u._latex_extension(base=GF(5))                                        # optional - sage.rings.finite_rings
            2 + 2 a - b + ab - a^{2}b + 2 b^{2} + 3 ab^{2} + 3 a^{2}b^{2}
        """
        cdef RingExtensionWithBasis parent = self._parent
        coeffs = self._vector(base)
        names = parent._basis_latex_names
        b = parent._base
        while b is not base:
            names = [ x + y for y in names for x in (<RingExtensionWithBasis>b)._basis_latex_names ]
            b = (<RingExtensionWithBasis>b)._base
        s = ""
        for i in range(len(names)):
            c = coeffs[i]
            if c.is_zero():
                continue
            sign = 1
            ss = ""
            if c == -1:
                sign = -1
            elif c != 1:
                atomic = c._is_atomic()
                if not atomic and (-c)._is_atomic():
                    c = -c
                    sign = -sign
                    atomic = True
                sc = latex(c)
                if atomic:
                    ss += sc
                else:
                    ss += r"\left(" + sc + r"\right)"
            if ss != "" and ss[0] == "-":
                ss = ss[1:]
                sign *= -1
            if s == "":
                if sign == -1:
                    s = "-"
            else:
                s += " + " if sign == 1 else " - "
            ss += names[i]
            if ss == "":
                ss += "1"
            s += ss
        if s == "":
            return "0"
        if s[:6] == r"\left(" and s[-7] == r"\right)":
            s = s[6:-7]
        return s

    def vector(self, base=None):
        r"""
        Return the vector of coordinates of this element over ``base``
        (in the basis output by the method :meth:`basis_over`).

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F = GF(5)                                                             # optional - sage.rings.finite_rings
            sage: K.<a> = GF(5^2).over()  # over F                                      # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: x = (a+b)^4; x                                                        # optional - sage.rings.finite_rings
            (-1 + a) + (3 + a)*b + (1 - a)*b^2

            sage: x.vector(K)  # basis is (1, b, b^2)                                   # optional - sage.rings.finite_rings
            (-1 + a, 3 + a, 1 - a)

            sage: x.vector(F)  # basis is (1, a, b, a*b, b^2, a*b^2)                    # optional - sage.rings.finite_rings
            (4, 1, 3, 1, 1, 4)

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: x.vector()                                                            # optional - sage.rings.finite_rings
            (-1 + a, 3 + a, 1 - a)

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: x.vector(GF(5^3))                                                     # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z3 of size 5^3
        """
        base = (<RingExtension_generic>self._parent)._check_base(base)
        return self._vector(base)

    cdef _vector(self, CommutativeRing base):
        r"""
        Return the vector of coordinates of this element over ``base``
        (in the basis output by the method :meth:`basis_over`).

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        TESTS::

            sage: K = GF(11^10).over(GF(11^2))                                          # optional - sage.rings.finite_rings
            sage: x = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: coeffs = x.vector()                                                   # optional - sage.rings.finite_rings
            sage: basis = K.basis_over()                                                # optional - sage.rings.finite_rings
            sage: x == sum(coeffs[i]*basis[i] for i in range(5))                        # optional - sage.rings.finite_rings
            True
        """
        _, _, j = (<RingExtensionWithBasis>self._parent)._free_module(base, map=True)
        return j(self)

    def polynomial(self, base=None, var='x'):
        r"""
        Return a polynomial (in one or more variables) over ``base``
        whose evaluation at the generators of the parent equals this
        element.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F.<a> = GF(5^2).over()  # over GF(5)                                  # optional - sage.rings.finite_rings
            sage: K.<b> = GF(5^4).over(F)                                               # optional - sage.rings.finite_rings
            sage: L.<c> = GF(5^12).over(K)                                              # optional - sage.rings.finite_rings
            sage: u = 1/(a + b + c); u                                                  # optional - sage.rings.finite_rings
            (2 + (-1 - a)*b) + ((2 + 3*a) + (1 - a)*b)*c + ((-1 - a) - a*b)*c^2

            sage: P = u.polynomial(K); P                                                # optional - sage.rings.finite_rings
            ((-1 - a) - a*b)*x^2 + ((2 + 3*a) + (1 - a)*b)*x + 2 + (-1 - a)*b
            sage: P.base_ring() is K                                                    # optional - sage.rings.finite_rings
            True
            sage: P(c) == u                                                             # optional - sage.rings.finite_rings
            True

        When the base is `F`, we obtain a bivariate polynomial::

            sage: P = u.polynomial(F); P                                                # optional - sage.rings.finite_rings
            (-a)*x0^2*x1 + (-1 - a)*x0^2 + (1 - a)*x0*x1 + (2 + 3*a)*x0 + (-1 - a)*x1 + 2

        We check that its value at the generators is the element we started with::

            sage: L.gens(F)                                                             # optional - sage.rings.finite_rings
            (c, b)
            sage: P(c, b) == u                                                          # optional - sage.rings.finite_rings
            True

        Similarly, when the base is ``GF(5)``, we get a trivariate polynomial:

            sage: P = u.polynomial(GF(5)); P                                            # optional - sage.rings.finite_rings
            -x0^2*x1*x2 - x0^2*x2 - x0*x1*x2 - x0^2 + x0*x1 - 2*x0*x2 - x1*x2 + 2*x0 - x1 + 2
            sage: P(c, b, a) == u                                                       # optional - sage.rings.finite_rings
            True

        Different variable names can be specified::

            sage: u.polynomial(GF(5), var='y')                                          # optional - sage.rings.finite_rings
            -y0^2*y1*y2 - y0^2*y2 - y0*y1*y2 - y0^2 + y0*y1 - 2*y0*y2 - y1*y2 + 2*y0 - y1 + 2
            sage: u.polynomial(GF(5), var=['x','y','z'])                                # optional - sage.rings.finite_rings
            -x^2*y*z - x^2*z - x*y*z - x^2 + x*y - 2*x*z - y*z + 2*x - y + 2

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.polynomial()                                                        # optional - sage.rings.finite_rings
            ((-1 - a) - a*b)*x^2 + ((2 + 3*a) + (1 - a)*b)*x + 2 + (-1 - a)*b

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.polynomial(GF(5^3))                                                 # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z3 of size 5^3
        """
        base = self._parent._check_base(base)
        degrees = [ ]
        b = self._parent
        degree = 1
        while b is not base:
            if not isinstance(b, RingExtensionWithGen):
                raise NotImplementedError
            reldeg = b.relative_degree()
            degree *= reldeg
            degrees.append(reldeg)
            b = b.base_ring()
        degrees.reverse()
        coeffs = { }
        v = self._vector(base)
        S = PolynomialRing(base, len(degrees), names=var)
        for i in range(degree):
            ii = ZZ(i)
            exponents = [ ]
            for d in degrees:
                ii, exponent = ii.quo_rem(d)
                exponents.append(exponent)
            coeffs[tuple(reversed(exponents))] = v[i]
        return S(coeffs)

    def matrix(self, base=None):
        r"""
        Return the matrix of the multiplication by this element (in
        the basis output by :meth:`basis_over`).

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: K.<a> = GF(5^3).over()  # over GF(5)                                  # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = a/(1+b)                                                           # optional - sage.rings.finite_rings

            sage: u                                                                     # optional - sage.rings.finite_rings
            (2 + a + 3*a^2) + (3 + 3*a + a^2)*b
            sage: b*u                                                                   # optional - sage.rings.finite_rings
            (3 + 2*a^2) + (2 + 2*a - a^2)*b
            sage: u.matrix(K)                                                           # optional - sage.rings.finite_rings
            [2 + a + 3*a^2 3 + 3*a + a^2]
            [    3 + 2*a^2 2 + 2*a - a^2]

            sage: u.matrix(GF(5))                                                       # optional - sage.rings.finite_rings
            [2 1 3 3 3 1]
            [1 3 1 2 0 3]
            [2 3 3 1 3 0]
            [3 0 2 2 2 4]
            [4 2 0 3 0 2]
            [0 4 2 4 2 0]

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.matrix()                                                            # optional - sage.rings.finite_rings
            [2 + a + 3*a^2 3 + 3*a + a^2]
            [    3 + 2*a^2 2 + 2*a - a^2]

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.matrix(GF(5^2))                                                     # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z2 of size 5^2
        """
        cdef RingExtension_generic parent = self._parent
        base = parent._check_base(base)
        if not (parent._is_finite_over(base) and parent._is_free_over(base)):
            raise ValueError("the extension is not finite free")
        return self._matrix(base)

    cdef _matrix(self, CommutativeRing base):
        r"""
        Return the matrix of the multiplication by this element (in
        the basis output by :meth:`basis_over`).

        This method does not check its input.
        Do not call it directly; use :meth:`matrix` instead.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension)

        TESTS::

            sage: F = GF(11^2)                                                          # optional - sage.rings.finite_rings
            sage: K = GF(11^6).over(F)                                                  # optional - sage.rings.finite_rings
            sage: L = GF(11^18).over(K)                                                 # optional - sage.rings.finite_rings

            sage: for base in L.bases():                                                # optional - sage.rings.finite_rings
            ....:     x = L.random_element()
            ....:     y = L.random_element()
            ....:     assert((x+y).matrix(base) == x.matrix(base) + y.matrix(base))
            ....:     assert((x*y).matrix(base) == x.matrix(base) * y.matrix(base))
        """
        from sage.matrix.matrix_space import MatrixSpace
        cdef RingExtensionWithBasis parent = self._parent
        _, _, j = parent._free_module(base, map=True)
        x = self._backend
        M = [ j(x * (<RingExtensionElement>b)._backend) for b in parent._basis_over(base) ]
        return MatrixSpace(base, len(M))(M)

    def trace(self, base=None):
        r"""
        Return the trace of this element over ``base``.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F = GF(5)                                                             # optional - sage.rings.finite_rings
            sage: K.<a> = GF(5^3).over(F)                                               # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = a/(1+b)                                                           # optional - sage.rings.finite_rings

            sage: tr = u.trace(K); tr                                                   # optional - sage.rings.finite_rings
            -1 + 3*a + 2*a^2

        We check that the trace lives in the base ring::

            sage: tr.parent()                                                           # optional - sage.rings.finite_rings
            Field in a with defining polynomial x^3 + 3*x + 3 over its base
            sage: tr.parent() is K                                                      # optional - sage.rings.finite_rings
            True

        Similarly, one can compute the trace over F::

            sage: u.trace(F)                                                            # optional - sage.rings.finite_rings
            0

        We check the transitivity of the trace::

            sage: u.trace(F) == tr.trace(F)                                             # optional - sage.rings.finite_rings
            True

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.trace()                                                             # optional - sage.rings.finite_rings
            -1 + 3*a + 2*a^2

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.trace(GF(5^2))                                                      # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z2 of size 5^2
        """
        cdef RingExtension_generic parent = self._parent
        base = parent._check_base(base)
        if not (parent._is_finite_over(base) and parent._is_free_over(base)):
            raise ValueError("the extension is not finite free")
        return self._trace(base)

    cdef _trace(self, CommutativeRing base):
        r"""
        Return the trace of this element over ``base``.

        This method does not check its input.
        Do not call it directly; use :meth:`trace` instead.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension)

        TESTS::

            sage: F = GF(11^2)                                                          # optional - sage.rings.finite_rings
            sage: K = GF(11^6).over(F)                                                  # optional - sage.rings.finite_rings
            sage: L = GF(11^18).over(K)                                                 # optional - sage.rings.finite_rings

            sage: x = L.random_element()                                                # optional - sage.rings.finite_rings
            sage: x.trace(F) == x.trace().trace()                                       # optional - sage.rings.finite_rings
            True

            sage: for base in L.bases():                                                # optional - sage.rings.finite_rings
            ....:     x = L.random_element()
            ....:     y = L.random_element()
            ....:     assert(x.trace(base) == x.matrix(base).trace())
            ....:     assert((x+y).trace(base) == x.trace(base) + y.trace(base))
        """
        cdef RingExtensionWithBasis parent = self._parent
        cdef CommutativeRing b
        if base is parent:
            return self
        b = parent._base
        t = self._matrix(b).trace()
        if base is b:
            return t
        return (<RingExtensionWithBasisElement>t)._trace(base)

    def norm(self, base=None):
        r"""
        Return the norm of this element over ``base``.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F = GF(5)                                                             # optional - sage.rings.finite_rings
            sage: K.<a> = GF(5^3).over(F)                                               # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = a/(1+b)                                                           # optional - sage.rings.finite_rings

            sage: nr = u.norm(K); nr                                                    # optional - sage.rings.finite_rings
            3 + 2*a^2

        We check that the norm lives in the base ring::

            sage: nr.parent()                                                           # optional - sage.rings.finite_rings
            Field in a with defining polynomial x^3 + 3*x + 3 over its base
            sage: nr.parent() is K                                                      # optional - sage.rings.finite_rings
            True

        Similarly, one can compute the norm over F::

            sage: u.norm(F)                                                             # optional - sage.rings.finite_rings
            4

        We check the transitivity of the norm::

            sage: u.norm(F) == nr.norm(F)                                               # optional - sage.rings.finite_rings
            True

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.norm()                                                              # optional - sage.rings.finite_rings
            3 + 2*a^2

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.norm(GF(5^2))                                                       # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z2 of size 5^2
        """
        cdef RingExtension_generic parent = self._parent
        base = parent._check_base(base)
        if not (parent._is_finite_over(base) and parent._is_free_over(base)):
            raise ValueError("the extension is not finite free")
        return self._norm(base)

    cdef _norm(self, CommutativeRing base):
        r"""
        Return the norm of this element over ``base``.

        This method does not check its input.
        Do not call it directly; use :meth:`norm` instead.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension)

        TESTS::

            sage: F = GF(11^2)                                                          # optional - sage.rings.finite_rings
            sage: K = GF(11^6).over(F)                                                  # optional - sage.rings.finite_rings
            sage: L = GF(11^18).over(K)                                                 # optional - sage.rings.finite_rings

            sage: x = L.random_element()                                                # optional - sage.rings.finite_rings
            sage: x.norm(F) == x.norm().norm()                                          # optional - sage.rings.finite_rings
            True

            sage: for base in L.bases():                                                # optional - sage.rings.finite_rings
            ....:     x = L.random_element()
            ....:     y = L.random_element()
            ....:     assert(x.norm(base) == x.matrix(base).determinant())
            ....:     assert((x*y).norm(base) == x.norm(base) * y.norm(base))
        """
        cdef RingExtensionWithBasis parent = self._parent
        cdef CommutativeRing b
        if base is parent:
            return self
        b = parent._base
        n = self._matrix(b).determinant()
        if base is b:
            return n
        return (<RingExtensionWithBasisElement>n)._norm(base)

    def charpoly(self, base=None, var='x'):
        r"""
        Return the characteristic polynomial of this element over ``base``.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F = GF(5)                                                             # optional - sage.rings.finite_rings
            sage: K.<a> = GF(5^3).over(F)                                               # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = a/(1+b)                                                           # optional - sage.rings.finite_rings

            sage: chi = u.charpoly(K); chi                                              # optional - sage.rings.finite_rings
            x^2 + (1 + 2*a + 3*a^2)*x + 3 + 2*a^2

        We check that the charpoly has coefficients in the base ring::

            sage: chi.base_ring()                                                       # optional - sage.rings.finite_rings
            Field in a with defining polynomial x^3 + 3*x + 3 over its base
            sage: chi.base_ring() is K                                                  # optional - sage.rings.finite_rings
            True

        and that it annihilates u::

            sage: chi(u)                                                                # optional - sage.rings.finite_rings
            0

        Similarly, one can compute the characteristic polynomial over F::

            sage: u.charpoly(F)                                                         # optional - sage.rings.finite_rings
            x^6 + x^4 + 2*x^3 + 3*x + 4

        A different variable name can be specified::

            sage: u.charpoly(F, var='t')                                                # optional - sage.rings.finite_rings
            t^6 + t^4 + 2*t^3 + 3*t + 4

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.charpoly()                                                          # optional - sage.rings.finite_rings
            x^2 + (1 + 2*a + 3*a^2)*x + 3 + 2*a^2

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.charpoly(GF(5^2))                                                   # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z2 of size 5^2

        TESTS:

        We check that the characteristic polynomial of an element in the base
        ring is a power of a polynomial of degree 1::

            sage: S.<x> = K[]                                                           # optional - sage.rings.finite_rings
            sage: u = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: L(u).charpoly() == (x - u)^2                                          # optional - sage.rings.finite_rings
            True
        """
        return self.matrix(base).charpoly(var)

    cpdef minpoly(self, base=None, var='x'):
        r"""
        Return the minimal polynomial of this element over ``base``.

        INPUT:

        - ``base`` -- a commutative ring (which might be itself an
          extension) or ``None``

        EXAMPLES::

            sage: F = GF(5)                                                             # optional - sage.rings.finite_rings
            sage: K.<a> = GF(5^3).over(F)                                               # optional - sage.rings.finite_rings
            sage: L.<b> = GF(5^6).over(K)                                               # optional - sage.rings.finite_rings
            sage: u = 1 / (a+b)                                                         # optional - sage.rings.finite_rings

            sage: chi = u.minpoly(K); chi                                               # optional - sage.rings.finite_rings
            x^2 + (2*a + a^2)*x - 1 + a

        We check that the minimal polynomial has coefficients in the base ring::

            sage: chi.base_ring()                                                       # optional - sage.rings.finite_rings
            Field in a with defining polynomial x^3 + 3*x + 3 over its base
            sage: chi.base_ring() is K                                                  # optional - sage.rings.finite_rings
            True

        and that it annihilates u::

            sage: chi(u)                                                                # optional - sage.rings.finite_rings
            0

        Similarly, one can compute the minimal polynomial over F::

            sage: u.minpoly(F)                                                          # optional - sage.rings.finite_rings
            x^6 + 4*x^5 + x^4 + 2*x^2 + 3

        A different variable name can be specified::

            sage: u.minpoly(F, var='t')                                                 # optional - sage.rings.finite_rings
            t^6 + 4*t^5 + t^4 + 2*t^2 + 3

        If ``base`` is omitted, it is set to its default which is the
        base of the extension::

            sage: u.minpoly()                                                           # optional - sage.rings.finite_rings
            x^2 + (2*a + a^2)*x - 1 + a

        Note that ``base`` must be an explicit base over which the
        extension has been defined (as listed by the method :meth:`bases`)::

            sage: u.minpoly(GF(5^2))                                                    # optional - sage.rings.finite_rings
            Traceback (most recent call last):
            ...
            ValueError: not (explicitly) defined over Finite Field in z2 of size 5^2

        TESTS:

        We check that the minimal polynomial of an element in the base
        ring has degree 1::

            sage: S.<x> = K[]                                                           # optional - sage.rings.finite_rings
            sage: u = K.random_element()                                                # optional - sage.rings.finite_rings
            sage: L(u).minpoly() == x - u                                               # optional - sage.rings.finite_rings
            True

        In a similar fashion, the minimal polynomial over `F` of an element
        of `K` should have degree 1 or 3::

            sage: L(u).minpoly(F).degree() in [ 1, 3 ]                                  # optional - sage.rings.finite_rings
            True
        """
        cdef RingExtensionWithBasis parent = self._parent

        if base is None:
            mod = parent.modulus()
            S = mod.parent().quotient(mod)
            try:
                return S(list(self.vector())).minpoly()
            except NotImplementedError:
                pass  # fall back to generic code below

        from sage.modules.free_module import FreeModule
        cdef MapRelativeRingToFreeModule j

        base = parent._check_base(base)
        if not (parent._is_finite_over(base) and parent._is_free_over(base)):
            raise ValueError("the extension is not finite free")
        if base not in Fields():
            raise NotImplementedError("minpoly is only implemented when the base is a field")
        K = backend_parent(base)
        degree = parent._degree_over(base)
        _, _, j = parent._free_module(base, map=True)
        V = FreeModule(K, degree)
        vector = [K(1)] + (degree-1)*[K(0)]
        vectors = [vector]
        W = V.span(vectors)
        elt = self
        while True:
            vector = V(j.backend_coefficients(elt))
            if vector in W: break
            vectors.append(vector)
            W += V.span([vector])
            elt *= self
        W = V.span_of_basis(vectors)
        coeffs = [ -c for c in W.coordinate_vector(vector) ] + [K(1)]
        return PolynomialRing(base, name=var)(coeffs)
