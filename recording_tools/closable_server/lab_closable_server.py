import errno
import sys
from contextlib import closing
import socket

from rpyc.lib.compat import get_exc_errno
from rpyc.utils.authenticators import AuthenticationError
from rpyc.utils.server import ThreadedServer
from abc import abstractmethod, ABC

# from rpyc.utils.server import ThreadedServer
from recording_tools.recording_service.lab_record_service import RecordingService


class Closable(ABC):

    @abstractmethod
    def continue_or_kill_server(self):
        pass


class RecordingServer(ThreadedServer, Closable):
    def __init__(self, service, port=0):
        super(ThreadedServer, self).__init__(service, port=port)

    def continue_or_kill_server(self):
        """implementing logic for closing server here"""
        try:
            will_shut_down = self.service.shutdown_service_flag
        except AttributeError:
            print('did not define service shutdown flag in your service. Server cannot be closed with this flag')
        else:
            if will_shut_down:
                self.active = False
                self.close()

    def _authenticate_and_serve_client(self, sock):
        try:
            if self.authenticator:
                addrinfo = sock.getpeername()
                try:
                    sock2, credentials = self.authenticator(sock)
                except AuthenticationError:
                    self.logger.info("%s failed to authenticate, rejecting connection", addrinfo)
                    return
                else:
                    self.logger.info("%s authenticated successfully", addrinfo)
            else:
                credentials = None
                sock2 = sock
            try:
                self._serve_client(sock2, credentials)
            except Exception:
                self.logger.exception("client connection terminated abruptly")
                raise
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                print(e)
            closing(sock)
            self.clients.discard(sock)
            self.continue_or_kill_server()

    def accept(self):
        """accepts an incoming socket connection (blocking)"""
        while self.active:
            try:
                sock, addrinfo = self.listener.accept()
                print('okkkkkkkkkkkkkkkk')
            except socket.timeout:
                pass
            except socket.error:
                ex = sys.exc_info()[1]
                if get_exc_errno(ex) in (errno.EINTR, errno.EAGAIN):
                    pass
                else:
                    raise EOFError()
            else:
                break

        if not self.active:
            return

        sock.setblocking(True)
        self.logger.info("accepted %s with fd %s", addrinfo, sock.fileno())
        self.clients.add(sock)
        self._accept_method(sock)
