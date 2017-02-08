from __future__ import print_function

import optparse
import glob
import json
import os
import pwd
import shutil
import socket
import subprocess

import irods_python_ci_utilities


def build_and_test_jargon(jargon_git_repository):
    install_testing_dependencies()

    local_jargon_git_dir = irods_python_ci_utilities.git_clone(jargon_git_repository, 'master')
    jargon_commit = irods_python_ci_utilities.subprocess_get_output(['git', 'rev-parse', 'HEAD'], cwd=local_jargon_git_dir)[1].strip()

    source_directory = os.path.dirname(os.path.realpath(__file__))
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'su', '-', 'irods', '-c', os.path.join(source_directory, 'prepare-irods.sh')])
    maven_output_file = os.path.expanduser('~/maven_output.log')
    irods_python_ci_utilities.subprocess_get_output("mvn install -fn --settings '{0}/maven-settings.xml' > {1}".format(source_directory, maven_output_file), cwd=local_jargon_git_dir, shell=True)
    return local_jargon_git_dir

def install_testing_dependencies():
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'apt-add-repository', '-y', 'ppa:webupd8team/java'], check_rc=True)
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'apt-get', 'update'], check_rc=True)
    irods_python_ci_utilities.subprocess_get_output('echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections', shell=True, check_rc=True)
    irods_python_ci_utilities.subprocess_get_output('echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections', shell=True, check_rc=True)
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'apt-get', 'install', '-y', 'oracle-java8-installer'], check_rc=True)
    irods_python_ci_utilities.install_os_packages(['git', 'maven2'])

def copy_output(output_root_directory, jargon_git_dir):
    irods_python_ci_utilities.mkdir_p(output_root_directory)
    xml_report_dirs = ['jargon-conveyor', 'jargon-core', 'jargon-data-utils', 'jargon-httpstream', 'jargon-ruleservice', 'jargon-ticket', 'jargon-user-profile', 'jargon-user-tagging', 'jargon-workflow']
    for d in xml_report_dirs:
        path = os.path.join(jargon_git_dir, d, 'target/surefire-reports')
        reports = glob.glob(path + '/*.xml')
        for r in reports:
            shutil.copy(r, output_root_directory)

def main():
    parser = optparse.OptionParser()
    parser.add_option('--output_root_directory')
    parser.add_option('--jargon_git_repository')
    options, _ = parser.parse_args()

    jargon_git_dir = build_and_test_jargon(options.jargon_git_repository)

    if options.output_root_directory:
        copy_output(options.output_root_directory, jargon_git_dir)

if __name__ == '__main__':
    main()
