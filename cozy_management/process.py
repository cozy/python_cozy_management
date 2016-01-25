'''
    Process management
'''

import psutil
USERNAME_WHITE_LIST = ['root', 'cozy-data-system', 'cozy-home', 'cozy-proxy']


def fix_oom_scores():
    for proc in psutil.process_iter():
        if proc.name == 'node':
            username = proc.username
            if username not in USERNAME_WHITE_LIST:
                # Need to not oom
                oom_score = get_oom_score(proc.pid)
                if oom_score < 100:
                    set_oom_adj(proc.pid, 15)
                    set_oom_score_adj(proc.pid, oom_score + 60)


def get_oom_scores():
    for proc in psutil.process_iter():
        if proc.name == 'node':
            username = proc.username
            if username not in USERNAME_WHITE_LIST:
                # Need to not oom
                oom_score = get_oom_score(proc.pid)
                print '{}: {}'.format(username, oom_score)


def get_oom_adj(pid):
    return int(open('/proc/{}/oom_adj'.format(pid)).readline())


def get_oom_score(pid):
    return int(open('/proc/{}/oom_score'.format(pid)).readline())


def set_oom_adj(pid, value):
    oom_adj = open('/proc/{}/oom_adj'.format(pid), 'w')
    oom_adj.write('{}\n'.format(value))
    oom_adj.close()


def set_oom_score_adj(pid, value):
    oom_score_adj = open('/proc/{}/oom_score_adj'.format(pid), 'w')
    oom_score_adj.write('{}\n'.format(value))
    oom_score_adj.close()
