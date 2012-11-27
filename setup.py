import os
import re
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links


setup(
    name = "pcp",
    version = "0.5",
    author = "Adam Strauch",
    author_email = "cx@initd.cz",
    description = ("Python control panel"),
    license = "BSD",
    keywords = "wsgi,uwsgi,python,webhosting,hosting,server",
    url = "https://github.com/creckx/pcp",
    #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description="Python control panel for your servers. Supports uwsgi, php, native apps, emails, mysql, pgsql, ...",#read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        ],
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = parse_dependency_links('requirements.txt'),
    #data_files = [
    #    ('wsgiadmin/templates', ['wsgiadmin/templates/%s' % x for x in os.listdir('wsgiadmin/templates') if os.path.isfile('wsgiadmin/templates/%s' % x)]),
    #],
    packages=['wsgiadmin'],
    package_dir={'wsgiadmin': 'wsgiadmin'},
    package_data={'wsgiadmin': [
        'templates/*.html',
        "static/css/*",
        "static/icons/*",
        "static/images/*",
        "static/img/*",
        "static/js/*",
        "static/scripts/*",
        "locale/cs/LC_MESSAGES/django.*"
    ]},
)