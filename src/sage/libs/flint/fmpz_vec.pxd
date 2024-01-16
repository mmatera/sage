# sage_setup: distribution = sagemath-flint
# distutils: libraries = flint
# distutils: depends = flint/fmpz_vec.h

################################################################################
# This file is auto-generated by the script
#   SAGE_ROOT/src/sage_setup/autogen/flint_autogen.py.
# Do not modify by hand! Fix and rerun the script instead.
################################################################################

from libc.stdio cimport FILE
from sage.libs.gmp.types cimport *
from sage.libs.mpfr.types cimport *
from sage.libs.flint.types cimport *

cdef extern from "flint_wrap.h":
    fmpz * _fmpz_vec_init(slong len) noexcept
    void _fmpz_vec_clear(fmpz * vec, slong len) noexcept
    void _fmpz_vec_randtest(fmpz * f, flint_rand_t state, slong len, flint_bitcnt_t bits) noexcept
    void _fmpz_vec_randtest_unsigned(fmpz * f, flint_rand_t state, slong len, flint_bitcnt_t bits) noexcept
    slong _fmpz_vec_max_bits(const fmpz * vec, slong len) noexcept
    slong _fmpz_vec_max_bits_ref(const fmpz * vec, slong len) noexcept
    void _fmpz_vec_sum_max_bits(slong * sumabs, slong * maxabs, const fmpz * vec, slong len) noexcept
    mp_size_t _fmpz_vec_max_limbs(const fmpz * vec, slong len) noexcept
    void _fmpz_vec_height(fmpz_t height, const fmpz * vec, slong len) noexcept
    slong _fmpz_vec_height_index(const fmpz * vec, slong len) noexcept
    int _fmpz_vec_fread(FILE * file, fmpz ** vec, slong * len) noexcept
    int _fmpz_vec_read(fmpz ** vec, slong * len) noexcept
    int _fmpz_vec_fprint(FILE * file, const fmpz * vec, slong len) noexcept
    int _fmpz_vec_print(const fmpz * vec, slong len) noexcept
    void _fmpz_vec_get_nmod_vec(mp_ptr res, const fmpz * poly, slong len, nmod_t mod) noexcept
    void _fmpz_vec_set_nmod_vec(fmpz * res, mp_srcptr poly, slong len, nmod_t mod) noexcept
    void _fmpz_vec_get_fft(mp_limb_t ** coeffs_f, const fmpz * coeffs_m, slong l, slong length) noexcept
    void _fmpz_vec_set_fft(fmpz * coeffs_m, slong length, const mp_ptr * coeffs_f, slong limbs, slong sign) noexcept
    slong _fmpz_vec_get_d_vec_2exp(double * appv, const fmpz * vec, slong len) noexcept
    void _fmpz_vec_set(fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_swap(fmpz * vec1, fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_zero(fmpz * vec, slong len) noexcept
    void _fmpz_vec_neg(fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_scalar_abs(fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    bint _fmpz_vec_equal(const fmpz * vec1, const fmpz * vec2, slong len) noexcept
    bint _fmpz_vec_is_zero(const fmpz * vec, slong len) noexcept
    void _fmpz_vec_max(fmpz * vec1, const fmpz * vec2, const fmpz * vec3, slong len) noexcept
    void _fmpz_vec_max_inplace(fmpz * vec1, const fmpz * vec2, slong len) noexcept
    void _fmpz_vec_sort(fmpz * vec, slong len) noexcept
    void _fmpz_vec_add(fmpz * res, const fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_sub(fmpz * res, const fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_scalar_mul_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t x) noexcept
    void _fmpz_vec_scalar_mul_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_mul_ui(fmpz * vec1, const fmpz * vec2, slong len2, ulong c) noexcept
    void _fmpz_vec_scalar_mul_2exp(fmpz * vec1, const fmpz * vec2, slong len2, ulong exp) noexcept
    void _fmpz_vec_scalar_divexact_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t x) noexcept
    void _fmpz_vec_scalar_divexact_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_divexact_ui(fmpz * vec1, const fmpz * vec2, slong len2, ulong c) noexcept
    void _fmpz_vec_scalar_fdiv_q_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t c) noexcept
    void _fmpz_vec_scalar_fdiv_q_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_fdiv_q_ui(fmpz * vec1, const fmpz * vec2, slong len2, ulong c) noexcept
    void _fmpz_vec_scalar_fdiv_q_2exp(fmpz * vec1, const fmpz * vec2, slong len2, ulong exp) noexcept
    void _fmpz_vec_scalar_fdiv_r_2exp(fmpz * vec1, const fmpz * vec2, slong len2, ulong exp) noexcept
    void _fmpz_vec_scalar_tdiv_q_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t c) noexcept
    void _fmpz_vec_scalar_tdiv_q_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_tdiv_q_ui(fmpz * vec1, const fmpz * vec2, slong len2, ulong c) noexcept
    void _fmpz_vec_scalar_tdiv_q_2exp(fmpz * vec1, const fmpz * vec2, slong len2, ulong exp) noexcept
    void _fmpz_vec_scalar_addmul_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_addmul_ui(fmpz * vec1, const fmpz * vec2, slong len2, ulong c) noexcept
    void _fmpz_vec_scalar_addmul_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t c) noexcept
    void _fmpz_vec_scalar_addmul_si_2exp(fmpz * vec1, const fmpz * vec2, slong len2, slong c, ulong exp) noexcept
    void _fmpz_vec_scalar_submul_fmpz(fmpz * vec1, const fmpz * vec2, slong len2, const fmpz_t x) noexcept
    void _fmpz_vec_scalar_submul_si(fmpz * vec1, const fmpz * vec2, slong len2, slong c) noexcept
    void _fmpz_vec_scalar_submul_si_2exp(fmpz * vec1, const fmpz * vec2, slong len2, slong c, ulong e) noexcept
    void _fmpz_vec_sum(fmpz_t res, const fmpz * vec, slong len) noexcept
    void _fmpz_vec_prod(fmpz_t res, const fmpz * vec, slong len) noexcept
    void _fmpz_vec_scalar_mod_fmpz(fmpz * res, const fmpz * vec, slong len, const fmpz_t p) noexcept
    void _fmpz_vec_scalar_smod_fmpz(fmpz * res, const fmpz * vec, slong len, const fmpz_t p) noexcept
    void _fmpz_vec_content(fmpz_t res, const fmpz * vec, slong len) noexcept
    void _fmpz_vec_content_chained(fmpz_t res, const fmpz * vec, slong len, const fmpz_t input) noexcept
    void _fmpz_vec_lcm(fmpz_t res, const fmpz * vec, slong len) noexcept
    void _fmpz_vec_dot(fmpz_t res, const fmpz * vec1, const fmpz * vec2, slong len2) noexcept
    void _fmpz_vec_dot_ptr(fmpz_t res, const fmpz * vec1, fmpz ** const vec2, slong offset, slong len) noexcept
