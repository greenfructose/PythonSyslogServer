# Syslog server with really annoying alert message
import logging
import socketserver
import webbrowser

LOG_FILE = 'syslog.log'
ALERT_FILE = 'alert.html'
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
    # 'ICMP PING'
]

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')


class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        for item in ALERT_CRITERIA:
            if item in data:
                print("%s : " % self.client_address[0], str(data))
                with open(ALERT_FILE, 'w+') as f:
                    f.write(f'{ALERT_FILE_HEADER}'
                            f'<p class="alert">{item} has been detected.</p>'
                            f'<p class="log">{data}<p>'
                            f' {ALERT_FILE_FOOTER}')
                webbrowser.open(ALERT_FILE)
                logging.warning(str(data))


if __name__ == "__main__":
    try:
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")
