from contextlib import closing
import socket
from rpyc.utils.authenticators import AuthenticationError
from rpyc.utils.server import ThreadedServer
from abc import abstractmethod, ABC

# from rpyc.utils.server import ThreadedServer
from labview_tools.recording_service.lab_record_service import RecordingService


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
            except Exception:
                pass
            closing(sock)
            self.clients.discard(sock)
            self.continue_or_kill_server()


if __name__ == '__main__':
    my_recording_server = RecordingServer(RecordingService(), port=18861)
    my_recording_server.start()
