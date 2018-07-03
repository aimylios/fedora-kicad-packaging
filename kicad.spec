%global version_suffix rc3

Name:           kicad
Version:        5.0.0
Release:        %{version_suffix}.1%{?dist}
Epoch:          1
Summary:        Electronic schematic diagrams and printed circuit board artwork

License:        GPLv3+
URL:            http://www.kicad-pcb.org

# Source files created with the following scripts ...
#   kicad-clone.sh ... clone GIT repositories of main, doc, libs, etc.
#   kicad-export.sh ... export GIT repositories and create tarballs
Source0:        %{name}-%{version}-%{version_suffix}.tar.gz
Source1:        %{name}-i18n-%{version}-%{version_suffix}.tar.gz
Source2:        %{name}-doc-%{version}-%{version_suffix}.tar.gz
Source3:        %{name}-templates-%{version}-%{version_suffix}.tar.gz
Source4:        %{name}-symbols-%{version}-%{version_suffix}.tar.gz
Source5:        %{name}-footprints-%{version}-%{version_suffix}.tar.gz
Source6:        %{name}-packages3D-%{version}-%{version_suffix}.tar.gz

# https://bugs.launchpad.net/kicad/+bug/1755752
ExclusiveArch: %{ix86} x86_64 %{arm} aarch64

BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  libappstream-glib
BuildRequires:  swig
BuildRequires:  boost-devel
BuildRequires:  compat-wxGTK3-gtk2-devel
BuildRequires:  glew-devel
BuildRequires:  glm-devel
BuildRequires:  libcurl-devel
BuildRequires:  OCE-devel
BuildRequires:  openssl-devel
BuildRequires:  python2-devel

# Documentation
BuildRequires:  asciidoc
BuildRequires:  po4a

Requires:       electronics-menu

%description
KiCad is an open-source software tool for the creation of electronic schematic
diagrams and PCB artwork. It does not present any board-size limitation and it
can handle up to 32 copper layers, 14 technical layers and 4 auxiliary layers.
Beneath its singular surface, KiCad incorporates an elegant ensemble of the
following software tools: KiCad (project manager), Eeschema (schematic editor
and component editor), Pcbnew (circuit board layout editor and footprint
editor) and GerbView (Gerber viewer).

%package doc
Summary:        Documentation for KiCad
License:        GPLv3+
BuildArch:      noarch
Requires:       kicad >= 5.0.0

%description doc
Documentation for KiCad.

%package templates
Summary:        Templates for KiCad
License:        CC-BY-SA
BuildArch:      noarch
Requires:       kicad >= 5.0.0

%description templates
Templates for KiCad.

%package symbols
Summary:        Schematic symbols for KiCad
License:        CC-BY-SA
BuildArch:      noarch
Requires:       kicad >= 5.0.0

%description symbols
Schematic symbols for KiCad.

%package footprints
Summary:        Footprints for KiCad
License:        CC-BY-SA
BuildArch:      noarch
Requires:       kicad >= 5.0.0

%description footprints
Footprints for KiCad.

%package packages3d
Summary:        3D models for KiCad
License:        CC-BY-SA
BuildArch:      noarch
Obsoletes:      kicad-packages3D
Requires:       kicad >= 5.0.0

%description packages3d
3D models for KiCad.


%prep

%setup -q -n %{name}-%{version}-%{version_suffix} -a 1 -a 2 -a 3 -a 4 -a 5 -a 6


%build

# compat-wxGTK3-gtk2-devel is now merged with wxGTK3-devel and uses a single wx-config
%if 0%{?fedora} > 27
%global wx_config wx-config
%else
%global wx_config wx-config-3.0-gtk2
%endif

# KiCad application
%cmake \
    -DUSE_WX_GRAPHICS_CONTEXT=OFF \
    -DUSE_WX_OVERLAY=OFF \
    -DKICAD_SCRIPTING=ON \
    -DKICAD_SCRIPTING_MODULES=ON \
    -DKICAD_SCRIPTING_WXPYTHON=OFF \
    -DKICAD_SCRIPTING_ACTION_MENU=ON \
    -DKICAD_USE_OCE=ON \
    -DKICAD_INSTALL_DEMOS=ON \
    -DBUILD_GITHUB_PLUGIN=ON \
    -DKICAD_SPICE=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DwxWidgets_CONFIG_EXECUTABLE=%{_bindir}/%{wx_config} \
    .
%make_build

# Localization
mkdir %{name}-i18n-%{version}-%{version_suffix}/build/
pushd %{name}-i18n-%{version}-%{version_suffix}/build/
%cmake \
    -DKICAD_I18N_UNIX_STRICT_PATH=ON \
    ..
%make_build
popd

# Documentation (HTML only)
mkdir %{name}-doc-%{version}-%{version_suffix}/build/
pushd %{name}-doc-%{version}-%{version_suffix}/build/
%cmake \
    -DPDF_GENERATOR=none \
    -DBUILD_FORMATS=html \
    ..
%make_build
popd

# Templates
pushd %{name}-templates-%{version}-%{version_suffix}/
%cmake
%make_build
popd

# Symbol libraries
pushd %{name}-symbols-%{version}-%{version_suffix}/
%cmake
%make_build
popd

# Footprint libraries
pushd %{name}-footprints-%{version}-%{version_suffix}/
%cmake
%make_build
popd

# 3D models
pushd %{name}-packages3D-%{version}-%{version_suffix}/
%cmake
%make_build
popd


%install

# KiCad application
%make_install
%{__cp} -p AUTHORS.txt %{buildroot}%{_docdir}/%{name}/

# Localization
pushd %{name}-i18n-%{version}-%{version_suffix}/build/
%make_install
popd

# Desktop integration
for desktopfile in %{buildroot}%{_datadir}/applications/*.desktop ; do
    desktop-file-install \
    --dir %{buildroot}%{_datadir}/applications \
    --remove-category Development \
    --delete-original \
    ${desktopfile}
done

# Documentation
pushd %{name}-doc-%{version}-%{version_suffix}/build/
%make_install
popd

# Templates
pushd %{name}-templates-%{version}-%{version_suffix}/
%make_install
popd

# Symbol libraries
pushd %{name}-symbols-%{version}-%{version_suffix}/
%make_install
popd

# Footprint libraries
pushd %{name}-footprints-%{version}-%{version_suffix}/
%make_install
popd

# 3D models
pushd %{name}-packages3D-%{version}-%{version_suffix}/
%make_install
popd

%find_lang %{name}


%check
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/*.appdata.xml


%files -f %{name}.lang
%{_bindir}/*
%{_libdir}/libkicad_3dsg.so*
%{_libdir}/%{name}/plugins/*
%{_prefix}/lib/python2.7/site-packages/*
%{_datadir}/%{name}/demos/*
%{_datadir}/%{name}/plugins/*
%{_datadir}/%{name}/scripting/*
%{_datadir}/%{name}/template/kicad.pro
%{_datadir}/appdata/*.xml
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/mimetypes/application-x-*.*
%{_datadir}/icons/hicolor/*/apps/*.*
%{_datadir}/mime/packages/*.xml

%files doc
%{_docdir}/%{name}/*.txt
%{_docdir}/%{name}/help/*
%{_docdir}/%{name}/scripts/*
%license %{name}-doc-%{version}-%{version_suffix}/LICENSE.adoc

%files templates
%exclude %{_datadir}/%{name}/template/fp-lib-table
%exclude %{_datadir}/%{name}/template/sym-lib-table
%exclude %{_datadir}/%{name}/template/kicad.pro
%{_datadir}/%{name}/template/*
%license %{name}-templates-%{version}-%{version_suffix}/LICENSE.md

%files symbols
%{_datadir}/%{name}/library/*.dcm
%{_datadir}/%{name}/library/*.lib
%{_datadir}/%{name}/template/sym-lib-table
%license %{name}-symbols-%{version}-%{version_suffix}/LICENSE.md

%files footprints
%{_datadir}/%{name}/modules/*.pretty
%{_datadir}/%{name}/template/fp-lib-table
%license %{name}-footprints-%{version}-%{version_suffix}/LICENSE.md

%files packages3d
%{_datadir}/%{name}/modules/packages3d/*.3dshapes
%license %{name}-packages3D-%{version}-%{version_suffix}/LICENSE.md


%changelog
* Tue Jul 3 2018 Aimylios <aimylios@xxx.xx> - 5.0.0-rc3.1
- Update to 5.0.0-RC3
- Update dependencies
- Remove obsolete post, postun and posttrans scriptlets

* Tue Jun 12 2018 Aimylios <aimylios@xxx.xx> - 5.0.0-rc2.1
- Update to 5.0.0-RC2
- Rename kicad-packages3D to kicad-packages3d
- Add ExclusiveArch tags
- Update dependencies

* Thu Mar 1 2018 Aimylios <aimylios@xxx.xx> - 5.0.0-rc1.3
- Enable all available languages for documentation, not just English
- Add license files to library packages
- Remove git from build requirements, it is useless for release builds

* Tue Feb 27 2018 Aimylios <aimylios@xxx.xx> - 5.0.0-rc1.2
- Add Epoch to allow automatic updates of older installations
- Make library packages depend on KiCad >= 5.0.0, this will help to avoid
  incompatibilities with Fedora upstream and nightly builds

* Mon Feb 26 2018 Aimylios <aimylios@xxx.xx> - 5.0.0-rc1.1
- Initial release for stable builds
- Loosely based on https://github.com/KiCad/fedora-packaging
