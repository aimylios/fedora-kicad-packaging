%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           kicad-nightly-doc
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        Documentation for KiCad
License:        GPLv3+
URL:            https://docs.kicad.org/

Source0:        https://gitlab.com/kicad/services/kicad-doc/-/archive/%{commit0}/kicad-doc-%{commit0}.tar.gz

BuildArch:      noarch

BuildRequires:  asciidoc
BuildRequires:  cmake
BuildRequires:  po4a

Recommends:     kicad-nightly

%description
KiCad is an open-source software tool for the creation of electronic schematic
diagrams and printed circuit board artwork. This package provides the
documentation for KiCad in multiple languages.


%prep

%autosetup -n kicad-doc-%{commit0}


%build

# HTML only
mkdir -p build/
pushd build/
%cmake \
    -DKICAD_DOC_PATH=%{_docdir}/kicad-nightly/help \
    -DBUILD_FORMATS=html \
    ..
%cmake_build
popd


%install

pushd build/
%cmake_install
popd


%files
%{_docdir}/kicad-nightly/help/
%license LICENSE.adoc


%changelog
* Thu Feb 25 2021 Aimylios <aimylios@xxx.xx>
- move documentation to its own SPEC file
