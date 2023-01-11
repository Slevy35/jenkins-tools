#!/usr/bin/python3

import os
from re import IGNORECASE, match
import argparse
import yaml
from datetime import datetime

from jenkins import Jenkins


OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'out')
OUTPUT_FILE = 'output.yaml'


def _get_credentials():
    username = os.getenv('JENKINS_USERNAME')
    password = os.getenv('JENKINS_PASSWORD')
    return {'username': username, 'password': password}


def _get_all_jobs(server: Jenkins, prefix: str, include_pipelines: bool):
    all_jobs = server.get_jobs()
    if not include_pipelines:
        all_jobs = list(filter(lambda job: "jobs" not in job, all_jobs))
    if prefix != '*':
        all_jobs = list(filter(lambda job: match(
            prefix, job['name'], IGNORECASE), all_jobs))
    return all_jobs


def _export_data(data: list, file_output: bool, sort_key: str = None):
    if sort_key:
        data['jobs'].sort(key=lambda job: job['sort_key'], reverse=True)
    if file_output:
        with open(f'{OUTPUT_FOLDER}/{OUTPUT_FILE}', 'w') as file:
            yaml.dump(data, file)
    else:
        print(yaml.dump(data))


def _list_jobs(server: Jenkins, jobs: list, include_disabled: bool, file_output: bool):
    export = {'count': len(jobs), 'jobs': []}
    for job in jobs:
        job_name = job['name']
        job_info = server.get_job_info(job_name)
        is_enabled = job_info.get('buildable', True)
        job_label = job_info.get('labelExpression')
        is_pipeline = 'jobs' in job
        is_multibranch_pipeline = is_pipeline and 'buildable' not in job
        last_build = 'None'
        if not is_multibranch_pipeline:
            build = job_info.get('lastBuild')
            if build:
                build_number = build['number']
                try:
                    build_info = server.get_build_info(job_name, build_number)
                    last_build = datetime.fromtimestamp(
                        build_info['timestamp'] / 1000).strftime('%d-%m-%y')
                except Exception as e:
                    print(
                        f'Failed to get build build info for job {job_name} number {build_number}, with error: "{e}"')
        if not include_disabled and not is_enabled:
            continue
        obj = {}
        obj['name'] = job_name
        obj['is_enabled'] = is_enabled
        obj['label'] = job_label
        obj['is_pipeline'] = is_pipeline
        obj['is_multibranch_pipeline'] = is_multibranch_pipeline
        obj['last_build'] = last_build
        export['jobs'].append(obj)
    if export['jobs'].count:
        _export_data(export, file_output, 'last_build')


def _disable_jobs(server: Jenkins, jobs: list, file_output: bool):
    export = {'count': len(jobs), 'jobs': []}
    approve = str(
        input(f'Are you shour that you want to disable {len(jobs)} jobs? press y/Y: '))
    if approve.lower() == 'y':
        for job in jobs:
            job_name = job['name']
            job_info = server.get_job_info(job_name)
            is_enabled = job_info.get('buildable', True)
            is_pipeline = 'jobs' in job
            is_multibranch_pipeline = is_pipeline and 'buildable' not in job
            if is_enabled and not is_multibranch_pipeline:
                server.disable_job(job_name)
                export['jobs'].append(job_name)
        if export['jobs'].count:
            _export_data(export, file_output)


def _enable_jobs(server: Jenkins, jobs: list, file_output: bool):
    export = {'count': len(jobs), 'jobs': []}
    for job in jobs:
        job_name = job['name']
        job_info = server.get_job_info(job_name)
        is_enabled = job_info.get('buildable', True)
        is_pipeline = 'jobs' in job
        is_multibranch_pipeline = is_pipeline and 'buildable' not in job
        if not is_enabled and not is_multibranch_pipeline:
            server.enable_job(job_name)
            export['jobs'].append(job_name)
    if export['jobs'].count:
        _export_data(export, file_output)


def _backup_jobs(server: Jenkins, jobs: list):
    for job in jobs:
        job_name = job['name']
        config = server.get_job_config(job_name)
        with open(f'{OUTPUT_FOLDER}/{job_name}.xml', "w") as file:
            file.write(config)


def manage(server_url: str, prefix: str, action: str, include_pipelines: bool, include_disabled: bool = False, file_output: bool = False):
    credentials = _get_credentials()
    server = Jenkins(
        server_url, credentials['username'], credentials['password'])
    jobs = _get_all_jobs(server, prefix, include_pipelines)
    print(f'Found {len(jobs)} jobs.')
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    match action:
        case 'list':
            _list_jobs(server, jobs, include_disabled, file_output)
        case 'disable':
            _disable_jobs(server, jobs)
        case 'enable':
            _enable_jobs(server, jobs)
        case 'backup':
            _backup_jobs(server, jobs)
        case _:
            print(f'Unknown action {action}')


def main():
    parser = argparse.ArgumentParser(
        description='Manage Jenkins Jobs through API')
    parser.add_argument('url', type=str, help='Jenkins server URL')
    parser.add_argument('--prefix', default='*', type=str,
                        help='Jenkins job name prefix')
    parser.add_argument('--action', type=str, choices=[
                        'list', 'disable', 'enable', 'backup'], default='list', help='Required action')
    parser.add_argument('--include-pipelines',
                        action='store_true', help='Include jenkins pipelines (for list)')
    parser.add_argument('--include-disabled',
                        action='store_true', help='Include disabled jobs (for list)')
    parser.add_argument('--file-output',
                        action='store_true', help='Output data to file (for list)')
    args = parser.parse_args()
    manage(server_url=args.url, prefix=args.prefix, action=args.action,
           include_pipelines=args.include_pipelines, include_disabled=args.include_disabled, file_output=args.file_output)


if __name__ == "__main__":
    main()
