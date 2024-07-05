import gevent.socket

try:
    import pymssql
except ImportError:
    pymssql = None

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def pymssql_wait_callback(read_fileno):
    gevent.socket.wait_read(read_fileno)


def psycopg2_wait_callback(conn, timeout=None):
    while 1:
        state = conn.poll()
        if state == psycopg2.extensions.POLL_OK:
            break
        elif state == psycopg2.extensions.POLL_READ:
            gevent.socket.wait_read(conn.fileno(), timeout=timeout)
        elif state == psycopg2.extensions.POLL_WRITE:
            gevent.socket.wait_write(conn.fileno(), timeout=timeout)
        else:
            raise psycopg2.OperationalError(
                "Bad result from poll: %r" % state
            )


def set_wait_callback():
    if pymssql is not None:
        pymssql.set_wait_callback(pymssql_wait_callback)

    # На основе примера:
    # https://github.com/gevent/gevent/blob/24.2.1/examples/psycopg2_pool.py
    if psycopg2 is not None:
        psycopg2.extensions.set_wait_callback(psycopg2_wait_callback)
