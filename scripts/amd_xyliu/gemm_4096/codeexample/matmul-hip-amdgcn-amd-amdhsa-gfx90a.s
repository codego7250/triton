	.text
	.amdgcn_target "amdgcn-amd-amdhsa--gfx90a"
	.protected	_Z14hgemm_16x16x16PKDF16_S0_Pf ; -- Begin function _Z14hgemm_16x16x16PKDF16_S0_Pf
	.globl	_Z14hgemm_16x16x16PKDF16_S0_Pf
	.p2align	8
	.type	_Z14hgemm_16x16x16PKDF16_S0_Pf,@function
_Z14hgemm_16x16x16PKDF16_S0_Pf:         ; @_Z14hgemm_16x16x16PKDF16_S0_Pf
; %bb.0:
	s_load_dwordx4 s[0:3], s[4:5], 0x0
	s_load_dwordx2 s[6:7], s[4:5], 0x10
	v_and_b32_e32 v1, 0x3ff, v0
	v_bfe_u32 v0, v0, 10, 10
	v_lshl_or_b32 v4, v0, 14, v1
	v_lshlrev_b32_e32 v0, 3, v0
	v_lshl_or_b32 v0, v1, 13, v0
	s_waitcnt lgkmcnt(0)
	global_load_dwordx2 v[0:1], v0, s[0:1]
	v_or_b32_e32 v6, 0x2000, v4
	v_or_b32_e32 v5, 0x1000, v4
	v_lshlrev_b32_e32 v7, 1, v6
	v_or_b32_e32 v8, 0x3000, v4
	v_lshlrev_b32_e32 v2, 1, v4
	v_lshlrev_b32_e32 v3, 1, v5
	v_lshlrev_b32_e32 v9, 1, v8
	global_load_ushort v10, v7, s[2:3]
	global_load_ushort v11, v9, s[2:3]
	global_load_ushort v12, v2, s[2:3]
	global_load_ushort v13, v3, s[2:3]
	s_mov_b32 s0, 0x5040100
	v_lshlrev_b32_e32 v4, 2, v4
	v_lshlrev_b32_e32 v5, 2, v5
	v_lshlrev_b32_e32 v6, 2, v6
	v_lshlrev_b32_e32 v7, 2, v8
	s_waitcnt vmcnt(2)
	v_perm_b32 v3, v11, v10, s0
	s_waitcnt vmcnt(0)
	v_perm_b32 v2, v13, v12, s0
	s_nop 1
	v_mfma_f32_16x16x16f16 v[0:3], v[0:1], v[2:3], 0
	s_nop 7
	s_nop 2
	global_store_dword v4, v0, s[6:7]
	global_store_dword v5, v1, s[6:7]
	global_store_dword v6, v2, s[6:7]
	global_store_dword v7, v3, s[6:7]
	s_endpgm
	.section	.rodata,#alloc
	.p2align	6, 0x0
	.amdhsa_kernel _Z14hgemm_16x16x16PKDF16_S0_Pf
		.amdhsa_group_segment_fixed_size 0
		.amdhsa_private_segment_fixed_size 0
		.amdhsa_kernarg_size 24
		.amdhsa_user_sgpr_count 6
		.amdhsa_user_sgpr_private_segment_buffer 1
		.amdhsa_user_sgpr_dispatch_ptr 0
		.amdhsa_user_sgpr_queue_ptr 0
		.amdhsa_user_sgpr_kernarg_segment_ptr 1
		.amdhsa_user_sgpr_dispatch_id 0
		.amdhsa_user_sgpr_flat_scratch_init 0
		.amdhsa_user_sgpr_private_segment_size 0
		.amdhsa_uses_dynamic_stack 0
		.amdhsa_system_sgpr_private_segment_wavefront_offset 0
		.amdhsa_system_sgpr_workgroup_id_x 1
		.amdhsa_system_sgpr_workgroup_id_y 0
		.amdhsa_system_sgpr_workgroup_id_z 0
		.amdhsa_system_sgpr_workgroup_info 0
		.amdhsa_system_vgpr_workitem_id 1
		.amdhsa_next_free_vgpr 14
		.amdhsa_next_free_sgpr 8
		.amdhsa_accum_offset 16
		.amdhsa_reserve_vcc 0
		.amdhsa_reserve_flat_scratch 0
		.amdhsa_reserve_xnack_mask 1
		.amdhsa_float_round_mode_32 0
		.amdhsa_float_round_mode_16_64 0
		.amdhsa_float_denorm_mode_32 3
		.amdhsa_float_denorm_mode_16_64 3
		.amdhsa_dx10_clamp 1
		.amdhsa_ieee_mode 1
		.amdhsa_fp16_overflow 0
		.amdhsa_tg_split 0
		.amdhsa_exception_fp_ieee_invalid_op 0
		.amdhsa_exception_fp_denorm_src 0
		.amdhsa_exception_fp_ieee_div_zero 0
		.amdhsa_exception_fp_ieee_overflow 0
		.amdhsa_exception_fp_ieee_underflow 0
		.amdhsa_exception_fp_ieee_inexact 0
		.amdhsa_exception_int_div_zero 0
	.end_amdhsa_kernel
	.text
.Lfunc_end0:
	.size	_Z14hgemm_16x16x16PKDF16_S0_Pf, .Lfunc_end0-_Z14hgemm_16x16x16PKDF16_S0_Pf
                                        ; -- End function
	.section	.AMDGPU.csdata
; Kernel info:
; codeLenInByte = 244
; NumSgprs: 12
; NumVgprs: 14
; NumAgprs: 0
; TotalNumVgprs: 14
; ScratchSize: 0
; MemoryBound: 0
; FloatMode: 240
; IeeeMode: 1
; LDSByteSize: 0 bytes/workgroup (compile time only)
; SGPRBlocks: 1
; VGPRBlocks: 1
; NumSGPRsForWavesPerEU: 12
; NumVGPRsForWavesPerEU: 14
; AccumOffset: 16
; Occupancy: 8
; WaveLimiterHint : 1
; COMPUTE_PGM_RSRC2:SCRATCH_EN: 0
; COMPUTE_PGM_RSRC2:USER_SGPR: 6
; COMPUTE_PGM_RSRC2:TRAP_HANDLER: 0
; COMPUTE_PGM_RSRC2:TGID_X_EN: 1
; COMPUTE_PGM_RSRC2:TGID_Y_EN: 0
; COMPUTE_PGM_RSRC2:TGID_Z_EN: 0
; COMPUTE_PGM_RSRC2:TIDIG_COMP_CNT: 1
; COMPUTE_PGM_RSRC3_GFX90A:ACCUM_OFFSET: 3
; COMPUTE_PGM_RSRC3_GFX90A:TG_SPLIT: 0
	.text
	.p2alignl 6, 3212836864
	.fill 256, 4, 3212836864
	.protected	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE ; @_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE
	.type	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE,@object
	.section	.rodata._ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE,#alloc
	.weak	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE
_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE:
	.zero	1
	.size	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE, 1

	.protected	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE ; @_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE
	.type	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE,@object
	.section	.rodata._ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE,#alloc
	.weak	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE
_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE:
	.zero	1
	.size	_ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE, 1

	.ident	"AMD clang version 16.0.0 (https://github.com/RadeonOpenCompute/llvm-project roc-5.6.0 23243 be997b2f3651a41597d7a41441fff8ade4ac59ac)"
	.section	".note.GNU-stack"
	.addrsig
	.addrsig_sym _ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1xE
	.addrsig_sym _ZN17__HIP_CoordinatesI15__HIP_ThreadIdxE1yE
	.amdgpu_metadata
---
amdhsa.kernels:
  - .agpr_count:     0
    .args:
      - .address_space:  global
        .offset:         0
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .offset:         8
        .size:           8
        .value_kind:     global_buffer
      - .address_space:  global
        .offset:         16
        .size:           8
        .value_kind:     global_buffer
    .group_segment_fixed_size: 0
    .kernarg_segment_align: 8
    .kernarg_segment_size: 24
    .language:       OpenCL C
    .language_version:
      - 2
      - 0
    .max_flat_workgroup_size: 1024
    .name:           _Z14hgemm_16x16x16PKDF16_S0_Pf
    .private_segment_fixed_size: 0
    .sgpr_count:     12
    .sgpr_spill_count: 0
    .symbol:         _Z14hgemm_16x16x16PKDF16_S0_Pf.kd
    .uniform_work_group_size: 1
    .uses_dynamic_stack: false
    .vgpr_count:     14
    .vgpr_spill_count: 0
    .wavefront_size: 64
amdhsa.target:   amdgcn-amd-amdhsa--gfx90a
amdhsa.version:
  - 1
  - 2
...

	.end_amdgpu_metadata
