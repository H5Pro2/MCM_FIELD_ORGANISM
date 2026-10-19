"""Bounded, whole-inventory retry for cooperating append/rename writers.

No policy, source, statistics, or research entry point. Missing paths invalidate
the entire sample; they never contribute zero to an accepted inventory.
"""
import hashlib
import os
from pathlib import Path
import stat
import time
import traceback
from tools._s2uc_ura1_v2_series import LIMITS, raw
from tools._s2uc_ura1_terminal_v3 import Terminal as BaseTerminal, SLOT, TIME_RESERVE

MAX_SCANS = 8
MAX_ENTRIES = 4096


class InventoryError(RuntimeError):
    def __init__(self, operation, path, cause):
        self.operation=operation;self.path=str(path);self.cause=str(cause)
        super().__init__(f'{operation}:{path}:{cause}')


def category(name):
    if name.endswith('.partial'):return 'temp'
    if name in ('terminal.json','result.json','closure.json'):return 'closure'
    if name.endswith('-source.json'):return 'source'
    if name.endswith('.gz'):return 'archive'
    return 'admin'


def inventory(folder, *, hook=None, stat_fn=None, deadline=None):
    """Accept two identical complete scans; at most eight scans total.

    Includes name, identity, size and modification time. Every failed/mismatched
    scan discards its totals. Unknown errors fail closed with their operation.
    hook/stat_fn are neutral deterministic test seams, unused by callers.
    """
    folder=Path(folder).resolve(); previous=None; last='initial'
    for attempt in range(1,MAX_SCANS+1):
        if deadline is not None and time.monotonic()>=deadline:
            raise InventoryError('deadline',folder,'INVENTORY_DEADLINE')
        entries=[]
        try:
            def walk(parent):
                try:
                    with os.scandir(parent) as scan:
                        names=sorted(e.name for e in scan)
                except OSError as exc:
                    raise InventoryError('list',parent,exc) from exc
                if hook is not None:hook(attempt,parent,names)
                for name in names:
                    path=parent/name
                    try:
                        info=stat_fn(path) if stat_fn else path.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        raise
                    except OSError as exc:
                        raise InventoryError('stat',path,exc) from exc
                    if stat.S_ISLNK(info.st_mode):
                        raise InventoryError('type',path,'SYMLINK_NOT_ALLOWED')
                    entries.append((path.relative_to(folder).as_posix(),info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_mode))
                    if len(entries)>MAX_ENTRIES:
                        raise InventoryError('list',folder,'INVENTORY_ENTRY_LIMIT')
                    if stat.S_ISDIR(info.st_mode):walk(path)
                    elif not stat.S_ISREG(info.st_mode):
                        raise InventoryError('type',path,'NONREGULAR_FILE')
            walk(folder)
        except FileNotFoundError as exc:
            previous=None;last='DISAPPEARED:'+str(exc.filename)
            continue
        current=tuple(sorted(entries))
        if current==previous:
            files={name:dict(bytes=size,category=category(Path(name).name)) for name,dev,ino,size,mtime,mode in current if stat.S_ISREG(mode)}
            groups={k:sum(v['bytes'] for v in files.values() if v['category']==k) for k in ('source','archive','admin','closure','temp')}
            return dict(files=files,groups=groups,total=sum(v['bytes'] for v in files.values()),scans=attempt)
        previous=current;last='CHANGED_INVENTORY'
    raise InventoryError('stable_snapshot',folder,'INVENTORY_UNSTABLE:'+last)


def bounded(text, size):
    text=str(text);lo=0;hi=len(text)
    while lo<hi:
        mid=(lo+hi+1)//2
        if len(raw(text[:mid]))<=size:lo=mid
        else:hi=mid-1
    return text[:lo]


class Terminal(BaseTerminal):
    def fail(self, reason):
        super().fail(bounded(reason,512))

    def __init__(self, folder, started, prep=0, limits=None):
        # Allocate exactly the historical slot; admission uses the new inventory.
        self.folder=Path(folder);self.started=started;self.limits=dict(LIMITS if limits is None else limits)
        self.path=self.folder/'terminal.json'
        self.value=dict(status='ADMITTED',first_failure=None,followup_failures=[],completed_cases=[],active_case=None,worker_ended=False,cleanup='UNCONFIRMED',retry_allowed=False)
        snap=inventory(self.folder,deadline=started+self.limits['total_seconds']-TIME_RESERVE)
        if SLOT>self.limits['closure'] or snap['groups']['closure']+SLOT>self.limits['closure']:
            raise ValueError('TERMINAL_RESERVE_CLOSURE')
        if prep+snap['total']+SLOT>self.limits['export']:
            raise ValueError('TERMINAL_RESERVE_EXPORT')
        with self.path.open('xb') as f:
            f.write(b' '*SLOT);f.flush();os.fsync(f.fileno())
        self.save()

    def diagnose(self, exc, phase):
        self.fail(type(exc).__name__+':'+str(exc))
        frames=traceback.extract_tb(exc.__traceback__)
        location='' if not frames else f'{frames[-1].filename}:{frames[-1].lineno}:{frames[-1].name}'
        diagnostic=dict(phase=bounded(phase,96),operation=bounded(getattr(exc,'operation','supervise'),128),
                        path=bounded(getattr(exc,'path',getattr(exc,'filename','') or ''),512),
                        exception=bounded(type(exc).__name__+':'+str(exc),768),
                        location=bounded(location,512),
                        traceback=bounded(''.join(traceback.format_exception(exc)),2304))
        while len(raw(diagnostic))>4096:
            diagnostic['traceback']=diagnostic['traceback'][:len(diagnostic['traceback'])//2]
        if 'first_diagnostic' not in self.value:
            self.value['first_diagnostic']=diagnostic
        else:
            self.value['last_followup_location']={k:diagnostic[k] for k in ('phase','operation','path')}


class Ledger:
    def __init__(self, terminal, prep=0, *, hook=None, stat_fn=None):
        self.terminal=terminal;self.folder=terminal.folder;self.started=terminal.started
        self.limits=terminal.limits;self.prep_bytes=prep;self.final=False
        self.hook=hook;self.stat_fn=stat_fn;self.last=None
        if prep>self.limits['preparation']:raise ValueError('PREPARATION_LIMIT')

    def check(self):
        elapsed=time.monotonic()-self.started
        if elapsed>=self.limits['total_seconds']-TIME_RESERVE:raise InventoryError('clock',self.folder,'GLOBAL_CLOSING_RESERVE')
        if not self.final and elapsed>self.limits['worker_seconds']:raise InventoryError('clock',self.folder,'WORKER_DEADLINE')
        s=inventory(self.folder,hook=self.hook,stat_fn=self.stat_fn,deadline=self.started+self.limits['total_seconds']-TIME_RESERVE)
        for key,used,cap in [('temp',s['groups']['temp'],self.limits['temp']),('export',self.prep_bytes+s['total'],self.limits['export'])]+[(c,s['groups'][c],self.limits[k]) for c,k in [('admin','administration'),('source','source_total'),('archive','archives'),('closure','closure')]]:
            if used>cap:raise InventoryError('budget:'+key,self.folder,f'LIMIT:{used}>{cap}')
        self.last=s;return s

    def register(self,path,group):
        path=Path(path).resolve()
        if not path.is_relative_to(self.folder.resolve()):raise ValueError('LEDGER_PATH')
        s=self.check();key=path.relative_to(self.folder.resolve()).as_posix()
        if key not in s['files'] or s['files'][key]['category']!=group:raise ValueError('LEDGER_CATEGORY')
        cap=self.limits[dict(source='source_case',archive='gzip',admin='administration',closure='closure')[group]]
        if s['files'][key]['bytes']>cap:raise InventoryError('file_limit',path,'FILE_LIMIT:'+group)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write(self,name,value,group='admin'):
        path=self.folder/name
        if path.parent.resolve()!=self.folder.resolve() or category(path.name)!=group:raise ValueError('LEDGER_PATH_OR_CATEGORY')
        if name=='worker.json' and value.get('first_failure'):
            self.terminal.fail(value['first_failure']);self.terminal.save()
        s=self.check();data=raw(value)
        cap=self.limits[dict(source='source_case',archive='gzip',admin='administration',closure='closure')[group]]
        groupcap=self.limits[dict(source='source_total',archive='archives',admin='administration',closure='closure')[group]]
        if len(data)>cap or s['groups'][group]+len(data)>groupcap:raise InventoryError('preflight:'+group,path,'CATEGORY_LIMIT')
        if self.prep_bytes+s['total']+len(data)>self.limits['export']:raise InventoryError('preflight:export',path,'EXPORT_LIMIT')
        if s['groups']['temp']+len(data)>self.limits['temp']:raise InventoryError('preflight:temp',path,'TEMP_LIMIT')
        if path.exists():raise FileExistsError(path)
        partial=path.with_name(path.name+'.partial')
        try:
            with partial.open('xb') as f:f.write(data)
            self.check();partial.rename(path)
            return self.register(path,group)
        finally:
            partial.unlink(missing_ok=True)


def treebytes(folder):
    return inventory(folder)['total']


def supervise(terminal, command, ledger, *, admitted=None, report_writer=None):
    """Bounded diagnostic supervisor; no research admission or policy changes."""
    import subprocess
    child=None;errors=[];phase='admission';worker_ended=False
    try:
        ledger.check()
        child=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if admitted:admitted(child)
        phase='monitor'
        while child.poll() is None:
            if time.monotonic()-terminal.started>=terminal.limits['worker_seconds']:
                raise InventoryError('worker_deadline',terminal.folder,'WORKER_DEADLINE')
            ledger.check();time.sleep(.01)
        phase='worker_exit'
        if child.returncode:raise InventoryError('worker_exit',terminal.folder,str(child.returncode))
        phase='report'
        if report_writer:report_writer(ledger)
        else:raise InventoryError('read_worker_report',terminal.folder/'worker.json','MISSING_REPORT_CALLBACK')
    except Exception as exc:
        errors.append((exc,phase))
    finally:
        try:
            if child is not None and child.poll() is None:
                child.kill();child.wait(timeout=2)
            worker_ended=child is None or child.poll() is not None
        except Exception as exc:errors.append((exc,'worker_end'))
        # Worker no longer writes. Preserve its first cause/diagnostic if present.
        try:terminal.refresh()
        except Exception as exc:errors.append((exc,'terminal_refresh'))
        terminal.value.update(worker_started=child is not None,worker_ended=worker_ended,
                              worker_exitcode=None if child is None else child.returncode)
        for exc,where in errors:terminal.diagnose(exc,where)
        try:
            if worker_ended:
                for path in terminal.folder.glob('*.partial'):path.unlink(missing_ok=True)
            remaining=[p.name for p in terminal.folder.glob('*.partial')]
            terminal.value.update(partial_files=[bounded(n,128) for n in remaining[:16]],file_cleanup_confirmed=worker_ended and not remaining)
        except Exception as exc:
            terminal.diagnose(exc,'file_cleanup');terminal.value['file_cleanup_confirmed']=False
        terminal.value['status']='TECHNICAL_ABORT' if terminal.value['first_failure'] else 'TERMINAL_COMPLETE'
        terminal.save()
    return terminal.value
