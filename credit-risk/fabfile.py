"""Fabric script run commands on a remote server.

Install Fabric to get started.

    pip install Fabric3

To list all available tasks:

    fab list

Run any task using the task name.

    fab hello
"""

from fabric.api import task, run, env, sudo, prompt, cd, put
import yaml

## Change this to IP address/hostname of your remote machine
env.hosts = ['ds00.pipal.in']

# change it to your name
env.user = 'root'

# Set a password
# env.password = open("password.txt").read().strip()

config = yaml.safe_load(open("project.yml"))

ANACONDA_INSTALLER = "https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh"
REPO_URL = config["repo"]

SYSTEM_PACKAGES = config["system_packages"]

SUPERVISOR_TEMPLATE ="""
[program:{name}]
command = {command}
directory = {directory}
redirect_stderr = true
stdout_logfile = /var/log/supervisor/{name}.log
"""

SERVICES = config["services"]

@task
def hello():
    run("echo hello")

@task
def ip():
    run("curl http://httpbin.org/ip")

@task
def provision():
    install_anaconda()
    install_system_packages()

def install_anaconda():
    run("wget -nv -O /tmp/anaconda-installer.sh " + ANACONDA_INSTALLER)
    run("bash /tmp/anaconda-installer.sh -b -p /usr/local/anaconda3")

    # Add anaconda3 to system path
    run("echo 'export PATH=$PATH:/usr/local/anaconda3/bin' > /etc/profile.d/anaconda.sh")

@task
def install_system_packages():
    run("apt-get install -y " + " ".join(SYSTEM_PACKAGES))

@task
def info():
    run("date")
    run("w")
    run("echo $PATH")
    run("python --version")
    run("ls")
    run("supervisorctl status")

@task
def clone():
    run("git clone " + REPO_URL)

@task
def deploy():
    with cd("/root/full-stack-data-science"):
        run("git pull")
        setup_services()

def setup_services():
    config = ""
    for s in SERVICES:
        config += SUPERVISOR_TEMPLATE.format(**s)
    print(config)

    with open("datascience.conf", "w") as f:
        f.write(config)

    put("datascience.conf", "/etc/supervisor/conf.d/datascience.conf")
    run("supervisorctl update")

@task
def train():
    with cd("/root/full-stack-data-science/credit-risk"):
        run("python train.py")

@task
def install_python_packages():
    with cd("/root/full-stack-data-science/credit-risk"):
        run("/usr/local/anaconda3/bin/pip install -r requirements.txt")

@task
def square_service():
    with cd("/root/full-stack-data-science/firefly-examples"):
        run("firefly sq.square -b 0.0.0.0:8000")
