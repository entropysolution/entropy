# -*- coding: utf-8 -*-
# ~
# Vortex AAA Radius (ARC) 
# entropysoln
# ~
#

import sys
import logging
import threading
import traceback
import multiprocessing
from logging.handlers import TimedRotatingFileHandler

class MultiProcessingLog(logging.Handler):
    def __init__(self, name, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        logging.Handler.__init__(self)

        #self._handler = RotatingFileHandler(name, mode, maxsize, rotate)
        self._handler = TimedRotatingFileHandler(name, when, interval, backupCount, encoding, delay, utc)
        self.queue = multiprocessing.Queue(-1)

        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self._handler.emit(record)
                #print('received on pid {}'.format(os.getpid()))
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args have been stringified. Removes any
        # chance of unpickleable things inside and possibly reduces message size
        # sent over the pipe
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            # dummy = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self._handler.close()
        logging.Handler.close(self)