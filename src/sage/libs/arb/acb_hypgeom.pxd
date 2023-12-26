# sage_setup: distribution = sagemath-flint
# distutils: libraries = gmp flint
# distutils: depends = acb_hypgeom.h

from sage.libs.arb.types cimport *

# acb_hypgeom.h
cdef extern from "arb_wrap.h":
    void acb_hypgeom_pfq_bound_factor(mag_t C, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, unsigned long n)
    long acb_hypgeom_pfq_choose_n(acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long prec)
    void acb_hypgeom_pfq_sum_forward(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    void acb_hypgeom_pfq_sum_rs(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    void acb_hypgeom_pfq_sum_bs(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    void acb_hypgeom_pfq_sum_fme(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    void acb_hypgeom_pfq_sum(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    void acb_hypgeom_pfq_sum_bs_invz(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t w, long n, long prec)
    void acb_hypgeom_pfq_sum_invz(acb_t s, acb_t t, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, const acb_t w, long n, long prec)
    void acb_hypgeom_pfq_direct(acb_t res, acb_srcptr a, long p, acb_srcptr b, long q, const acb_t z, long n, long prec)
    # void acb_hypgeom_pfq_series_direct(acb_poly_t res, const acb_poly_struct * a, long p, const acb_poly_struct * b, long q, const acb_poly_t z, int regularized, long n, long len, long prec)
    void acb_hypgeom_u_asymp(acb_t res, const acb_t a, const acb_t b, const acb_t z, long n, long prec)
    bint acb_hypgeom_u_use_asymp(const acb_t z, long prec)
    # void acb_hypgeom_u_1f1_series(acb_poly_t res, const acb_poly_t a, const acb_poly_t b, const acb_poly_t z, long len, long prec)
    void acb_hypgeom_u_1f1(acb_t res, const acb_t a, const acb_t b, const acb_t z, long prec)
    void acb_hypgeom_u(acb_t res, const acb_t a, const acb_t b, const acb_t z, long prec)
    void acb_hypgeom_m_asymp(acb_t res, const acb_t a, const acb_t b, const acb_t z, bint regularized, long prec)
    void acb_hypgeom_m_1f1(acb_t res, const acb_t a, const acb_t b, const acb_t z, bint regularized, long prec)
    void acb_hypgeom_m(acb_t res, const acb_t a, const acb_t b, const acb_t z, bint regularized, long prec)
    void acb_hypgeom_erf_1f1a(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_erf_1f1b(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_erf_asymp(acb_t res, const acb_t z, long prec, long prec2)
    void acb_hypgeom_erf(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_erfc(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_erfi(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_bessel_j_asymp(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_j_0f1(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_j(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_jy(acb_t res1, acb_t res2, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_y(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_i_asymp(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_i_0f1(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_i(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_k_asymp(acb_t res, const acb_t nu, const acb_t z, long prec)
    # void acb_hypgeom_bessel_k_0f1_series(acb_poly_t res, const acb_poly_t nu, const acb_poly_t z, long len, long prec)
    void acb_hypgeom_bessel_k_0f1(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_bessel_k(acb_t res, const acb_t nu, const acb_t z, long prec)
    void acb_hypgeom_gamma_upper_asymp(acb_t res, const acb_t s, const acb_t z, bint modified, long prec)
    void acb_hypgeom_gamma_upper_1f1a(acb_t res, const acb_t s, const acb_t z, bint modified, long prec)
    void acb_hypgeom_gamma_upper_1f1b(acb_t res, const acb_t s, const acb_t z, bint modified, long prec)
    void acb_hypgeom_gamma_upper_singular(acb_t res, long s, const acb_t z, bint modified, long prec)
    void acb_hypgeom_gamma_upper(acb_t res, const acb_t s, const acb_t z, bint modified, long prec)
    void acb_hypgeom_expint(acb_t res, const acb_t s, const acb_t z, long prec)
    void acb_hypgeom_ei_asymp(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_ei_2f2(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_ei(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_si_asymp(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_si_1f2(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_si(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_ci_asymp(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_ci_2f3(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_ci(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_shi(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_chi_asymp(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_chi_2f3(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_chi(acb_t res, const acb_t z, long prec)
    void acb_hypgeom_li(acb_t res, const acb_t z, int offset, long prec)
    void acb_hypgeom_0f1(acb_t res, const acb_t b, const acb_t z, bint regularized, long prec)
    void acb_hypgeom_2f1(acb_t res, const acb_t a, const acb_t b, const acb_t z, const acb_t z, bint regularized, long prec)
    void acb_hypgeom_legendre_p(acb_t res, const acb_t n, const acb_t m, const acb_t z, int type, long prec)
    void acb_hypgeom_legendre_q(acb_t res, const acb_t n, const acb_t m, const acb_t z, int type, long prec)
    void acb_hypgeom_jacobi_p(acb_t res, const acb_t n, const acb_t a, const acb_t b, const acb_t z, long prec)
    void acb_hypgeom_gegenbauer_c(acb_t res, const acb_t n, const acb_t m, const acb_t z, long prec)
    void acb_hypgeom_laguerre_l(acb_t res, const acb_t n, const acb_t m, const acb_t z, long prec)
    void acb_hypgeom_hermite_h(acb_t res, const acb_t n, const acb_t z, long prec)
    void acb_hypgeom_chebyshev_t(acb_t res, const acb_t n, const acb_t z, long prec)
    void acb_hypgeom_chebyshev_u(acb_t res, const acb_t n, const acb_t z, long prec)
    void acb_hypgeom_spherical_y(acb_t res, long n, long m, const acb_t theta, const acb_t phi, long prec)
    void acb_hypgeom_airy(acb_t ai, acb_t aip, acb_t bi, acb_t bip, const acb_t z, long prec)

from sage.libs.flint.acb_hypgeom cimport (
    acb_hypgeom_pfq_bound_factor,
    acb_hypgeom_pfq_choose_n,
    acb_hypgeom_pfq_sum_forward,
    acb_hypgeom_pfq_sum_rs,
    acb_hypgeom_pfq_sum_bs,
    acb_hypgeom_pfq_sum_fme,
    acb_hypgeom_pfq_sum,
    acb_hypgeom_pfq_sum_bs_invz,
    acb_hypgeom_pfq_sum_invz,
    acb_hypgeom_pfq_direct,
    acb_hypgeom_pfq_series_direct,
    acb_hypgeom_u_asymp,
    acb_hypgeom_u_use_asymp,
    acb_hypgeom_u_1f1_series,
    acb_hypgeom_u_1f1,
    acb_hypgeom_u,
    acb_hypgeom_m_asymp,
    acb_hypgeom_m_1f1,
    acb_hypgeom_m,
    acb_hypgeom_erf_1f1a,
    acb_hypgeom_erf_1f1b,
    acb_hypgeom_erf_asymp,
    acb_hypgeom_erf,
    acb_hypgeom_erfc,
    acb_hypgeom_erfi,
    acb_hypgeom_bessel_j_asymp,
    acb_hypgeom_bessel_j_0f1,
    acb_hypgeom_bessel_j,
    acb_hypgeom_bessel_jy,
    acb_hypgeom_bessel_y,
    acb_hypgeom_bessel_i_asymp,
    acb_hypgeom_bessel_i_0f1,
    acb_hypgeom_bessel_i,
    acb_hypgeom_bessel_k_asymp,
    acb_hypgeom_bessel_k_0f1_series,
    acb_hypgeom_bessel_k_0f1,
    acb_hypgeom_bessel_k,
    acb_hypgeom_gamma_upper_asymp,
    acb_hypgeom_gamma_upper_1f1a,
    acb_hypgeom_gamma_upper_1f1b,
    acb_hypgeom_gamma_upper_singular,
    acb_hypgeom_gamma_upper,
    acb_hypgeom_expint,
    acb_hypgeom_ei_asymp,
    acb_hypgeom_ei_2f2,
    acb_hypgeom_ei,
    acb_hypgeom_si_asymp,
    acb_hypgeom_si_1f2,
    acb_hypgeom_si,
    acb_hypgeom_ci_asymp,
    acb_hypgeom_ci_2f3,
    acb_hypgeom_ci,
    acb_hypgeom_shi,
    acb_hypgeom_chi_asymp,
    acb_hypgeom_chi_2f3,
    acb_hypgeom_chi,
    acb_hypgeom_li,
    acb_hypgeom_0f1,
    acb_hypgeom_2f1,
    acb_hypgeom_legendre_p,
    acb_hypgeom_legendre_q,
    acb_hypgeom_jacobi_p,
    acb_hypgeom_gegenbauer_c,
    acb_hypgeom_laguerre_l,
    acb_hypgeom_hermite_h,
    acb_hypgeom_chebyshev_t,
    acb_hypgeom_chebyshev_u,
    acb_hypgeom_spherical_y,
    acb_hypgeom_airy)
