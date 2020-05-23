%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global commit1 @COMMITHASH1@
%global commit2 @COMMITHASH2@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%global kicad_prefix %{_prefix}/lib/kicad-nightly
%global kicad_bindir %{kicad_prefix}/bin
%global kicad_datadir %{kicad_prefix}/share

Name:           kicad-nightly
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        Electronic schematic diagrams and printed circuit board artwork

License:        AGPLv3+
URL:            https://www.kicad-pcb.org

Source0:        https://gitlab.com/kicad/code/kicad/-/archive/%{commit0}/kicad-%{commit0}.tar.gz
Source1:        https://gitlab.com/kicad/code/kicad-i18n/-/archive/%{commit1}/kicad-i18n-%{commit1}.tar.gz
Source2:        https://gitlab.com/kicad/services/kicad-doc/-/archive/%{commit2}/kicad-doc-%{commit2}.tar.gz

BuildRequires:  chrpath
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  libappstream-glib
BuildRequires:  swig
BuildRequires:  boost-devel
BuildRequires:  glew-devel
BuildRequires:  glm-devel
BuildRequires:  libcurl-devel
BuildRequires:  libngspice-devel
BuildRequires:  opencascade-devel
BuildRequires:  openssl-devel
BuildRequires:  python3-devel
BuildRequires:  python3-wxpython4
BuildRequires:  wxGTK3-devel

# Documentation
BuildRequires:  asciidoc
BuildRequires:  po4a

Requires:       electronics-menu
Requires:       python3-wxpython4

Suggests:       kicad

%description
KiCad is an open-source software tool for the creation of electronic schematic
diagrams and PCB artwork. It does not present any board-size limitation and it
can handle up to 32 copper layers, 14 technical layers and 4 auxiliary layers.
Beneath its singular surface, KiCad incorporates an elegant ensemble of the
following software tools: KiCad (project manager), Eeschema (schematic editor
and symbol editor), Pcbnew (circuit board layout editor and footprint editor)
and GerbView (Gerber viewer).

This package provides a nightly development build of KiCad and can be installed
in parallel to the stable release package. Nightly builds are untested, might be
affected by serious bugs and/or produce files that are incompatible with the
latest stable release. This can potentially lead to a corruption or even loss of
data. Always take a backup of your files before opening them with the
applications from this package.

%package doc
Summary:        Documentation for KiCad
License:        GPLv3+
BuildArch:      noarch
Recommends:     kicad-nightly

%description doc
KiCad is an open-source software tool for the creation of electronic schematic
diagrams and printed circuit board artwork. This package provides the
documentation for KiCad in multiple languages.


%prep

%setup -q -n kicad-%{commit0} -a 1 -a 2

# Set the version of the application to the version of the package
sed -i 's/-unknown/-%{release}/g' CMakeModules/KiCadVersion.cmake


%build

# KiCad application
%cmake \
    -DKICAD_SCRIPTING=ON \
    -DKICAD_SCRIPTING_MODULES=ON \
    -DKICAD_SCRIPTING_PYTHON3=ON \
    -DKICAD_SCRIPTING_WXPYTHON=ON \
    -DKICAD_SCRIPTING_WXPYTHON_PHOENIX=ON \
    -DKICAD_SCRIPTING_ACTION_MENU=ON \
    -DKICAD_USE_OCE=OFF \
    -DKICAD_USE_OCC=ON \
    -DKICAD_INSTALL_DEMOS=ON \
    -DKICAD_BUILD_QA_TESTS=OFF \
    -DBUILD_GITHUB_PLUGIN=ON \
    -DKICAD_SPICE=ON \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_INSTALL_PREFIX=%{kicad_prefix} \
    -DCMAKE_INSTALL_DATADIR=%{_datadir}/%{name} \
    -DCMAKE_INSTALL_DOCDIR=%{_docdir}/%{name} \
    -DDEFAULT_INSTALL_PATH=%{kicad_prefix} \
    -DKICAD_DATA=%{_datadir}/%{name} \
    -DKICAD_DOCS=%{_docdir}/%{name} \
    .
%make_build

# Localization
mkdir -p kicad-i18n-%{commit1}/build/
pushd kicad-i18n-%{commit1}/build/
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{kicad_prefix} \
    -DKICAD_I18N_UNIX_STRICT_PATH=ON \
    ..
%make_build
popd

# Documentation (HTML only)
mkdir -p kicad-doc-%{commit2}/build/
pushd kicad-doc-%{commit2}/build/
%cmake \
    -DKICAD_DOC_PATH=%{_docdir}/%{name} \
    -DBUILD_FORMATS=html \
    ..
%make_build
popd


%install

# KiCad application
%make_install

# Binaries must be executable to be detected by find-debuginfo.sh
chmod +x %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# Binaries are not allowed to contain rpaths
chrpath --delete %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# Python scripts in non-standard paths require manual byte compilation
%py_byte_compile %{python3} %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/

# Wrapper scripts
mkdir -p  %{buildroot}%{_bindir}
ls -1 %{buildroot}%{kicad_bindir}/ | grep -v -F '.kiface' | \
    while read application; do
        (
            echo '#!/usr/bin/sh'
            echo ''
            echo 'export LD_LIBRARY_PATH=%{kicad_prefix}/%{_lib}/:%{kicad_prefix}/lib/'
            echo ''
            echo '[ -z "${KICAD_TEMPLATE_DIR}" ] && export KICAD_TEMPLATE_DIR=%{_datadir}/%{name}/template/'
            echo '[ -z "${KICAD_SYMBOL_DIR}" ] && export KICAD_SYMBOL_DIR=%{_datadir}/%{name}/library/'
            echo '[ -z "${KISYSMOD}" ] && export KISYSMOD=%{_datadir}/%{name}/modules/'
            echo '[ -z "${KISYS3DMOD}" ] && export KISYS3DMOD=%{_datadir}/%{name}/modules/packages3d/'
            echo ''
            echo "%{kicad_bindir}/${application} \"\$@\""
        ) > %{buildroot}%{_bindir}/${application}-nightly
    done

# Icons
ls -1 %{buildroot}%{kicad_datadir}/icons/hicolor/ | \
    while read size; do
        mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/
        ls -1 %{buildroot}%{kicad_datadir}/icons/hicolor/${size}/apps/ | \
            while read icon; do
                mv %{buildroot}%{kicad_datadir}/icons/hicolor/${size}/apps/${icon} \
                    %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/${icon%%.*}-nightly.${icon##*.}
            done
        mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${size}/mimetypes/
        ls -1 %{buildroot}%{kicad_datadir}/icons/hicolor/${size}/mimetypes/ | grep 'kicad' | \
            while read icon; do
                mv %{buildroot}%{kicad_datadir}/icons/hicolor/${size}/mimetypes/${icon} \
                    %{buildroot}%{_datadir}/icons/hicolor/${size}/mimetypes/${icon%%%%kicad*}kicad-nightly${icon#*kicad}
            done
    done
rm -rf %{buildroot}%{kicad_datadir}/icons/

# MIME files
mkdir -p %{buildroot}%{_datadir}/mime/packages/
sed -i \
    -e 's/x-kicad/x-kicad-nightly/g' \
    -e 's/KiCad/KiCad Nightly/g' \
    %{buildroot}%{kicad_datadir}/mime/packages/kicad-kicad.xml
ls -1 %{buildroot}%{kicad_datadir}/mime/packages/ | grep -F '.xml' | \
    while read mimefile; do
        mv %{buildroot}%{kicad_datadir}/mime/packages/${mimefile} \
            %{buildroot}%{_datadir}/mime/packages/${mimefile%%%%-*}-nightly-${mimefile#*-}
    done
rm -rf %{buildroot}%{kicad_datadir}/mime/

# Desktop files
ls -1 %{buildroot}%{kicad_datadir}/applications/ | grep -F '.desktop' | \
    while read desktopfile; do
        sed -i \
            -e 's/^Exec=\([^ ]*\)\(.*\)$/Exec=\1-nightly\2/g' \
            -e 's/^Name=\(.*\)$/Name=\1 NIGHTLY/g' \
            -e 's/^Icon=\(.*\)$/Icon=\1-nightly/g' \
            -e 's/x-kicad/x-kicad-nightly/g' \
            %{buildroot}%{kicad_datadir}/applications/${desktopfile}
        mv %{buildroot}%{kicad_datadir}/applications/${desktopfile} \
            %{buildroot}%{kicad_datadir}/applications/${desktopfile%%.*}-nightly.desktop
        desktop-file-install \
            --dir %{buildroot}%{_datadir}/applications/ \
            --remove-category Development \
            --delete-original \
            %{buildroot}%{kicad_datadir}/applications/${desktopfile%%.*}-nightly.desktop
    done
rm -rf %{buildroot}%{kicad_datadir}/applications/

# Library folders
mkdir -p %{buildroot}%{_datadir}/%{name}/library/
mkdir -p %{buildroot}%{_datadir}/%{name}/modules/
mkdir -p %{buildroot}%{_datadir}/%{name}/modules/packages3d/
ln -s -r %{buildroot}%{_datadir}/%{name}/ %{buildroot}%{kicad_datadir}/kicad

# Localization
pushd kicad-i18n-%{commit1}/build/
%make_install
popd

# Documentation
pushd kicad-doc-%{commit2}/build/
%make_install
popd
cp -p AUTHORS.txt %{buildroot}%{_docdir}/%{name}/


%check

appstream-util validate-relax --nonet %{buildroot}%{kicad_datadir}/appdata/*.appdata.xml


%files
%attr(0755, root, root) %{_bindir}/*
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
%{_datadir}/icons/hicolor/*/mimetypes/application-x-*.*
%{_datadir}/mime/packages/*.xml
%{kicad_prefix}/
%license LICENSE.*

%files doc
%{_docdir}/%{name}/
%license kicad-doc-%{commit2}/LICENSE.adoc


%changelog
* Sat May 23 2020 Aimylios <aimylios@xxx.xx>
- allow installation in parallel to stable release
- set correct version of package and application

* Sat Apr 4 2020 Aimylios <aimylios@xxx.xx>
- relax git build requirement to git-core
- switch to Python 3 and GTK3
- switch from OCE to OCC
- update build options
- use wildcard to include all license texts

* Sat Mar 30 2019 Aimylios <aimylios@xxx.xx>
- add license text for CC-BY-SA-4.0
- remove ExclusiveArch tag

* Mon Feb 11 2019 Aimylios <aimylios@xxx.xx>
- add license text for Boost 1.0 and ISC

* Fri Feb 8 2019 Aimylios <aimylios@xxx.xx>
- remove support for Fedora 27
- add build options related to Python 3 and Phoenix

* Sun Feb 3 2019 Aimylios <aimylios@xxx.xx>
- remove explicit libngspice runtime dependency
- change license from GPLv3+ to AGPLv3+

* Sat Nov 10 2018 Aimylios <aimylios@xxx.xx>
- remove Python shebang patch

* Sun Sep 23 2018 Aimylios <aimylios@xxx.xx>
- fix ambiguous Python shebang

* Wed Aug 8 2018 Aimylios <aimylios@xxx.xx>
- fix creation and ownership of library directories

* Tue Jul 24 2018 Aimylios <aimylios@xxx.xx>
- remove %post, %postun and %posttrans scriptlets
- drop dblatex dependency

* Thu Jun 14 2018 Aimylios <aimylios@xxx.xx>
- Backport changes from official nightly

* Fri Mar 16 2018 Aimylios <aimylios@xxx.xx>
- Initial release for nightly development builds
- Loosely based on https://github.com/KiCad/fedora-packaging
