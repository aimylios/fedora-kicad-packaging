

# SPDX-License-Identifier: MIT

import copr.v3 as copr
import os
import subprocess
import time


class LocalBuilder:

    build_path = ''

    def __init__(self, rpmbuild_path):
        self.build_path = rpmbuild_path

    def get_sources(self, spec):
        subprocess.run('rpmbuild --define "_topdir ' + self.build_path + '" ' +
            '--undefine "_disable_source_fetch" --nobuild ' + spec, shell=True)

    def build_srpm(self, spec):
        subprocess.run('rpmbuild --define "_topdir ' + self.build_path + '" ' +
            '--undefine "_disable_source_fetch" -bs ' + spec, shell=True)

    def build_rpm(self, spec_or_srpm):
        subprocess.run('rpmbuild --define "_topdir ' + self.build_path + '" ' +
            '--undefine "_disable_source_fetch" -ba ' + spec_or_srpm, shell=True)


class MockBuilder:

    build_path = ''
    chroot_config = ''
    result_path = ''
    builder = None

    def __init__(self, rpmbuild_path, chroot_config, result_path):
        self.build_path = rpmbuild_path
        self.chroot_config = chroot_config
        self.result_path = result_path
        self.builder = LocalBuilder(rpmbuild_path)

    def build_srpm(self, spec, sources=None):
        if not sources:
            self.builder.get_sources(spec)
            sources=os.path.join(rpmbuild_path, 'SOURCES')
        subprocess.run('mock --root=' + self.chroot_config + ' --buildsrpm' +
            ' --spec=' + spec + ' --sources=' + sources + ' --resultdir=' +
            self.result_path, shell=True)

    def build_rpm(self, spec, sources=None):
        if not sources:
            self.builder.get_sources(spec)
            sources=os.path.join(rpmbuild_path, 'SOURCES')
        subprocess.run('mock --root=' + self.chroot_config + ' --rebuild' +
            ' --spec=' + spec + ' --sources=' + sources + ' --resultdir=' +
            self.result_path, shell=True)


class CoprBuilder:

    _client = None

    user = ''
    name = ''

    def __init__(self, config, repository):
        self._client = copr.Client.create_from_config_file(config)
        self.user = repository.split('/', 1)[0]
        self.name = repository.split('/', 1)[1]

    def build_rpm(self, spec_or_srpm):
        self._client.build_proxy.create_from_file(self.user, self.name, spec_or_srpm)
        time.sleep(5)   # give the server some time between build requests
