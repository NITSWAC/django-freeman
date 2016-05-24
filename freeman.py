'''
==============================================================================
Django-Freeman: A one click tool to Django project creation
==============================================================================
'''

from fabric.api import *
from fabric.contrib import django
from fabvenv import virtualenv
import sys, os
from importlib import import_module
from tempfile import NamedTemporaryFile
import colorama
from colorama import Fore, Back, Style

from unchained import *


env.venv_path = "/home/venvs/"
env.gunicorn_path = "/etc/init/"
env.nginx_path = "/etc/nginx/sites-available/"



def localprint(message):
	print Fore.GREEN + message
	print(Style.RESET_ALL)

'''
Usage: Listing home directory of the home/ folder of the server
'''
def list_homedir():
	with cd("/home"):
		l = run("ls")
		return l

'''
Usage: Create virtualenv of the name specified in the config
Checks whether an exsisting virtualenv is there, and if not creates a new one
'''
def create_virtualenv():
	localprint("Creating a virtualenv")
	with cd("/home"):
		run("if [ ! -d venvs ]; then mkdir venvs; fi")
		with cd("venvs"):
			exists = run("if [ -d {venv} ]; then echo True; fi".format(venv = env.venv))
			if exists:
				_continue = prompt("A virtual environment with the same name already exists. Do you want to replace(y/n)?\n")
				if _continue == 'y':
					result = run("virtualenv {venv}".format(venv=env.venv))
					print "Created a Virtual Environment {venv}".format(venv = env.venv)
				else:
					print "Virtual Environment {venv} already exists. No changes made.".format(venv = env.venv)
			else:
				result = run("virtualenv {venv}".format(venv=env.venv))
				print "Created a Virtual Environment {venv}".format(venv = env.venv)

'''
Usage: Activates the virtualenv that is specified in the config
'''

def install_virtualenv():
	run("pip install virtualenv")

def pip_freeze():
	with virtualenv(env.venv_path + env.venv):
		run("pip freeze")

def pip_install(library):
	with virtualenv(env.venv_path + env.venv):
		run("pip install {library}".format(library = library))

def pip_requirements():
	localprint("Installing required pip libraries")
	file_path = env.project_dir+"requirements.txt"
	with virtualenv(env.venv_path + env.venv):
		run("pip install -r {file_path}".format(file_path = file_path))

def pip_install_dependencies():
	localprint("Installing required packages for the pip requirements")
	file_path = env.project_dir+"requirements.txt"
	libraries = []
	print "fahkjadlasdada", file_path
	libraries = run("cat {file_path}".format(file_path = file_path)).split("\n")
	libraries = [library[:library.index("=")] for library in libraries]
	for library in libraries:
		if library in packages.keys():
			apt_install(packages[library])

def apt_install(package):
	run("apt-get install -y {package}".format(package = package))

def apt_update():
	run("apt-get update")

'''
Usage: Clones the repo specified in the config
'''
def clone_repo():
	localprint("Cloning repository from GIT")
	with cd("/home"):
		run("git clone {repository}".format(repository = env.repo))



def configure_db():
	print env.project_name + ".settings"
	django.settings.module(env.project_name + ".settings")
	from django.conf import settings
	print settings.DATABASES

def get_project_folder():
	search_path = "/home/"+env.project_name
	env.project_dir = run("find {search_path} -name 'manage.py' -printf '%h'".format(search_path = search_path)) + "/"


def set_mysql_password():
	run("debconf-set-selections <<< 'mysql-server mysql-server/root_password password {pw}';\
		debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password {pw}'".format(pw=env.mysql_password))


def make_migrations():
	localprint("Making migrations..")
	with virtualenv(env.venv_path + env.venv):
		with cd(env.project_dir):
			run("python manage.py makemigrations")


def migrate():
	localprint("Migrating..")
	with virtualenv(env.venv_path + env.venv):
		with cd(env.project_dir):
			run("python manage.py migrate")


def collect_static():
	localprint("Collecting static files")
	with virtualenv(env.venv_path + env.venv):
		with cd(env.project_dir):
			run("python manage.py collectstatic")

def start_gunicorn():
	run("service gunicorn start")

def configure_gunicorn():
	localprint("Configuring gunicorn..")
	gconf = NamedTemporaryFile(delete=False)
	localgconf = open("gunicorn.conf")
	gconf.write(localgconf.read().format(project_name = env.project_name, venv_path = env.venv_path + env.venv, project_path = env.project_dir, username = env.user))
	gconf.close()
	put(gconf.name, env.gunicorn_path+"gunicorn.conf")
	os.unlink(gconf.name)
	start_gunicorn()


def test_nginx():
	localprint("Testing nginx..")
	run("nginx -t")

def restart_nginx():
	run("service nginx restart")

def configure_nginx():
	localprint("Configuring nginx..")
	nconf = NamedTemporaryFile(delete=False)
	localnconf = open("nginx.conf")
	nconf.write(localnconf.read().format(host_port = env.deploy_port, host_ip = env.host_string, project_name = env.project_name, project_path = env.project_dir))
	nconf.close()
	put(nconf.name, env.nginx_path + env.project_name)
	os.unlink(nconf.name)
	run("ln -s /etc/nginx/sites-available/{project_name} /etc/nginx/sites-enabled".format(project_name = env.project_name))
	run("rm /etc/nginx/sites-enabled/default")
	test_nginx()
	restart_nginx()


def import_config(config_file):
	config_file = config_file[:config_file.index(".py")]
	module = import_module(config_file)
	for attr in dir(module):
		if not attr.startswith('_'):
			globals()[attr] = getattr(module, attr)
	env.host_string = config['host']
	env.deploy_port = config['port']
	env.user = config['user']
	env.password = config['password']
	env.mysql_password = config['mysql_password']
	env.venv = config['venv']
	env.repo = config['repo']
	env.project_name = env.repo[env.repo.rindex("/")+1:env.repo.rindex(".git")]




def initialize():
	config_file = sys.argv[1]
	import_config(config_file)
	set_mysql_password()
	colorama.init()
	localprint("Inited")



def deploy():
	apt_update()
	apt_install(packages['general'])
	apt_install(packages['nginx'])
	apt_install(packages['git'])

	clone_repo()
	get_project_folder()
	install_virtualenv()
	create_virtualenv()

	pip_install_dependencies()
	pip_requirements()
	pip_install(pip_libraries['gunicorn'])

	make_migrations()
	migrate()
	collect_static()

	configure_gunicorn()
	configure_nginx()




if __name__ == "__main__":
	initialize()
	deploy()






