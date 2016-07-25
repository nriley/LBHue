#!/usr/bin/python

import argparse
import compileall
import distutils.version
import json
import os
import pip
import plistlib
import subprocess
import sys
import tempfile
import urllib
import virtualenv
import webbrowser

def export_bundle(bundle_path):
    toplevel_path = subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel']).rstrip()
    git = ['git', '-C', toplevel_path]
    dest_path = tempfile.mkdtemp()
    ls_files = subprocess.Popen(git +
        ['ls-files', '-cz', bundle_path], stdout=subprocess.PIPE)
    checkout_index = subprocess.Popen(git +
        ['checkout-index', '--prefix=%s/'% dest_path, '--stdin', '-z'],
        stdin=ls_files.stdout)
    ls_files.stdout.close()
    checkout_index.communicate()
    return os.path.abspath(os.path.join(dest_path, bundle_path))

def expand_url_template(url_template, *args, **query):
    url = url_template
    if args:
        url = url % tuple(map(urllib.quote, args))
    if query:
        url += '?' + urllib.urlencode(query)
    return url

def archive_dir_name(bundle_path, version):
    dir_path, bundle_filename = os.path.split(bundle_path)
    bundle_name, bundle_ext = os.path.splitext(bundle_filename)
    # GitHub will replace spaces with periods; dashes look better
    bundle_name = bundle_name.replace(' ', '-')
    return dir_path, '%s-%s%s' % (bundle_name, version, bundle_ext)

def tag_for_version(version):
    return 'v' + version

def create_virtualenv(bundle_path, requirements_path):
    scripts_path = os.path.join(bundle_path, 'Contents', 'Scripts')
    virtualenv.create_environment(scripts_path, site_packages=True)
    virtualenv.make_environment_relocatable(scripts_path)
    pip.main(['install', '--prefix', scripts_path, '-r', requirements_path])
    compileall.compile_dir(scripts_path, maxlevels=0)

def update_bundle_info(bundle_path, version, repo):
    info_plist_path = os.path.join(bundle_path, 'Contents', 'Info.plist')
    info_plist = plistlib.readPlist(info_plist_path)
    info_plist['CFBundleVersion'] = version
    info_plist['LBDescription']['LBDownloadURL'] = expand_url_template(
        'https://github.com/%s/releases/download/%s/%s', repo,
        tag_for_version(version), archive_dir_name(bundle_path, version)[1])

    plistlib.writePlist(info_plist, info_plist_path)

def sign_bundle(bundle_path):
    subprocess.check_call(['/usr/bin/codesign', '-fs',
                           'Developer ID Application: Nicholas Riley',
                           bundle_path])

def archive_bundle(bundle_path, version):
    archive_path = os.path.join(*archive_dir_name(bundle_path, version))
    subprocess.check_call(['/usr/bin/ditto', '--keepParent', '-ck',
                           bundle_path, archive_path])

    return archive_path

def upload_release(repo, version, archive_path, github_access_token):
    strict_version = distutils.version.StrictVersion(version)

    releases_url = expand_url_template(
        'https://api.github.com/repos/%s/releases', repo,
        access_token=github_access_token)

    release_name = tag_for_version(version)
    release_json = dict(tag_name=release_name, target_commitish='master',
                        name=release_name, body='', draft=True,
                        prerelease=bool(strict_version.prerelease))

    releases_api = subprocess.Popen(
        ['/usr/bin/curl', '--data', '@-', releases_url],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    release_json_data, _ = releases_api.communicate(json.dumps(release_json))
    release_json = json.loads(release_json_data)

    html_url = release_json['html_url']
    upload_url = release_json['upload_url'].split('{', 1)[0]
    upload_url = expand_url_template(upload_url,
        name=os.path.basename(archive_path), access_token=github_access_token)
    subprocess.check_call(
        ['/usr/bin/curl', '-H', 'Content-Type: application/zip',
         '--data-binary', '@' + archive_path, upload_url])

    return html_url

def release(version, github_access_token):
    repo = 'nriley/LBHue'
    project_path = os.path.join(os.path.dirname(__file__), '..')
    action_path = os.path.join(project_path, 'Hue.lbaction')

    # exported version is equivalent to committed version
    export_path = export_bundle(action_path)
    # except for version number and download URL
    update_bundle_info(export_path, version, repo)

    # update the same info in the working copy so it can be committed
    update_bundle_info(action_path, version, repo)

    requirements_path = os.path.join(project_path, 'requirements.txt')
    create_virtualenv(export_path, requirements_path)

    sign_bundle(export_path)

    archive_path = archive_bundle(export_path, version)
    html_url = upload_release(repo, version, archive_path, github_access_token)

    webbrowser.open(html_url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Release to GitHub.')
    parser.add_argument('version')
    parser.add_argument('github_access_token')

    args = parser.parse_args()

    release(args.version, args.github_access_token)
