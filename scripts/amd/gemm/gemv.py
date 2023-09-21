from typing import Tuple
import argparse
import sys

import torch
import triton
import triton.language as tl
from torch.autograd.function import FunctionCtx


@triton.autotune(
    configs=[
        #triton.Config({"N_SIZE": 64}, num_warps=1, num_stages=1),
        #triton.Config({"N_SIZE": 32}, num_warps=1, num_stages=1),
        triton.Config({"N_SIZE": 16}, num_warps=1, num_stages=1),
        #triton.Config({"N_SIZE": 8}, num_warps=1, num_stages=1),
        #triton.Config({"N_SIZE": 4}, num_warps=1, num_stages=1),
        #triton.Config({"N_SIZE": 2}, num_warps=1, num_stages=1),
        #triton.Config({"N_SIZE": 1}, num_warps=1, num_stages=1),
    ],
    key=["vec_col_size", "matrix_row_size", "matrix_col_size", "output_col_size"],
)
@triton.jit
def vec_mat(
    vec_col_size: tl.constexpr,
    matrix_row_size: tl.constexpr,
    matrix_col_size: tl.constexpr,
    output_col_size: tl.constexpr,
    vec_ptr,
    vec_row_stride,
    vec_col_stride,
    matrix_ptr,
    matrix_row_stride,
    matrix_col_stride,
    output_ptr,
    output_row_stride,
    output_col_stride,
    SCALER: tl.constexpr,
    VEC_COL_ROUNDED_SIZE: tl.constexpr,
    N_SIZE: tl.constexpr,
):
    block_n_idx = tl.program_id(0)
    n_range_offs = tl.arange(0, N_SIZE)
    vec_col_rounded_range_offs = tl.arange(0, VEC_COL_ROUNDED_SIZE)

    vec_ptrs = vec_ptr + vec_col_stride * vec_col_rounded_range_offs[:, None]
    vec_ptr_mask = vec_col_rounded_range_offs[:, None] < vec_col_size
    vec = tl.load(pointer=vec_ptrs, mask=vec_ptr_mask, other=0.0).to(tl.float32)

    if SCALER != 1.0:
        vec = vec * SCALER

    matrix_ptrs = matrix_ptr + (
        vec_col_rounded_range_offs[:, None] * matrix_row_stride  # cols
        + (block_n_idx * N_SIZE + n_range_offs)[None, :] * matrix_col_stride  # rows
    )
    matrix_ptr_mask = (vec_col_rounded_range_offs[:, None] < matrix_row_size) & (
        (block_n_idx * N_SIZE + n_range_offs)[None, :] < matrix_col_size
    )
    matrix = tl.load(pointer=matrix_ptrs, mask=matrix_ptr_mask, other=0.0).to(tl.float32)

    result = vec * matrix
    result = tl.sum(input=result, axis=0)

    output_ptrs = output_ptr + (
        (block_n_idx * N_SIZE + n_range_offs) * output_col_stride
    )
    output_ptr_mask = (block_n_idx * N_SIZE + n_range_offs) < output_col_size
    tl.store(pointer=output_ptrs, value=result, mask=output_ptr_mask)


def vec_mat_wrapper(
    vec: torch.Tensor,
    matrix: torch.Tensor,
    output: torch.Tensor,
    scaler: float,
    transpose_mat: bool,
) -> torch.Tensor:
    """
    Matrix multiplication of a vector and a matrix:
    Oi = sum_j Vj * Mij
    If transpose_mat is True, the matrix is transposed:
    Oi = sum_j Vj * Mji
    @param vec: vector to multiply with the matrix
    @param matrix: matrix to multiply with the vector
    @param output: output tensor
    @param scaler: scaler to multiply the vector with before multiplication
    @param transpose_mat: whether to transpose the matrix before multiplication
    @return: output tensor
    """
    vec_cols = vec.shape[-1]
    out_cols = output.shape[-1]

    mat_rows, mat_cols = matrix.shape
    matrix_stride = list(matrix.stride())
    if transpose_mat:
        matrix_stride[-1], matrix_stride[-2] = matrix_stride[-2], matrix_stride[-1]
        mat_rows, mat_cols = mat_cols, mat_rows
    print(f"vec shape {vec.shape} output_shape {output.shape}")

    assert mat_cols == out_cols
    assert vec_cols == mat_rows

    #def grid(args) -> Tuple[int, int, int]:
    def grid(args) -> Tuple[int,int]:
        return triton.cdiv(mat_cols, args["N_SIZE"]),1

    vec_cols_pow_2 = triton.next_power_of_2(vec_cols)
    print(f"vec cols {vec_cols_pow_2}")

    vec_mat[grid](
        vec_cols,
        mat_rows,
        mat_cols,
        out_cols,
        vec,
        *vec.stride(),
        matrix,
        *matrix_stride,
        output,
        *output.stride(),
        scaler,
        vec_cols_pow_2,
    )
    return output

def tune_gemm(SIZE_M, SIZE_N, SIZE_K):
    assert SIZE_M == 1
    a = torch.randn((SIZE_M, SIZE_K), device='cuda', dtype=torch.float16)
    #a1d = a.flatten()
    b = torch.randn((SIZE_K, SIZE_N), device='cuda', dtype=torch.float16)
    c = torch.zeros((SIZE_M, SIZE_N), device=a.device, dtype=torch.float16)

    # call pytorch function to get golden
    golden = torch.matmul(a, b)
    golden = torch.matmul(a, b)
    golden = torch.matmul(a, b)
    rt = vec_mat_wrapper(a,b,c,1.0,False)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="tune a specific gemm size",
        allow_abbrev=False,
    )

    parser.add_argument("-m", type=int, default=argparse.SUPPRESS)
    parser.add_argument("-n", type=int, default=argparse.SUPPRESS)
    parser.add_argument("-k", type=int, default=argparse.SUPPRESS)
    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    M = args.m
    N = args.n
    K = args.k

    tune_gemm(M, N, K)

if __name__ == '__main__':
    sys.exit(main())
