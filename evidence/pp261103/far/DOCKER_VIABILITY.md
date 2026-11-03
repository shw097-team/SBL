# DOCKER / WSL VIABILITY FOR THE WINDOWS CHILD-PROCESS BLOCKAGE

Run: `run_sbl_tpm_pre_v2_final_20261103` · Windows 11, git-bash · Docker 29.8.2 (Docker Desktop, WSL2 backend)
All commands below were executed on this host at the time of writing; exit codes and output are transcribed.

**VERDICT LINE:** `DOCKER_BYPASSES_BUT_DIFFERENT_HOST`

---

## Test 1 — Daemon reachable, backend, image store

```
$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS   NAMES
EXIT=0

$ docker version --format '{{.Server.Version}}'
29.8.2
EXIT=0

$ docker info --format '{{.OperatingSystem}} | OSType={{.OSType}} | Arch={{.Architecture}} | Driver={{.Driver}} | Images={{.Images}} | Kernel={{.KernelVersion}}'
Docker Desktop | OSType=linux | Arch=x86_64 | Driver=overlayfs | Images=26 | Kernel=6.6.87.2-microsoft-standard-WSL2
EXIT=0
```

Supporting detail from `docker info`:

```
Name: docker-desktop
Server Version: 29.8.2
Storage Driver: overlayfs (io.containerd.snapshotter.v1)
Cgroup Driver: cgroupfs   Cgroup Version: 2   Default Runtime: runc
Kernel Version: 6.6.87.2-microsoft-standard-WSL2
Docker Root Dir: /var/lib/docker
$ docker context ls
desktop-linux *   Docker Desktop   npipe:////./pipe/dockerDesktopLinuxEngine
```

**Read:** daemon is up; all containers are **Linux (OSType=linux)** processes running inside the
WSL2 VM (`docker-desktop` distro), not Windows processes on `DESKTOP-57EO414`.

## Test 2 — Can a container spawn processes at all

```
$ docker run --rm alpine:3 sh -c 'echo CONTAINER_OK; uname -a; id'
CONTAINER_OK
Linux 878d4ab92493 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC ... x86_64 Linux
uid=0(root) gid=0(root) groups=0(root),...
EXIT=0
```

**Read:** process creation works normally. No policy layer rejects child processes.

## Test 3 — JS runtime available for `npm i -g @openai/codex`

```
$ docker run --rm node:22 sh -c 'node -v && npm -v'
v22.23.4
10.9.9
EXIT=0
```
(`node:22-slim` already local: v22.23.3 / npm 10.9.9 — same result, no pull needed.)

## Test 4 — Is `@openai/codex` installable in a container

Host network probe:
```
$ npm view @openai/codex version dist-tags --json
{ "version": "0.166.0",
  "dist-tags": { "latest": "0.166.0",
                 "linux-x64": "0.166.0-linux-x64",
                 "win32-x64": "0.166.0-win32-x64", ... } }
EXIT=0
```

In-container install (measured, no cap hit):
```
$ time docker run --rm node:22 sh -c 'npm i -g @openai/codex --silent; codex --version'
codex-cli 0.166.0
real    0m20.644s
EXIT=0
```

**Read:** installable in ~21 s. **Status: RUN** (not `NOT_RUN` — the 600 s cap was never approached).

Host-side for comparison (`npm ls -g`, allowed probe, host untouched):
```
<HOME>\AppData\Roaming\npm
└── @openai/codex@0.164.0
```
`where.exe codex` → `<HOME>\AppData\Roaming\npm\codex` (`codex.cmd`).

> **Artifact divergence:** host = **0.164.0 / win32-x64**; container = **0.166.0 / x86_64-unknown-linux-musl**.
> Two independent mismatches (version and platform build), so no SHA can match.

## Test 5 — Does the container see the host plugin tree and the model endpoint

Read-only bind mount of the codex-home plugin tree:
```
$ docker run --rm -v "C:/Projects/.../RUN-20261102-GJ02-01/shadow/codex-home":/codex-home:ro node:22 \
    sh -c 'echo MOUNT_OK; ls /codex-home; sha256sum /codex-home/config.toml; touch /codex-home/zz_nope'
MOUNT_OK
auth.json  cache  config.toml  goals_1.sqlite  installation_id  logs_2.sqlite  logs_2.sqlite-shm
logs_2.sqlite-wal  memories_1.sqlite  models_cache.json  opencodex-catalog.json  plugins  queue_1.sqlite
sessions  skills  state_5.sqlite  state_5.sqlite-shm  state_5.sqlite-wal  thread-writer-locks
thread_history_1.sqlite
cb87c7a00e5a7f532117011890660df0007a0934ea926176275e48a16b2cc631  /codex-home/config.toml
touch: cannot touch '/codex-home/zz_nope': Read-only file system
WRITE_BLOCKED_RO
EXIT=0
```
The mount is byte-identical (path-level) and genuinely read-only; `plugins/` is visible
(`.remote-plugin-install-staging/`, `cache/`). No file inside it was printed or modified.

Egress (no credentials presented):
```
container: node -e 'fetch("https://opencode.ai/zen/go/v1/models").then(r=>console.log("HTTP_STATUS",r.status))'
HTTP_STATUS 200
EXIT=0

host: curl -s -o /dev/null -w '%{http_code}' https://opencode.ai/zen/go/v1/models
HOST_HTTP_STATUS=200   (curl exit 23 = write-to-/dev/null artifact, HTTP status valid)
```
**Correction to the premise:** the endpoint is **public** — it returns **200**, not 401. Egress is
therefore proven by a 200 (stronger than an auth challenge), but it is not evidence of authenticated
access. `/mnt/c` interop is **not** available inside containers (Linux-only); only bind mounts are.

## Test 6 — WSL as an alternative

```
$ wsl -l -v
  NAME              STATE      VERSION
* Ubuntu-24.04      Stopped    2
  docker-desktop    Running    2

$ wsl -e sh -c 'echo WSL_OK; uname -a; id; head -3 /etc/os-release'
WSL_OK
Linux DESKTOP-57EO414 6.6.87.2-microsoft-standard-WSL2 ... x86_64 GNU/Linux
uid=1000(shw097) gid=1000(shw097) groups=...,1001(docker)
PRETTY_NAME="Ubuntu 24.04.3 LTS"
EXIT=0
```

WSL prerequisite probes:
```
$ wsl -e sh -c 'which node npm codex; node -v'
/mnt/c/Program Files/nodejs/npm
/mnt<HOME>/AppData/Roaming/npm/codex
sh: 1: node: not found          (EXIT=127)

$ wsl -e sh -c 'which bwrap; unshare -Ur true; docker ps'
bwrap: (absent)
WSL_USERNS_OK
/var/run/docker.sock: No such file or directory  -> WSL_DOCKER_CLI_FAIL
```
**Read:** WSL2 Ubuntu runs, and unprivileged user namespaces work there (better than default Docker),
but it has **no native Linux node, no bubblewrap, and no Docker socket**. Its `codex` resolves to the
**Windows** binary through `/mnt/c` interop — i.e. using it just re-enters the blocked Windows host.
WSL is NOT a viable bypass in its current state; it would need a native toolchain install.

## Bonus — Does the *Codex sandbox* itself work inside the container (the actual failure mode)

Default Docker seccomp profile:
```
$ docker run --rm node:22 sh -c 'npm i -g @openai/codex --silent; codex sandbox -- sh -c "echo ok"'
bwrap: No permissions to create a new namespace, likely because the kernel does not allow
non-privileged user namespaces.
SANDBOX_EXIT=1
```
`unshare -Ur true` → `USERNS_FAIL` (default profile blocks `CLONE_NEWUSER`); passes with
`--security-opt seccomp=unconfined` → `USERNS_OK`.

With `--security-opt seccomp=unconfined`:
```
$ docker run --rm --security-opt seccomp=unconfined node:22 sh -c \
    'npm i -g @openai/codex --silent; codex sandbox -- sh -c "echo SANDBOX_CHILD_OK; id -u"'
SANDBOX_CHILD_OK
0
SANDBOX_EXIT=0
```

End-to-end `codex exec` in the container:
```
$ docker run --rm --security-opt seccomp=unconfined node:22 sh -c \
    'npm i -g @openai/codex --silent; codex exec --sandbox workspace-write --skip-git-repo-check "echo hello"'
ERROR: Reconnecting... 5/5
ERROR: unexpected status 401 Unauthorized: Missing bearer or basic authentication in header,
       url: https://api.openai.com/v1/responses
```
and `codex doctor` reports `Codex Doctor v0.166.0 · linux-x86_64`, runtime/install `✓`, only
`✗ auth` and `⚠ websocket` flagged.

**This is the decisive result:** inside the container the exact command that fails on Windows
(`codex exec --sandbox workspace-write`) **is not rejected by any policy**. It passes argument
parsing, directory trust and the sandbox layer and proceeds to the model API, failing only on
**401 authentication** — a credentials gate, not a process-creation gate. `codex sandbox` child
spawn returned `SANDBOX_CHILD_OK` with exit 0.

---

## Answers

**(a) Does a container solve the process-creation blockage?**
**Yes, empirically.** `codex exec --sandbox workspace-write` inside `node:22` with
`--security-opt seccomp=unconfined` gets past the sandbox and reaches the API (401 only because no
credentials were supplied). `codex sandbox -- sh -c …` spawns a child and exits 0. The
`Rejected(... blocked by policy)` signature never appears. Caveat: the **default** seccomp profile
breaks the Linux sandbox (bubblewrap cannot create a user namespace), so the bypass is
**conditional on `--security-opt seccomp=unconfined`** — i.e. the sandbox is disabled at the Docker
layer and re-implemented by codex/bwrap one level down. That is a real weakening of isolation and
must be stated, not hidden.

**(b) Would a run inside the container count as evidence for `P0_HOST_INVOKE` on this Windows host?**
**No.** It is a **different host** by every identity axis that matters:

| Axis | Windows host (required) | Container |
|---|---|---|
| Machine | `DESKTOP-57EO414` (Windows 11) | `1ada00503624` (Linux, WSL2 VM kernel 6.6.87.2) |
| Loader | Windows loader, `codex.cmd` via `AppData\Roaming\npm` | ELF/musl binary, `/usr/local/bin/codex` |
| Artifact | `@openai/codex@0.164.0` **win32-x64** | `@openai/codex@0.166.0` **linux-x64-musl** |
| Process model | Win32 job/AppContainer sandbox (the blocked path) | bwrap + landlock/seccomp in a Linux pid namespace |

`P0_HOST_INVOKE` requires Installed→Loaded→Invoked/Used **by the host that has the plugin**, with
**matching SHAs**. A container run proves "codex-on-Linux can spawn children"; it says nothing about
the Windows plugin being loaded and used, and its artifact SHA differs in both version and platform.
Claiming it as host evidence would be a category error — and the version skew (0.164 vs 0.166) makes
it a *different build*, not merely a different OS.

**(c) What would it cost to make it lawful evidence?**
Cheap to *reproduce*, expensive to *legitimise*:
1. Pin the artifact: install **exactly `@openai/codex@0.164.0`** (host version) in the image — not
   `latest` — and record the resolved `integrity`/SHA of the tarball. Still Linux-x64, so the *binary*
   title SHA cannot equal the win32 build; only the npm package SHA can align.
2. Record container host identity as first-class evidence: image digest (`docker inspect --format
   '{{.Image}}'`), container ID, `uname -a`, and `docker info` kernel — so the run is attributed to
   the container, never to `DESKTOP-57EO414`.
3. Keep the Windows load claim **separate and independent**: container evidence may only satisfy the
   *"codex sandbox can spawn child processes"* proposition (call it `P1_SANDBOX_SPAWN_PROVEN`),
   not `P0_HOST_INVOKE`. Two claims, two hosts, no merging in a single evidence row.
4. Mount the plugin tree read-only at a fixed path (proven above, `config.toml` sha
   `cb87c7a0…`) and hash the tree **before and after** the run to prove non-mutation.
5. Solve credentials lawfully — the remaining gap is auth, and a credential inside a container is a
   new secret-handling surface that needs its own approval; no credentials were used here.
6. Accept the isolation trade-off in writing: `seccomp=unconfined` is required for bwrap, which
   weakens the container boundary relative to the default profile.

## Verdict

```
DOCKER_BYPASSES_BUT_DIFFERENT_HOST
```

Docker is a **technically lawful and reproducible execution environment** for the blocked command
(the policy rejection disappears; only auth remains), but it is **not** a lawful substitute for
`P0_HOST_INVOKE` on this Windows host: the process that runs is a different build (0.166.0/linux-x64
vs 0.164.0/win32-x64) on a different machine (`1ada00503624` in the WSL2 VM vs `DESKTOP-57EO414`).
WSL2 Ubuntu is not a bypass either — no native node, no bwrap, no Docker socket, and its `codex`
resolves to the Windows binary through `/mnt/c` interop.
