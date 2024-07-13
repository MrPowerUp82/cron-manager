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

def get_cron_jobs():
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE)
    cron_jobs = result.stdout.decode('utf-8').split('\n')
    return [job for job in cron_jobs if not job.startswith('#') and len(job) >= 5]

def set_cron_job(cron_job):
    current_jobs = get_cron_jobs()
    current_jobs.append(cron_job)
    cron_tab = '\n'.join(current_jobs) + '\n'
    subprocess.run(['crontab', '-'], input=cron_tab.encode('utf-8'))

def delete_cron_job(index):
    current_jobs = get_cron_jobs()
    if 0 <= index < len(current_jobs):
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')
        datetime_now = dt.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        with open(f'./tmp/backup_cron_{datetime_now}.txt', 'w') as f:
            f.write('\n'.join(current_jobs) + '\n')
        current_jobs.pop(index)
        cron_tab = '\n'.join(current_jobs) + '\n'
        subprocess.run(['crontab', '-'], input=cron_tab.encode('utf-8'))

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
            delete_cron_job(int(request.GET.get('idx')))
            set_cron_job(cmd)
            return redirect('cron_jobs')
    if request.method == 'POST':
        if request.POST.get('cmd') and request.POST.get('interval'):
            set_cron_job(request.POST.get('interval').strip() +
                         ' ' + request.POST.get('cmd').strip())
            return redirect('cron_jobs')
    return render(request, 'cron_jobs.html', ctx)
