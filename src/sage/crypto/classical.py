r"""
Classical Cryptosystems

A convenient user interface to various classical ciphers. These include:

- Hill or matrix cipher; see :class:`HillCryptosystem`
- shift cipher; see :class:`ShiftCryptosystem`
- substitution cipher; see :class:`SubstitutionCryptosystem`
- transposition cipher; see :class:`TranspositionCryptosystem`
- Vigenere cipher; see :class:`VigenereCryptosystem`

These classical cryptosystems support alphabets such as:

- the capital letters of the English alphabet; see
  :func:`AlphabeticStrings() <sage.monoids.string_monoid.AlphabeticStrings>`
- the hexadecimal number system; see
  :func:`HexadecimalStrings() <sage.monoids.string_monoid.HexadecimalStrings>`
- the binary number system; see
  :func:`BinaryStrings() <sage.monoids.string_monoid.BinaryStrings>`
- the octal number system; see
  :func:`OctalStrings() <sage.monoids.string_monoid.OctalStrings>`
- the radix-64 number system; see
  :func:`Radix64Strings() <sage.monoids.string_monoid.Radix64Strings>`

AUTHORS:

- David Kohel (2007): initial version with the Hill, substitution,
  transposition, and Vigenere cryptosystems.

- Minh Van Nguyen (2009-08): shift cipher
"""

#*****************************************************************************
#       Copyright (C) 2007 David Kohel <kohel@maths.usyd.edu.au>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# TODO: check off this todo list:
# - implement the affine cipher
# - methods for cryptanalysis of the affine cipher
# - methods to cryptanalyze the Hill, substitution, transposition, and
#   Vigenere ciphers

from sage.monoids.string_monoid import (
    StringMonoid_class,
    AlphabeticStringMonoid)
from sage.monoids.string_monoid_element import StringMonoidElement
from sage.monoids.string_ops import strip_encoding
from sage.groups.perm_gps.permgroup_named import SymmetricGroup
from sage.groups.perm_gps.permgroup_element import PermutationGroupElement
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ
from sage.rings.integer_mod_ring import IntegerModRing
from sage.rings.arith import xgcd
from random import randint
from sage.matrix.matrix_space import MatrixSpace

from cryptosystem import SymmetricKeyCryptosystem
from classical_cipher import (
     HillCipher,
     ShiftCipher,
     SubstitutionCipher,
     TranspositionCipher,
     VigenereCipher)

class HillCryptosystem(SymmetricKeyCryptosystem):
    """
    Create a Hill cryptosystem defined by the `m` x `m` matrix space
    over `\ZZ / N \ZZ`, where `N` is the alphabet size of
    the string monoid ``S``.

    INPUT:

    - ``S`` - a string monoid over some alphabet

    - ``m`` - integer `> 0`; the block length of matrices that specify
      block permutations

    OUTPUT:

    - A Hill cryptosystem of block length ``m`` over the alphabet ``S``.

    EXAMPLES::

        sage: S = AlphabeticStrings()
        sage: E = HillCryptosystem(S,3)
        sage: E
        Hill cryptosystem on Free alphabetic string monoid on A-Z of block length 3
        sage: R = IntegerModRing(26)
        sage: M = MatrixSpace(R,3,3)
        sage: A = M([[1,0,1],[0,1,1],[2,2,3]])
        sage: A
        [1 0 1]
        [0 1 1]
        [2 2 3]
        sage: e = E(A)
        sage: e
        Hill cipher on Free alphabetic string monoid on A-Z of block length 3
        sage: e(S("LAMAISONBLANCHE"))
        JYVKSKQPELAYKPV

    TESTS::

        sage: S = AlphabeticStrings()
        sage: E = HillCryptosystem(S,3)
        sage: E == loads(dumps(E))
        True
    """

    def __init__(self, S, m):
        """
        See ``HillCryptosystem`` for full documentation.

        Create a Hill cryptosystem defined by the `m` x `m` matrix space
        over `\ZZ / N \ZZ`, where `N` is the alphabet size of
        the string monoid ``S``.

        INPUT:

        - ``S`` - a string monoid over some alphabet

        - ``m`` - integer `> 0`; the block length of matrices that specify
          block permutations

        OUTPUT:

        - A Hill cryptosystem of block length ``m`` over the alphabet ``S``.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = HillCryptosystem(S,3)
            sage: E
            Hill cryptosystem on Free alphabetic string monoid on A-Z of block length 3
        """
        if not isinstance(S, StringMonoid_class):
            raise TypeError("S (= %s) must be a string monoid." % S)
        R = IntegerModRing(S.ngens())
        M = MatrixSpace(R, m, m)
        SymmetricKeyCryptosystem.__init__(self, S, S, M, block_length=m)

    def __call__(self, A):
        """
        Create a Hill cipher.

        INPUT:

        - ``A`` - a matrix which specifies a block permutation

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = HillCryptosystem(S,3)
            sage: E
            Hill cryptosystem on Free alphabetic string monoid on A-Z of block length 3
            sage: M = E.key_space()
            sage: A = M([[1,0,1],[0,1,1],[2,2,3]])
            sage: A
            [1 0 1]
            [0 1 1]
            [2 2 3]
            sage: e = E(A)
            sage: e
            Hill cipher on Free alphabetic string monoid on A-Z of block length 3
            sage: m = S("LAMAISONBLANCHE")
            sage: e(m)
            JYVKSKQPELAYKPV
            sage: c = e.inverse()
            sage: c(e(m))
            LAMAISONBLANCHE
        """
        M = self.key_space()
        m = self.block_length()
        if isinstance(A, list):
            try:
                A = M(A)
            except:
                raise TypeError("A (= %s) must specify a square matrix of degree %s." % (A, m))
        return HillCipher(self, A)

    def _repr_(self):
        """
        Return a string representation of self.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: H = HillCryptosystem(A, 3)
            sage: H
            Hill cryptosystem on Free alphabetic string monoid on A-Z of block length 3
            sage: H._repr_()
            'Hill cryptosystem on Free alphabetic string monoid on A-Z of block length 3'
        """
        return "Hill cryptosystem on %s of block length %s" % (
            self.cipher_domain(), self.block_length())

    def block_length(self):
        """
        The row or column dimension of a matrix specifying a block
        permutation. Encryption and decryption keys of a Hill cipher are
        square matrices, i.e. the row and column dimensions of an encryption
        or decryption key are the same. This row/column dimension is referred
        to as the *block length*.

        OUTPUT:

        - The block length of an encryption/decryption key.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: n = randint(1, A.ngens() - 1)
            sage: H = HillCryptosystem(A, n)
            sage: H.block_length() == n
            True
        """
        return self.key_space().nrows()

    def random_key(self):
        """
        A random key within the key space of this Hill cipher. That is,
        generate a random `m` x `m` matrix to be used as a block
        permutation, where `m` is the block length of this Hill cipher. If
        `n` is the size of the cryptosystem alphabet, then there are
        `n^{m^2}` possible keys. However the number of valid keys,
        i.e. invertible `m` x `m` square matrices, is smaller than
        `n^{m^2}`.

        OUTPUT:

        - A random key within the key space of this Hill cipher.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: n = 3
            sage: H = HillCryptosystem(A, n)
            sage: K = H.random_key()
            sage: Ki = H.inverse_key(K)
            sage: M = "LAMAISONBLANCHE"
            sage: e = H(K)
            sage: d = H(Ki)
            sage: d(e(A(M))) == A(M)
            True
        """
        M = self.key_space()
        R = M.base_ring()
        m = M.nrows()
        N = Integer(self.cipher_domain().ngens())
        while True:
            A = M([ randint(0, N-1) for i in range(m**2) ])
            if N.gcd(A.det()) == 1:
                break
        return A

    def inverse_key(self, A):
        """
        The inverse key corresponding to the key ``A``.

        INPUT:

        - ``A`` - an invertible matrix of the key space of this Hill cipher

        OUTPUT:

        - The inverse matrix of ``A``.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = HillCryptosystem(S,3)
            sage: A = E.random_key()
            sage: B = E.inverse_key(A)
            sage: M = S("LAMAISONBLANCHE")
            sage: e = E(A)
            sage: c = E(B)
            sage: c(e(M))
            LAMAISONBLANCHE
        """
        S = self.plaintext_space()
        M = self.key_space()
        if not A in M:
            raise TypeError("A (= %s) must be a matrix in the key space of %s." % (A, self))
        m = self.block_length()
        MatZZ = MatrixSpace(ZZ, m)
        AZ = MatZZ([ [ A[i, j].lift() for j in range(m) ] for i in range(m) ])
        AZ_adj = AZ.adjoint()
        u, r, s = xgcd(A.det().lift(), S.ngens())
        if u != 1:
            raise ValueError("Argument:\n\n%s\n\nis not invertible." % (A))
        return r * A.parent()(AZ_adj)

    def encoding(self, M):
        """
        The encoding of the string ``M`` over the string monoid of this
        Hill cipher. For example, if the string monoid of this Hill cipher
        is :class:`AlphabeticStringMonoid`, then the encoding of ``M`` would
        be its upper-case equivalent stripped of all non-alphabetic
        characters.

        INPUT:

        - ``M`` - a string, possibly empty

        OUTPUT:

        - The encoding of ``M`` over the string monoid of this Hill cipher.

        EXAMPLES::

            sage: M = "The matrix cipher by Lester S. Hill."
            sage: A = AlphabeticStrings()
            sage: H = HillCryptosystem(A, 7)
            sage: H.encoding(M) == A.encoding(M)
            True
        """
        S = self.cipher_domain()
        if isinstance(S, AlphabeticStringMonoid):
            return S(strip_encoding(M))
        try:
            return S.encoding(M)
        except:
            raise TypeError("Argument M = %s does not encode in the cipher domain" % M)

    def deciphering(self, A, C):
        """
        Decrypt the ciphertext ``C`` using the key ``A``.

        INPUT:

        - ``A`` - a key within the key space of this Hill cipher

        - ``C`` - a string (possibly empty) over the string monoid of this
          Hill cipher

        OUTPUT:

        - The plaintext corresponding to the ciphertext ``C``.

        EXAMPLES::

            sage: H = HillCryptosystem(AlphabeticStrings(), 3)
            sage: K = H.random_key()
            sage: M = H.encoding("Good day, mate! How ya going?")
            sage: H.deciphering(K, H.enciphering(K, M)) == M
            True
        """
        # TODO: some type checking that A is invertible hence a valid key
        i = self(self.inverse_key(A))
        return i(C)

    def enciphering(self, A, M):
        """
        Encrypt the plaintext ``M`` using the key ``A``.

        INPUT:

        - ``A`` - a key within the key space of this Hill cipher

        - ``M`` - a string (possibly empty) over the string monoid of this
          Hill cipher.

        OUTPUT:

        - The ciphertext corresponding to the plaintext ``M``.

        EXAMPLES::

            sage: H = HillCryptosystem(AlphabeticStrings(), 3)
            sage: K = H.random_key()
            sage: M = H.encoding("Good day, mate! How ya going?")
            sage: H.deciphering(K, H.enciphering(K, M)) == M
            True
        """
        # TODO: some type checking that A is invertible hence a valid key
        e = self(A)
        return e(M)

class ShiftCryptosystem(SymmetricKeyCryptosystem):
    r"""
    Create a shift cryptosystem.

    Let `A = \{ a_0, a_1, a_2, \dots, a_{n-1} \}` be a non-empty alphabet
    consisting of `n` unique elements. Define a mapping
    `f : A \longrightarrow \ZZ/ n\ZZ` from the alphabet `A` to
    the set `\ZZ / n\ZZ` of integers modulo `n`, given by
    `f(a_i) = i`. Thus we can identify each element of the alphabet `A`
    with a unique integer `0 \leq i < n`. A key of the shift cipher is an
    integer `0 \leq k < n`. Therefore the key space is `\ZZ / n\ZZ`. Since
    we assume that `A` does not have repeated elements, the mapping
    `f : A \longrightarrow \ZZ/ n\ZZ` is bijective.
    Encryption works by moving along the alphabet by `k` positions, with
    wrap around. Decryption reverses the process by moving backwards by
    `k` positions, with wrap around. More generally, let `k` be a secret key,
    i.e. an element of the key space, and let `p` be a plaintext
    character and consequently `p \in \ZZ / n\ZZ`. Then the ciphertext
    character `c` corresponding to `p` is given by

    .. MATH::

        c \equiv p + k \pmod{n}

    Similarly, given a ciphertext character `c \in \ZZ / n\ZZ` and a secret
    key `k`, we can recover the corresponding plaintext character as follows:

    .. MATH::

        p \equiv c - k \pmod{n}

    Use the bijection `f : A \longrightarrow \ZZ/ n\ZZ` to convert `c`
    and `p` back to elements of the alphabet `A`. Currently, the following
    alphabets are supported for the shift cipher:

    - capital letters of the English alphabet as implemented in
      :func:`AlphabeticStrings()
      <sage.monoids.string_monoid.AlphabeticStrings>`

    - the alphabet consisting of the hexadecimal number system as
      implemented in
      :func:`HexadecimalStrings()
      <sage.monoids.string_monoid.HexadecimalStrings>`

    - the alphabet consisting of the binary number system as implemented in
      :func:`BinaryStrings() <sage.monoids.string_monoid.BinaryStrings>`

    EXAMPLES:

    Some examples illustrating encryption and decryption over various
    alphabets. Here is an example over the upper-case letters of the English
    alphabet::

        sage: S = ShiftCryptosystem(AlphabeticStrings()); S
        Shift cryptosystem on Free alphabetic string monoid on A-Z
        sage: P = S.encoding("The shift cryptosystem generalizes the Caesar cipher.")
        sage: P
        THESHIFTCRYPTOSYSTEMGENERALIZESTHECAESARCIPHER
        sage: K = 7
        sage: C = S.enciphering(K, P); C
        AOLZOPMAJYFWAVZFZALTNLULYHSPGLZAOLJHLZHYJPWOLY
        sage: S.deciphering(K, C)
        THESHIFTCRYPTOSYSTEMGENERALIZESTHECAESARCIPHER
        sage: S.deciphering(K, C) == P
        True

    The previous example can also be done as follows::

        sage: S = ShiftCryptosystem(AlphabeticStrings())
        sage: P = S.encoding("The shift cryptosystem generalizes the Caesar cipher.")
        sage: K = 7
        sage: E = S(K); E
        Shift cipher on Free alphabetic string monoid on A-Z
        sage: C = E(P); C
        AOLZOPMAJYFWAVZFZALTNLULYHSPGLZAOLJHLZHYJPWOLY
        sage: D = S(S.inverse_key(K)); D
        Shift cipher on Free alphabetic string monoid on A-Z
        sage: D(C) == P
        True
        sage: D(C) == P == D(E(P))
        True

    Over the hexadecimal number system::

        sage: S = ShiftCryptosystem(HexadecimalStrings()); S
        Shift cryptosystem on Free hexadecimal string monoid
        sage: P = S.encoding("Encryption & decryption shifts along the alphabet."); P
        456e6372797074696f6e20262064656372797074696f6e2073686966747320616c6f6e672074686520616c7068616265742e
        sage: K = 5
        sage: C = S.enciphering(K, P); C
        9ab3b8c7cec5c9beb4b3757b75b9bab8c7cec5c9beb4b375c8bdbebbc9c875b6b1b4b3bc75c9bdba75b6b1c5bdb6b7bac973
        sage: S.deciphering(K, C)
        456e6372797074696f6e20262064656372797074696f6e2073686966747320616c6f6e672074686520616c7068616265742e
        sage: S.deciphering(K, C) == P
        True

    And over the binary number system::

        sage: S = ShiftCryptosystem(BinaryStrings()); S
        Shift cryptosystem on Free binary string monoid
        sage: P = S.encoding("The binary alphabet is very insecure."); P
        01010100011010000110010100100000011000100110100101101110011000010111001001111001001000000110000101101100011100000110100001100001011000100110010101110100001000000110100101110011001000000111011001100101011100100111100100100000011010010110111001110011011001010110001101110101011100100110010100101110
        sage: K = 1
        sage: C = S.enciphering(K, P); C
        10101011100101111001101011011111100111011001011010010001100111101000110110000110110111111001111010010011100011111001011110011110100111011001101010001011110111111001011010001100110111111000100110011010100011011000011011011111100101101001000110001100100110101001110010001010100011011001101011010001
        sage: S.deciphering(K, C)
        01010100011010000110010100100000011000100110100101101110011000010111001001111001001000000110000101101100011100000110100001100001011000100110010101110100001000000110100101110011001000000111011001100101011100100111100100100000011010010110111001110011011001010110001101110101011100100110010100101110
        sage: S.deciphering(K, C) == P
        True

    A shift cryptosystem with key `k = 3` is commonly referred to as the
    Caesar cipher. Create a Caesar cipher over the upper-case letters of the
    English alphabet::

        sage: caesar = ShiftCryptosystem(AlphabeticStrings())
        sage: K = 3
        sage: P = caesar.encoding("abcdef"); P
        ABCDEF
        sage: C = caesar.enciphering(K, P); C
        DEFGHI
        sage: caesar.deciphering(K, C) == P
        True

    Generate a random key for encryption and decryption::

        sage: S = ShiftCryptosystem(AlphabeticStrings())
        sage: P = S.encoding("Shift cipher with a random key.")
        sage: K = S.random_key()
        sage: C = S.enciphering(K, P)
        sage: S.deciphering(K, C) == P
        True

    Decrypting with the key ``K`` is equivalent to encrypting with its
    corresponding inverse key::

        sage: S.enciphering(S.inverse_key(K), C) == P
        True

    TESTS:

    Currently, the octal number system is not supported as an alphabet for
    this shift cryptosystem::

        sage: ShiftCryptosystem(OctalStrings())
        Traceback (most recent call last):
        ...
        TypeError: A (= Free octal string monoid) is not supported as a cipher domain of this shift cryptosystem.

    Nor is the radix-64 number system supported::

        sage: ShiftCryptosystem(Radix64Strings())
        Traceback (most recent call last):
        ...
        TypeError: A (= Free radix 64 string monoid) is not supported as a cipher domain of this shift cryptosystem.

    Testing of dumping and loading objects::

        sage: SA = ShiftCryptosystem(AlphabeticStrings())
        sage: SA == loads(dumps(SA))
        True
        sage: SH = ShiftCryptosystem(HexadecimalStrings())
        sage: SH == loads(dumps(SH))
        True
        sage: SB = ShiftCryptosystem(BinaryStrings())
        sage: SB == loads(dumps(SB))
        True

    The key ``K`` must satisfy the inequality `0 \leq K < n` with `n`
    being the size of the plaintext, ciphertext, and key spaces. For the
    shift cryptosystem, all these spaces are the same alphabet. This
    inequality must be satisfied for each of the supported alphabets.
    The capital letters of the English alphabet::

        sage: S = ShiftCryptosystem(AlphabeticStrings())
        sage: S(2 + S.alphabet_size())
        Traceback (most recent call last):
        ...
        ValueError: K (=28) is outside the range of acceptable values for a key of this shift cryptosystem.
        sage: S(-2)
        Traceback (most recent call last):
        ...
        ValueError: K (=-2) is outside the range of acceptable values for a key of this shift cryptosystem.

    The hexadecimal number system::

        sage: S = ShiftCryptosystem(HexadecimalStrings())
        sage: S(1 + S.alphabet_size())
        Traceback (most recent call last):
        ...
        ValueError: K (=17) is outside the range of acceptable values for a key of this shift cryptosystem.
        sage: S(-1)
        Traceback (most recent call last):
        ...
        ValueError: K (=-1) is outside the range of acceptable values for a key of this shift cryptosystem.

    The binary number system::

        sage: S = ShiftCryptosystem(BinaryStrings())
        sage: S(1 + S.alphabet_size())
        Traceback (most recent call last):
        ...
        ValueError: K (=3) is outside the range of acceptable values for a key of this shift cryptosystem.
        sage: S(-2)
        Traceback (most recent call last):
        ...
        ValueError: K (=-2) is outside the range of acceptable values for a key of this shift cryptosystem.
    """

    def __init__(self, A):
        r"""
        See ``ShiftCryptosystem`` for full documentation.

        Create a shift cryptosystem defined over the alphabet ``A``.

        INPUT:

        - ``A`` -- a string monoid over some alphabet; this is the non-empty
          alphabet over which the plaintext and ciphertext spaces
          are defined.

        OUTPUT:

        - A shift cryptosystem over the alphabet ``A``.

        EXAMPLES::

            sage: S = ShiftCryptosystem(AlphabeticStrings()); S
            Shift cryptosystem on Free alphabetic string monoid on A-Z
            sage: P = S.encoding("The shift cryptosystem generalizes the Caesar cipher.")
            sage: P
            THESHIFTCRYPTOSYSTEMGENERALIZESTHECAESARCIPHER
            sage: K = 7
            sage: C = S.enciphering(K, P); C
            AOLZOPMAJYFWAVZFZALTNLULYHSPGLZAOLJHLZHYJPWOLY
            sage: S.deciphering(K, C)
            THESHIFTCRYPTOSYSTEMGENERALIZESTHECAESARCIPHER
            sage: S.deciphering(K, C) == P
            True
        """
        # sanity check
        from sage.monoids.string_monoid import (
            AlphabeticStringMonoid,
            BinaryStringMonoid,
            HexadecimalStringMonoid)
        if not isinstance(A, ( AlphabeticStringMonoid,
                               BinaryStringMonoid,
                               HexadecimalStringMonoid )):
            raise TypeError("A (= %s) is not supported as a cipher domain of this shift cryptosystem." % A)
        # Initialize the shift cryptosystem with the plaintext, ciphertext,
        # and key spaces.
        SymmetricKeyCryptosystem.__init__(self, A, A, IntegerModRing(A.ngens()))

    def __call__(self, K):
        r"""
        Create a shift cipher with key ``K``.

        INPUT:

        - ``K`` -- a secret key; this key is used for both encryption and
          decryption. For the shift cryptosystem whose plaintext and
          ciphertext spaces are `A`, a key is any integer `k` such that
          `0 \leq k < n` where `n` is the size or cardinality of the set
          `A`.

        OUTPUT:

        - A shift cipher with secret key ``K``.

        EXAMPLES::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Shifting sand."); P
            SHIFTINGSAND
            sage: K = 3
            sage: E = S(K); E
            Shift cipher on Free alphabetic string monoid on A-Z
            sage: E(P)
            VKLIWLQJVDQG
            sage: D = S(S.inverse_key(K)); D
            Shift cipher on Free alphabetic string monoid on A-Z
            sage: D(E(P))
            SHIFTINGSAND

        TESTS:

        The key ``K`` must satisfy the inequality `0 \leq K < n` with `n`
        being the size of the plaintext, ciphertext, and key spaces. For the
        shift cryptosystem, all these spaces are the same alphabet. This
        inequality must be satisfied for each of the supported alphabets.
        The capital letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: S(2 + S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=28) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S(-2)
            Traceback (most recent call last):
            ...
            ValueError: K (=-2) is outside the range of acceptable values for a key of this shift cryptosystem.

        The hexadecimal number system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: S(1 + S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=17) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S(-1)
            Traceback (most recent call last):
            ...
            ValueError: K (=-1) is outside the range of acceptable values for a key of this shift cryptosystem.

        The binary number system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: S(1 + S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=3) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S(-2)
            Traceback (most recent call last):
            ...
            ValueError: K (=-2) is outside the range of acceptable values for a key of this shift cryptosystem.
        """
        # Sanity check: the key K must satisfy the inequality
        # 0 <= K < n with n being the size of the plaintext, ciphertext, and
        # key spaces. For the shift cryptosystem, all these spaces are the
        # same alphabet.
        if 0 <= K < self.alphabet_size():
            return ShiftCipher(self, K)
            # from sage.rings.integer_mod import Mod
            # return ShiftCipher(self, Mod(K, self.alphabet_size()).lift())
        else:
            raise ValueError("K (=%s) is outside the range of acceptable values for a key of this shift cryptosystem." % K)

    def _repr_(self):
        r"""
        Return the string representation of ``self``.

        EXAMPLES::

            sage: ShiftCryptosystem(AlphabeticStrings())
            Shift cryptosystem on Free alphabetic string monoid on A-Z
            sage: ShiftCryptosystem(HexadecimalStrings())
            Shift cryptosystem on Free hexadecimal string monoid
            sage: ShiftCryptosystem(BinaryStrings())
            Shift cryptosystem on Free binary string monoid
        """
        # The shift cipher has the plaintext and ciphertext spaces defined
        # over the same non-empty alphabet. The cipher domain is the same
        # as the alphabet used for the plaintext and ciphertext spaces.
        return "Shift cryptosystem on %s" % self.cipher_domain()

    def rank_by_chi_square(self, C, pdict):
        r"""
        Use the chi-square statistic to rank all possible keys. Currently,
        this method only applies to the capital letters of the English
        alphabet.

        ALGORITHM:

        Consider a non-empty alphabet `A` consisting of `n`
        elements, and let `C` be a ciphertext encoded using elements of
        `A`. The plaintext `P` corresponding to `C` is also encoded using
        elements of `A`. Let `M` be a candidate decipherment of `C`,
        i.e. `M` is the result of attempting to decrypt `C` using a key
        `k \in \ZZ/n\ZZ` which is not necessarily the same key used to
        encrypt `P`. Suppose `F_A(e)` is the characteristic frequency
        probability of `e \in A` and let `F_M(e)` be the message frequency
        probability with respect to `M`. The characteristic frequency
        probability distribution of an alphabet is the expected frequency
        probability distribution for that alphabet. The message frequency
        probability distribution of `M` provides a distribution of the ratio
        of character occurrences over message length. One can interpret the
        characteristic frequency probability `F_A(e)` as the expected
        probability, while the message frequency probability `F_M(e)` is
        the observed probability. If `M` is of length `L`, then the observed
        frequency of `e \in A` is

        .. MATH::

            O_M(e)
            =
            F_M(e) \cdot L

        and the expected frequency of `e \in A` is

        .. MATH::

            E_A(e)
            =
            F_A(e) \cdot L

        The chi-square rank `R_{\chi^2}(M)` of `M` corresponding to a key
        `k \in \ZZ/n\ZZ` is given by

        .. MATH::

            R_{\chi^2}(M)
            =
            \sum_{e \in A} \frac {\big( O_M(e) - E_A(e) \big)^2}
                                 {E_A(e)}

        Cryptanalysis by exhaustive key search produces a candidate
        decipherment `M_{k}` for each possible key `k \in \ZZ/n\ZZ`. For
        a set
        `D = \big\{M_{k_1}, M_{k_2}, \dots, M_{k_r} \big\}`
        of all candidate decipherments corresponding to a ciphertext `C`,
        the smaller is the rank `R_{\chi^2}(M_{k_i})` the more likely
        that `k_i` is the secret key. This key ranking method is based on
        the Pearson chi-square test [PearsonTest09]_.

        INPUT:

        - ``C`` -- The ciphertext, a non-empty string. The ciphertext
          must be encoded using the upper-case letters of the English
          alphabet.

        - ``pdict`` -- A dictionary of key, possible plaintext pairs.
          This should be the output of :func:`brute_force` with
          ``ranking="none"``.

        OUTPUT:

        - A list ranking the most likely keys first. Each element of the
          list is a tuple of key, possible plaintext pairs.

        EXAMPLES:

        Use the chi-square statistic to rank all possible keys and their
        corresponding decipherment::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Shi."); P
            SHI
            sage: K = 5
            sage: C = S.enciphering(K, P)
            sage: Pdict = S.brute_force(C)
            sage: S.rank_by_chi_square(C, Pdict)
            <BLANKLINE>
            [(9, ODE),
            (5, SHI),
            (20, DST),
            (19, ETU),
            (21, CRS),
            (10, NCD),
            (25, YNO),
            (6, RGH),
            (12, LAB),
            (8, PEF),
            (1, WLM),
            (11, MBC),
            (18, FUV),
            (17, GVW),
            (2, VKL),
            (4, TIJ),
            (3, UJK),
            (0, XMN),
            (16, HWX),
            (15, IXY),
            (23, APQ),
            (24, ZOP),
            (22, BQR),
            (7, QFG),
            (13, KZA),
            (14, JYZ)]

        As more ciphertext is available, the reliability of the chi-square
        ranking function increases::

            sage: P = S.encoding("Shift cipher."); P
            SHIFTCIPHER
            sage: C = S.enciphering(K, P)
            sage: Pdict = S.brute_force(C)
            sage: S.rank_by_chi_square(C, Pdict)
            <BLANKLINE>
            [(5, SHIFTCIPHER),
            (9, ODEBPYELDAN),
            (18, FUVSGPVCURE),
            (2, VKLIWFLSKHU),
            (20, DSTQENTASPC),
            (19, ETURFOUBTQD),
            (21, CRSPDMSZROB),
            (6, RGHESBHOGDQ),
            (7, QFGDRAGNFCP),
            (12, LABYMVBIAXK),
            (17, GVWTHQWDVSF),
            (24, ZOPMAJPWOLY),
            (1, WLMJXGMTLIV),
            (0, XMNKYHNUMJW),
            (11, MBCZNWCJBYL),
            (8, PEFCQZFMEBO),
            (25, YNOLZIOVNKX),
            (10, NCDAOXDKCZM),
            (3, UJKHVEKRJGT),
            (4, TIJGUDJQIFS),
            (22, BQROCLRYQNA),
            (16, HWXUIRXEWTG),
            (15, IXYVJSYFXUH),
            (14, JYZWKTZGYVI),
            (13, KZAXLUAHZWJ),
            (23, APQNBKQXPMZ)]

        TESTS:

        The ciphertext cannot be an empty string::

            sage: S.rank_by_chi_square("", Pdict)
            Traceback (most recent call last):
            ...
            AttributeError: 'str' object has no attribute 'parent'
            sage: S.rank_by_chi_square(S.encoding(""), Pdict)
            Traceback (most recent call last):
            ...
            ValueError: The ciphertext must be a non-empty string.
            sage: S.rank_by_chi_square(S.encoding(" "), Pdict)
            Traceback (most recent call last):
            ...
            ValueError: The ciphertext must be a non-empty string.

        The ciphertext must be encoded using the capital letters of the
        English alphabet as implemented in
        :func:`AlphabeticStrings()
        <sage.monoids.string_monoid.AlphabeticStrings>`::

            sage: H = HexadecimalStrings()
            sage: S.rank_by_chi_square(H.encoding("shift"), Pdict)
            Traceback (most recent call last):
            ...
            TypeError: The ciphertext must be capital letters of the English alphabet.
            sage: B = BinaryStrings()
            sage: S.rank_by_chi_square(B.encoding("shift"), Pdict)
            Traceback (most recent call last):
            ...
            TypeError: The ciphertext must be capital letters of the English alphabet.

        The dictionary ``pdict`` cannot be empty::

            sage: S.rank_by_chi_square(C, {})
            Traceback (most recent call last):
            ...
            KeyError: 0

        REFERENCES:

        .. [PearsonTest09] `Pearson chi-square test
          <http://en.wikipedia.org/wiki/Goodness_of_fit>`_. Wikipedia,
          accessed 13th October 2009.
        """
        # sanity check
        from sage.monoids.string_monoid import (
            AlphabeticStringMonoid,
            AlphabeticStrings)
        if not isinstance(C.parent(), AlphabeticStringMonoid):
            raise TypeError("The ciphertext must be capital letters of the English alphabet.")
        if str(C) == "":
            raise ValueError("The ciphertext must be a non-empty string.")

        # compute the rank of each key
        AS = AlphabeticStrings()
        # the alphabet in question
        Alph = self.encoding("".join([str(e) for e in AS.gens()]))
        StrAlph = str(Alph)
        # message length
        L = len(C)
        # expected frequency tally
        EA = AS.characteristic_frequency()
        for e in EA:
            EA[e] *= L
        # the rank R(M, k) of M for each key
        Rank = []
        for key in xrange(self.alphabet_size()):
            # observed frequency tally
            OM = pdict[key].frequency_distribution().function()
            for e in Alph:
                if e in OM:
                    OM[e] *= L
                else:
                    OM.setdefault(e, 0.0)
            # the rank R(M, K) of M with shift key k
            RMk = [(OM[AS(e)] - EA[e])**2 / EA[e] for e in StrAlph]
            Rank.append((sum(RMk), key))
        # Sort in non-decreasing order of chi-square statistic. It's
        # possible that two different keys share the same chi-square
        # statistic.
        Rank = sorted(Rank)
        RankedList = []
        # In the following line, the value of val is not used at all, making
        # it redundant to access val in the first place. This line
        # of code is written with readability in mind.
        [RankedList.append((key, pdict[key])) for val, key in Rank]
        return RankedList

    def rank_by_squared_differences(self, C, pdict):
        r"""
        Use the squared-differences measure to rank all possible keys.
        Currently, this method only applies to the capital letters of
        the English alphabet.

        ALGORITHM:

        Consider a non-empty alphabet `A` consisting of `n`
        elements, and let `C` be a ciphertext encoded using elements of
        `A`. The plaintext `P` corresponding to `C` is also encoded using
        elements of `A`. Let `M` be a candidate decipherment of `C`,
        i.e. `M` is the result of attempting to decrypt `C` using a key
        `k \in \ZZ/n\ZZ` which is not necessarily the same key used to
        encrypt `P`. Suppose `F_A(e)` is the characteristic frequency
        probability of `e \in A` and let `F_M(e)` be the message
        frequency probability with respect to `M`. The characteristic
        frequency probability distribution of an alphabet is the expected
        frequency probability distribution for that alphabet. The message
        frequency probability distribution of `M` provides a distribution
        of the ratio of character occurrences over message length. One can
        interpret the characteristic frequency probability `F_A(e)` as the
        expected probability, while the message frequency probability
        `F_M(e)` is the observed probability. If `M` is of length `L`, then
        the observed frequency of `e \in A` is

        .. MATH::

            O_M(e)
            =
            F_M(e) \cdot L

        and the expected frequency of `e \in A` is

        .. MATH::

            E_A(e)
            =
            F_A(e) \cdot L

        The squared-differences, or residual sum of squares, rank
        `R_{RSS}(M)` of `M` corresponding to a key
        `k \in \ZZ/n\ZZ` is given by

        .. MATH::

            R_{RSS}(M)
            =
            \sum_{e \in A} \big( O_M(e) - E_A(e) \big)^2

        Cryptanalysis by exhaustive key search produces a candidate
        decipherment `M_{k}` for each possible key `k \in \ZZ/n\ZZ`. For
        a set
        `D = \big\{M_{k_1}, M_{k_2}, \dots, M_{k_r} \big\}`
        of all candidate decipherments corresponding to a ciphertext `C`,
        the smaller is the rank `R_{RSS}(M_{k_i})` the more likely
        that `k_i` is the secret key. This key ranking method is based
        on the residual sum of squares measure [RSS09]_.

        INPUT:

        - ``C`` -- The ciphertext, a non-empty string. The ciphertext
          must be encoded using the upper-case letters of the English
          alphabet.

        - ``pdict`` -- A dictionary of key, possible plaintext pairs.
          This should be the output of :func:`brute_force` with
          ``ranking="none"``.

        OUTPUT:

        - A list ranking the most likely keys first. Each element of the
          list is a tuple of key, possible plaintext pairs.

        EXAMPLES:

        Use the method of squared differences to rank all possible keys
        and their corresponding decipherment::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Shi."); P
            SHI
            sage: K = 5
            sage: C = S.enciphering(K, P)
            sage: Pdict = S.brute_force(C)
            sage: S.rank_by_squared_differences(C, Pdict)
            <BLANKLINE>
            [(19, ETU),
            (9, ODE),
            (20, DST),
            (5, SHI),
            (8, PEF),
            (4, TIJ),
            (25, YNO),
            (21, CRS),
            (6, RGH),
            (10, NCD),
            (12, LAB),
            (23, APQ),
            (24, ZOP),
            (0, XMN),
            (13, KZA),
            (15, IXY),
            (1, WLM),
            (16, HWX),
            (22, BQR),
            (11, MBC),
            (18, FUV),
            (2, VKL),
            (17, GVW),
            (7, QFG),
            (3, UJK),
            (14, JYZ)]

        As more ciphertext is available, the reliability of the squared
        differences ranking function increases::

            sage: P = S.encoding("Shift cipher."); P
            SHIFTCIPHER
            sage: C = S.enciphering(K, P)
            sage: Pdict = S.brute_force(C)
            sage: S.rank_by_squared_differences(C, Pdict)
            <BLANKLINE>
            [(20, DSTQENTASPC),
            (5, SHIFTCIPHER),
            (9, ODEBPYELDAN),
            (19, ETURFOUBTQD),
            (6, RGHESBHOGDQ),
            (16, HWXUIRXEWTG),
            (8, PEFCQZFMEBO),
            (21, CRSPDMSZROB),
            (22, BQROCLRYQNA),
            (25, YNOLZIOVNKX),
            (3, UJKHVEKRJGT),
            (18, FUVSGPVCURE),
            (4, TIJGUDJQIFS),
            (10, NCDAOXDKCZM),
            (7, QFGDRAGNFCP),
            (24, ZOPMAJPWOLY),
            (2, VKLIWFLSKHU),
            (12, LABYMVBIAXK),
            (17, GVWTHQWDVSF),
            (1, WLMJXGMTLIV),
            (13, KZAXLUAHZWJ),
            (0, XMNKYHNUMJW),
            (15, IXYVJSYFXUH),
            (14, JYZWKTZGYVI),
            (11, MBCZNWCJBYL),
            (23, APQNBKQXPMZ)]

        TESTS:

        The ciphertext cannot be an empty string::

            sage: S.rank_by_squared_differences("", Pdict)
            Traceback (most recent call last):
            ...
            AttributeError: 'str' object has no attribute 'parent'
            sage: S.rank_by_squared_differences(S.encoding(""), Pdict)
            Traceback (most recent call last):
            ...
            ValueError: The ciphertext must be a non-empty string.
            sage: S.rank_by_squared_differences(S.encoding(" "), Pdict)
            Traceback (most recent call last):
            ...
            ValueError: The ciphertext must be a non-empty string.

        The ciphertext must be encoded using the capital letters of the
        English alphabet as implemented in
        :func:`AlphabeticStrings()
        <sage.monoids.string_monoid.AlphabeticStrings>`::

            sage: H = HexadecimalStrings()
            sage: S.rank_by_squared_differences(H.encoding("shift"), Pdict)
            Traceback (most recent call last):
            ...
            TypeError: The ciphertext must be capital letters of the English alphabet.
            sage: B = BinaryStrings()
            sage: S.rank_by_squared_differences(B.encoding("shift"), Pdict)
            Traceback (most recent call last):
            ...
            TypeError: The ciphertext must be capital letters of the English alphabet.

        The dictionary ``pdict`` cannot be empty::

            sage: S.rank_by_squared_differences(C, {})
            Traceback (most recent call last):
            ...
            KeyError: 0

        REFERENCES:

        .. [RSS09] `Residual sum of squares
          <http://en.wikipedia.org/wiki/Residual_sum_of_squares>`_.
          Wikipedia, accessed 13th October 2009.
        """
        # NOTE: the code in this method is very similar to that in the
        # method rank_by_chi_square(). The only difference here is the
        # line that computes the list RMk.

        # sanity check
        from sage.monoids.string_monoid import (
            AlphabeticStringMonoid,
            AlphabeticStrings)
        if not isinstance(C.parent(), AlphabeticStringMonoid):
            raise TypeError("The ciphertext must be capital letters of the English alphabet.")
        if str(C) == "":
            raise ValueError("The ciphertext must be a non-empty string.")

        # compute the rank of each key
        AS = AlphabeticStrings()
        # the alphabet in question
        Alph = self.encoding("".join([str(e) for e in AS.gens()]))
        StrAlph = str(Alph)
        # message length
        L = len(C)
        # expected frequency tally
        EA = AS.characteristic_frequency()
        for e in EA:
            EA[e] *= L
        # the rank R(M, k) of M for each key
        Rank = []
        for key in xrange(self.alphabet_size()):
            # observed frequency tally
            OM = pdict[key].frequency_distribution().function()
            for e in Alph:
                if e in OM:
                    OM[e] *= L
                else:
                    OM.setdefault(e, 0.0)
            # the rank R(M, K) of M with shift key k
            RMk = [(OM[AS(e)] - EA[e])**2 for e in StrAlph]
            Rank.append((sum(RMk), key))
        # Sort in non-decreasing order of chi-square statistic. It's
        # possible that two different keys share the same chi-square
        # statistic.
        Rank = sorted(Rank)
        RankedList = []
        # In the following line, the value of val is not used at all, making
        # it redundant to access val in the first place. This line
        # of code is written with readability in mind.
        [RankedList.append((key, pdict[key])) for val, key in Rank]
        return RankedList

    def brute_force(self, C, ranking="none"):
        r"""
        Attempt a brute force cryptanalysis of the ciphertext ``C``.

        INPUT:

        - ``C`` -- A ciphertext over one of the supported alphabets of this
          shift cryptosystem. See the class :class:`ShiftCryptosystem` for
          documentation on the supported alphabets.

        - ``ranking`` -- (default ``"none"``) the method to use for
          ranking all possible keys. If ``ranking="none"``, then do not
          use any ranking function. The following ranking functions are
          supported:

          - ``"chisquare"`` -- the chi-square ranking function as
            implemented in the method :func:`rank_by_chi_square`.

          - ``"squared_differences"`` -- the squared differences ranking
            function as implemented in the method
            :func:`rank_by_squared_differences`.

        OUTPUT:

        - All the possible plaintext sequences corresponding to the
          ciphertext ``C``. This method effectively uses all the possible
          keys in this shift cryptosystem to decrypt ``C``. The method is
          also referred to as exhaustive key search. The output is
          a dictionary of key, plaintext pairs.

        EXAMPLES:

        Cryptanalyze using all possible keys for various alphabets. Over
        the upper-case letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("The shift cryptosystem generalizes the Caesar cipher.")
            sage: K = 7
            sage: C = S.enciphering(K, P)
            sage: Dict = S.brute_force(C)
            sage: for k in xrange(len(Dict)):
            ...       if Dict[k] == P:
            ...           print "key =", k
            ...
            key = 7

        Over the hexadecimal number system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: P = S.encoding("Encryption & decryption shifts along the alphabet.")
            sage: K = 5
            sage: C = S.enciphering(K, P)
            sage: Dict = S.brute_force(C)
            sage: for k in xrange(len(Dict)):
            ...       if Dict[k] == P:
            ...           print "key =", k
            ...
            key = 5

        And over the binary number system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: P = S.encoding("The binary alphabet is very insecure.")
            sage: K = 1
            sage: C = S.enciphering(K, P)
            sage: Dict = S.brute_force(C)
            sage: for k in xrange(len(Dict)):
            ...       if Dict[k] == P:
            ...           print "key =", k
            ...
            key = 1

        Don't use any ranking functions, i.e. ``ranking="none"``::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Shifting using modular arithmetic.")
            sage: K = 8
            sage: C = S.enciphering(K, P)
            sage: pdict = S.brute_force(C)
            sage: sorted(pdict.items())
            <BLANKLINE>
            [(0, APQNBQVOCAQVOUWLCTIZIZQBPUMBQK),
            (1, ZOPMAPUNBZPUNTVKBSHYHYPAOTLAPJ),
            (2, YNOLZOTMAYOTMSUJARGXGXOZNSKZOI),
            (3, XMNKYNSLZXNSLRTIZQFWFWNYMRJYNH),
            (4, WLMJXMRKYWMRKQSHYPEVEVMXLQIXMG),
            (5, VKLIWLQJXVLQJPRGXODUDULWKPHWLF),
            (6, UJKHVKPIWUKPIOQFWNCTCTKVJOGVKE),
            (7, TIJGUJOHVTJOHNPEVMBSBSJUINFUJD),
            (8, SHIFTINGUSINGMODULARARITHMETIC),
            (9, RGHESHMFTRHMFLNCTKZQZQHSGLDSHB),
            (10, QFGDRGLESQGLEKMBSJYPYPGRFKCRGA),
            (11, PEFCQFKDRPFKDJLARIXOXOFQEJBQFZ),
            (12, ODEBPEJCQOEJCIKZQHWNWNEPDIAPEY),
            (13, NCDAODIBPNDIBHJYPGVMVMDOCHZODX),
            (14, MBCZNCHAOMCHAGIXOFULULCNBGYNCW),
            (15, LABYMBGZNLBGZFHWNETKTKBMAFXMBV),
            (16, KZAXLAFYMKAFYEGVMDSJSJALZEWLAU),
            (17, JYZWKZEXLJZEXDFULCRIRIZKYDVKZT),
            (18, IXYVJYDWKIYDWCETKBQHQHYJXCUJYS),
            (19, HWXUIXCVJHXCVBDSJAPGPGXIWBTIXR),
            (20, GVWTHWBUIGWBUACRIZOFOFWHVASHWQ),
            (21, FUVSGVATHFVATZBQHYNENEVGUZRGVP),
            (22, ETURFUZSGEUZSYAPGXMDMDUFTYQFUO),
            (23, DSTQETYRFDTYRXZOFWLCLCTESXPETN),
            (24, CRSPDSXQECSXQWYNEVKBKBSDRWODSM),
            (25, BQROCRWPDBRWPVXMDUJAJARCQVNCRL)]

        Use the chi-square ranking function, i.e. ``ranking="chisquare"``::

            sage: S.brute_force(C, ranking="chisquare")
            <BLANKLINE>
            [(8, SHIFTINGUSINGMODULARARITHMETIC),
            (14, MBCZNCHAOMCHAGIXOFULULCNBGYNCW),
            (20, GVWTHWBUIGWBUACRIZOFOFWHVASHWQ),
            (13, NCDAODIBPNDIBHJYPGVMVMDOCHZODX),
            (1, ZOPMAPUNBZPUNTVKBSHYHYPAOTLAPJ),
            (23, DSTQETYRFDTYRXZOFWLCLCTESXPETN),
            (10, QFGDRGLESQGLEKMBSJYPYPGRFKCRGA),
            (6, UJKHVKPIWUKPIOQFWNCTCTKVJOGVKE),
            (22, ETURFUZSGEUZSYAPGXMDMDUFTYQFUO),
            (15, LABYMBGZNLBGZFHWNETKTKBMAFXMBV),
            (12, ODEBPEJCQOEJCIKZQHWNWNEPDIAPEY),
            (21, FUVSGVATHFVATZBQHYNENEVGUZRGVP),
            (16, KZAXLAFYMKAFYEGVMDSJSJALZEWLAU),
            (25, BQROCRWPDBRWPVXMDUJAJARCQVNCRL),
            (9, RGHESHMFTRHMFLNCTKZQZQHSGLDSHB),
            (24, CRSPDSXQECSXQWYNEVKBKBSDRWODSM),
            (3, XMNKYNSLZXNSLRTIZQFWFWNYMRJYNH),
            (5, VKLIWLQJXVLQJPRGXODUDULWKPHWLF),
            (7, TIJGUJOHVTJOHNPEVMBSBSJUINFUJD),
            (2, YNOLZOTMAYOTMSUJARGXGXOZNSKZOI),
            (18, IXYVJYDWKIYDWCETKBQHQHYJXCUJYS),
            (4, WLMJXMRKYWMRKQSHYPEVEVMXLQIXMG),
            (11, PEFCQFKDRPFKDJLARIXOXOFQEJBQFZ),
            (19, HWXUIXCVJHXCVBDSJAPGPGXIWBTIXR),
            (0, APQNBQVOCAQVOUWLCTIZIZQBPUMBQK),
            (17, JYZWKZEXLJZEXDFULCRIRIZKYDVKZT)]

        Use the squared differences ranking function, i.e.
        ``ranking="squared_differences"``::

            sage: S.brute_force(C, ranking="squared_differences")
            <BLANKLINE>
            [(8, SHIFTINGUSINGMODULARARITHMETIC),
            (23, DSTQETYRFDTYRXZOFWLCLCTESXPETN),
            (12, ODEBPEJCQOEJCIKZQHWNWNEPDIAPEY),
            (2, YNOLZOTMAYOTMSUJARGXGXOZNSKZOI),
            (9, RGHESHMFTRHMFLNCTKZQZQHSGLDSHB),
            (7, TIJGUJOHVTJOHNPEVMBSBSJUINFUJD),
            (21, FUVSGVATHFVATZBQHYNENEVGUZRGVP),
            (22, ETURFUZSGEUZSYAPGXMDMDUFTYQFUO),
            (1, ZOPMAPUNBZPUNTVKBSHYHYPAOTLAPJ),
            (16, KZAXLAFYMKAFYEGVMDSJSJALZEWLAU),
            (20, GVWTHWBUIGWBUACRIZOFOFWHVASHWQ),
            (24, CRSPDSXQECSXQWYNEVKBKBSDRWODSM),
            (14, MBCZNCHAOMCHAGIXOFULULCNBGYNCW),
            (13, NCDAODIBPNDIBHJYPGVMVMDOCHZODX),
            (3, XMNKYNSLZXNSLRTIZQFWFWNYMRJYNH),
            (10, QFGDRGLESQGLEKMBSJYPYPGRFKCRGA),
            (15, LABYMBGZNLBGZFHWNETKTKBMAFXMBV),
            (6, UJKHVKPIWUKPIOQFWNCTCTKVJOGVKE),
            (11, PEFCQFKDRPFKDJLARIXOXOFQEJBQFZ),
            (25, BQROCRWPDBRWPVXMDUJAJARCQVNCRL),
            (17, JYZWKZEXLJZEXDFULCRIRIZKYDVKZT),
            (19, HWXUIXCVJHXCVBDSJAPGPGXIWBTIXR),
            (4, WLMJXMRKYWMRKQSHYPEVEVMXLQIXMG),
            (0, APQNBQVOCAQVOUWLCTIZIZQBPUMBQK),
            (18, IXYVJYDWKIYDWCETKBQHQHYJXCUJYS),
            (5, VKLIWLQJXVLQJPRGXODUDULWKPHWLF)]

        TESTS:

        Currently, the octal number system is not supported as an alphabet for
        this shift cryptosystem::

            sage: SA = ShiftCryptosystem(AlphabeticStrings())
            sage: OctStr = OctalStrings()
            sage: C = OctStr([1, 2, 3])
            sage: SA.brute_force(C)
            Traceback (most recent call last):
            ...
            TypeError: ciphertext must be encoded using one of the supported cipher domains of this shift cryptosystem.

        Nor is the radix-64 alphabet supported::

            sage: Rad64 = Radix64Strings()
            sage: C = Rad64([1, 2, 3])
            sage: SA.brute_force(C)
            Traceback (most recent call last):
            ...
            TypeError: ciphertext must be encoded using one of the supported cipher domains of this shift cryptosystem.
        """
        # Sanity check: ensure that C is encoded using one of the
        # supported alphabets of this shift cryptosystem.
        from sage.monoids.string_monoid import (
            AlphabeticStringMonoid,
            BinaryStringMonoid,
            HexadecimalStringMonoid)
        if not isinstance(C.parent(), (
                AlphabeticStringMonoid,
                BinaryStringMonoid,
                HexadecimalStringMonoid)):
            raise TypeError("ciphertext must be encoded using one of the supported cipher domains of this shift cryptosystem.")
        ranking_functions = ["none", "chisquare", "squared_differences"]
        if ranking not in ranking_functions:
            raise ValueError("Keyword 'ranking' must be either 'none', 'chisquare', or 'squared_differences'.")

        # Now do the actual task of cryptanalysis by means of exhaustive key
        # search, also known as the brute force method.
        # let D be a dictionary of key/plaintext pairs
        D = {}

        # NOTE: This loop is a good candidate for loop unrolling. Unless we
        # can justify that this block of code is a bottleneck on the runtime
        # of the method, we should leave it as is. For the alphabets that
        # are supported by this shift cryptosystem, it can be a waste of
        # time optimizing the code when the largest alphabet size is less
        # than 100.
        for k in xrange(self.alphabet_size()):
            D.setdefault(k, self.deciphering(k, C))

        if ranking == "none":
            return D
        if ranking == "chisquare":
            return self.rank_by_chi_square(C, D)
        if ranking == "squared_differences":
            return self.rank_by_squared_differences(C, D)

    def deciphering(self, K, C):
        r"""
        Decrypt the ciphertext ``C`` with the key ``K`` using shift cipher
        decryption.

        INPUT:

        - ``K`` -- a secret key; a key belonging to the key space of this
          shift cipher. This key is an integer `k` satisfying the inequality
          `0 \leq k < n`, where `n` is the size of the cipher domain.

        - ``C`` -- a string of ciphertext; possibly an empty string.
          Characters in this string must be encoded using one of the
          supported alphabets. See the method :func:`encoding()`
          for more information.

        OUTPUT:

        - The plaintext corresponding to the ciphertext ``C``.

        EXAMPLES:

        Let's perform decryption over the supported alphabets. Here is
        decryption over the capital letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Stop shifting me."); P
            STOPSHIFTINGME
            sage: K = 13
            sage: C = S.enciphering(K, P); C
            FGBCFUVSGVATZR
            sage: S.deciphering(K, C) == P
            True

        Decryption over the hexadecimal number system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: P = S.encoding("Shift me now."); P
            5368696674206d65206e6f772e
            sage: K = 7
            sage: C = S.enciphering(K, P); C
            cadfd0ddeb97d4dc97d5d6ee95
            sage: S.deciphering(K, C) == P
            True

        Decryption over the binary number system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: P = S.encoding("OK, enough shifting."); P
            0100111101001011001011000010000001100101011011100110111101110101011001110110100000100000011100110110100001101001011001100111010001101001011011100110011100101110
            sage: K = 1
            sage: C = S.enciphering(K, P); C
            1011000010110100110100111101111110011010100100011001000010001010100110001001011111011111100011001001011110010110100110011000101110010110100100011001100011010001
            sage: S.deciphering(K, C) == P
            True
        """
        E = self(self.inverse_key(K))
        return E(C)

    def enciphering(self, K, P):
        r"""
        Encrypt the plaintext ``P`` with the key ``K`` using shift cipher
        encryption.

        INPUT:

        - ``K`` -- a key belonging to the key space of this shift cipher.
          This key is an integer `k` satisfying the inequality
          `0 \leq k < n`, where `n` is the size of the cipher domain.

        - ``P`` -- a string of plaintext; possibly an empty string.
          Characters in this string must be encoded using one of the
          supported alphabets. See the method :func:`encoding()` for more
          information.

        OUTPUT:

        - The ciphertext corresponding to the plaintext ``P``.

        EXAMPLES:

        Let's perform encryption over the supported alphabets. Here is
        encryption over the capital letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: P = S.encoding("Shift your gear."); P
            SHIFTYOURGEAR
            sage: K = 3
            sage: S.enciphering(K, P)
            VKLIWBRXUJHDU

        Encryption over the hexadecimal number system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: P = S.encoding("Capitalize with the shift key."); P
            4361706974616c697a65207769746820746865207368696674206b65792e
            sage: K = 5
            sage: S.enciphering(K, P)
            98b6c5bec9b6b1becfba75ccbec9bd75c9bdba75c8bdbebbc975b0bace73

        Encryption over the binary number system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: P = S.encoding("Don't shift."); P
            010001000110111101101110001001110111010000100000011100110110100001101001011001100111010000101110
            sage: K = 1
            sage: S.enciphering(K, P)
            101110111001000010010001110110001000101111011111100011001001011110010110100110011000101111010001
        """
        E = self(K)
        return E(P)

    def encoding(self, S):
        r"""
        The encoding of the string ``S`` over the string monoid of this
        shift cipher. For example, if the string monoid of this cryptosystem
        is
        :class:`AlphabeticStringMonoid <sage.monoids.string_monoid.AlphabeticStringMonoid>`,
        then the encoding of ``S`` would be its upper-case equivalent
        stripped of all non-alphabetic characters. The following alphabets
        are supported for the shift cipher:

        - capital letters of the English alphabet as implemented in
          :func:`AlphabeticStrings() <sage.monoids.string_monoid.AlphabeticStrings>`

        - the alphabet consisting of the hexadecimal number system as
          implemented in
          :func:`HexadecimalStrings() <sage.monoids.string_monoid.HexadecimalStrings>`

        - the alphabet consisting of the binary number system as implemented in
          :func:`BinaryStrings() <sage.monoids.string_monoid.BinaryStrings>`

        INPUT:

        - ``S`` -- a string, possibly empty.

        OUTPUT:

        - The encoding of ``S`` over the string monoid of this cryptosystem.
          If ``S`` is an empty string, return an empty string.

        EXAMPLES:

        Encoding over the upper-case letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: S.encoding("Shift cipher on capital letters of the English alphabet.")
            SHIFTCIPHERONCAPITALLETTERSOFTHEENGLISHALPHABET

        Encoding over the binary system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: S.encoding("Binary")
            010000100110100101101110011000010111001001111001

        Encoding over the hexadecimal system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: S.encoding("Over hexadecimal system.")
            4f7665722068657861646563696d616c2073797374656d2e

        The argument ``S`` can be an empty string, in which case an empty
        string is returned::

            sage: ShiftCryptosystem(AlphabeticStrings()).encoding("")
            <BLANKLINE>
            sage: ShiftCryptosystem(HexadecimalStrings()).encoding("")
            <BLANKLINE>
            sage: ShiftCryptosystem(BinaryStrings()).encoding("")
            <BLANKLINE>
        """
        D = self.cipher_domain()
        if isinstance(D, AlphabeticStringMonoid):
            return D(strip_encoding(S))
        try:
            return D.encoding(S)
        except:
            raise TypeError("Argument S = %s does not encode in the cipher domain" % S)

    def inverse_key(self, K):
        r"""
        The inverse key corresponding to the key ``K``. For the shift cipher,
        the inverse key corresponding to ``K`` is `-K \bmod n`, where
        `n > 0` is the size of the cipher domain, i.e. the
        plaintext/ciphertext space. A key `k` of the shift cipher is an
        integer `0 \leq k < n`. The key `k = 0` has no effect on either the
        plaintext or the ciphertext.

        INPUT:

        - ``K`` -- a key for this shift cipher. This must be an integer `k`
          such that `0 \leq k < n`, where `n` is the size of the cipher domain.

        OUTPUT:

        - The inverse key corresponding to ``K``.

        EXAMPLES:

        Some random keys and their respective inverse keys::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: key = S.random_key(); key  # random
            2
            sage: S.inverse_key(key)         # random
            24
            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: key = S.random_key(); key  # random
            12
            sage: S.inverse_key(key)         # random
            4
            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: key = S.random_key(); key  # random
            1
            sage: S.inverse_key(key)         # random
            1
            sage: key = S.random_key(); key  # random
            0
            sage: S.inverse_key(key)         # random
            0

        Regardless of the value of a key, the addition of the key and its
        inverse must be equal to the alphabet size. This relationship holds
        exactly when the value of the key is non-zero::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: K = S.random_key()
            sage: while K == 0:
            ...       K = S.random_key()
            ...
            sage: invK = S.inverse_key(K)
            sage: K + invK == S.alphabet_size()
            True
            sage: invK + K == S.alphabet_size()
            True
            sage: K = S.random_key()
            sage: while K != 0:
            ...       K = S.random_key()
            ...
            sage: invK = S.inverse_key(K)
            sage: K + invK != S.alphabet_size()
            True
            sage: K; invK
            0
            0

        TESTS:

        The key ``K`` must satisfy the inequality `0 \leq K < n` with `n`
        being the size of the plaintext, ciphertext, and key spaces. For the
        shift cryptosystem, all these spaces are the same alphabet. This
        inequality must be satisfied for each of the supported alphabets.
        The capital letters of the English alphabet::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: S.inverse_key(S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=26) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S.inverse_key(-1)
            Traceback (most recent call last):
            ...
            ValueError: K (=-1) is outside the range of acceptable values for a key of this shift cryptosystem.

        The hexadecimal number system::

            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: S.inverse_key(S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=16) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S.inverse_key(-1)
            Traceback (most recent call last):
            ...
            ValueError: K (=-1) is outside the range of acceptable values for a key of this shift cryptosystem.

        The binary number system::

            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: S.inverse_key(S.alphabet_size())
            Traceback (most recent call last):
            ...
            ValueError: K (=2) is outside the range of acceptable values for a key of this shift cryptosystem.
            sage: S.inverse_key(-1)
            Traceback (most recent call last):
            ...
            ValueError: K (=-1) is outside the range of acceptable values for a key of this shift cryptosystem.
        """
        # Sanity check: the key K must satisfy the inequality
        # 0 <= K < n with n being the size of the plaintext, ciphertext, and
        # key spaces. For the shift cryptosystem, all these spaces are the
        # same alphabet.
        if 0 <= K < self.alphabet_size():
            # Let A be the alphabet of this cryptosystem and let n be the
            # number of elements in A. If k is a key, then the corresponding
            # inverse key is -k mod n.
            return self.key_space()(-Integer(K)).lift()
        else:
            raise ValueError("K (=%s) is outside the range of acceptable values for a key of this shift cryptosystem." % K)

    def random_key(self):
        r"""
        Generate a random key within the key space of this shift cipher.
        The generated key is an integer `0 \leq k < n` with `n` being the
        size of the cipher domain. Thus there are `n` possible keys in the
        key space, which is the set `\ZZ / n\ZZ`. The key `k = 0` has no
        effect on either the plaintext or the ciphertext.

        OUTPUT:

        - A random key within the key space of this shift cryptosystem.

        EXAMPLES::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: S.random_key()  # random
            18
            sage: S = ShiftCryptosystem(BinaryStrings())
            sage: S.random_key()  # random
            0
            sage: S = ShiftCryptosystem(HexadecimalStrings())
            sage: S.random_key()  # random
            5

        Regardless of the value of a key, the addition of the key and its
        inverse must be equal to the alphabet size. This relationship holds
        exactly when the value of the key is non-zero::

            sage: S = ShiftCryptosystem(AlphabeticStrings())
            sage: K = S.random_key()
            sage: while K == 0:
            ...       K = S.random_key()
            ...
            sage: invK = S.inverse_key(K)
            sage: K + invK == S.alphabet_size()
            True
            sage: invK + K == S.alphabet_size()
            True
            sage: K = S.random_key()
            sage: while K != 0:
            ...       K = S.random_key()
            ...
            sage: invK = S.inverse_key(K)
            sage: K + invK != S.alphabet_size()
            True
            sage: K; invK
            0
            0
        """
        # Return a random element in ZZ/nZZ where n is the number of elements
        # in the plaintext/ciphertext alphabet and key space.
        from sage.misc.prandom import randint
        return Integer(randint(0, self.alphabet_size() - 1))

class SubstitutionCryptosystem(SymmetricKeyCryptosystem):
    """
    Create a substitution cryptosystem.

    INPUT:

    - ``S`` - a string monoid over some alphabet

    OUTPUT:

    - A substitution cryptosystem over the alphabet ``S``.

    EXAMPLES::

        sage: M = AlphabeticStrings()
        sage: E = SubstitutionCryptosystem(M)
        sage: E
        Substitution cryptosystem on Free alphabetic string monoid on A-Z
        sage: K = M([ 25-i for i in range(26) ])
        sage: K
        ZYXWVUTSRQPONMLKJIHGFEDCBA
        sage: e = E(K)
        sage: m = M("THECATINTHEHAT")
        sage: e(m)
        GSVXZGRMGSVSZG

    TESTS::

        sage: M = AlphabeticStrings()
        sage: E = SubstitutionCryptosystem(M)
        sage: E == loads(dumps(E))
        True
    """

    def __init__(self, S):
        """
        See ``SubstitutionCryptosystem`` for full documentation.

        EXAMPLES::

            sage: M = AlphabeticStrings()
            sage: E = SubstitutionCryptosystem(M)
            sage: E
            Substitution cryptosystem on Free alphabetic string monoid on A-Z
        """
        if not isinstance(S, StringMonoid_class):
            raise TypeError("S (= %s) must be a string monoid." % S)
        SymmetricKeyCryptosystem.__init__(self, S, S, S)

    def __call__(self, K):
        """
        Create a substitution cipher.

        INPUT:

        - ``K`` - a key which is a permutation of the cryptosystem alphabet

        EXAMPLES::

            sage: M = AlphabeticStrings()
            sage: E = SubstitutionCryptosystem(M)
            sage: E
            Substitution cryptosystem on Free alphabetic string monoid on A-Z
            sage: K = M([ 25-i for i in range(26) ])
            sage: K
            ZYXWVUTSRQPONMLKJIHGFEDCBA
            sage: e = E(K)
            sage: m = M("THECATINTHEHAT")
            sage: e(m)
            GSVXZGRMGSVSZG
        """
        if not isinstance(K, StringMonoidElement):
            raise TypeError("K (= %s) must be a string." % K)
        if K.parent() != self.key_space():
            raise TypeError("K (= %s) must be a string in the key space." % K)
        return SubstitutionCipher(self, K)

    def _repr_(self):
        """
        Return a string representation of self.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: S = SubstitutionCryptosystem(A)
            sage: S
            Substitution cryptosystem on Free alphabetic string monoid on A-Z
            sage: S._repr_()
            'Substitution cryptosystem on Free alphabetic string monoid on A-Z'
        """
        return "Substitution cryptosystem on %s" % self.cipher_domain()

    def random_key(self):
        """
        Generate a random key within the key space of this substitution
        cipher. The generated key is a permutation of the cryptosystem
        alphabet. Let `n` be the length of the alphabet. Then there are
        `n!` possible keys in the key space.

        OUTPUT:

        - A random key within the key space of this cryptosystem.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: S = SubstitutionCryptosystem(A)
            sage: K = S.random_key()
            sage: Ki = S.inverse_key(K)
            sage: M = "THECATINTHEHAT"
            sage: e = S(K)
            sage: d = S(Ki)
            sage: d(e(A(M))) == A(M)
            True
        """
        S = self.cipher_domain()
        n = S.ngens()
        I = SymmetricGroup(n).random_element().list()
        return S([ i-1 for i in I ])

    def inverse_key(self, K):
        """
        The inverse key corresponding to the key ``K``. The specified key is a
        permutation of the cryptosystem alphabet.

        INPUT:

        - ``K`` - a key belonging to the key space of this cryptosystem

        OUTPUT:

        - The inverse key of ``K``.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = SubstitutionCryptosystem(S)
            sage: K = E.random_key()
            sage: L = E.inverse_key(K)
            sage: M = S("THECATINTHEHAT")
            sage: e = E(K)
            sage: c = E(L)
            sage: c(e(M))
            THECATINTHEHAT
        """
        I = K._element_list
        S = self.cipher_domain()
        n = S.ngens()
        return S([ I.index(i) for i in range(n) ])

    def encoding(self, M):
        """
        The encoding of the string ``M`` over the string monoid of this
        substitution cipher. For example, if the string monoid of this
        cryptosystem is :class:`AlphabeticStringMonoid`, then the encoding
        of ``M`` would be its upper-case equivalent stripped of all
        non-alphabetic characters.

        INPUT:

        - ``M`` - a string, possibly empty

        OUTPUT:

        - The encoding of ``M`` over the string monoid of this cryptosystem.

        EXAMPLES::

            sage: M = "Peter Pan(ning) for gold."
            sage: A = AlphabeticStrings()
            sage: S = SubstitutionCryptosystem(A)
            sage: S.encoding(M) == A.encoding(M)
            True
        """
        S = self.cipher_domain()
        if isinstance(S, AlphabeticStringMonoid):
            return S(strip_encoding(M))
        try:
            return S.encoding(M)
        except:
            raise TypeError("Argument M = %s does not encode in the cipher domain" % M)

    def deciphering(self, K, C):
        """
        Decrypt the ciphertext ``C`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this substitution cipher

        - ``C`` - a string (possibly empty) over the string monoid of this
          cryptosystem.

        OUTPUT:

        - The plaintext corresponding to the ciphertext ``C``.

        EXAMPLES::

            sage: S = SubstitutionCryptosystem(AlphabeticStrings())
            sage: K = S.random_key()
            sage: M = S.encoding("Don't substitute me!")
            sage: S.deciphering(K, S.enciphering(K, M)) == M
            True
        """
        i = self(self.inverse_key(K))
        return i(C)

    def enciphering(self, K, M):
        """
        Encrypt the plaintext ``M`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this substitution cipher

        - ``M`` - a string (possibly empty) over the string monoid of this
          cryptosystem.

        OUTPUT:

        - The ciphertext corresponding to the plaintext ``M``.

        EXAMPLES::

            sage: S = SubstitutionCryptosystem(AlphabeticStrings())
            sage: K = S.random_key()
            sage: M = S.encoding("Don't substitute me.")
            sage: S.deciphering(K, S.enciphering(K, M)) == M
            True
        """
        e = self(K)
        return e(M)

class TranspositionCryptosystem(SymmetricKeyCryptosystem):
    """
    Create a transposition cryptosystem of block length ``n``.

    INPUT:

    - ``S`` - a string monoid over some alphabet

    - ``n`` - integer `> 0`; a block length of a block permutation

    OUTPUT:

    - A transposition cryptosystem of block length ``n`` over the
      alphabet ``S``.

    EXAMPLES::

        sage: S = AlphabeticStrings()
        sage: E = TranspositionCryptosystem(S,14)
        sage: E
        Transposition cryptosystem on Free alphabetic string monoid on A-Z of block length 14
        sage: K = [ 14-i for i in range(14) ]
        sage: K
        [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        sage: e = E(K)
        sage: e(S("THECATINTHEHAT"))
        TAHEHTNITACEHT

    TESTS::

        sage: S = AlphabeticStrings()
        sage: E = TranspositionCryptosystem(S,14)
        sage: E == loads(dumps(E))
        True
    """

    def __init__(self, S, n):
        """
        See ``TranspositionCryptosystem`` for full documentation.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = TranspositionCryptosystem(S,14)
            sage: E
            Transposition cryptosystem on Free alphabetic string monoid on A-Z of block length 14
        """
        if not isinstance(S, StringMonoid_class):
            raise TypeError("S (= %s) must be a string monoid." % S)
        key_space = SymmetricGroup(n)
        SymmetricKeyCryptosystem.__init__(self, S, S, key_space, block_length=n)

    def __call__(self, K):
        """
        Create a transposition cipher.

        INPUT:

        - ``K`` - a key which specifies a block permutation

        EXAMPLES::

            sage: M = AlphabeticStrings()
            sage: E = TranspositionCryptosystem(M,14)
            sage: E
            Transposition cryptosystem on Free alphabetic string monoid on A-Z of block length 14
            sage: K = [ 14-i for i in range(14) ]
            sage: K
            [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
            sage: e = E(K)
            sage: m = M("THECATINTHEHAT")
            sage: e(m)
            TAHEHTNITACEHT
        """
        G = self.key_space()
        if isinstance(K, list):
            try:
                K = G(K)
            except:
                raise TypeError("K (= %s) must specify a permutation." % K)
        if not isinstance(K, PermutationGroupElement) and K.parent() == G:
            raise TypeError("K (= %s) must be a permutation or list specifying a permutation." % K)
        return TranspositionCipher(self, K)

    def _repr_(self):
        """
        Return a string representation of self.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: T = TranspositionCryptosystem(A, 14)
            sage: T
            Transposition cryptosystem on Free alphabetic string monoid on A-Z of block length 14
            sage: T._repr_()
            'Transposition cryptosystem on Free alphabetic string monoid on A-Z of block length 14'
        """
        return "Transposition cryptosystem on %s of block length %s" % (
            self.cipher_domain(), self.block_length())

    def random_key(self):
        """
        Generate a random key within the key space of this transposition
        cryptosystem. Let `n > 0` be the block length of this cryptosystem.
        Then there are `n!` possible keys.

        OUTPUT:

        - A random key within the key space of this cryptosystem.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = TranspositionCryptosystem(S, 14)
            sage: K = E.random_key()
            sage: Ki = E.inverse_key(K)
            sage: e = E(K)
            sage: d = E(Ki)
            sage: M = "THECATINTHEHAT"
            sage: C = e(S(M))
            sage: d(S(C)) == S(M)
            True
        """
        n = self.block_length()
        return SymmetricGroup(n).random_element()

    def inverse_key(self, K, check=True):
        """
        The inverse key corresponding to the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this transposition
          cipher

        - ``check`` - bool (default: ``True``); check that ``K`` belongs to
          the key space of this cryptosystem.

        OUTPUT:

        - The inverse key corresponding to ``K``.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = TranspositionCryptosystem(S, 14)
            sage: K = E.random_key()
            sage: Ki = E.inverse_key(K)
            sage: e = E(K)
            sage: d = E(Ki)
            sage: M = "THECATINTHEHAT"
            sage: C = e(S(M))
            sage: d(S(C)) == S(M)
            True
        """
        if check:
            if not K in self.key_space():
                raise TypeError("Argument K (= %s) is not in the key space." % K)
        return K**-1

    def encoding(self, M):
        """
        The encoding of the string ``M`` over the string monoid of this
        transposition cipher. For example, if the string monoid of this
        cryptosystem is :class:`AlphabeticStringMonoid`, then the encoding
        of ``M`` would be its upper-case equivalent stripped of all
        non-alphabetic characters.

        INPUT:

        - ``M`` - a string, possibly empty

        OUTPUT:

        - The encoding of ``M`` over the string monoid of this cryptosystem.

        EXAMPLES::

            sage: M = "Transposition cipher is not about matrix transpose."
            sage: A = AlphabeticStrings()
            sage: T = TranspositionCryptosystem(A, 11)
            sage: T.encoding(M) == A.encoding(M)
            True
        """
        S = self.cipher_domain()
        if isinstance(S, AlphabeticStringMonoid):
            return S(strip_encoding(M))
        try:
            return S.encoding(M)
        except:
            raise TypeError("Argument M = %s does not encode in the cipher domain" % M)

    def deciphering(self, K, C):
        """
        Decrypt the ciphertext ``C`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this transposition
          cipher

        - ``C`` - a string (possibly empty) over the string monoid of this
          cryptosystem.

        OUTPUT:

        - The plaintext corresponding to the ciphertext ``C``.

        EXAMPLES::

            sage: T = TranspositionCryptosystem(AlphabeticStrings(), 14)
            sage: K = T.random_key()
            sage: M = T.encoding("The cat in the hat.")
            sage: T.deciphering(K, T.enciphering(K, M)) == M
            True
        """
        i = self(self.inverse_key(K))
        return i(C)

    def enciphering(self, K, M):
        """
        Encrypt the plaintext ``M`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this transposition
          cipher

        - ``M`` - a string (possibly empty) over the string monoid of this
          cryptosystem

        OUTPUT:

        - The ciphertext corresponding to the plaintext ``M``.

        EXAMPLES::

            sage: T = TranspositionCryptosystem(AlphabeticStrings(), 14)
            sage: K = T.random_key()
            sage: M = T.encoding("The cat in the hat.")
            sage: T.deciphering(K, T.enciphering(K, M)) == M
            True
        """
        e = self(K)
        return e(M)

class VigenereCryptosystem(SymmetricKeyCryptosystem):
    """
    Create a Vigenere cryptosystem of block length ``n``.

    INPUT:

    - ``S``-- a string monoid over some alphabet

    - ``n`` - integer `> 0`; block length of an encryption/decryption key

    OUTPUT:

    - A Vigenere cryptosystem of block length ``n`` over the alphabet
      ``S``.

    EXAMPLES::

        sage: S = AlphabeticStrings()
        sage: E = VigenereCryptosystem(S,14)
        sage: E
        Vigenere cryptosystem on Free alphabetic string monoid on A-Z of period 14
        sage: K = S('ABCDEFGHIJKLMN')
        sage: K
        ABCDEFGHIJKLMN
        sage: e = E(K)
        sage: e
        Cipher on Free alphabetic string monoid on A-Z
        sage: e(S("THECATINTHEHAT"))
        TIGFEYOUBQOSMG

    TESTS::

        sage: S = AlphabeticStrings()
        sage: E = VigenereCryptosystem(S,14)
        sage: E == loads(dumps(E))
        True
    """

    def __init__(self, S, n):
        """
        See ``VigenereCryptosystem`` for full documentation.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = VigenereCryptosystem(S,14)
            sage: E
            Vigenere cryptosystem on Free alphabetic string monoid on A-Z of period 14
        """
        if not isinstance(S, StringMonoid_class):
            raise TypeError("S (= %s) must be a string monoid." % S)
        SymmetricKeyCryptosystem.__init__(self, S, S, S, block_length=1, period=n)

    def __call__(self, K):
        """
        Create a Vigenere cipher.

        INPUT: A key which specifies a block permutation.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = VigenereCryptosystem(S,14)
            sage: E
            Vigenere cryptosystem on Free alphabetic string monoid on A-Z of period 14
            sage: K = S('ABCDEFGHIJKLMN')
            sage: K
            ABCDEFGHIJKLMN
            sage: e = E(K)
            sage: e
            Cipher on Free alphabetic string monoid on A-Z
            sage: e(S("THECATINTHEHAT"))
            TIGFEYOUBQOSMG
        """
        S = self.key_space()
        m = self.period()
        if isinstance(K, list):
            try:
                K = S(K)
            except:
                raise TypeError("K (= %s) must specify a string of length %s." % (K, m))
        if not len(K) == m:
            raise TypeError("K (= %s) must specify a string of length %s." % (K, m))
        return VigenereCipher(self, K)

    def _repr_(self):
        """
        Return a string representation of self.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: V = VigenereCryptosystem(A, 14)
            sage: V
            Vigenere cryptosystem on Free alphabetic string monoid on A-Z of period 14
            sage: V._repr_()
            'Vigenere cryptosystem on Free alphabetic string monoid on A-Z of period 14'
        """
        return "Vigenere cryptosystem on %s of period %s" % (
            self.cipher_domain(), self.period())

    def random_key(self):
        """
        Generate a random key within the key space of this Vigenere
        cryptosystem. Let `n > 0` be the length of the cryptosystem alphabet
        and let `m > 0` be the block length of this cryptosystem. Then there
        are `n^m` possible keys.

        OUTPUT:

        - A random key within the key space of this cryptosystem.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: V = VigenereCryptosystem(A, 14)
            sage: M = "THECATINTHEHAT"
            sage: K = V.random_key()
            sage: Ki = V.inverse_key(K)
            sage: e = V(K)
            sage: d = V(Ki)
            sage: d(e(A(M))) == A(M)
            True
        """
        S = self.key_space()
        n = S.ngens()
        m = self.period()
        return S([ randint(0, n-1) for i in range(m) ])

    def inverse_key(self, K):
        """
        The inverse key corresponding to the key ``K``.

        INPUT:

        - ``K`` - a key within the key space of this Vigenere cryptosystem

        OUTPUT:

        - The inverse key corresponding to ``K``.

        EXAMPLES::

            sage: S = AlphabeticStrings()
            sage: E = VigenereCryptosystem(S,14)
            sage: K = E.random_key()
            sage: L = E.inverse_key(K)
            sage: M = S("THECATINTHEHAT")
            sage: e = E(K)
            sage: c = E(L)
            sage: c(e(M))
            THECATINTHEHAT
        """
        S = self.key_space()
        n = S.ngens()
        return S([ (-i)%(n) for i in K._element_list ])

    def encoding(self, M):
        """
        The encoding of the string ``M`` over the string monoid of this
        Vigenere cipher. For example, if the string monoid of this
        cryptosystem is :class:`AlphabeticStringMonoid`, then the encoding
        of ``M`` would be its upper-case equivalent stripped of all
        non-alphabetic characters.

        INPUT:

        - ``M`` - a string, possibly empty

        OUTPUT:

        - The encoding of ``M`` over the string monoid of this cryptosystem.

        EXAMPLES::

            sage: A = AlphabeticStrings()
            sage: V = VigenereCryptosystem(A, 24)
            sage: M = "Jack and Jill went up the hill."
            sage: V.encoding(M) == A.encoding(M)
            True
        """
        S = self.cipher_domain()
        if isinstance(S, AlphabeticStringMonoid):
            return S(strip_encoding(M))
        try:
            return S.encoding(M)
        except:
            raise TypeError("Argument M = %s does not encode in the cipher domain" % M)

    def deciphering(self, K, C):
        """
        Decrypt the ciphertext ``C`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this Vigenere cipher

        - ``C`` - a string (possibly empty) over the string monoid of this
          cryptosystem

        OUTPUT:

        - The plaintext corresponding to the ciphertext ``C``.

        EXAMPLES::

            sage: V = VigenereCryptosystem(AlphabeticStrings(), 24)
            sage: K = V.random_key()
            sage: M = V.encoding("Jack and Jill went up the hill.")
            sage: V.deciphering(K, V.enciphering(K, M)) == M
            True
        """
        i = self(self.inverse_key(K))
        return i(C)

    def enciphering(self, K, M):
        """
        Encrypt the plaintext ``M`` using the key ``K``.

        INPUT:

        - ``K`` - a key belonging to the key space of this Vigenere cipher

        - ``M`` - a string (possibly empty) over the string monoid of this
          cryptosystem

        OUTPUT:

        - The ciphertext corresponding to the plaintext ``M``.

        EXAMPLES::

            sage: V = VigenereCryptosystem(AlphabeticStrings(), 24)
            sage: K = V.random_key()
            sage: M = V.encoding("Jack and Jill went up the hill.")
            sage: V.deciphering(K, V.enciphering(K, M)) == M
            True
        """
        e = self(K)
        return e(M)
