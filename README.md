# Packaging nightly builds of KiCad for Fedora

KiCad is a cross platform and open source Electronics Design Automation suite. Please visit the [official KiCad website](http://kicad-pcb.org/) for details.

As of March 2018, Fedora still ships [version 4.0.7 of KiCad](https://src.fedoraproject.org/rpms/kicad), which was released in August 2017 and is just a bugfix release based on version 4.0.0 from November 2015. In the meantime, KiCad has evolved quite a bit. To make it easier for me and other Fedora users to try out the new features, I decided to set up my own respository for nightly builds of KiCad.

Because of the official libraries having grown to a size of several gigabyte, I do not bundle them together with the main application any more. Instead, they have been moved to separate (sub)packages:
* kicad (just the main applications including all translations)
* kicad-doc (documentation)
* kicad-templates (project templates)
* kicad-symbols (schematic symbol libraries)
* kicad-footprints (footprint libraries)
* kicad-packages3d (3D models)

This repository only includes the SPEC description files for the KiCad RPMs and all of the packaging scripts. The ready-made RPMs are available via my personal [aimylios/kicad-nightly](https://copr.fedorainfracloud.org/coprs/aimylios/kicad-nightly/) Copr repository. They are rebuilt automatically every day at 04:00 CE(S)T in case new commits have been added since the last build.

Different to the official KiCad nightly builds ([source](https://github.com/KiCad/fedora-packaging), [repository](https://copr.fedorainfracloud.org/coprs/g/kicad/kicad/)), my personal nightlies offer support for simulation via ngspice and Python scripting (including the scripting console in Pcbnew). Both of these features rely on libraries which are currently not part of the offical Fedora repositories. To circumvent this, I prepared custom packages called [libngspice](https://github.com/aimylios/fedora-libngspice-packaging) and [wxPython-GTK2](https://github.com/aimylios/fedora-wxpython-packaging-upstream/tree/aimylios/wxPython-GTK2) which are also part of the repository.
