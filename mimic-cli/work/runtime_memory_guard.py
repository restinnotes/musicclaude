"""Windows physical and global commit headroom for RCA probes."""
import ctypes
from datetime import datetime, timezone
import json
from pathlib import Path
import threading

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1625Z/memory'

class MemoryStatus(ctypes.Structure):
    _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong) for name in ('total_physical','available_physical',
            'total_pagefile','available_pagefile','total_virtual','available_virtual','available_extended_virtual')]

class PerformanceInfo(ctypes.Structure):
    _fields_ = [('size', ctypes.c_ulong)] + [
        (name, ctypes.c_size_t) for name in ('commit_total','commit_limit','commit_peak',
            'physical_total','physical_available','system_cache','kernel_total',
            'kernel_paged','kernel_nonpaged','page_size')] + [
        (name, ctypes.c_ulong) for name in ('handle_count','process_count','thread_count')]

def snapshot():
    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError('Windows physical-memory query failed')
    performance = PerformanceInfo()
    performance.size = ctypes.sizeof(performance)
    if not ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(performance), performance.size):
        raise RuntimeError('Windows global commit query failed')
    commit_unit = performance.page_size / 2**30
    return {'utc':datetime.now(timezone.utc).isoformat(), 'physical_load_percent':status.load,
        'total_physical_gib':round(status.total_physical / 2**30,3),
        'available_physical_gib':round(status.available_physical / 2**30,3),
        'total_commit_gib':round(performance.commit_limit * commit_unit,3),
        'used_commit_gib':round(performance.commit_total * commit_unit,3),
        'available_commit_gib':round((performance.commit_limit - performance.commit_total) * commit_unit,3),
        'commit_load_percent':round(100 * performance.commit_total / performance.commit_limit,1)}

def headroom_error(row, minimum_physical_gib=3, minimum_commit_gib=3):
    # Single-request diagnostics: reserve space above the already-running browser.
    # Do not apply this budget to an eight-request stress run.
    if row['available_physical_gib'] < minimum_physical_gib:
        return f'Windows has less than {minimum_physical_gib} GiB free physical memory'
    if row['available_commit_gib'] < minimum_commit_gib:
        return f'Windows has less than {minimum_commit_gib} GiB global commit headroom'
    return None

class ProbeMemoryTimeline:
    def __init__(self, container, minimum_physical_gib=3, minimum_commit_gib=3):
        self.container = container
        self.minimum_physical_gib = minimum_physical_gib
        self.minimum_commit_gib = minimum_commit_gib
        self.stop = threading.Event()
        self.minimum_available_gib = None
        self.minimum_commit_available_gib = None
        self.samples = 0
        self.thread = None

    def sample(self, stage):
        row = {**snapshot(), 'stage':stage, 'container':self.container}
        available = row['available_physical_gib']
        self.minimum_available_gib = min(available, self.minimum_available_gib) if self.minimum_available_gib is not None else available
        commit_available = row['available_commit_gib']
        self.minimum_commit_available_gib = min(commit_available, self.minimum_commit_available_gib) if self.minimum_commit_available_gib is not None else commit_available
        self.samples += 1
        OUT.mkdir(exist_ok=True)
        with (OUT / 'probe-memory-timeline.jsonl').open('a',encoding='utf-8') as file:
            file.write(json.dumps(row) + '\n')
        return row

    def __enter__(self):
        row = self.sample('before_probe')
        reason = headroom_error(row, self.minimum_physical_gib, self.minimum_commit_gib)
        if reason:
            raise RuntimeError('RCA probe not submitted: ' + reason)
        def observe():
            while not self.stop.wait(5):
                self.sample('generation_wait')
        self.thread = threading.Thread(target=observe,daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *arguments):
        self.stop.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        self.sample('after_probe')

    def summary(self):
        return {'minimum_windows_available_gib':self.minimum_available_gib,
            'minimum_windows_commit_available_gib':self.minimum_commit_available_gib,
            'memory_samples':self.samples,'sampling_interval_seconds':5,
            'minimum_free_before_probe_gib':self.minimum_physical_gib,
            'minimum_commit_headroom_before_probe_gib':self.minimum_commit_gib,
            'budget_scope':'one_request_with_existing_browser',
            'in_flight_generation_automatically_aborted':False}
