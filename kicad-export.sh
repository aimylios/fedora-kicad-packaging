#!/bin/sh

set -e
set -x

REVISION="5.0.0-rc1"

cd kicad
echo "Creating kicad-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-$REVISION/ HEAD > ../kicad-$REVISION.tar.gz

cd ../kicad-i18n
echo "Creating kicad-i18n-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-i18n-$REVISION/ HEAD > ../kicad-i18n-$REVISION.tar.gz

cd ../kicad-doc
echo "Creating kicad-doc-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-doc-$REVISION/ HEAD > ../kicad-doc-$REVISION.tar.gz

cd ../kicad-templates
echo "Creating kicad-templates-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-templates-$REVISION/ HEAD > ../kicad-templates-$REVISION.tar.gz

cd ../kicad-symbols
echo "Creating kicad-symbols-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-symbols-$REVISION/ HEAD > ../kicad-symbols-$REVISION.tar.gz

cd ../kicad-footprints
echo "Creating kicad-footprints-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-footprints-$REVISION/ HEAD > ../kicad-footprints-$REVISION.tar.gz

cd ../kicad-packages3D
echo "Creating kicad-packages3D-$REVISION.tar.gz ..."
git archive --format=tar.gz --prefix=kicad-packages3D-$REVISION/ HEAD > ../kicad-packages3D-$REVISION.tar.gz
