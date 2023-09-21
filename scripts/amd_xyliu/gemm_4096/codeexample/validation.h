#ifndef __VALIDATION_H__
#define __VALIDATION_H__

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

#include <vector>

template<typename T, typename U=T>
std::vector<U> gemm_host(const std::vector<T>& A, const std::vector<T>& B,
			 int M, int N, int K, int LDA, int LDB, int LDD){
  std::vector<U> D(M*LDD);
  for(int row = 0; row != M; ++row){
    for(int col = 0; col != N; ++col){
      U dot = 0.0;
      int A_idx = row * LDA;
      int B_idx = col;
      for(int i = 0; i != K; ++i){
        dot += static_cast<U>(A[A_idx]) * static_cast<U>(B[B_idx]);
        ++A_idx;
        B_idx += LDB;
      }
      D[row * LDD + col] = dot;
    }
  }
  return D;
}

template<typename T>
float sum_sqr_diff(int N, int M,
                   const std::vector<T>& A, int LDA,
                   const std::vector<T>& B, int LDB){
  assert(A.size() == M*LDA);
  assert(B.size() == M*LDB);
  T sum = 0;
  for(int j = 0; j < M; ++j){
    for(int i = 0; i < N; ++i){
      sum += (A[i+j*LDA] - B[i+j*LDB]) * (A[i+j*LDA] - B[i+j*LDB]);
    }
  }
  return sum;
}

#endif // __VALIDATION_H__
