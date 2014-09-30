
if os.name == 'nt':
    from nt import NtColor as color
else:
    from posix import PosixColor as color
