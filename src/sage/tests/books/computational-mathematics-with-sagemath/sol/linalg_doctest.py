# sage_setup: distribution = sagemath-repl
## -*- encoding: utf-8 -*-
"""
This file (./sol/linalg_doctest.sage) was *autogenerated* from ./sol/linalg.tex,
with sagetex.sty version 2011/05/27 v2.3.1.
It contains the contents of all the sageexample environments from this file.
You should be able to doctest this file with:
sage -t ./sol/linalg_doctest.sage
It is always safe to delete this file; it is not used in typesetting your
document.

Sage example in ./sol/linalg.tex, line 89::

  sage: A = matrix(GF(7),[[0,0,3,0,0],[1,0,6,0,0],[0,1,5,0,0],
  ....:                   [0,0,0,0,5],[0,0,0,1,5]])
  sage: P = A.minpoly(); P
  x^5 + 4*x^4 + 3*x^2 + 3*x + 1
  sage: P.factor()
  (x^2 + 2*x + 2) * (x^3 + 2*x^2 + x + 4)

Sage example in ./sol/linalg.tex, line 100::

  sage: e1 = identity_matrix(GF(7),5)[0]
  sage: e4 = identity_matrix(GF(7),5)[3]
  sage: A.transpose().maxspin(e1)
  [(1, 0, 0, 0, 0), (0, 1, 0, 0, 0), (0, 0, 1, 0, 0)]
  sage: A.transpose().maxspin(e4)
  [(0, 0, 0, 1, 0), (0, 0, 0, 0, 1)]
  sage: A.transpose().maxspin(e1 + e4)
  [(1, 0, 0, 1, 0), (0, 1, 0, 0, 1), (0, 0, 1, 5, 5),
  (3, 6, 5, 4, 2), (1, 5, 3, 3, 0)]

Sage example in ./sol/linalg.tex, line 168::

  sage: def Similar(A, B):
  ....:     F1, U1 = A.frobenius_form(2)
  ....:     F2, U2 = B.frobenius_form(2)
  ....:     if F1 == F2:
  ....:         return True, ~U2*U1
  ....:     else:
  ....:         return False, F1 - F2
  sage: B = matrix(ZZ, [[0,1,4,0,4],[4,-2,0,-4,-2],[0,0,0,2,1],
  ....:                 [-4,2,2,0,-1],[-4,-2,1,2,0]])
  sage: U = matrix(ZZ, [[3,3,-9,-14,40],[-1,-2,4,2,1],[2,4,-7,-1,-13],
  ....:                 [-1,0,1,4,-15],[-4,-13,26,8,30]])
  sage: A = (U^-1 * B * U).change_ring(ZZ)
  sage: ok, V = Similar(A, B); ok
  True
  sage: V
  [                 1    2824643/1601680   -6818729/1601680 -43439399/11211760  73108601/11211760]
  [                 0      342591/320336     -695773/320336  -2360063/11211760  -10291875/2242352]
  [                 0     -367393/640672      673091/640672    -888723/4484704   15889341/4484704]
  [                 0     661457/3203360    -565971/3203360  13485411/22423520 -69159661/22423520]
  [                 0   -4846439/3203360    7915157/3203360 -32420037/22423520 285914347/22423520]
  sage: ok, V = Similar(2*A, B); ok
  False

"""
