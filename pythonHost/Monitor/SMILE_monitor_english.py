"""Configurable ZeroRPC monitor. Run: python SMILE_monitor_universal.py"""
from __future__ import annotations

import configparser
from collections import deque
import math
from pathlib import Path
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

CONFIG_FILE = Path(__file__).resolve().with_name('monitor.ini')
DEFAULTS = {
    'connection': {'host': '127.0.0.1', 'port': '2020', 'timeout': '3'},
    'device': {'hello': 'SMILE'},
    'monitor': {'poll_seconds': '1.0', 'history_points': '300',
                'commands': 'f1, f2', 'mode_command': 'mode'},
    'mode_colors': {'0': '#25a65a', '1': '#f3c623', '3': '#f28c28',
                    '4': '#df3b47', 'other': '#888888'},
    'graph': {'color1': '#f39c35', 'color2': '#46a8ec'},
}


def read_config():
    cfg = configparser.ConfigParser()
    cfg.read_dict(DEFAULTS)
    cfg.read(CONFIG_FILE, encoding='utf-8')
    commands = [x.strip() for x in cfg.get('monitor', 'commands').split(',') if x.strip()]
    if not 1 <= len(commands) <= 2 or any(not x.isidentifier() for x in commands):
        raise ValueError('[monitor] commands must contain 1 or 2 names, for example f1, f2')
    interval = cfg.getfloat('monitor', 'poll_seconds')
    points = cfg.getint('monitor', 'history_points')
    timeout = cfg.getfloat('connection', 'timeout')
    if not 0.1 <= interval <= 3600 or not 10 <= points <= 10000 or not 0.1 <= timeout <= 120:
        raise ValueError('Invalid poll_seconds, history_points, or timeout in monitor.ini')
    if not cfg.get('monitor', 'mode_command').isidentifier():
        raise ValueError('Invalid mode_command')
    return cfg, commands, interval, points, timeout


def save_host_port(host, port):
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE, encoding='utf-8')
    if not cfg.has_section('connection'):
        cfg.add_section('connection')
    cfg.set('connection', 'host', host)
    cfg.set('connection', 'port', str(port))
    with CONFIG_FILE.open('w', encoding='utf-8') as f:
        cfg.write(f)


def scalar(value, label):
    """Reject unexpected RPC response types; do not silently plot list elements."""
    if isinstance(value, bool) or isinstance(value, (list, tuple, dict)):
        raise ValueError(f'{label}: expected a number, received {value!r}')
    try:
        number = float(value)
    except (TypeError, ValueError) as ex:
        raise ValueError(f'{label}: expected a number, received {value!r}') from ex
    if not math.isfinite(number):
        raise ValueError(f'{label}: invalid value {value!r}')
    return number


class RpcWorker(threading.Thread):
    """Sole owner of the RPC client. All GUI work runs on Tk thread."""
    def __init__(self, endpoint, expected, mode_cmd, plot_cmds, interval, timeout, events, stop_event):
        super().__init__(daemon=True)
        self.endpoint, self.expected = endpoint, expected
        self.mode_cmd, self.plot_cmds = mode_cmd, plot_cmds
        self.interval, self.timeout = interval, timeout
        self.events, self.stop_event = events, stop_event

    def run(self):
        client = None
        authenticated = False
        try:
            import zerorpc
            client = zerorpc.Client(timeout=self.timeout)
            client.connect(self.endpoint)
            self.events.put(('log', f'Connecting: {self.endpoint}'))
            try:
                response = client.command('hello')
            except Exception as ex:
                self.events.put(('error', f'No response to hello: {ex}'))
                return
            self.events.put(('log', f"client.command('hello') -> {response!r}"))
            if response != self.expected:
                self.events.put(('error', f'Unexpected hello response: {response!r} instead of {self.expected!r}'))
                return
            authenticated = True
            self.events.put(('connected', f'Connected: hello = {response}'))
            next_poll = time.monotonic()
            while not self.stop_event.is_set():
                remaining = next_poll - time.monotonic()
                if remaining > 0:
                    self.stop_event.wait(min(remaining, 0.2))
                    continue
                next_poll = time.monotonic() + self.interval
                # Read each command independently: transient errors do not erase history.
                try:
                    mode = scalar(client.command(self.mode_cmd), self.mode_cmd)
                    if not mode.is_integer():
                        raise ValueError(f'{self.mode_cmd}: mode must be an integer')
                    self.events.put(('mode', int(mode)))
                except Exception as ex:
                    self.events.put(('poll_error', f'{self.mode_cmd}: {ex}'))
                values = {}
                for cmd in self.plot_cmds:
                    try:
                        values[cmd] = scalar(client.command(cmd), cmd)
                    except Exception as ex:
                        self.events.put(('poll_error', f'{cmd}: {ex}'))
                if values:
                    self.events.put(('sample', (time.monotonic(), values)))
        except Exception as ex:
            self.events.put(('error', f'Connection error: {ex}'))
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception as ex:
                    self.events.put(('log', f'client.close() — {ex}'))
            self.events.put(('disconnected', 'Connection closed' if authenticated else 'No active connection'))


class Monitor:
    def __init__(self, root):
        self.root = root
        self.cfg, self.plot_cmds, self.interval, points, self.timeout = read_config()
        self.history = deque(maxlen=points)
        self.events = queue.Queue()
        self.worker = None
        self.stop_event = None
        self.connected = False
        self.closing = False
        self.last_error = ''
        root.title('ZeroRPC Monitor')
        root.geometry('1000x650')
        root.minsize(640, 420)
        self.host = tk.StringVar(value=self.cfg.get('connection', 'host'))
        self.port = tk.StringVar(value=self.cfg.get('connection', 'port'))
        self.status = tk.StringVar(value='Disconnected')
        self.mode_label = tk.StringVar(value='MODE: —')
        self.values_label = tk.StringVar(value=' | '.join(f'{c}: —' for c in self.plot_cmds))
        self.diagnostic = tk.StringVar(value='')

        main = ttk.Frame(root, padding=12)
        main.pack(fill='both', expand=True)
        line = ttk.Frame(main)
        line.pack(fill='x')
        ttk.Label(line, text='Address:').pack(side='left')
        ttk.Entry(line, textvariable=self.host, width=22).pack(side='left', padx=(5, 12))
        ttk.Label(line, text='Port:').pack(side='left')
        ttk.Entry(line, textvariable=self.port, width=8).pack(side='left', padx=(5, 12))
        self.open_button = ttk.Button(line, text='Open', command=self.open)
        self.open_button.pack(side='left', padx=(0, 6))
        self.close_button = ttk.Button(line, text='Close', command=self.disconnect, state='disabled')
        self.close_button.pack(side='left')
        ttk.Label(main, textvariable=self.diagnostic, foreground='#c0392b', wraplength=900).pack(fill='x', anchor='w', pady=(8, 2))
        statusline = ttk.Frame(main)
        statusline.pack(fill='x', pady=(2, 8))
        ttk.Label(statusline, textvariable=self.status).pack(side='left')
        self.mode_display = tk.Label(statusline, textvariable=self.mode_label, bg='#888888', fg='white',
                                     font=('TkDefaultFont', 15, 'bold'), padx=18, pady=8)
        self.mode_display.pack(side='right')
        ttk.Label(main, textvariable=self.values_label, font=('TkDefaultFont', 12, 'bold')).pack(anchor='w', pady=(0, 7))
        chart_box = ttk.LabelFrame(main, text=f'Last {points} points — {", ".join(self.plot_cmds)}', padding=8)
        chart_box.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(chart_box, bg='#18212b', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda _: self.draw())
        footer = ttk.Frame(main)
        footer.pack(fill='x', pady=(7, 0))
        ttk.Label(footer, text=f'Refresh interval: {self.interval:g} s').pack(side='left')
        self.legend_colors = [self.cfg.get('graph', 'color1'), self.cfg.get('graph', 'color2')]
        for i, cmd in enumerate(self.plot_cmds):
            ttk.Label(footer, text=f'● {cmd}', foreground=self.legend_colors[i]).pack(side='right', padx=12)
        root.protocol('WM_DELETE_WINDOW', self.quit)
        root.after(100, self.process_events)

    def open(self):
        if self.worker and self.worker.is_alive():
            return
        host = self.host.get().strip()
        try:
            port = int(self.port.get().strip())
            if not host or '/' in host or ':' in host or not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror('Address', 'Enter a valid address and a port between 1 and 65535.')
            return
        try:
            save_host_port(host, port)
        except OSError as ex:
            self.diagnostic.set(f'Cannot save monitor.ini: {ex}')
        else:
            self.diagnostic.set('')
        self.history.clear()
        self.draw()
        self.mode_label.set('MODE: —')
        self.mode_display.configure(bg='#888888')
        self.values_label.set(' | '.join(f'{c}: —' for c in self.plot_cmds))
        self.status.set('Connecting...')
        self.open_button.configure(state='disabled')
        self.close_button.configure(state='normal')
        self.stop_event = threading.Event()
        self.worker = RpcWorker(f'tcp://{host}:{port}', self.cfg.get('device', 'hello'),
                                self.cfg.get('monitor', 'mode_command'), self.plot_cmds,
                                self.interval, self.timeout, self.events, self.stop_event)
        self.worker.start()

    def disconnect(self):
        if self.stop_event:
            self.stop_event.set()
        self.close_button.configure(state='disabled')
        self.status.set('Closing...')

    def process_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == 'connected':
                    self.connected = True
                    self.status.set(payload)
                    self.diagnostic.set('')
                elif kind == 'mode':
                    self.mode_label.set(f'MODE: {payload}')
                    color = self.cfg.get('mode_colors', str(payload), fallback=self.cfg.get('mode_colors', 'other'))
                    self.mode_display.configure(bg=color)
                elif kind == 'sample':
                    sample_time, values = payload
                    # Missing command responses are gaps; graph does not substitute stale values.
                    self.history.append((sample_time, values))
                    self.values_label.set(' | '.join(f'{c}: {values[c]:g}' if c in values else f'{c}: —' for c in self.plot_cmds))
                    self.draw()
                elif kind == 'error':
                    self.diagnostic.set(payload)
                    self.status.set('Error')
                elif kind == 'poll_error':
                    self.diagnostic.set(f'Read error (will retry): {payload}')
                elif kind == 'disconnected':
                    self.connected = False
                    self.open_button.configure(state='normal')
                    self.close_button.configure(state='disabled')
                    if self.status.get() not in ('Error',):
                        self.status.set(payload)
        except queue.Empty:
            pass
        if not self.closing:
            self.root.after(100, self.process_events)

    def draw(self):
        c = self.canvas
        c.delete('all')
        w, h = c.winfo_width(), c.winfo_height()
        if w < 120 or h < 100:
            return
        left, right, top, bottom = 68, w - 18, 22, h - 38
        c.create_rectangle(left, top, right, bottom, outline='#617080')
        all_vals = [v for _, vals in self.history for v in vals.values()]
        if not all_vals:
            c.create_text(w / 2, h / 2, text='No measurements', fill='#d4dce4')
            return
        lo, hi = min(all_vals), max(all_vals)
        margin = max((hi - lo) * 0.08, abs(hi) * 0.02, 0.1)
        lo -= margin
        hi += margin
        if hi <= lo:
            hi = lo + 1
        for i in range(5):
            val = lo + (hi - lo) * i / 4
            y = bottom - (val - lo) / (hi - lo) * (bottom - top)
            c.create_line(left, y, right, y, fill='#2d3b48')
            c.create_text(left - 7, y, text=f'{val:.3g}', fill='#c6d0da', anchor='e')
        first = self.history[0][0]
        last = self.history[-1][0]
        span = max(last - first, self.interval, 1e-6)
        for i, name in enumerate(self.plot_cmds):
            segment = []
            for timestamp, vals in self.history:
                if name not in vals:
                    if len(segment) >= 4:
                        c.create_line(*segment, fill=self.legend_colors[i], width=2)
                    segment = []
                    continue
                x = left + (timestamp - first) / span * (right - left)
                y = bottom - (vals[name] - lo) / (hi - lo) * (bottom - top)
                segment.extend((x, y))
            if len(segment) >= 4:
                c.create_line(*segment, fill=self.legend_colors[i], width=2)
            elif len(segment) == 2:
                x, y = segment
                c.create_oval(x-3, y-3, x+3, y+3, fill=self.legend_colors[i], outline='')
        c.create_text(left, h - 15, text=f'{span:.0f} s', fill='#c6d0da', anchor='w')
        c.create_text(right, h - 15, text='now', fill='#c6d0da', anchor='e')

    def quit(self):
        self.closing = True
        if self.stop_event:
            self.stop_event.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        Monitor(root)
    except Exception as ex:
        messagebox.showerror('Configuration', str(ex))
        root.destroy()
        return
    root.mainloop()


if __name__ == '__main__':
    main()
