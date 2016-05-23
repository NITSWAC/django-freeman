'''
==============================================================================
Django-Freeman: A one click tool to Django project creation
==============================================================================
'''

from fabric.api import *
from fabvenv import virtualenv
import sys
from importlib import import_module

from unchained import *


env.venv_path = "/home/venvs/"


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


def pip_freeze():
	with virtualenv(env.venv_path + env.venv):
		run("pip freeze")

def pip_install(library):
	with virtualenv(env.venv_path + env.venv):
		run("pip install {library}".format(library = library))

def pip_requirements():
	file_path = env.project_dir+"requirements.txt"
	with virtualenv(env.venv_path + env.venv):
		run("pip install -r {file_path}".format(file_path = file_path))

def pip_install_dependencies():
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
	with cd("/home"):
		run("git clone {repository}".format(repository = env.repo))


def get_project_folder():
	search_path = "/home/"+env.project_name
	env.project_dir = run("find {search_path} -name 'manage.py' -printf '%h'".format(search_path = search_path)) + "/"


def set_mysql_password():
	run("debconf-set-selections <<< 'mysql-server mysql-server/root_password password {pw}';\
		debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password {pw}'".format(pw=env.mysql_password))


def import_config(config_file):
	config_file = config_file[:config_file.index(".py")]
	module = import_module(config_file)
	for attr in dir(module):
		if not attr.startswith('_'):
			globals()[attr] = getattr(module, attr)
	env.host_string = config['host']
	env.user = config['user']
	env.password = config['password']
	env.mysql_password = config['mysql_password']
	env.venv = config['venv']
	env.repo = config['repo']
	env.project_name = env.repo[env.repo.rindex("/")+1:env.repo.rindex(".git")]




if __name__ == "__main__":
	config_file = sys.argv[1]
	import_config(config_file)
	set_mysql_password()
	# pip_freeze()
	# clone_repo()
	get_project_folder()
	pip_install_dependencies()
	pip_requirements()






