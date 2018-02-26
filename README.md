# Packaging KiCad for Fedora

KiCad is a cross platform and open source Electronics Design Automation suite. Please visit the [official KiCad website](http://kicad-pcb.org/) for details.

As of February 2018, Fedora still ships [version 4.0.7 of KiCad](https://src.fedoraproject.org/rpms/kicad), which was released in August 2017 and is just a bugfix release based on version 4.0.0 from November 2015. In the meantime, KiCad has evolved quite a bit. To make it easier for me and other Fedora users to try out the new features, I decided to set up my own KiCad respository for stable (pre-)releases of the upcoming KiCad v5.

Because of the official libraries having grown to a size of several gigabyte, I do not bundle them together with the main application any more. Instead, they have been moved to separate subpackages:
* kicad (just the main applications including all translations)
* kicad-doc (documentation)
* kicad-templates (project templates)
* kicad-symbols (schematic symbol libraries)
* kicad-footprints (footprint libraries)
* kicad-packages3D (3D models)

This repository only includes the SPEC description file for the KiCad RPM and all of the packaging scripts. The ready-made RPMs are available via my personal [aimylios/kicad-release](https://copr.fedorainfracloud.org/coprs/aimylios/kicad-release/) Copr repository.
