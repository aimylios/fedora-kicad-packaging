%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           kicad-nightly-symbols
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        Schematic symbols for KiCad

License:        CC-BY-SA
URL:            https://kicad-pcb.org/libraries/

Source0:        https://gitlab.com/kicad/libraries/kicad-symbols/-/archive/%{commit0}/kicad-symbols-%{commit0}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake

Recommends:     kicad-nightly

%description
KiCad is an open-source software tool for the creation of electronic schematic
diagrams and printed circuit board artwork. This package provides the schematic
symbols which are part of the official KiCad libraries.

%global debug_package %{nil}


%prep

%autosetup -n kicad-symbols-%{commit0}


%build

mkdir build
pushd build
%cmake \
    -DKICAD_DATA=%{_datadir}/kicad-nightly \
    ..
%cmake_build
popd


%install

pushd build
%cmake_install
popd


%files
%{_datadir}/kicad-nightly/library/*.kicad_sym
%{_datadir}/kicad-nightly/template/sym-lib-table
%doc README.md
%license LICENSE.md


%changelog
* Sat Feb 13 2021 Aimylios <aimylios@xxx.xx>
- get sources from GitLab
- adapt to new library file format

* Sat Aug 1 2020 Aimylios <aimylios@xxx.xx>
- update cmake macros

* Sat May 23 2020 Aimylios <aimylios@xxx.xx>
- allow installation in parallel to stable release
- set correct version of package

* Fri Mar 16 2018 Aimylios <aimylios@xxx.xx>
- Initial release for nightly development builds
- Loosely based on https://github.com/KiCad/fedora-packaging
