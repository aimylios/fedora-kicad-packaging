%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%global kicad_prefix %{_prefix}/lib/kicad-nightly
%global kicad_bindir %{kicad_prefix}/bin
%global kicad_datadir %{kicad_prefix}/share
%global kicad_docdir %{kicad_prefix}/share/doc

Name:           kicad-nightly
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        Electronic schematic diagrams and printed circuit board artwork
License:        GPLv3+
URL:            https://kicad.org/

Source0:        https://gitlab.com/kicad/code/kicad/-/archive/%{commit0}/kicad-%{commit0}.tar.bz2

BuildRequires:  boost-devel
BuildRequires:  chrpath
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  doxygen
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  glew-devel
BuildRequires:  glm-devel
BuildRequires:  gtk3-devel
BuildRequires:  libappstream-glib
BuildRequires:  libcurl-devel
BuildRequires:  libngspice-devel
BuildRequires:  opencascade-devel
BuildRequires:  openssl-devel
BuildRequires:  python3-devel
BuildRequires:  python3-wxpython4
BuildRequires:  shared-mime-info
BuildRequires:  swig
BuildRequires:  wxGTK3-devel
BuildRequires:  zlib-devel

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


%prep

%autosetup -n kicad-%{commit0}

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
    -DKICAD_USE_OCC=ON \
    -DKICAD_INSTALL_DEMOS=ON \
    -DKICAD_BUILD_QA_TESTS=OFF \
    -DKICAD_SPICE=ON \
    -DKICAD_BUILD_I18N=ON \
    -DKICAD_I18N_UNIX_STRICT_PATH=ON \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_INSTALL_PREFIX=%{kicad_prefix} \
    -DCMAKE_INSTALL_DATADIR=%{_datadir} \
    -DCMAKE_INSTALL_DOCDIR=%{_docdir} \
    -DDEFAULT_INSTALL_PATH=%{kicad_prefix} \
    -DKICAD_DATA=%{_datadir}/%{name} \
    -DKICAD_DOCS=%{_docdir}/%{name} \
    .
%cmake_build


%install

# KiCad application
%cmake_install
cp -p AUTHORS.txt %{buildroot}%{_docdir}/%{name}/

# Binaries must be executable to be detected by find-debuginfo.sh
chmod +x %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# Binaries are not allowed to contain rpaths
chrpath --delete %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# Python scripts in non-standard paths require manual byte compilation
%py_byte_compile %{python3} %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/

# Fallback links
mkdir -p %{buildroot}%{kicad_datadir}
ln -s -r %{buildroot}%{_datadir}/%{name}/ %{buildroot}%{kicad_datadir}/kicad
mkdir -p %{buildroot}%{kicad_docdir}
ln -s -r %{buildroot}%{_docdir}/%{name}/ %{buildroot}%{kicad_docdir}/kicad

# Wrapper scripts
mkdir -p %{buildroot}%{_bindir}
ls -1 %{buildroot}%{kicad_bindir}/ | grep -v -F '.kiface' | \
    while read application; do
        (
            echo '#!/usr/bin/sh'
            echo ''
            echo 'export LD_LIBRARY_PATH=%{kicad_prefix}/%{_lib}/:%{kicad_prefix}/lib/'
            echo ''
            echo '[ -z "${KICAD_PATH}" ] && export KICAD_PATH=%{_datadir}/%{name}/'
            echo '[ -z "${KICAD6_SCRIPTING_DIR}" ] && export KICAD6_SCRIPTING_DIR=%{_datadir}/%{name}/scripting/'
            echo '[ -z "${KICAD6_TEMPLATE_DIR}" ] && export KICAD6_TEMPLATE_DIR=%{_datadir}/%{name}/template/'
            echo '[ -z "${KICAD6_SYMBOL_DIR}" ] && export KICAD6_SYMBOL_DIR=%{_datadir}/%{name}/library/'
            echo '[ -z "${KICAD6_FOOTPRINT_DIR}" ] && export KICAD6_FOOTPRINT_DIR=%{_datadir}/%{name}/modules/'
            echo '[ -z "${KICAD6_3DMODEL_DIR}" ] && export KICAD6_3DMODEL_DIR=%{_datadir}/%{name}/3dmodels/'
            echo ''
            echo "%{kicad_bindir}/${application} \"\$@\""
        ) > %{buildroot}%{_bindir}/${application}-nightly
    done

# Icons
pushd %{buildroot}%{_datadir}/icons/hicolor/
ls -1 | \
    while read size; do
        ls -1 ${size}/apps/ | \
            while read icon; do
                mv ${size}/apps/${icon} ${size}/apps/${icon%%.*}-nightly.${icon##*.}
            done
        ls -1 ${size}/mimetypes/ | grep 'kicad' | \
            while read icon; do
                mv ${size}/mimetypes/${icon} ${size}/mimetypes/${icon%%%%kicad*}kicad-nightly${icon#*kicad}
            done
    done
popd

# MIME files
pushd %{buildroot}%{_datadir}/mime/packages/
sed -i \
    -e 's/x-kicad/x-kicad-nightly/g' \
    -e 's/KiCad/KiCad Nightly/g' \
    kicad-kicad.xml
ls -1 | grep -F '.xml' | \
    while read mimefile; do
        mv ${mimefile} ${mimefile%%%%-*}-nightly-${mimefile#*-}
    done
popd

# Desktop files
pushd %{buildroot}%{_datadir}/applications/
ls -1 | grep -F '.desktop' | \
    while read desktopfile; do
        sed -i \
            -e 's/^Exec=\([^ ]*\)\(.*\)$/Exec=\1-nightly\2/g' \
            -e 's/^Name\(.*\)=\(.*\)$/Name\1=\2 NIGHTLY/g' \
            -e 's/^Icon=\(.*\)$/Icon=\1-nightly/g' \
            -e 's/x-kicad/x-kicad-nightly/g' \
            ${desktopfile}
        mv ${desktopfile} ${desktopfile%%.*}-nightly.desktop
        desktop-file-install \
            --dir %{buildroot}%{_datadir}/applications/ \
            --remove-category Development \
            --delete-original \
            ${desktopfile%%.*}-nightly.desktop
    done
popd

# AppStream file
pushd %{buildroot}%{_datadir}/appdata/
sed -i \
    -e 's/org.kicad_pcb.kicad/org.kicad_pcb.kicad_nightly/g' \
    -e 's/<name\(.*\)>\(.*\)<\/name>/<name\1>\2 Nightly<\/name>/g' \
    -e 's/kicad.desktop/kicad-nightly.desktop/g' \
    -e 's/<binary>\(.*\)<\/binary>/<binary>\1-nightly<\/binary>/g' \
    kicad.appdata.xml
mv kicad.appdata.xml kicad-nightly.appdata.xml
popd

# Library folders
mkdir -p %{buildroot}%{_datadir}/%{name}/library/
mkdir -p %{buildroot}%{_datadir}/%{name}/modules/
mkdir -p %{buildroot}%{_datadir}/%{name}/3dmodels/


%check

appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/*.appdata.xml


%files
%attr(0755, root, root) %{_bindir}/*
%{_datadir}/%{name}/
%{_datadir}/appdata/*.xml
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
%{_datadir}/icons/hicolor/*/mimetypes/application-x-*.*
%{_datadir}/mime/packages/*.xml
%{_docdir}/%{name}/
%{kicad_prefix}/
%license LICENSE*


%changelog
* Sat Feb 27 2021 Aimylios <aimylios@xxx.xx>
- rely on %%cmake macro for out-of-tree build

* Thu Feb 25 2021 Aimylios <aimylios@xxx.xx>
- patch translated names in .desktop files
- build everything out-of-tree
- move documentation to its own SPEC file
- patch and install AppStream file
- clean up and optimise SPEC file

* Sun Feb 14 2021 Aimylios <aimylios@xxx.xx>
- fix usage of CMAKE_INSTALL_DATADIR and CMAKE_INSTALL_DOCDIR

* Sat Feb 13 2021 Aimylios <aimylios@xxx.xx>
- change license from AGPLv3+ to GPLv3+ and include all license texts
- add new build requirements
- adapt to new installation path of 3D models
- build translations from main KiCAD source repository
- update build options
- switch to new environment variables

* Sat Aug 1 2020 Aimylios <aimylios@xxx.xx>
- update cmake macros

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
