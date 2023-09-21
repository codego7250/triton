import torch

import triton
import triton.language as tl

import random
import argparse
import traceback
from itertools import product

def debug_config(kwargs):
    #print(kwargs)
    pass

def gen_tune_config():
    m_range = [32, 64]
    n_range = [32, 64]
    k_range = [32, 64, 128]
    stages = [1,2,3,4,5,6]
    warps = [4, 8, 16]
    g_range = [2,4,8,16]
    grid_dim_range = [128, 208, 256, 312, 416, 512]
    split_k_range = [1, 2, 4, 8, 16]
    configs = []
    for m,n,k,g,s,w,griddim,splitk in product(m_range, n_range, k_range, g_range, stages, warps, grid_dim_range, split_k_range):
        configs.append(triton.Config({'BLOCK_M':m, 'BLOCK_N':n, 'BLOCK_K':k, 'GROUP_M':g, 'GRID_DIM':griddim, 'SPLIT_K':splitk}, num_stages=s, num_warps=w, pre_hook=debug_config))

    return configs


@triton.autotune(
    # configs=gen_tune_config(),
    configs=[
       triton.Config({'BLOCK_M': 32, 'BLOCK_N': 32, 'BLOCK_K': 32, 'SPLIT_K': 16, 'GROUP_M': 4, 'GRID_DIM':128}, num_stages=1, num_warps=2),
       triton.Config({'BLOCK_M': 32, 'BLOCK_N': 32, 'BLOCK_K': 32, 'SPLIT_K': 1, 'GROUP_M': 4, 'GRID_DIM':416}, num_stages=1, num_warps=4),
       triton.Config({'BLOCK_M': 64, 'BLOCK_N': 32, 'BLOCK_K': 32, 'SPLIT_K': 4, 'GROUP_M': 4, 'GRID_DIM':208}, num_stages=1, num_warps=2),
       triton.Config({'BLOCK_M': 64, 'BLOCK_N': 32, 'BLOCK_K': 32, 'SPLIT_K': 1, 'GROUP_M': 4, 'GRID_DIM':416}, num_stages=1, num_warps=4),
       triton.Config({'BLOCK_M': 128, 'BLOCK_N': 64, 'BLOCK_K': 32, 'SPLIT_K': 1, 'GROUP_M': 4, 'GRID_DIM':312}, num_stages=1, num_warps=4),
       triton.Config({'BLOCK_M': 128, 'BLOCK_N': 64, 'BLOCK_K': 32, 'SPLIT_K': 1, 'GROUP_M': 4, 'GRID_DIM':416}, num_stages=1, num_warps=4),
    ],
    key=['K', 'N'],
)
@triton.heuristics({
    'EVEN_K': lambda args: args['K'] % args['BLOCK_K'] == 0,
})
@triton.jit
def grouped_gemm_kernel(num_of_matrix,
        N, K,
        alpha, beta,
        params,
        NUM_PARAMS: tl.constexpr,
        DTYPE: tl.constexpr,
        ACC_DTYPE: tl.constexpr,
        BETA_ZERO: tl.constexpr,
        TRANS_A: tl.constexpr, TRANS_B: tl.constexpr,
        BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
        GROUP_M: tl.constexpr, EVEN_K: tl.constexpr, SPLIT_K: tl.constexpr,
        GRID_DIM: tl.constexpr,
    ):
    pid = tl.program_id(0)
    pid_k = tl.program_id(1)

    num_pids = tl.num_programs(0)

    # reset DTYPE, because it is tl.constexpr, can't be used in tl.pointer_type
    if DTYPE == tl.constexpr(tl.float16):
        DTYPE = tl.float16
    else:
        DTYPE = tl.float32

    grid_n = (N + BLOCK_N - 1) // BLOCK_N 

    matrix_start = 0
    i = 0
    while i < num_of_matrix:
        offset = NUM_PARAMS * i
        M = tl.load(params + offset).to(tl.int32)
        grid_m = (M + BLOCK_M - 1) // BLOCK_M
        tile_num = grid_m * grid_n
        next_matrix_start = matrix_start + tile_num
        while pid >= matrix_start and pid < next_matrix_start:

            A = tl.load(params + offset + 1).to(tl.pointer_type(DTYPE))
            lda = tl.load(params + offset + 2).to(tl.int32)
            B = tl.load(params + offset + 3).to(tl.pointer_type(DTYPE))
            ldb = tl.load(params + offset + 4).to(tl.int32)
            C = tl.load(params + offset + 5).to(tl.pointer_type(DTYPE))
            ldc = tl.load(params + offset + 6).to(tl.int32)
            D = tl.load(params + offset + 7).to(tl.pointer_type(DTYPE))
            ldd = tl.load(params + offset + 8).to(tl.int32)

            new_pid = pid - matrix_start

            # re-order program ID for better L2 performance
            width = GROUP_M * grid_m
            group_id = new_pid // width
            group_size = min(grid_n - group_id * GROUP_M, GROUP_M)
            pid_n = group_id * GROUP_M + (new_pid % group_size)
            pid_m = (new_pid % width) // (group_size)
            # do matrix multiplication
            rm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
            rn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
            rk = pid_k * BLOCK_K + tl.arange(0, BLOCK_K)
            ram = tl.max_contiguous(tl.multiple_of(rm % M, BLOCK_M), BLOCK_M)
            rbn = tl.max_contiguous(tl.multiple_of(rn % N, BLOCK_N), BLOCK_N)
            # pointers
            if TRANS_A == 1:
                A = A + (ram[None, :] * lda + rk[:, None])  # KxM
            else:
                A = A + (ram[None, :] + rk[:, None] * lda)  # KxM

            if TRANS_B == 1:
                B = B + (rk[None, :] * ldb + rbn[:, None])  # NxK
            else:
                B = B + (rk[None, :] + rbn[:, None] * ldb)  # NxK

            acc = tl.zeros((BLOCK_N, BLOCK_M), dtype=ACC_DTYPE)
            for k in range(0, tl.cdiv(K, BLOCK_K * SPLIT_K)):
                if EVEN_K:
                    a = tl.load(A)
                    b = tl.load(B)
                else:
                    k_remaining = K - k * BLOCK_K * SPLIT_K
                    if TRANS_A == 1:
                        a = tl.load(A, mask=rk[:, None] < k_remaining, other=0.)
                    else:
                        a = tl.load(A, mask=rk[:, None] < k_remaining, other=0.)

                    if TRANS_B == 1:
                        b = tl.load(B, mask=rk[None, :] < k_remaining, other=0.)
                    else:
                        b = tl.load(B, mask=rk[None, :] < k_remaining, other=0.)

                # do compute
                acc += tl.dot(b, a)

                if TRANS_A == 1:
                    A += BLOCK_K * SPLIT_K
                else:
                    A += BLOCK_K * SPLIT_K * lda

                if TRANS_B == 1:
                    B += BLOCK_K * SPLIT_K * ldb
                else:
                    B += BLOCK_K * SPLIT_K

            # rematerialize rm and rn to save registers
            rm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
            rn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
            C = C + (rm[None, :] + rn[:, None] * ldc)
            mask = (rm < M)[None, :] & (rn < N)[:, None]
            if BETA_ZERO:
                acc = acc * alpha
            else:
                c = tl.load(C, mask=mask)
                # compute alpha * AB + beta * C
                acc = acc * alpha + beta * c

            acc = acc.to(D.dtype.element_ty)
            D = D + (rm[None, :] + rn[:, None] * ldd)
            if SPLIT_K == 1:
                tl.store(D, acc, mask=mask)
            else:
                tl.atomic_add(D, acc, mask=mask)
            pid += num_pids

        matrix_start = next_matrix_start
        i += 1


def triton_grouped_gemm(alpha, array_a, array_b, beta, array_c):
    """
    grouped gemm's signature is (trans_a, trans_b
                             vector<> m, vector<> n, vector<> k
                             vector<> alpha,
                             vector<> A, vector<> lda, vector<> B, vector<> ldb,
                             vector<> beta,
                             vector<> C, vector<> ldc,
                             vector<> D, vector<> ldd,
                             int gemm_count,
                             )
    where D[i] = alpha * A[i]*B[i] + beta * C[i], i = [0, gemm_count).
    A,B,C,D are in column-major format, then lda, ldb is the number of elements in one line.

    Here we use a list of tensor: array_a, array_b, array_c for vector of A, B, C pointers, and use the tensor shape for m, n, k

    To simplify the problem, we do some assumptions:
        1. all n in vector<> n are same, k in vector<> k are same, only m is variant. 
        2. all tensor have same layout, then only need 1 trans_a and 1 trans_b
        3. C has already been added into D with shape (m,n), so we compute C[i] = alpha * A[i]B[i] + beta *C[i]
        4. tensor a,b,c are all row-major. a shape is MxK, b shape is KxN, c shape is MxN

    """
    a = array_a[0]
    device = a.device
    M = a.shape[0]
    K = a.shape[1]

    params = []
    trans_a = 0
    trans_b = 0

    for a,b,c in zip(array_a, array_b, array_c):
        M = a.shape[0]
        K = a.shape[1]
        N = b.shape[1]
        # n_sizes.append(N)

        # all parameters
        params.append(N)
        params.append(b.data_ptr())
        params.append(N)
        params.append(a.data_ptr())
        params.append(K)
        params.append(c.data_ptr())
        params.append(N)
        params.append(c.data_ptr())
        params.append(N)
        # params.append(triton.cdiv(M, BLOCK_M) * triton.cdiv(N, BLOCK_N))
        # pad to 16 elements
        params.extend([N, N, N, N, N, N, N])

    # convert list into cuda tensors
    params_tensor = torch.tensor(tuple(params), dtype=torch.int64, device=device)
    
    grid = lambda META: (META['GRID_DIM'], META['SPLIT_K'])
    grouped_gemm_kernel[grid](len(array_a),
                  M, K,
                  alpha, beta,
                  params_tensor, 16,
                  DTYPE=tl.float32 if array_a[0].dtype == torch.float32 else tl.float16,
                  ACC_DTYPE=tl.float32,
                  BETA_ZERO=(beta == 0.0),  # beta is zero
                  TRANS_A=trans_b, TRANS_B=trans_a,  # 0 for N, 1 for T
                  )
    return array_c

def triton_groupedgemm_wrap(list_a, list_b):
    """
    list_a is a list of tensor a, with shape MxK, where M may be different.
    b is a tensor, with shape KxN.
    """
    array_a = []
    array_b = []
    array_c = []
    for a,b in zip(list_a, list_b):
      array_a.append(a)
      array_b.append(b)
      M,K = a.shape[0], a.shape[1]
      K1,N = b.shape[0], b.shape[1]
      assert K == K1
      c = torch.zeros((M, N), device=a.device, dtype=a.dtype)
      array_c.append(c)

    triton_grouped_gemm(1.0, array_a, array_b, 0.0, array_c)

    return array_c

def torch_grouped_gemm(list_a, list_b):
    list_c = []
    for a, b in zip(list_a, list_b):
        c = torch.matmul(a, b)
        list_c.append(c)
    return list_c

def test_speed(mnk_array, device, dtype):
    a_list = []
    b_list = []
    max_m, max_n, max_k = 0, 0, 0
    # generate input data for triton
    for (m, n, k) in mnk_array:
        a_list.append(torch.randn(m, k, device=device, dtype=dtype))
        b_list.append(torch.randn(k, n, device=device, dtype=dtype))
        max_m = max(max_m, m)
        max_n = max(max_n, n)
        max_k = max(max_k, k)

    batch = len(a_list)
    aligned = 16
    max_m = (max_m // aligned + 1) * aligned
    max_n = (max_n // aligned + 1) * aligned
    max_k = (max_k // aligned + 1) * aligned

    # generate aligned input data for torch
    A_torch = torch.randn(batch, max_m, max_k, device=device, dtype=dtype)
    B_torch = torch.randn(batch, max_k, max_n, device=device, dtype=dtype)

    print('torch: ', triton.testing.do_bench(lambda: torch.matmul(A_torch, B_torch)))
    print('triton: ', triton.testing.do_bench(lambda: triton_groupedgemm_wrap(a_list, b_list)))


def compare(mnk_array, device, dtype):
    a_list = []
    b_list = []
    # generate input data for triton
    for (m, n, k) in mnk_array:
        a_list.append(torch.randn(m, k, device=device, dtype=dtype))
        b_list.append(torch.randn(k, n, device=device, dtype=dtype))

    # compare results
    triton_res = triton_groupedgemm_wrap(a_list, b_list)
    torch_res = torch_grouped_gemm(a_list, b_list)
    for t1, t2 in zip(triton_res, torch_res):
        if torch.allclose(t1, t2):
            print('dtype: ', dtype, ' shape: ', t1.shape, ' SAME')
        else:
            diff = abs(t1 - t2)
            print('dtype: ', dtype, ' shape: ', t1.shape, ' max diff: ', diff.max(), ' rel-diff: ', (diff / t2).max())
            #print('triton: ', t1)
            #print('torch: ', t2)

def get_arges():
    parser = argparse.ArgumentParser(description="PyTorch Template Finetune Example")
    parser.add_argument('--fp16', action='store_true', default=False)
    parser.add_argument('--compare', action='store_true', default=False)

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_arges()
    batch=16
    M_start = 64
    M_end = 4096
    M = []
    N = 2048
    K = 1024
    row1 = []
    for i in range(batch):
        m = random.randint(M_start, M_end)
        row1.append([m, N, K])

    row2 = [[768,1,4608], [768,1,4608]]
    row3 = [[4608,1,384], [4608,1,384]]
    row6 = [ [ 768, 2, 4608], [ 768, 1, 4608], [ 768, 1, 4608], [ 768, 1, 4608], [ 768, 1, 4608], [ 768, 1, 4608], [ 768, 3, 4608], [ 768, 4, 4608], [ 768, 3, 4608], [ 768, 5, 4608], [ 768, 2, 4608], [ 768, 4, 4608], [ 768, 2, 4608], [ 768, 1, 4608], [ 768, 1, 4608]]
    row7 = [[4608, 2, 384], [4608, 1, 384], [4608, 1, 384], [4608, 1, 384], [4608, 1, 384], [4608, 1, 384], [4608, 3, 384], [4608, 4, 384], [4608, 3, 384], [4608, 5, 384], [4608, 2, 384], [4608, 4, 384], [4608, 2, 384], [4608, 1, 384], [4608, 1, 384]]
    row8 = [[768, 167, 4608], [768, 183, 4608], [768, 177, 4608], [768, 181, 4608], [768, 153, 4608], [768, 139, 4608], [768, 156, 4608], [768, 173, 4608], [768, 163, 4608], [768, 150, 4608], [768, 204, 4608], [768, 184, 4608], [768, 168, 4608], [768, 156, 4608], [768, 168, 4608], [768, 148, 4608]]
    row9 = [[4608, 167, 384], [4608, 183, 384], [4608, 177, 384], [4608, 181, 384], [4608, 153, 384], [4608, 139, 384], [4608, 156, 384], [4608, 173, 384], [4608, 163, 384], [4608, 150, 384], [4608, 204, 384], [4608, 184, 384], [4608, 168, 384], [4608, 156, 384], [4608, 168, 384], [4608, 148, 384]]

    device = torch.device(0)
    torch.cuda.manual_seed(42)
    dtype = torch.float32
    if args.fp16:
        dtype = torch.float16

    for i, mnk in enumerate([row2, row3, row6, row7, row8, row9]):
        print('test row ', i)
        if args.compare:
            compare(mnk, device, dtype)
        test_speed(mnk, device, dtype)
