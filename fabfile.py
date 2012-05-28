import os

from fabric.api import env, run, sudo, put
from fabric.context_managers import cd

from os.path import join, expanduser, isfile, exists, abspath
from ConfigParser import RawConfigParser, NoOptionError
import sys

PROJECT_DIR = 'pcp'
TMP_NAME = 'pcp.tar.gz'
# this will probably not work on Windows.
env.key_filename = [os.path.join(os.path.expanduser("~/.ssh"), k) for k in os.listdir(os.path.join(os.path.expanduser("~/.ssh"))) if os.path.basename(k).startswith("id_") and not os.path.basename(k).endswith(".pub")]


def get_deploy_cfg(project_dir=None):
    project_dir = project_dir or PROJECT_DIR
    conf_dir = join(expanduser('~'), '.config', project_dir)
    cfg_file = join(conf_dir, 'deploy.cfg')

    if not exists(conf_dir):
        os.mkdir(conf_dir)

    cfg = RawConfigParser()
    if not isfile(cfg_file):
        open(cfg_file, 'w').close()
    else:
        cfg.read(cfg_file)

    if 'machine' not in cfg.sections():
        print """
        Seems like you run deployment for the first time.
        You'll be asked about deployment data, which will be saved into
        config file for later use.
        However you can quit now and create this file by you own
        file:
        %s
        format:
        [machine]
        machine = ssh machine
        user = ssh user (optional)
        project_dir = install directory
        virtualenv = virtualenv directory
        tmp_dir = (optional) tmp dir. for data manipulation (CONTENT WILL BE DESTROYED) (default is /tmp/pcp)
        """ % cfg_file
        #sudo_user = user owning app directory

        machine = raw_input("ssh machine: ")
        cfg.add_section('machine')
        cfg.set('machine', 'machine', machine.strip())

        user = raw_input("ssh user (leave empty to use current user): ")
        if user.strip():
            cfg.set('machine', 'user', user.strip())

        project_dir = raw_input("app directory: ")
        cfg.set('machine', 'project_dir', project_dir.strip())

        virtual = raw_input("virtualenv path: ")
        cfg.set('machine', 'virtualenv', virtual.strip())

        #tmp_dir = raw_input("temp. working directory: ")
        #cfg.set('machine', 'tmp_dir', tmp_dir.strip())

        cfg.write(open(cfg_file, 'w'))

    return cfg

def update_env(decorated_function):
    cfg = get_deploy_cfg()
    if not getattr(env, 'vanyli_updated_env', False):
        if not env.host_string:
            try:
                machine = cfg.get('machine', 'machine')
            except NoOptionError:
                print """
                    ERROR: Target machine not found in config file, I'm out"""
                sys.exit(1)
            else:
                env.host_string = machine


        try:
            tmp_dir = cfg.get('machine', 'tmp_dir')
        except NoOptionError:
            tmp_dir = None

        if not tmp_dir:
            tmp_dir = '/tmp/pcp'

        if abspath(tmp_dir) == '/':
            print """
                ERROR: Using root directory as tmp. directory is not best practice, I'm out"""
            sys.exit(1)
        env.tmp_dir = tmp_dir


        env.virtualenv = cfg.get('machine', 'virtualenv')
        env.project_dir = cfg.get('machine', 'project_dir')


        env.vanyli_updated_env = True

    return decorated_function

def install_requirements():
    pass

@update_env
def fab_upload_package(file):
    run('if [ -e %(dir)s ];then rm -Rf %(dir)s;fi; mkdir -p %(dir)s' % {'dir': env.tmp_dir  })
    put(file, join(env.tmp_dir, TMP_NAME))

@update_env
def deploy():
    install_package()
    #install_sites()
    reload_server()
    sync_db()

@update_env
def install_package():
    with cd(env.tmp_dir):
        extract_symlink = 'extract'
        extract_path = join(env.tmp_dir, extract_symlink)

        run('tar xzf %(file)s; ln -s `tar -tzf %(file)s | sort -nr |tail -n1` %(extract)s' %
            {'file': TMP_NAME,
             'extract': extract_symlink,
             })

        run('pip install -E %(virtualenv)s -r %(extract_path)s/requirements.txt' %
            {
                'extract_path': extract_path,
                'virtualenv': env.virtualenv,
            })

        run('echo "source /etc/pcp/manage-pcp\n%s/bin/django-admin.py \\\$*" > %s' % (env.virtualenv, join(extract_path, 'wsgiadmin', 'bin', 'manage-pcp')))

        run('if [ ! -e %(project_path)s ]; then mkdir -p %(project_path)s; fi; rsync -a --delete %(extract_path)s/* %(project_path)s' % {
            'extract_path' : extract_path,
            'project_path' : env.project_dir,
        })


def install_sites():
    sudo('cp %(rootdir)s/%(project)s/etc/apache2/sites-available/* /etc/apache2/sites-available/' % env)
    sudo('a2ensite %(project)s-mod-wsgi' % env) 

def install_conf():
    sudo('rm -Rf %(confdir)s/*' % env)
    sudo('cp %(rootdir)s/%(project)s/%(confdir)s/* %(confdir)s/' % env)

def reload_server():
    sudo("/etc/init.d/apache2 reload")

def sync_db():
    with cd(env.project_dir):
        run("./wsgiadmin/bin/manage-pcp-sync")


'''

def init_environment():
    #TODO

    return

    REQUIRED_DEBS = ('apache2', 'libapache2-mod-wsgi', 'python', 'python-dev',
                     'python-virtualenv', 'sudo', 'python-lxml', 'rsync',
                     'git', 'mysql-server', 'python-mysqldb', 'python-imaging',)

    sudo("aptitude install -y %s" % " ".join(REQUIRED_DEBS))

    sudo("if [ ! -d %(rootdir)s ]; then mkdir -p %(rootdir)s; chown %(www_user)s %(rootdir)s; fi;" % env)
    sudo("if [ ! -d %(rootdir)s/venv ]; then cd %(rootdir)s; virtualenv %(rootdir)s/venv; fi;" % env, user=env.www_user)
    sudo("if [ ! -d %(confdir)s ]; then mkdir %(confdir)s; fi;" % env)

    MYSQL_INIT = (
        "SET GLOBAL storage_engine=innodb;",
        "DROP DATABASE IF EXISTS pcp",
        "CREATE DATABASE pcp CHARACTER SET utf8 COLLATE utf8_general_ci",
        "GRANT ALL ON pcp.* TO 'pcp'@'localhost' IDENTIFIED BY 'pwd'",
        "FLUSH PRIVILEGES",
    )
    for one in MYSQL_INIT:
        run('mysql --execute="%s"' % one)
'''
