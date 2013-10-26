from wsgiadmin.apps.models import Db
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.utils import get_mysql_server, get_pgsql_server


class DbObject(Db):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):

        super(DbObject, self).__init__(*args, **kwargs)
        if self.db_type == "mysql":
            database_server = get_mysql_server()[0] if not self.app.db_server else self.app.db_server
            self.script = Script(database_server)
        elif self.db_type == "pgsql":
            database_server = get_pgsql_server()[0] if not self.app.db_server else self.app.db_server
            self.script = Script(database_server)
        if not self.app.db_server:
            self.app.db_server = database_server
            self.app.save()

    def install(self):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="CREATE DATABASE %s;" % self.name)
            self.script.add_cmd("mysql -u root", stdin="CREATE USER '%s'@'%%' IDENTIFIED BY '%s';" % (self.name, self.password))
            self.script.add_cmd("mysql -u root", stdin="GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' WITH GRANT OPTION;" % (self.name, self.name))
        elif self.db_type == "pgsql":
            self.script.add_cmd("createuser -D -R -S %s" % self.name)
            if self.pg_postgis:
                self.script.add_cmd("createdb -T template_postgis -O %s %s" % (self.name, self.name))
            else:
                self.script.add_cmd("createdb -O %s %s" % (self.name, self.name))
            self.passwd(self.password)

    def passwd(self, password):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="UPDATE mysql.user SET Password=PASSWORD('%s') WHERE User = '%s';" % (password, self.name))
            self.script.add_cmd("mysql -u root", stdin="FLUSH PRIVILEGES;")
        elif self.db_type == "pgsql":
            sql = "ALTER USER %s WITH PASSWORD '%s';" % (self.name, password)
            self.script.add_cmd("psql template1", stdin=sql)

    def uninstall(self):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="DROP DATABASE %s;" % self.name)
            self.script.add_cmd("mysql -u root", stdin="DROP USER %s;" % self.name)
        elif self.db_type == "pgsql":
            self.script.add_cmd("dropdb %s" % self.name)
            self.script.add_cmd("dropuser %s" % self.name)

    def commit(self, no_thread=False):
        self.script.commit(no_thread)