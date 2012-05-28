from __future__ import with_statement

import sys
import os


from os.path import join, exists
from subprocess import check_call

from paver.easy import (
    task, needs, call_task, sh, options, consume_args
)
from paver.setuputils import setup

from setuptools import find_packages
from shutil import rmtree

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
def translate(options):
    """ Make messages for all languages from settings"""
    common_trans = True
    locales = ('cs', )

    curdir = os.getcwd()
    root_dir = join(curdir, PROJECT_ROOT)
    os.chdir(root_dir)

    if common_trans:
        if not os.path.exists(join(root_dir, 'locale')):
            os.mkdir(join(root_dir, 'locale'))
    else:
        for root, dirs, files in os.walk(root_dir):
            if 'models.py' in files and 'locale' not in dirs:
                os.mkdir(join(root_dir, root, 'locale'))
                for one in locales:
                    print 'mkdir in %s' % join(root, 'locale', one)
                    os.mkdir(join(root_dir, root, 'locale', one))

    from django.core.management import call_command
    for one in locales:
        call_command('makemessages', locale=one)

    os.chdir(curdir)

@task
def compile_translations(options):
    curdir = os.getcwd()
    root_dir = join(curdir, PROJECT_ROOT)
    os.chdir(root_dir)

    from django.core.management import call_command
    call_command('compilemessages')
    os.chdir(curdir)

@task
def remove_source_translations(options):
    curdir = os.getcwd()
    root_dir = join(curdir, PROJECT_ROOT)
    os.chdir(root_dir)

    for lang in os.listdir("locale"):
        for file in os.listdir(join("locale", lang)):
            if file.endswith(".mo"):
                os.remove(join("locale", lang, file))
    os.chdir(curdir)

@task
def create_package(options):
    #TODO - use repo w/ packages
    curdir = os.getcwd()
    if exists(join(curdir, 'dist')):
        rmtree(join(curdir, 'dist'))

    call_task('setuptools.commands.sdist')


@task
@needs([
    'create_package'
])
def upload_package(options):
    curdir = os.getcwd()
    dist_dir = join(curdir, 'dist')
    for one in os.listdir(dist_dir):
        check_call(['fab', 'fab_upload_package:file=%s' % join(dist_dir, one)])

@task
@needs([
    'compile_translations',
])
def deploy(options):
    call_task('upload_package')
    check_call(['fab', 'deploy'])


def djangonize_test_environment(test_project_module):

    root_dir = os.getcwd()

    sys.path.insert(0, root_dir)
    sys.path.insert(0, join(root_dir, "tests"))

    if exists(join(root_dir, "tests", test_project_module)):
        sys.path.insert(0, join(root_dir, "tests", test_project_module))

    os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" % test_project_module

def run_tests(test_project_module, nose_args, nose_run_kwargs=None):
    djangonize_test_environment(test_project_module)

    import nose

    root_dir = os.getcwd()

    os.chdir(join(root_dir, "tests", test_project_module))

    argv = ["--with-django"] + nose_args

    nose_run_kwargs = nose_run_kwargs or {}

    nose.run_exit(
        argv = ["nosetests"] + argv,
        defaultTest = test_project_module,
        **nose_run_kwargs
    )

@task
@consume_args
def unit(args, nose_run_kwargs=None):
    """ Run unittests """
    run_tests(test_project_module="unit_project", nose_args=args, nose_run_kwargs=nose_run_kwargs)


@task
@consume_args
def integrate(args, nose_run_kwargs=None):
    """ Run integration tests """
    run_tests(test_project_module="integrate_project", nose_args=["--with-selenium", "--with-djangoliveserver"]+args, nose_run_kwargs=nose_run_kwargs)
