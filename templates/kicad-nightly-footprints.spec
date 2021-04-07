%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           kicad-nightly-footprints
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        PCB footprints for KiCad
License:        CC-BY-SA
URL:            https://kicad.org/libraries/

Source0:        https://gitlab.com/kicad/libraries/kicad-footprints/-/archive/%{commit0}/kicad-footprints-%{commit0}.tar.bz2

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  make

Recommends:     kicad-nightly

%description
KiCad is an open-source electronic design automation software suite for the
creation of electronic schematic diagrams and printed circuit board artwork.
This package provides the PCB footprints which are part of the official KiCad
libraries.


%prep

%autosetup -n kicad-footprints-%{commit0}


%build

%cmake -DKICAD_DATA=%{_datadir}/kicad-nightly
%cmake_build


%install

%cmake_install


%files
%{_datadir}/kicad-nightly/modules/*.pretty
%{_datadir}/kicad-nightly/template/fp-lib-table
%doc README.md
%license LICENSE.md


%changelog
* Wed Apr 7 2021 Aimylios <aimylios@xxx.xx>
- fix usage of %%cmake macro
- add make as explicit build-time dependency

* Sat Feb 27 2021 Aimylios <aimylios@xxx.xx>
- rely on %%cmake macro for out-of-tree build

* Sat Feb 13 2021 Aimylios <aimylios@xxx.xx>
- get sources from GitLab

* Sat Aug 1 2020 Aimylios <aimylios@xxx.xx>
- update cmake macros

* Sat May 23 2020 Aimylios <aimylios@xxx.xx>
- allow installation in parallel to stable release
- set correct version of package

* Fri Mar 16 2018 Aimylios <aimylios@xxx.xx>
- Initial release for nightly development builds
- Loosely based on https://github.com/KiCad/fedora-packaging
