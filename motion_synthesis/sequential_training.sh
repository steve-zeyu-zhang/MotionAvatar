#!/bin/bash

# 默认参数
BASE_DIR="dataset/zoo"
SAVE_DIR="ckpt_samples"
NUM_STEPS=60000
DEVICE=0

# 从命令行获取参数
while getopts b:s:n:d: option
do
case "${option}"
in
b) BASE_DIR=${OPTARG};;
s) SAVE_DIR=${OPTARG};;
n) NUM_STEPS=${OPTARG};;
d) DEVICE=${OPTARG};;
esac
done

# 调用 Python 脚本
python sequential_training.py --base_dir "$BASE_DIR" --save_dir "$SAVE_DIR" --num_steps "$NUM_STEPS" --device "$DEVICE"
