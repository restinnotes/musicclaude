"""Probe: read physical memory headroom via GlobalMemoryStatusEx (read-only)."""
import ctypes


class MEM(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


m = MEM()
m.dwLength = ctypes.sizeof(MEM)
ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
print("ok=%s" % bool(ok))
print("avail_phys_GiB=%.2f" % (m.ullAvailPhys / 2 ** 30))
print("total_phys_GiB=%.2f" % (m.ullTotalPhys / 2 ** 30))
print("load_pct=%d" % m.dwMemoryLoad)
