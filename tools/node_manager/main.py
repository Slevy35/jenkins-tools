#!/usr/bin/python3

import argparse
import os

from jenkinsapi.jenkins import Jenkins


def _get_credentials():
    username = os.getenv('JENKINS_USERNAME')
    password = os.getenv('JENKINS_PASSWORD')
    return {'username': username, 'password': password}


def get_nodes(jenkins_server: str, prefix: str):
    node_list = []
    for node_name, node in jenkins_server.get_nodes().items():
        if node_name.startswith(prefix):
            node_list.append(dict(name=node_name, node=node))
    return node_list


def manage(server_url: str, prefix: str, action: str):
    credentials = _get_credentials()
    jenkins_server = Jenkins(server_url,
                             credentials['username'],
                             credentials['password'])
    node_list = get_nodes(jenkins_server=jenkins_server, prefix=prefix)
    match action:
        case 'list':
            for item in node_list:
                print(f"Found node: {item['name']}")
        case 'disable':
            for item in node_list:
                if item['node'].is_online():
                    print(f"Disabling {item['name']}")
                    item['node'].set_offline()
        case 'enable':
            for item in node_list:
                if item['node'].is_temporarily_offline():
                    print(f"Enabling {item['name']}")
                    item['node'].set_online()
        case 'delete':
            for item in node_list:
                if item['node'].is_idle():
                    print(f"Deleting {item['name']}")
                    jenkins_server.delete_node(item['name'])
        case _:
            print(f'Unknown action {action}')


def main():
    parser = argparse.ArgumentParser(
        description='Manage Jenkins nodes through API')
    parser.add_argument('url', type=str, help='Jenkins server URL')
    parser.add_argument('prefix', type=str, help='Jenkins node name prefix')
    parser.add_argument('--action', type=str, choices=[
                        'list', 'disable', 'delete', 'enable'], default='list', help='Required action')
    args = parser.parse_args()
    manage(server_url=args.url, prefix=args.prefix, action=args.action)


if __name__ == "__main__":
    main()
