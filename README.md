# Disclaimer
Hard Disk Performance Analyzer is now roughly 85% complete, and a few key features are still missing. That said,
it runs and basically does what it's designed to do at this point.

# Getting started (Mac/Linux)
Open a new xterm:
* `sudo easy_install pip`
* `sudo pip install bottle`
* `sudo pip install psutil`
* `ssh-keygen -t rsa` **Do not input a passphrase!**
* Copy the contents of `~/.ssh/id_rsa.pub` into `~/.ssh/known_hosts`
* `PYTHONPATH=.;export PYTHONPATH`
* `python -m perf_analyzer.Server`
* Open `http://localhost:8080` in your favorite web browser