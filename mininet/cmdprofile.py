"""Lightweight command timing profiler for Mininet."""

import os
import threading


_ENABLED = os.environ.get('MININET_CMD_PROFILE', '0').lower() in (
    '1', 'true', 'yes', 'on'
)
_LOCK = threading.Lock()
_STATS = {}


def _new_source():
    return {'count': 0, 'total_s': 0.0, 'ip_link_count': 0, 'ip_link_s': 0.0}


def _init():
    global _STATS
    _STATS = {
        'count': 0,
        'total_s': 0.0,
        'ip_link_count': 0,
        'ip_link_s': 0.0,
        'sources': {}
    }


_init()


def set_enabled(enabled):
    "Enable/disable profiler."
    global _ENABLED
    _ENABLED = bool(enabled)


def enabled():
    "Return whether command profiling is enabled."
    return _ENABLED


def reset():
    "Reset profiler counters."
    with _LOCK:
        _init()


def _cmd_to_text(cmd):
    if isinstance(cmd, str):
        return cmd.strip()
    if isinstance(cmd, (list, tuple)):
        return ' '.join(str(arg) for arg in cmd).strip()
    return str(cmd).strip()


def _is_ip_link(cmd_text):
    cmd_text = cmd_text.lstrip()
    return cmd_text.startswith('ip link ')


def record_command_timing(source, cmd, duration_s):
    "Record one command timing event."
    if not _ENABLED or duration_s < 0:
        return
    cmd_text = _cmd_to_text(cmd)
    is_ip_link = _is_ip_link(cmd_text)
    with _LOCK:
        _STATS['count'] += 1
        _STATS['total_s'] += duration_s
        if is_ip_link:
            _STATS['ip_link_count'] += 1
            _STATS['ip_link_s'] += duration_s
        src = _STATS['sources'].setdefault(source, _new_source())
        src['count'] += 1
        src['total_s'] += duration_s
        if is_ip_link:
            src['ip_link_count'] += 1
            src['ip_link_s'] += duration_s


def snapshot():
    "Return a copy of current stats."
    with _LOCK:
        snap = {
            'count': _STATS['count'],
            'total_s': _STATS['total_s'],
            'ip_link_count': _STATS['ip_link_count'],
            'ip_link_s': _STATS['ip_link_s'],
            'sources': {}
        }
        for src, vals in _STATS['sources'].items():
            snap['sources'][src] = dict(vals)
        return snap
