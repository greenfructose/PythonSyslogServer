# Syslog server with really annoying alert message
import logging
import socketserver
import webbrowser
import tempfile
import os
import time

LOG_FILE = 'syslog.log'
HOST, PORT = "0.0.0.0", 514
ALERT_FILE_HEADER = '''
        <!DOCTYPE html>
        <html>
          <head>
            <title>SYSLOG ALERT</title>
            <style>
              .blink {
                animation: blinker 0.6s linear infinite;
                color: red;
                font-size: 60px;
                font-weight: bold;
                font-family: sans-serif;
                text-align: center;
              }
              @keyframes blinker {
                50% {
                  opacity: 0;
                }
              }
              .alert {
                color: red;
                font-size: 30px;
                font-weight: bold;
                font-family: sans-serif;
                text-align: center;
              }
              .log {
                color: gray;
                font-size: 15px;
                font-weight: bold;
                font-family: sans-serif;
                text-align: center;
              }
            </style>
          </head>
          <body>
            <h1 class="blink">Alert</h1>
    '''

ALERT_FILE_FOOTER = '''
        <p class="alert">Check Syslog for details.</p>
          </body>
        </html>       
    '''

ALERT_CRITERIA = [
    'Possible port scan',
    'Probable port scan',
    'ICMP PING'
]

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')


class AlertTemporaryFile:

    def __init__(self, mode='w', delete=True):
        self._mode = mode
        self._delete = delete

    def __enter__(self, item, data):
        # Create randomized file name
        file_name = f'{os.path.join(tempfile.gettempdir(), os.urandom(24).hex())}.html'
        print(file_name)
        # Check that file was created succsefully
        open(file_name, "x").close()
        self._tempFile = open(file_name, self._mode)
        # Write alert HTML file
        self._tempFile.write((f'{ALERT_FILE_HEADER}'
                              f'<p class="alert">{item} has been detected.</p>'
                              f'<p class="log">{data}<p>'
                              f' {ALERT_FILE_FOOTER}'))
        return self._tempFile

    def __exit__(self):
        self._tempFile.close()
        # Open Alert HTML file
        webbrowser.open(self._tempFile.name)
        # Give time for file to open before deleting
        time.sleep(1)
        if self._delete:
            os.remove(self._tempFile.name)

    @property
    def tempFile(self):
        return self._tempFile


class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        for item in ALERT_CRITERIA:
            if item in data:
                print("%s : " % self.client_address[0], str(data))
                ALERT_FILE = AlertTemporaryFile()
                ALERT_FILE.__enter__(data=data, item=item)
                ALERT_FILE.__exit__()
                logging.warning(str(data))


if __name__ == "__main__":
    try:
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")
