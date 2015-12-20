# Disclaimer
THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INOMALY LLC
OR ANY OF IT'S CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

# Prerequisites to Running this Benchmark Suite

## Install SSH (Servers & Clients)
* Ubuntu 14 - open a new xterm and run `sudo apt-get install openssh-server` to install SSH.
* Mac OS - see [Apple's instructions](https://support.apple.com/kb/PH18726?locale=en_US to enable SSH).

## Configure SSH (Server-only)
If you don't already have SSH configured for password-less access, open a new xterm and run the following for each user
account that will be starting the server:
* `ssh-keygen -t rsa`. **Do not input a passphrase!**
* Copy the contents of `~/.ssh/id_rsa.pub` into `~/.ssh/authorized_keys`.
* Run `slogin $HOSTNAME` to check that password-less SSH access has been enabled and to add to your current PC's hostname to the list of known SSH hosts.
* Optional - repeat the previous step for client machines to get them added into `~/.ssh/known_hosts`

## Install the Python Package Index (PyPI) and Required Python Packages (Servers & Clients)
Open a new xterm:
* On Mac OS, run `sudo easy_install pip` to install PyPI. For Ubuntu, the necessary command is `sudo apt-get install python-pip`.
* `sudo pip install bottle` **Only required for machines acting as servers.**
* `sudo pip install psutil` **Only required for machines acting as clients.** **On Debian-based boxes, you'll likely have to run `sudo apt-get install python-dev` first for this command to succeed.**

# Startup Instructions (Server)
Open a new xterm:
* `PYTHONPATH=.;export PYTHONPATH`
* `python -m perf_analyzer.Server` to start the benchmark suite or `python -m perf_analyzer.Server --help` to see a list of available options.
* Open `http://localhost:8080` in your favorite web browser to view the real-time status of the suite, results, etc.