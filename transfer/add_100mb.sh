#!/bin/bash

echo "filename: "
read orig_file
echo "output_file: "
read out_file

touch /tmp/tmp_random_data.bin

dd if=/dev/urandom of=/tmp/tmp_random_data.bin bs=1M count=100
cat /tmp/tmp_random_data.bin $orig_file > /tmp/new_file
rm /tmp/tmp_random_data.bin
mv /tmp/new_file $out_file
