; ModuleID = 'matmul-hip-amdgcn-amd-amdhsa-gfx90a.bc'
source_filename = "llvm-link"
target datalayout = "e-p:64:64-p1:64:64-p2:32:32-p3:32:32-p4:64:64-p5:32:32-p6:32:32-i64:64-v16:16-v24:32-v32:32-v48:64-v96:128-v192:256-v256:256-v512:512-v1024:1024-v2048:2048-n32:64-S32-A5-G1-ni:7"
target triple = "amdgcn-amd-amdhsa"

%"struct.__HIP_Coordinates<__HIP_ThreadIdx>::__X" = type { i8 }

$_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE = comdat any

$_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE = comdat any

@llvm.compiler.used = appending addrspace(1) global [2 x ptr] [ptr addrspacecast (ptr addrspace(4) @_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE to ptr), ptr addrspacecast (ptr addrspace(4) @_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE to ptr)], section "llvm.metadata"
@_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE = weak protected addrspace(4) externally_initialized constant %"struct.__HIP_Coordinates<__HIP_ThreadIdx>::__X" undef, comdat, align 1
@_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE = weak protected addrspace(4) externally_initialized constant %"struct.__HIP_Coordinates<__HIP_ThreadIdx>::__X" undef, comdat, align 1

; Function Attrs: convergent mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define protected amdgpu_kernel void @_Z14hgemm_16x16x16PKDF16_S0_Pf(ptr addrspace(1) nocapture readonly %0, ptr addrspace(1) nocapture readonly %1, ptr addrspace(1) nocapture writeonly %2) local_unnamed_addr #0 {
  %4 = tail call i32 @llvm.amdgcn.workitem.id.x(), !range !5
  %5 = shl nuw nsw i32 %4, 12
  %6 = tail call i32 @llvm.amdgcn.workitem.id.y(), !range !5
  %7 = shl nuw nsw i32 %6, 2
  %8 = or i32 %5, %7
  %9 = shl nuw nsw i32 %6, 14
  %10 = or i32 %9, %4
  %11 = zext i32 %8 to i64
  %12 = getelementptr inbounds half, ptr addrspace(1) %0, i64 %11
  %13 = zext i32 %10 to i64
  %14 = getelementptr inbounds half, ptr addrspace(1) %1, i64 %13
  %15 = load half, ptr addrspace(1) %14, align 2, !tbaa !6, !amdgpu.noclobber !10
  %16 = insertelement <4 x half> poison, half %15, i64 0
  %17 = or i32 %10, 4096
  %18 = load <2 x half>, ptr addrspace(1) %12, align 2, !tbaa !6
  %19 = zext i32 %17 to i64
  %20 = getelementptr inbounds half, ptr addrspace(1) %1, i64 %19
  %21 = load half, ptr addrspace(1) %20, align 2, !tbaa !6, !amdgpu.noclobber !10
  %22 = insertelement <4 x half> %16, half %21, i64 1
  %23 = or i32 %8, 2
  %24 = or i32 %10, 8192
  %25 = zext i32 %23 to i64
  %26 = getelementptr inbounds half, ptr addrspace(1) %0, i64 %25
  %27 = zext i32 %24 to i64
  %28 = getelementptr inbounds half, ptr addrspace(1) %1, i64 %27
  %29 = load half, ptr addrspace(1) %28, align 2, !tbaa !6, !amdgpu.noclobber !10
  %30 = insertelement <4 x half> %22, half %29, i64 2
  %31 = or i32 %10, 12288
  %32 = load <2 x half>, ptr addrspace(1) %26, align 2, !tbaa !6
  %33 = shufflevector <2 x half> %18, <2 x half> %32, <4 x i32> <i32 0, i32 1, i32 2, i32 3>
  %34 = zext i32 %31 to i64
  %35 = getelementptr inbounds half, ptr addrspace(1) %1, i64 %34
  %36 = load half, ptr addrspace(1) %35, align 2, !tbaa !6, !amdgpu.noclobber !10
  %37 = insertelement <4 x half> %30, half %36, i64 3
  %38 = tail call contract <4 x float> @llvm.amdgcn.mfma.f32.16x16x16f16(<4 x half> %33, <4 x half> %37, <4 x float> zeroinitializer, i32 0, i32 0, i32 0)
  %39 = extractelement <4 x float> %38, i64 0
  %40 = getelementptr inbounds float, ptr addrspace(1) %2, i64 %13
  store float %39, ptr addrspace(1) %40, align 4, !tbaa !11
  %41 = extractelement <4 x float> %38, i64 1
  %42 = getelementptr inbounds float, ptr addrspace(1) %2, i64 %19
  store float %41, ptr addrspace(1) %42, align 4, !tbaa !11
  %43 = extractelement <4 x float> %38, i64 2
  %44 = getelementptr inbounds float, ptr addrspace(1) %2, i64 %27
  store float %43, ptr addrspace(1) %44, align 4, !tbaa !11
  %45 = extractelement <4 x float> %38, i64 3
  %46 = getelementptr inbounds float, ptr addrspace(1) %2, i64 %34
  store float %45, ptr addrspace(1) %46, align 4, !tbaa !11
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.amdgcn.workitem.id.x() #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.amdgcn.workitem.id.y() #1

; Function Attrs: convergent nocallback nofree nosync nounwind willreturn memory(none)
declare <4 x float> @llvm.amdgcn.mfma.f32.16x16x16f16(<4 x half>, <4 x half>, <4 x float>, i32 immarg, i32 immarg, i32 immarg) #2

attributes #0 = { convergent mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) "amdgpu-flat-work-group-size"="1,1024" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="gfx90a" "target-features"="+16-bit-insts,+ci-insts,+dl-insts,+dot1-insts,+dot2-insts,+dot3-insts,+dot4-insts,+dot5-insts,+dot6-insts,+dot7-insts,+dpp,+gfx8-insts,+gfx9-insts,+gfx90a-insts,+mai-insts,+s-memrealtime,+s-memtime-inst,+wavefrontsize64" "uniform-work-group-size"="true" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { convergent nocallback nofree nosync nounwind willreturn memory(none) }

!opencl.ocl.version = !{!0}
!llvm.ident = !{!1}
!llvm.module.flags = !{!2, !3, !4}

!0 = !{i32 2, i32 0}
!1 = !{!"AMD clang version 16.0.0 (https://github.com/RadeonOpenCompute/llvm-project roc-5.6.0 23243 be997b2f3651a41597d7a41441fff8ade4ac59ac)"}
!2 = !{i32 1, !"amdgpu_code_object_version", i32 500}
!3 = !{i32 1, !"wchar_size", i32 4}
!4 = !{i32 8, !"PIC Level", i32 1}
!5 = !{i32 0, i32 1024}
!6 = !{!7, !7, i64 0}
!7 = !{!"_Float16", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C++ TBAA"}
!10 = !{}
!11 = !{!12, !12, i64 0}
!12 = !{!"float", !8, i64 0}
