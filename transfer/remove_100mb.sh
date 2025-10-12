#!/bin/bash

echo "filename: "
read orig_file
echo "output_file: "
read out_file

dd if=$orig_file of=$out_file bs=1M skip=100
