%global snapdate @SNAPSHOTDATE@
%global commit0 @COMMITHASH0@
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

%global kicad_prefix %{_prefix}/lib/kicad-nightly
%global kicad_bindir %{kicad_prefix}/bin
%global kicad_docdir %{kicad_prefix}/share/doc

Name:           kicad-nightly
Version:        @VERSION@
Release:        1.%{snapdate}git%{shortcommit0}%{?dist}
Summary:        EDA software suite for creation of schematic diagrams and PCBs
License:        GPLv3+
URL:            https://kicad.org/

Source0:        https://gitlab.com/kicad/code/kicad/-/archive/%{commit0}/kicad-%{commit0}.tar.bz2

BuildRequires:  boost-devel
BuildRequires:  chrpath
BuildRequires:  cmake
BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  gettext
BuildRequires:  glew-devel
BuildRequires:  glm-devel
BuildRequires:  gtk3-devel
BuildRequires:  libappstream-glib
BuildRequires:  libcurl-devel
BuildRequires:  libngspice-devel
BuildRequires:  make
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
KiCad is an open-source electronic design automation software suite for the
creation of electronic schematic diagrams and printed circuit board artwork.
This package provides a nightly development build of KiCad and can be installed
in parallel to the stable release package. Nightly builds are untested, might be
affected by serious bugs and/or produce files that are incompatible with the
latest stable release. This can potentially lead to a corruption or even loss of
data. Always take a backup of your files before opening them with the
applications from this package.


%prep

%autosetup -n kicad-%{commit0}

# set the version of the application to the version of the package
sed -i 's/-unknown/-%{release}/g' CMakeModules/KiCadVersion.cmake


%build

# KiCad application
%cmake \
    -DKICAD_SCRIPTING_WXPYTHON=ON \
    -DKICAD_USE_OCC=ON \
    -DKICAD_INSTALL_DEMOS=OFF \
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
    -DKICAD_DOCS=%{_docdir}/%{name}
%cmake_build


%install

# KiCad application
%cmake_install
cp -p AUTHORS.txt %{buildroot}%{_docdir}/%{name}/

# binaries must be executable to be detected by find-debuginfo.sh
chmod +x %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# binaries are not allowed to contain rpaths
chrpath --delete %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/_pcbnew.so

# Python scripts in non-standard paths require manual byte compilation
%py_byte_compile %{python3} %{buildroot}%{kicad_prefix}/lib/python%{python3_version}/site-packages/

# make available hardcoded paths relative to %%{kicad_bindir}
mkdir -p %{buildroot}%{kicad_docdir}
ln -s -r %{buildroot}%{_docdir}/%{name}/ %{buildroot}%{kicad_docdir}/kicad

# wrapper scripts
mkdir -p %{buildroot}%{_bindir}
ls -1 %{buildroot}%{kicad_bindir}/ | grep -v -F '.kiface' | \
    while read application; do
        (
            echo '#!/usr/bin/sh'
            echo ''
            echo 'export LD_LIBRARY_PATH=%{kicad_prefix}/%{_lib}/:%{kicad_prefix}/lib/'
            echo ''
            echo "%{kicad_bindir}/${application} \"\$@\""
        ) > %{buildroot}%{_bindir}/${application}-nightly
    done

# icons
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

# application launchers
pushd %{buildroot}%{_datadir}/applications/
ls -1 | grep -F '.desktop' | \
    while read desktopfile; do
        sed -i \
            -e 's/^Name\(.*\)=\(.*\)$/Name\1=\2 NIGHTLY/g' \
            -e 's/^Icon=\(.*\)$/Icon=\1-nightly/g' \
            -e 's/^Exec=\([^ ]*\)\(.*\)$/Exec=\1-nightly\2/g' \
            -e 's/^MimeType=\(.*kicad\)\(.*;\)$/MimeType=\1\2\1-nightly\2/g' \
            ${desktopfile}
        mv ${desktopfile} ${desktopfile%%.*}-nightly.desktop
        desktop-file-install \
            --dir %{buildroot}%{_datadir}/applications/ \
            --remove-category Science \
            --delete-original \
            ${desktopfile%%.*}-nightly.desktop
    done
popd

# AppStream metainfo file
pushd %{buildroot}%{_metainfodir}
sed -i \
    -e 's/org.kicad.kicad/org.kicad.kicad-nightly/g' \
    -e 's/<name\(.*\)>\(.*\)<\/name>/<name\1>\2 Nightly<\/name>/g' \
    -e 's/<binary>\(.*\)<\/binary>/<binary>\1-nightly<\/binary>/g' \
    -e 's/x-kicad/x-kicad-nightly/g' \
    org.kicad.kicad.metainfo.xml
mv org.kicad.kicad.metainfo.xml org.kicad.kicad-nightly.metainfo.xml
popd

# create library folders
mkdir -p %{buildroot}%{_datadir}/%{name}/library/
mkdir -p %{buildroot}%{_datadir}/%{name}/modules/
mkdir -p %{buildroot}%{_datadir}/%{name}/3dmodels/


%check

appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml


%files
%attr(0755, root, root) %{_bindir}/*
%{_datadir}/%{name}/
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
%{_datadir}/icons/hicolor/*/mimetypes/application-x-*.*
%{_datadir}/mime/packages/*.xml
%{_docdir}/%{name}/
%{_metainfodir}/*.metainfo.xml
%{kicad_prefix}/
%license LICENSE*


%changelog
* Thu Jun 3 2021 Aimylios <aimylios@xxx.xx>
- remove obsolete build options related to Python

* Sat Apr 17 2021 Aimylios <aimylios@xxx.xx>
- handle updated AppStream metainfo file

* Wed Apr 7 2021 Aimylios <aimylios@xxx.xx>
- drop doxygen dependency
- fix usage of %%cmake macro
- add make as explicit build-time dependency

* Mon Mar 22 2021 Aimylios <aimylios@xxx.xx>
- remove workarounds to help KiCad find the stock libraries

* Sun Feb 28 2021 Aimylios <aimylios@xxx.xx>
- do not install demo projects

* Sat Feb 27 2021 Aimylios <aimylios@xxx.xx>
- rely on %%cmake macro for out-of-tree build
- drop unused KICAD_PATH environment variable
- register all MIME types in launchers

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
