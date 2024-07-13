from django.shortcuts import render, redirect
from .models import Page, Component
from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import sys
import os
import json
from slugify import slugify
import datetime as dt


def get_domains_vmail():
    result = subprocess.run(['ls', '/var/vmail/'], stdout=subprocess.PIPE)
    domains = result.stdout.decode('utf-8').split('\n')
    return domains


def get_domains_mysql():
    command = 'mysql root_cwp -B -N -s -e "SELECT domain FROM domains WHERE 1;"'
    output = os.popen(command).read()
    domains = output.strip().split('\n')
    return domains


def get_users_mysql():
    command = '''mysql root_cwp -B -N -s -e "SELECT username FROM user WHERE backup='on'"'''
    output = os.popen(command).read()
    users = output.strip().split('\n')
    return users


def get_users_passwd():
    result = subprocess.run(
        ['cut', '-d:', '-f1', '/etc/passwd'], stdout=subprocess.PIPE)
    users = result.stdout.decode('utf-8').split('\n')
    return users


def get_cron_jobs():
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE)
    cron_jobs = result.stdout.decode('utf-8').split('\n')
    return [job for job in cron_jobs if not job.startswith('#') and len(job) >= 5]


def set_cron_job(cron_job):
    current_jobs = get_cron_jobs()
    current_jobs.append(cron_job)
    cron_tab = '\n'.join(current_jobs) + '\n'
    subprocess.run(['crontab', '-'], input=cron_tab.encode('utf-8'))


def delete_cron_job(index, edit=False, code=None):
    current_jobs = get_cron_jobs()
    if 0 <= index < len(current_jobs):
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')

        datetime_now = dt.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        with open(f'./tmp/backup_cron_{datetime_now}.txt', 'w') as f:
            f.write('\n'.join(current_jobs) + '\n')

        if not edit:
            job_item = current_jobs[index]
            cmd = ' '.join(job_item.split(' ')[5:]).strip()
            if not " " in cmd:
                if os.path.exists(cmd):
                    os.remove(cmd)
        elif edit and code:
            job_item = current_jobs[index]
            cmd = ' '.join(job_item.split(' ')[5:]).strip()
            if not " " in cmd:
                with open(cmd, 'w') as f:
                    f.write(code)
        current_jobs.pop(index)
        cron_tab = '\n'.join(current_jobs) + '\n'
        subprocess.run(['crontab', '-'], input=cron_tab.encode('utf-8'))


def custom_crons(request):
    # domains = get_domains_mysql()
    # domains = '\n'.join(domains).strip()
    ctx = {
        'domains': json.dumps(get_domains_mysql()),
        'users': json.dumps(get_users_mysql()),
    }
    if request.method == 'POST':
        if request.POST.get('domains') and request.POST.get('cmd'):
            domains = request.POST.get(
                'domains').strip().replace('\r', '').split('\n')
            cmd = request.POST.get('cmd').strip()
            ext = request.POST.get('ext')
            script = ''
            if ext == 'py':
                script = f"""#!{sys.executable}
import os
domains = {domains}
for domain in domains:
    os.system('{cmd}'.format(domain))
"""
            elif ext == 'sh':
                script = f"""#!/bin/bash
for i in {' '.join(domains)}; do
    {cmd.replace('{}', '$i')}
done
"""
            filename = slugify(cmd)[int(len(slugify(cmd))/2):].strip('-') + dt.datetime.now().strftime('%Y%m%d%H%M%S')
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            full_filename = f'{base_dir}/{filename}.{ext}'
            with open(full_filename, 'w') as f:
                f.write(script)
            subprocess.run(['chmod', '+x', full_filename],
                           stdout=subprocess.PIPE)
            set_cron_job(request.POST.get('interval').strip() +' ' + full_filename.strip())
            # set_cron_job(request.POST.get('interval').strip() +' ' + full_filename.strip() + ' > /root/log_do_backup.txt')

            return redirect('cron_jobs')
    return render(request, 'custom_crons.html', ctx)


def cron_jobs(request):
    cron_jobs = [(i, x) for i, x in enumerate(get_cron_jobs())]
    ctx = {
        'cron_jobs': cron_jobs,
    }
    if request.method == 'GET' and request.GET.get('idx'):
        if request.GET.get('delete'):
            delete_cron_job(int(request.GET.get('idx')))
            return redirect('cron_jobs')
        if request.GET.get('edit'):
            cron_job = get_cron_jobs()[int(request.GET.get('idx'))].strip()
            only_file = ' '.join(cron_job.split(' ')[5:]).strip()
            if not " " in only_file:
                with open(only_file, 'r') as f:
                    ctx['code'] = f.read()
                    ctx['type_'] = 'python' if only_file.endswith('.py') else 'shell'
            ctx['cron_job'] = {
                "idx": int(request.GET.get('idx')),
                "cmd": ' '.join(cron_job.split(' ')[5:]),
                'interval': ' '.join(cron_job.split(' ')[:5]),
            }
        if request.GET.get('play'):
            cron_job = get_cron_jobs()[int(request.GET.get('idx'))].strip()
            cmd = ' '.join(cron_job.split(' ')[5:])
            output = os.popen(cmd).read()
            ctx['result'] = output.strip()
    if request.method == 'POST' and request.GET.get('idx'):
        if request.POST.get('cmd') and request.POST.get('interval'):
            cmd = request.POST.get('interval').strip(
            ) + ' ' + request.POST.get('cmd').strip()
            code = request.POST.get('code').replace('\r', '')
            delete_cron_job(int(request.GET.get('idx')), True, code)
            set_cron_job(cmd)
            return redirect('cron_jobs')
    if request.method == 'POST':
        if request.POST.get('cmd') and request.POST.get('interval'):
            set_cron_job(request.POST.get('interval').strip() +
                         ' ' + request.POST.get('cmd').strip())
            return redirect('cron_jobs')
    return render(request, 'cron_jobs.html', ctx)
