#!/bin/bash

# update
clear ; python3 tunnel/redirect_pizza.py -u -i 1572326897 --dest_url google.com --src_url laern.duckdns.org token

# list
clear ; python3 tunnel/redirect_pizza.py -l token

# add
clear ; python3 tunnel/redirect_pizza.py -c --dest_url youtube.com --src_url laern.duckdns.org token
