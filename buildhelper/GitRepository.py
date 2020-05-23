

from datetime import datetime
import json
import posixpath
import time
import urllib.parse as urlparse
import urllib.request as urlreq


class RemoteGitRepository:

    _api_base_url = ''

    name = ''
    branch = ''

    def __init__(self, name, branch):
        self.name = name
        self.branch = branch

    def _api_get(self, url):
        api_url = urlparse.urljoin(self._api_base_url, url)
        time.sleep(1)   # limit maximum API call frequency
        api_response = urlreq.urlopen(api_url)
        return json.load(api_response)


class GitLabRepository(RemoteGitRepository):

    _api_response_project = None
    _api_response_commit = None

    project_id = ''

    def __init__(self, project_id, branch=None):
        self._api_base_url = 'https://gitlab.com/api/v4/projects/'
        self.project_id = str(project_id)
        name = self.get_name()
        if not branch:
            branch = self.get_default_branch()
        super().__init__(name, branch)

    def _api_fetch_project(self, force_update=False):
        if not self._api_response_project or force_update:
            self._api_response_project = self._api_get(self.project_id)

    def _api_fetch_commit(self, force_update=False):
        commit_url = posixpath.join(self.project_id, 'repository', 'commits', self.branch)
        if not self._api_response_commit or force_update:
            self._api_response_commit = self._api_get(commit_url)

    def get_name(self):
        self._api_fetch_project()
        project_name = self._api_response_project['name']
        return project_name

    def get_default_branch(self):
        self._api_fetch_project()
        default_branch = self._api_response_project['default_branch']
        if not default_branch:
            default_branch = 'master'
        return default_branch

    def get_latest_commit_hash(self):
        self._api_fetch_commit()
        commit_hash = self._api_response_commit['id']
        return commit_hash

    def get_latest_commit_date(self):
        self._api_fetch_commit()
        time_string = self._api_response_commit['created_at']
        time = datetime.strptime(time_string[:10], '%Y-%m-%d')
        return datetime.strftime(time, '%Y%m%d')


class GitHubRepository(RemoteGitRepository):

    _api_response_commit = None

    organisation = ''

    def __init__(self, organisation, name, branch='master'):
        self._api_base_url = 'https://api.github.com/repos/'
        self.organisation = organisation
        super().__init__(name, branch)

    def _api_fetch_commit(self, force_update=False):
        commit_url = posixpath.join(self.organisation, self.name, 'commits', self.branch)
        if not self._api_response_commit or force_update:
            self._api_response_commit = self._api_get(commit_url)

    def get_latest_commit_hash(self):
        self._api_fetch_commit()
        commit_hash = self._api_response_commit['sha']
        return commit_hash

    def get_latest_commit_date(self):
        self._api_fetch_commit()
        time_string = self._api_response_commit['commit']['committer']['date']
        time = datetime.strptime(time_string[:10], '%Y-%m-%d')
        return datetime.strftime(time, '%Y%m%d')
