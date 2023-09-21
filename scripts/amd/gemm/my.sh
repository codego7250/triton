
#export MLIR_ENABLE_DUMP=1
#export LLVM_IR_ENABLE_DUMP=1
#export AMDGCN_ENABLE_DUMP=1

#python matmul.py -m 1 -n 4608 -k 320
#python matmul.py -m 1 -n 16 -k 12288 --specify_size
#python matmul.py -m 1 -n 4992 -k 12288
#python matmul.py -m 1 -n 12288 -k 1536
#python matmul.py -m 1335 -n 1040 -k 4608 --specify_size
python matmul.py -m 1104 -n 1 -k 4608 --specify_size --compare
#python matmul.py -m 1335 -n 4608 -k 320
#python matmul.py -m 4096 -n 4096 -k 4096
