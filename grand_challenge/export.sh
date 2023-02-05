#!/usr/bin/env bash

./build.sh

# docker save rnrexm_zebrafish | gzip -c > rnrexm_zebrafish.tar.gz
# docker save rnrexm_mouse | gzip -c > rnrexm_mouse.tar.gz
docker save rnrexm_c_elegan | gzip -c > rnrexm_c_elegan.tar.gz
