#!/usr/bin/python3

from buildhelper.GitRepository import GitLabRepository
from buildhelper.RPM import LocalBuilder, CoprBuilder

import argparse
import os
import re
import urllib.request as urlreq

# local folders used by the script
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_PATH, 'templates')

# GitLab Project IDs
GITLAB_ID_KICAD = 15502567              # https://gitlab.com/kicad/code/kicad
GITLAB_ID_KICAD_I18N = 15622045         # https://gitlab.com/kicad/code/kicad-i18n
GITLAB_ID_KICAD_DOC = 15621628          # https://gitlab.com/kicad/services/kicad-doc
GITLAB_ID_KICAD_TEMPLATES = 21506275    # https://gitlab.com/kicad/libraries/kicad-templates
GITLAB_ID_KICAD_SYMBOLS = 21545491      # https://gitlab.com/kicad/libraries/kicad-symbols
GITLAB_ID_KICAD_FOOTPRINTS = 21601606   # https://gitlab.com/kicad/libraries/kicad-footprints
GITLAB_ID_KICAD_PACKAGES3D = 21604637   # https://gitlab.com/kicad/libraries/kicad-packages3D

# The version of the packages will be set to the current KICAD_SEMANTIC_VERSION
# defined in the master branch of the KiCad source code. This is the URL to the
# file where the corresponding CMake variable is defined.
KICAD_SEMANTIC_VERSION_URL = 'https://gitlab.com/kicad/code/kicad/-/raw/master/CMakeModules/KiCadVersion.cmake'

# create a SPEC file from a template
def export_spec_file(dst_path, name, version, *args):
    template_file = os.path.join(TEMPLATE_PATH, name + '.spec')
    if not os.path.isfile(template_file):
        print('Template not found at: ' + template_file)
        print('Skipping component ' + name + '...')
        return ''
    with open(template_file, 'r') as f_src:
        spec = f_src.read()
    spec = spec.replace('@VERSION@', version)
    spec = spec.replace('@SNAPSHOTDATE@', args[0].get_latest_commit_date())
    for i in range(0, len(args)):
        spec = spec.replace('@COMMITHASH' + str(i) + '@', args[i].get_latest_commit_hash())
    spec_file = os.path.join(dst_path, name + '.spec')
    with open(spec_file, 'w+') as f_dst:
        f_dst.write(spec)
    return spec_file

# configure command line options
cl_parser = argparse.ArgumentParser(description='Build KiCad nightly RPMs')
cl_parser.add_argument('--skip', help='do not generate SPEC file for specified '
    'component', choices=['kicad', 'templates', 'symbols', 'footprints',
    'packages3d'], action='append')
cl_parser.add_argument('--skip-libraries', help='do not generate SPEC files '
    'for templates, symbols, footprints, and 3D models', action='store_true')
cl_parser.add_argument('--force-update', help='always update SPEC files, even '
    'when one for the exact same version already exists', action='store_true')
cl_parser.add_argument('--do-not-build', help='just generate SPEC files, do '
    'not build any RPM packages', action='store_true')
cl_parser.add_argument('--build-type', help='type of build to trigger, '
    'default: copr', choices=['copr', 'local'], default='copr')
cl_parser.add_argument('--rpmbuild-path', help='path to RPM build environment, '
    'default: ./rpmbuild/', default=os.path.join(SCRIPT_PATH, 'rpmbuild'))
cl_parser.add_argument('--copr-config', help='path to Copr configuration file, '
    'default: ~/.config/copr', default='~/.config/copr')
cl_parser.add_argument('--copr-repository', help='Copr repository to be used, '
    'default: aimylios/kicad-nightly', default='aimylios/kicad-nightly')
args = cl_parser.parse_args()

# set local paths used by the script
rpmbuild_path = os.path.abspath(os.path.expanduser(args.rpmbuild_path))
spec_path = os.path.join(rpmbuild_path, 'SPECS')

# prepare build
builder = None
if not args.do_not_build and args.build_type == 'local':
    print('Configuring local build environment...')
    builder = LocalBuilder(rpmbuild_path)
elif not args.do_not_build and args.build_type == 'copr':
    print('Configuring Copr build environment...')
    builder = CoprBuilder(os.path.abspath(os.path.expanduser(args.copr_config)),
        args.copr_repository)

# determine current version of KiCad master branch
print('Querying current version of KiCad...')
kicad_semantic_version_cmake_file = urlreq.urlopen(urlreq.Request(KICAD_SEMANTIC_VERSION_URL,
    headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
kicad_semantic_version_cmake = re.findall('KICAD_SEMANTIC_VERSION "[^"]*"',
    kicad_semantic_version_cmake_file)[0]
if kicad_semantic_version_cmake:
    pkg_version = kicad_semantic_version_cmake.split('"')[1].split('-')[0]
    print('The version of all packages will be set to "' + pkg_version + '".')
else:
    print('Unable to determine KiCad semantic version. Aborting...')
    exit(1)

# set up interfaces to source code repositories
print('Initialising remote repositories...')
components = []
if not args.skip or 'kicad' not in args.skip:
    kicad = GitLabRepository(GITLAB_ID_KICAD)
    kicad_i18n = GitLabRepository(GITLAB_ID_KICAD_I18N)
    kicad_doc = GitLabRepository(GITLAB_ID_KICAD_DOC)
    components.append(['kicad-nightly', pkg_version, kicad, kicad_i18n, kicad_doc])
if not args.skip_libraries:
    if not args.skip or 'templates' not in args.skip:
        kicad_templates = GitLabRepository(GITLAB_ID_KICAD_TEMPLATES)
        components.append(['kicad-nightly-templates', pkg_version, kicad_templates])
    if not args.skip or 'symbols' not in args.skip:
        kicad_symbols = GitLabRepository(GITLAB_ID_KICAD_SYMBOLS)
        components.append(['kicad-nightly-symbols', pkg_version, kicad_symbols])
    if not args.skip or 'footprints' not in args.skip:
        kicad_footprints = GitLabRepository(GITLAB_ID_KICAD_FOOTPRINTS)
        components.append(['kicad-nightly-footprints', pkg_version, kicad_footprints])
    if not args.skip or 'packages3d' not in args.skip:
        kicad_packages3d = GitLabRepository(GITLAB_ID_KICAD_PACKAGES3D)
        components.append(['kicad-nightly-packages3d', pkg_version, kicad_packages3d])

# generate SPEC files and trigger build of RPMs
for component in components:
    print('Generating SPEC file for ' + component[0] + '...')
    spec_file_old = os.path.join(spec_path, component[0] + '.spec')
    if not args.force_update and os.path.isfile(spec_file_old):
        with open(spec_file_old, 'r') as f:
            spec_old = f.read()
        if component[2].get_latest_commit_hash() in spec_old:
            print('SPEC file already exists at: ' + spec_file_old)
            print('Skipping component ' + component[0] + '...')
            continue
    spec_file = export_spec_file(spec_path, *component)
    if spec_file and builder:
        print('Triggering build of RPM for ' + component[0] + '...')
        builder.build_rpm(spec_file)

print('Done.')
