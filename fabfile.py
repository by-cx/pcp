from subprocess import CalledProcessError
from getpass import getpass
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

    msg = """
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

        [db]
        type = db type (mysql or pgsql)
        name = db name
        user = db user
        host = db host
        """ % cfg_file

    if not exists(conf_dir):
        os.mkdir(conf_dir)

    cfg = RawConfigParser()
    if not isfile(cfg_file):
        open(cfg_file, 'w').close()
    else:
        cfg.read(cfg_file)

    cfg_update = False
    if 'machine' not in cfg.sections():
        cfg_update = True
        print msg
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


    if 'db' not in cfg.sections():
        cfg_update = True
        print msg

        cfg.add_section('db')
        db_type = raw_input("db type (mysql/pgsql): ")
        cfg.set('db', 'type', db_type.strip())

        cfg.add_section('db')
        db_name = raw_input("db name: ")
        cfg.set('db', 'name', db_name.strip())

        cfg.add_section('db')
        db_user = raw_input("db user: ")
        cfg.set('db', 'user', db_user.strip())

        cfg.add_section('db')
        db_host = raw_input("db host: ")
        cfg.set('db', 'host', db_host.strip())

    if cfg_update:
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
                ERROR: Using root directory as tmp. directory is not allowed, I'm out"""
            sys.exit(1)
        if os.path.exists(tmp_dir) and os.listdir(tmp_dir):
            orly = raw_input("Temp. directory is not empty, are you sure you want continue? (y/N) ")
            if orly.strip() not in ['y', 'Y']:
                sys.exit(0)

        env.tmp_dir = tmp_dir

        env.virtualenv = cfg.get('machine', 'virtualenv')
        env.project_dir = cfg.get('machine', 'project_dir')

        env.db_type = cfg.get('db', 'type')
        env.db_name = cfg.get('db', 'name')
        env.db_user = cfg.get('db', 'user')
        env.db_host = cfg.get('db', 'host')

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

        run('rsync -a --delete %(extract_path)s/* %(project_path)s' % {
            'extract_path' : extract_path,
            'project_path' : env.project_dir,
        })

@update_env
def init_env():
    try:
        # same path as in wsgiadmin/settings/__init__.py, line 5
        CONF_DIR = '/etc/pcp/'
        run("if [ ! -d %(confdir)s ]; then mkdir %(confdir)s; fi;" % {
            'confdir': CONF_DIR,
        })
    except SystemExit:
        print 'error while creating config directory %s, create it yourself and then try again' % CONF_DIR
        raw_input("press any key to quit")
        sys.exit(0)

    run("if [ ! -e %(project_path)s ]; then mkdir -p %(project_path)s; fi;" % {
        'project_path': env.project_dir,
        })

    run("if [ ! -d %(virtualenv)s ]; then virtualenv %(virtualenv)s; fi;" % {
        'virtualenv': env.virtualenv,
        })

    if env.db_type.lower() == 'mysql':
        pwd = "pwd"
        pwd2 = "pwd2"

        while pwd.strip() != pwd2.strip():
            pwd = getpass("Insert db password: ")
            pwd2 = getpass("Retype db password (typo check): ")

        env.db_pwd = pwd.strip()
        MYSQL_INIT = (
            "SET GLOBAL storage_engine=innodb;",
            "DROP DATABASE IF EXISTS %(db_name)s" % env,
            "CREATE DATABASE %(db_name)s CHARACTER SET utf8 COLLATE utf8_general_ci" % env,
            "GRANT ALL ON %(db_name)s.* TO '%(db_user)s'@'%(db_host)s' IDENTIFIED BY '%(db_pwd)s'" % env,
            "FLUSH PRIVILEGES",
        )
        for one in MYSQL_INIT:
            env.db_cmd = one
            run('mysql -u%(db_user) -p%(db_pwd) -h%(db_host) --execute="%(db_cmd)s"' % env)
        env.db_pwd = ""

    elif  env.db_type.lower() == 'pgsql':
        print "posgresql db init not yet implemented, sorry .("

    else:
        print "not sure which type of database to use, sorry. Do it yourself"

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
