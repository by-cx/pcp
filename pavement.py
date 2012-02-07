from __future__ import with_statement

from paver.easy import (
    task, needs, call_task,
    sh, path, options,
)
from paver.setuputils import setup

from os.path import join
import os
import sys

from setuptools import find_packages


# must be in sync with pcp.VERSION
VERSION = (0, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

PROJECT_ROOT = 'wsgiadmin'

USE_SHELL = os.name == 'nt'

setup(
    name = 'pcp',
    version = __versionstr__,
    description = 'python control panel',
    long_description = '\n'.join((
        'PCP',
        '',
        'Python based control panel',
    )),
    author = 'bycx, yedpodtrzitko',
    author_email='cx@initd.cz',
    license = 'BSD',
    url='https://github.com/creckx/pcp/',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    entry_points = {
#        'setuptools.installation': ['eggsecutable = tvcafe.manage'],
    },
    install_requires = [
        'setuptools>=0.6b1',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
)

try:
    from paver.discovery import discover_django
    discover_django(options)

except ImportError:
    pass

@task
def install_dependencies():
    sh('pip install --download-cache=/tmp/pip-download-cache -r requirements.txt')

@task
def translate(options):
    """ Make messages for all languages from settings"""
    locales = ('cs', )
    curdir = os.getcwd()
    proot = join(curdir, PROJECT_ROOT)
    common_trans = True

    os.chdir(proot)
    if common_trans:
        if not os.path.exists(join(proot, 'locale')):
            os.mkdir(join(proot, 'locale'))
    else:
        for root, dirs, files in os.walk(proot):
            if 'models.py' in files and 'locale' not in dirs:
                os.mkdir(join(proot, root, 'locale'))
                for one in locales:
                    print 'mkdir in %s' % join(root, 'locale', one)
                    os.mkdir(join(proot, root, 'locale', one))

    from django.core.management import call_command
    for one in locales:
        call_command('makemessages', locale=one)

    os.chdir(curdir)

@task
def compile_translations(options):
    curdir = os.getcwd()
    from django.core.management import call_command
    os.chdir(options.name)

    call_command('compilemessages')
    os.chdir(curdir)

@task
def remove_source_translations(options):
    curdir = os.getcwd()
    os.chdir(options.name)
    for lang in os.listdir("locale"):
        for file in os.listdir(join("locale", lang)):
            if file.endswith(".mo"):
                os.remove(join("locale", lang, file))
    os.chdir(curdir)


@task
@needs([
    'compile_translations',
    #'minify'
])
def deploy(options):
    #TODO
    pass
