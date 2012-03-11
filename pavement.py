from __future__ import with_statement

import sys
import os

from os.path import join, exists
from subprocess import check_call

from paver.easy import *
from paver.setuputils import setup
from shutil import rmtree

PROJECT_ROOT = 'wsgiadmin'

USE_SHELL = os.name == 'nt'

setup(
    name = 'pcp',
    version = "0.4",
    description = 'Webhosting administration',
    long_description = '\n'.join((
        'PCP',
        'Python based control panel',
    )),
    author = 'bycx, yedpodtrzitko',
    author_email='cx@initd.cz',
    license = 'BSD',
    url='https://github.com/creckx/pcp/',
)

try:
    from paver.discovery import discover_django
    discover_django(options)

except ImportError:
    pass


@task
def init_env(options):
    check_call(["fab", "init_env"])


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
