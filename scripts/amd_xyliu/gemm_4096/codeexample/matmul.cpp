/*
Copyright (c) 2015-present Advanced Micro Devices, Inc. All rights reserved.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

#include <hip/hip_runtime.h>
#include <cstdio>
#include <vector>
#include <cassert>
#include <algorithm>
#include <cmath>
#include "validation.h"

// We're going to compute D = A x B + C, where
// A: a M x K matrix
// B: a K x N matrix
// C, D: M x N matrices

// First attempt: all square matrices, C is the null matrix and can be ignored.
// Data type: 16bit float input, 32bit float output
// All matrices are row-major

// Figuring out the mapping of input/output matrix elements to registers is
// highly non-trivial. Joe Greathouse's "AMD Matrix Instruction Calculator"
// at https://github.com/RadeonOpenCompute/amd_matrix_instruction_calculator/
// simplifies this considerably. To figure out the mapping for input matrices A
// and B and output matrix D, we use the following commands:
//
//   ./matrix_calculator.py -a mi200 -i v_mfma_f32_16x16x16f16 -R -A
//   ./matrix_calculator.py -a mi200 -i v_mfma_f32_16x16x16f16 -R -B
//   ./matrix_calculator.py -a mi200 -i v_mfma_f32_16x16x16f16 -R -D

constexpr int M = 4096;
constexpr int N = 4096;
constexpr int K = 4096;

constexpr int LDA = K;
constexpr int LDB = N;
constexpr int LDD = N;

constexpr int A_size = M * LDA;
constexpr int B_size = K * LDB;
constexpr int D_size = M * LDD;


// C++23 defines a 16bit float: float16_t. Our version of LLVM/clang doesn't support C++23 yet.
// The HIP include files define a 16bit float type to: _Float16. We'll use that here.

using hfloat = _Float16;

__global__ void hgemm_16x16x16(const hfloat* A, const hfloat* B, float* D){
  using hfloat4 = __attribute__((__vector_size__(4 * sizeof(hfloat)))) hfloat;
  using float4 = __attribute__((__vector_size__(4 * sizeof(float)))) float;

  hfloat4 a = {0};                 // use 4 half-registers times 64 lanes for input A
  hfloat4 b = {0};                 // similarly for input B
  float4 result = {0};             // use 4 (full) registers times 64 lanes for output D.

  for(int i = 0; i < 4; ++i){      // iterate over 4 input/output half-registers (2 registers)
    const int a_idx =              // for matrix A:
      threadIdx.x * LDA            // consecutive threads cover 16 consecutive rows
      + 4 * threadIdx.y            // groups of 16 lanes skip 4 colums
      + i;                         // consecutive half-registers take consecutive columns
    
    const int b_idx =              // for matrix B:
      threadIdx.x                  // consecutive threads cover 16 consecutive columns
      + i * LDB                    // consecutive half-registers take consecutive rows of 16 hfloats
      + threadIdx.y * 4 * LDB;     // groups of 16 lanes skip 4 rows (128 hfloats)

    a[i] = A[a_idx];    
    b[i] = B[b_idx];
  }

  result = __builtin_amdgcn_mfma_f32_16x16x16f16(a, b, result, 0, 0, 0);
  #pragma unroll 4
  for(int i = 0; i < 4; ++i){      // iterate over 4 output registers
    const int d_idx =  threadIdx.x // consecutive threads cover 16 consecutive columns
      + i * LDD                    // consecutive registers take consecutive rows of 16 floats
      + threadIdx.y * 4 * LDD;     // groups of 16 lanes skip 4 rows (128 floats)
    
    D[d_idx] = result[i];
  }
}


int main(){
  std::vector<hfloat> A_h(A_size);
  std::generate(A_h.begin(), A_h.end(), [n=0] () mutable { return sinf(2 * M_PI * ((float)n++ / A_size)); });
  std::vector<hfloat> B_h(B_size);
  std::copy(A_h.crbegin(), A_h.crend(), B_h.begin());
  auto Gold_h = gemm_host<hfloat, float>(A_h, B_h, M, N, K, LDA, LDB, LDD);

  hfloat* A_d;  hipMalloc(&A_d, A_size * sizeof(hfloat));
  hfloat* B_d;  hipMalloc(&B_d, B_size * sizeof(hfloat));
  float* D_d;  hipMalloc(&D_d, D_size * sizeof(float));
  hipMemcpy(A_d, A_h.data(), A_size * sizeof(hfloat), hipMemcpyHostToDevice);
  hipMemcpy(B_d, B_h.data(), B_size * sizeof(hfloat), hipMemcpyHostToDevice);

  hipLaunchKernelGGL(hgemm_16x16x16, 1, dim3(16,4), 0, 0, A_d, B_d, D_d);
  hipDeviceSynchronize();
  std::vector<float> D_h(D_size);
  hipMemcpy(D_h.data(), D_d, D_size * sizeof(float), hipMemcpyDeviceToHost);

  printf("Sum of squared differences of host/device result matrices: %e\n", sum_sqr_diff(M, N, Gold_h, LDD, D_h, LDD));

  hipFree(D_d); hipFree(B_d); hipFree(A_d);

  for(int i = 0; i != 16; ++i){
    for(int j = 0; j != 16; ++j){
      printf("Gold_h[%02d][%02d] = %f  D_h[%02d][%02d] = %f, diff = %e\n",
	     i, j, Gold_h[16*i+j],
	     i, j, D_h[16*i+j],
	     Gold_h[16*i+j] - D_h[16*i+j]);
    }
    printf("\n");
  }

  return 0;
}
