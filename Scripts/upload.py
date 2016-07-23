#!/usr/bin/python

import argparse
import compileall
import distutils.version
import json
import os
import plistlib
import subprocess
import sys
import urllib
import webbrowser

def compile_scripts(bundle_path):
    scripts_path = os.path.join(bundle_path, 'Contents', 'Scripts')
    compileall.compile_dir(scripts_path, maxlevels=0)

def update_bundle_version(bundle_path, version):
    info_plist_path = os.path.join(bundle_path, 'Contents', 'Info.plist')
    info_plist = plistlib.readPlist(info_plist_path)
    info_plist['CFBundleVersion'] = version
    plistlib.writePlist(info_plist, info_plist_path)

def sign_bundle(bundle_path):
    subprocess.check_call(['/usr/bin/codesign', '-fs',
                           'Developer ID Application: Nicholas Riley',
                           bundle_path])

def archive_bundle(bundle_path, version):
    dir_path, bundle_filename = os.path.split(bundle_path)
    bundle_name, bundle_ext = os.path.splitext(bundle_filename)
    # GitHub will replace spaces with periods; dashes look better
    bundle_name = bundle_name.replace(' ', '-')
    archive_path = os.path.join(dir_path, '%s-%s%s' %
                                (bundle_name, version, bundle_ext))
    subprocess.check_call(['/usr/bin/ditto', '--keepParent', '-ck',
                           bundle_path, archive_path])

    return archive_path

def expand_url_template(url_template, query=None, *args):
    url = url_template
    if args:
        url = url % tuple(map(urllib.quote, args))
    if query:
        url += '?' + urllib.urlencode(query)
    return url

def upload_release(repo, version, archive_path, github_access_token):
    strict_version = distutils.version.StrictVersion(version)

    releases_url = expand_url_template(
        'https://api.github.com/repos/%s/releases',
        dict(access_token=github_access_token), repo)

    release_name = 'v' + version
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
    upload_url = expand_url_template(
        upload_url, dict(name=os.path.basename(archive_path),
                         access_token=github_access_token))
    subprocess.check_call(
        ['/usr/bin/curl', '-H', 'Content-Type: application/zip',
         '--data-binary', '@' + archive_path, upload_url])

    return html_url

def release(version, github_access_token):
    project_path = os.path.join(os.path.dirname(__file__), '..')
    action_path = os.path.join(project_path, 'Hue.lbaction')

    compile_scripts(action_path)
    update_bundle_version(action_path, version)
    sign_bundle(action_path)

    archive_path = archive_bundle(action_path, version)
    html_url = upload_release('nriley/LBHue', version, archive_path,
                              github_access_token)

    webbrowser.open(html_url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Release to GitHub.')
    parser.add_argument('version')
    parser.add_argument('github_access_token')

    args = parser.parse_args()

    release(args.version, args.github_access_token)
