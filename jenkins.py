# -*- coding: utf-8 -*-

from workflow import Workflow3, ICON_WARNING
from jenkins.jenkins_interface import JenkinsInterface, NotSettingLoginCredentials, NotSettingURL, BuildFail
import sys
reload(sys)
sys.setdefaultencoding('utf8')

ICON_UPDATE = 'icon_update.png'


def check_update(wf):
    # 检查更新
    if wf.update_available:
        arg = ['', '', '', '', 'error']
        arg = '$%'.join(arg)
        wf.add_item(
            title='有新版本更新', subtitle='', arg=arg,
            valid=True, icon=ICON_UPDATE)
    else:
        wf.add_item('Jenkins Helper')
    wf.send_feedback()


def main(wf):
    command = wf.args[0].strip().replace("\\", "")
    if not command:
        check_update(wf)

    query = wf.args[1] if len(wf.args) > 1 else None
    interface = JenkinsInterface(wf)

    options_jobs = {
        'failing': interface.get_failed_jobs,
        'building': interface.get_building_jobs,
        'all': interface.get_all_jobs,
    }

    options_other = {
        'build': interface.build_job,
        'set_url': interface.set_jenkins_url,
        'login': interface.set_login,
        'clear_login': interface.clear_login,
    }

    action_query_jobs = options_jobs.get(command)
    if not action_query_jobs:
        action_other = options_other.get(command)

    if action_query_jobs:
        try:
            jobs = action_query_jobs(query)
        except NotSettingURL:
            wf.add_item('Jenkins URL not Setting. Enter jks_url', icon=ICON_WARNING)
            wf.send_feedback()
            return 0
        except NotSettingLoginCredentials:
            wf.add_item('Jenkins Login Credentials not Setting. Enter jks_login', icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        if not jobs:
            wf.add_item('No projects found', icon=ICON_WARNING)
            wf.send_feedback()
            return 0

        for job in jobs:
            wf.add_item(title=job.name,
                        subtitle=job.description,
                        arg=job.url,
                        valid=True,
                        icon=job.image
                        ).add_modifier(key='ctrl', subtitle='Trigger a build, and open')
    elif action_other:
        try:
            if action_other(query):
                wf.add_item(query, subtitle='构建成功', arg=query, valid=True)
        except BuildFail:
            wf.add_item(query, subtitle='构建失败', arg=query, valid=True)

    wf.send_feedback()


if __name__ == u'__main__':
    wf = Workflow3(update_settings={
        'github_slug': 'kenneth-hao/alfred-workflow-jenkins-helper',
    })
    sys.exit(wf.run(main))
