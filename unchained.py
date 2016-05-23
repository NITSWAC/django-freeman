

# commands = {
# 	'MySQL-python' : "debconf-set-selections <<< 'mysql-server mysql-server/root_password password {pw}';\
# 					debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password {pw}'".format(pw=config['password']),
# }

packages = {
	'general' : 'python-pip python-dev',
	'nginx' : 'nginx',
	'git' : 'git',
	'Pillow': 'libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk',
	'MySQL-python': 'mysql-server libmysqlclient-dev'
}


pip_libraries = {
	'virtualenv' : 'virtualenv',
	'gunicorn' : 'gunicorn'
}