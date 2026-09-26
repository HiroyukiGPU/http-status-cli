from .common import tls_context
import time
import urllib.request
import urllib.error
from urllib.parse import urlsplit


def check(url,timeout=10):
    started=time.perf_counter()
    if urlsplit(url).scheme not in ('http','https') or not urlsplit(url).hostname:
        return dict(url=url,status=None,ms=0,error='有効なHTTP(S) URLが必要です')
    try:
        for method in ['HEAD','GET']:
            try:
                req=urllib.request.Request(url,method=method,headers={'User-Agent':'HiroyukiGPU-CLI/1.0'})
                with urllib.request.urlopen(req,timeout=timeout,context=tls_context()) as r: status=r.status; final=r.url
                break
            except urllib.error.HTTPError as e:
                status=e.code; final=e.url; e.close()
                if status in (405,501) and method=='HEAD': continue
                break
        return dict(url=url,status=status,ms=round((time.perf_counter()-started)*1000,2),final_url=final,error=None)
    except (OSError,ValueError) as e:
        return dict(url=url,status=None,ms=round((time.perf_counter()-started)*1000,2),error=str(e))

from concurrent.futures import ThreadPoolExecutor
from .common import entry,parser,emit,positive
@entry
def main():
    p=parser('HTTPステータスとヘッダー応答時間'); p.add_argument('urls',nargs='+'); p.add_argument('--timeout',type=positive,default=10); p.add_argument('--workers',type=int,default=4); p.add_argument('--json',action='store_true'); a=p.parse_args()
    if not 1<=a.workers<=32: p.error('--workersは1〜32')
    with ThreadPoolExecutor(max_workers=a.workers) as pool: rows=list(pool.map(lambda u:check(u,a.timeout),a.urls))
    if a.json: emit(rows)
    else:
        for r in rows: print(f"{r['status'] or 'ERROR'}  {r['ms']:.1f} ms  {r['url']}  {r['error'] or ''}")
    return 1 if any(r['status'] is None or r['status']>=400 for r in rows) else 0
