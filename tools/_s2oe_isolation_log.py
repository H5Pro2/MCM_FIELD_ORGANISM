"""Diagnostic-only forwarding of native ERROR/FATAL messages; no media values."""
import logging


def install(av, send):
    class NativeHandler(logging.Handler):
        def emit(self, record):
            send(dict(level=record.levelno, component=record.name, message=record.getMessage()))
    logger = logging.getLogger("libav")
    logger.handlers = [NativeHandler()]
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    av.logging.set_skip_repeated(False)
    av.logging.set_level(av.logging.ERROR)
