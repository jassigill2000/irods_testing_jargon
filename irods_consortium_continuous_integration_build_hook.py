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
   
    source_directory = os.path.dirname(os.path.realpath(__file__))
    irods_python_ci_utilities.subprocess_get_output(['chmod', '-R', 'a+rx', '{0}'.format(source_directory)])
    edit_core_re_file = os.path.join(source_directory, 'edit_core_re_for_jargon.py')
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'su', '-', 'irods', '-c', 'rsync -r {0} /var/lib/irods/scripts/'.format(edit_core_re_file)])
    prepare_irods = os.path.join(source_directory, 'prepare-irods.sh')
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'su', '-', 'irods', '-c', '{0}'.format(prepare_irods)])
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'su', '-', 'irods', '-c', 'python2 scripts/edit_core_re_for_jargon.py'])

    local_jargon_git_dir = irods_python_ci_utilities.git_clone(jargon_git_repository, 'master')
    jargon_commit = irods_python_ci_utilities.subprocess_get_output(['git', 'rev-parse', 'HEAD'], cwd=local_jargon_git_dir)[1].strip()

    maven_output_file = os.path.expanduser('~/maven_output.log')
    irods_python_ci_utilities.subprocess_get_output("mvn install -fn --settings '{0}/maven-settings.xml' > {1}".format(source_directory, maven_output_file), cwd=local_jargon_git_dir, shell=True)
    return local_jargon_git_dir

def install_testing_dependencies():
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'apt-get', 'install', '-y', 'openjdk-8-jdk'], check_rc=True)
    irods_python_ci_utilities.subprocess_get_output(['sudo', 'apt-get', 'install', '-y', 'maven'], check_rc=True)

def copy_output(output_root_directory, jargon_git_dir):
    irods_python_ci_utilities.mkdir_p(output_root_directory)
    xml_report_dirs = ['jargon-core', 'jargon-pool', 'jargon-user-profile', 'jargon-data-utils', 'jargon-ruleservice', 'jargon-user-tagging', 'jargon-mdquery', 'jargon-ticket', 'jargon-zipservice']
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
