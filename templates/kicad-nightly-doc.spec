%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           kicad-nightly-doc
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        Documentation for KiCad
License:        GPLv3+ or CC-BY
URL:            https://docs.kicad.org/

Source0:        https://gitlab.com/kicad/services/kicad-doc/-/archive/%{commit0}/kicad-doc-%{commit0}.tar.bz2

BuildArch:      noarch

BuildRequires:  asciidoc
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  po4a

Recommends:     kicad-nightly

%description
KiCad is an open-source electronic design automation software suite for the
creation of electronic schematic diagrams and printed circuit board artwork.
This package provides the documentation for the nightly development build of
KiCad in multiple languages.


%prep

%autosetup -n kicad-doc-%{commit0}


%build

# HTML only
%cmake \
    -DKICAD_DOC_PATH=%{_docdir}/kicad-nightly/help \
    -DBUILD_FORMATS=html
%cmake_build


%install

%cmake_install


%files
%{_docdir}/kicad-nightly/help/
%license LICENSE*


%changelog
* Wed Apr 7 2021 Aimylios <aimylios@xxx.xx>
- include actual license texts (available since 4ab0fd4)
- fix usage of %%cmake macro
- add make as explicit build-time dependency

* Sat Feb 27 2021 Aimylios <aimylios@xxx.xx>
- add CC-BY to License tag
- rely on %%cmake macro for out-of-tree build

* Thu Feb 25 2021 Aimylios <aimylios@xxx.xx>
- move documentation to its own SPEC file
