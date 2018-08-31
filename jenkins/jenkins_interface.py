# -*- coding: utf-8 -*-

import base64

from workflow import web
from jenkins.job import Job
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class JenkinsInterface(object):

    def __init__(self, workflow):
        super(JenkinsInterface, self).__init__()
        self._workflow = workflow

    def set_jenkins_url(self, url):
        self._workflow.settings['jenkins_url'] = url
        self._workflow.settings.save()

    def set_job_build_default_branch(self, query):
        query = query.split(u' ')
        job = query[0]
        default_branch = query[1]
        self._workflow.settings['job_build_default_branch' + ':' + job] = default_branch
        self._workflow.settings.save()

    def set_login(self, query):
        query = query.split(u' ')
        username = query[0]
        api_token = query[1]
        self._workflow.settings['username'] = username
        self._workflow.save_password('jenkins_api_token', api_token)

    def clear_login(self):
        del self._workflow.settings['username']
        self._workflow.clear_password('jenkins_api_token')

    @staticmethod
    def parse_jobs(data, https):
        jobs = [Job(data, https)]
        if data.get('jobs', []):
            for job in data.get('jobs', []):
                job['name'] = '{}/{}'.format(data.get('name'), job['name'])
                jobs.append(Job(job, https))
        return jobs

    '''
    eg. https://jk.dxy.net/job/ask/
    '''
    @staticmethod
    def parse_job_name_by_url(url):
        job = url[url.find("/", url.find('/', url.find('://') + 3) + 1) + 1:]
        if job.endswith("/"):
            job = job[:-1]
        return job

    def valid_setting(self):
        if not self.get_jenkins_url():
            raise NotSettingURL
        if not self._workflow.settings.get('username') or not self._workflow.get_password('jenkins_api_token'):
            raise NotSettingLoginCredentials

    def append_auth_2_header(self, headers={}):
        self.valid_setting()
        username = self._workflow.settings['username']
        token = self._workflow.get_password('jenkins_api_token')
        base64string = base64.encodestring('%s:%s' % (username, token)).replace('\n', '')
        headers['Authorization'] = "Basic %s" % base64string
        return headers

    def build_job(self, query=None):
        self.valid_setting()
        r = web.get(self.get_jenkins_url() + "/crumbIssuer/api/json", headers=self.append_auth_2_header())
        crumb = r.json().get(u'crumb')

        job = self.parse_job_name_by_url(query)
        branch = self._workflow.settings.get('job_build_default_branch' + ':' + job)
        if not branch:
            branch = "test"

        data = {"branch": branch, "Jenkins-Crumb": crumb}
        r = web.post(query + '/buildWithParameters', data=data, headers=self.append_auth_2_header())
        if r.status_code == 201:
            return True
        else:
            raise BuildFail

    def get_all_jobs(self, query=None):
        def _get_jobs_json():
            jenkins_url = self.get_jenkins_url()
            job_params = 'name,url,color,healthReport[description,score,iconUrl]'
            url = "{}/api/json?tree=jobs[{params}]".format(jenkins_url, params=job_params)
            headers = self.append_auth_2_header()
            json = web.get(url, headers=headers).json()
            return json['jobs']

        self.valid_setting()
        jobs = []
        for job in _get_jobs_json():
            jobs.extend(self.parse_jobs(job, self.get_jenkins_url().startswith("https")))

        if query:
            filtered_jobs = self._workflow.filter(query, jobs, lambda x: x.name)
            return filtered_jobs
        else:
            if not jobs:
                raise NoJobsFound()
            return jobs

    def get_failed_jobs(self, query=None):
        all_jobs = self.get_all_jobs(query)
        return [job for job in all_jobs if 'red' in job.status]

    def get_building_jobs(self, query=None):
        all_jobs = self.get_all_jobs(query)
        return [job for job in all_jobs if 'anime' in job.status]

    def get_jenkins_url(self):
        return self._workflow.settings.get('jenkins_url')


class NotSettingURL(Exception):
    pass


class NotSettingLoginCredentials(Exception):
    pass

class BuildFail(Exception):
    pass

class NoJobsFound(Exception):
    pass

