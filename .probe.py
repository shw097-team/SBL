import sys, os, time, pathlib
sys.path.insert(0, r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent")
os.environ["HERMES_HOME"] = r"C:\Projects\Agent_Workspace\_r152_ev\.probe_hermes"
import hermes_cli.kanban_db as kb, hermes_cli.kanban_db_connect as kbc
print("host_prefix", kb._host_prefix())
print("claimer_id", kb._claimer_id())
d = pathlib.Path(r"C:\Projects\Agent_Workspace\_r152_ev\.probe_hermes\db3.sqlite"); kbc.init_db(d)
conn = kbc.connect(d)
print("statuses constant", [n for n in dir(kb) if n.isupper()][:20])
tid = kb.create_task(conn, title="p3", workspace_kind="scratch")
kb.claim_task(conn, tid, ttl_seconds=1, claimer=kb._claimer_id())
time.sleep(2.1)
row = conn.execute("SELECT status, claim_lock, claim_expires, worker_pid, last_heartbeat_at, assignee, current_run_id FROM tasks WHERE id=?", (tid,)).fetchone()
print("row", dict(row), "now", int(time.time()))
print("worker_alive(None)?", kb._worker_alive(None, None))
n = kb.release_stale_claims(conn)
print("reclaimed", n, dict(conn.execute("SELECT status, claim_lock, claim_expires FROM tasks WHERE id=?", (tid,)).fetchone()))
conn.close()
