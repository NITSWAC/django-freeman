from fabric.api import *
import sys
from importlib import import_module

# env.host_string = "128.199.243.42"
# env.user = 'root'
# env.password = 'panacea!@#$90-='
# env.venv = "panvenv"




def list_homedir():
	with cd("/home"):
		l = run("ls")
		return l


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

def activate_virtualenv():
	with cd("/home/venvs"):
		run("source {venv}/bin/activate".format(venv = env.venv))


def pip_freeze():
	run("pip freeze")

def pip_install(library):
	run("pip install {library}".format(library = library))

def apt_install(package):
	run("apt-get install -y {package}".format(package = package))

def apt_update():
	run("apt-get update")

# create_virtualenv()
# activate_virtualenv()
# pip_install("requests")





def import_config(config_file):
	config_file = config_file[:config_file.index(".py")]
	module = import_module(config_file)
	for attr in dir(module):
		if not attr.startswith('_'):
			globals()[attr] = getattr(module, attr)
	env.host_string = config['host']
	env.user = config['user']
	env.password = config['password']
	env.venv = config['venv']




if __name__ == "__main__":
	config_file = sys.argv[1]
	import_config(config_file)
	from unchained import *
	print config
	apt_install(packages['general'])

