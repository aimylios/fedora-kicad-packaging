# Packaging nightly builds of KiCad for Fedora

KiCad is a cross platform and open source Electronics Design Automation suite. Please visit the [official KiCad website](http://kicad-pcb.org/) for details.

Fedora usually ships the [latest stable release of KiCad](https://src.fedoraproject.org/rpms/kicad). But the time between major updates of KiCad is rather long (4.0 was released in November 2015, 5.0 in July 2018, 5.1 in March 2019), and the minor updates published in between are only meant to fix bugs. KiCad evolves quickly and new features are continuously added to the codebase. To make it easier for me and other Fedora users to try out these new features, I decided to set up my own repository for nightly builds of KiCad.

Because of the official libraries having grown to a size of several gigabyte, I do not bundle them together with the main application. Instead, they have been moved to separate (sub)packages:
* kicad-nightly (just the main applications including translations)
* kicad-nightly-doc (documentation)
* kicad-nightly-templates (project templates)
* kicad-nightly-symbols (schematic symbol libraries)
* kicad-nightly-footprints (footprint libraries)
* kicad-nightly-packages3d (3D models)

This repository only includes the SPEC description files for the KiCad RPMs and all of the packaging scripts. The ready-made RPMs are available via my personal [aimylios/kicad-nightly](https://copr.fedorainfracloud.org/coprs/aimylios/kicad-nightly/) Copr repository. They are rebuilt automatically on a regular basis in case new commits have been added since the last build.

Different to the official KiCad nightly builds ([source](https://gitlab.com/kicad/packaging/kicad-fedora-builder), [repository](https://copr.fedorainfracloud.org/coprs/g/kicad/kicad/)), my personal nightlies can be installed in parallel to the stable release from the Fedora repositories.
