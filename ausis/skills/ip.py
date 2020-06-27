from os import system
from colorama import Fore

from core.GeneralUtilities import executable_exists
from plugin import plugin, require, UNIX, WINDOWS


@require(platform=UNIX)
@plugin('ip')
class IP():
    """
    Display local and public ip address
    """

    def __init__(self):
        self._local_ip = """ifconfig | grep -Eo 'inet (addr:)?([0-9]*\\.){3}[0-9]*' |
                    grep -Eo '([0-9]*\\.){3}[0-9]*' | grep -v '127.0.0.1'"""

        # 10 seconds time out if not connected to internet
        self._public_ip_v4 = "curl -4 ifconfig.co --connect-timeout 10 2> /dev/null || echo 'not available'"
        self._public_ip_v6 = "curl -6 ifconfig.co --connect-timeout 10 2> /dev/null || echo 'not available'"

    def __call__(self, ausis, s):
        if executable_exists('ifconfig'):
            self._get_local_ip(ausis)
            ausis.say("")

        self._get_public_ip(ausis)

    def _get_local_ip(self, ausis):
        ausis.say("List of local ip addresses :", Fore.BLUE)
        system(self._local_ip)

    def _get_public_ip(self, ausis):
        ausis.say("Public ip v4 address :", Fore.BLUE)
        system(self._public_ip_v4)
        ausis.say("Public ip v6 address :", Fore.BLUE)
        system(self._public_ip_v6)


@require(platform=WINDOWS)
@plugin('ip')
def ip_WIN32(ausis, s):
    """
    Returns information about IP for windows
    """
    import socket

    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    ausis.say("IP address: " + str(IP))
