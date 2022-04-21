import sys
import subprocess
from subprocess import Popen, PIPE

AV_LOG_QUIET   = "quiet"
AV_LOG_PANIC   = "panic"
AV_LOG_FATAL   = "fatal"
AV_LOG_ERROR   = "error"
AV_LOG_WARNING = "warning"
AV_LOG_INFO    = "info"
AV_LOG_VERBOSE = "verbose"
AV_LOG_DEBUG   = "debug"

ffmpeg_loglevel = AV_LOG_ERROR

IS_WIN32 = 'win32' in str(sys.platform).lower()
SUBPROCESS_ARGS = {}
if IS_WIN32:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    SUBPROCESS_ARGS['startupinfo'] = startupinfo


def popen_ffmpeg(inner_args):

    cmd = [
        'ffmpeg',

        *inner_args,

        # logging
        '-loglevel', ffmpeg_loglevel,
        '-hide_banner',
    ]

    process = Popen(cmd, stdout=PIPE, stderr=PIPE, **SUBPROCESS_ARGS)
    stdout, stderr = process.communicate()
    print(stderr.decode(), end='', file=sys.stderr)
    return stdout, stderr