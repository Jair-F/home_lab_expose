#!/bin/bash

# update
clear ; python3 tools/update_pizza_redirect.py -u -i 1572326897 --dest_url google.com --src_url laern.duckdns.org token

# list
clear ; python3 tools/update_pizza_redirect.py -l token

# add
clear ; python3 tools/update_pizza_redirect.py -c --dest_url youtube.com --src_url laern.duckdns.org token
