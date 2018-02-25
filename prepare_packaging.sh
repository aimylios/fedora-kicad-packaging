#!/bin/sh

set -e
set -x

./kicad-clone.sh
./kicad-export.sh

md5sum *.gz > sources
