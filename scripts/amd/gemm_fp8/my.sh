
#export MLIR_ENABLE_DUMP=1
#export LLVM_IR_ENABLE_DUMP=1
#export AMDGCN_ENABLE_DUMP=1

#python matmul.py -m 1 -n 4608 -k 320
#python matmul.py -m 1  -n 4608 -k 320
python matmul.py -m 1  -n 1040 -k 4608 --specify_size
#python matmul.py -m 1  -n 16 -k 4608
#python matmul.py -m 16  -n 4608 -k 384
