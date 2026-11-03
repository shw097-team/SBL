# 受限 Sandbox 實測原始證據（脫敏）

只保留命令與 host 層錯誤；模型推理內容不轉錄。

## host_probe_err.txt
```
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\Users\\\\\\\\user\\\\\\\\pwsh7\\\\\\\\pwsh.exe\\\" -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\WINDOWS\\\\\\\\system32\\\\\\\\cmd.exe\\\" /c 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\Users\\\\\\\\user\\\\\\\\pwsh7\\\\\\\\pwsh.exe\\\" -NoProfile -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
```

## host_probe2_err.txt
```
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\Users\\\\\\\\user\\\\\\\\pwsh7\\\\\\\\pwsh.exe\\\" -NoProfile -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\WINDOWS\\\\\\\\system32\\\\\\\\cmd.exe\\\" /c 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
```

## host_probe3_err.txt
```
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\Users\\\\\\\\user\\\\\\\\pwsh7\\\\\\\\pwsh.exe\\\" -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\Users\\\\\\\\user\\\\\\\\pwsh7\\\\\\\\pwsh.exe\\\" -NoProfile -Command 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
ERROR codex_core::tools::router: error=exec_command failed: CreateProcess { message: "Rejected(\"`\\\"C:\\\\\\\\WINDOWS\\\\\\\\system32\\\\\\\\cmd.exe\\\" /c 'echo HOST_PROBE_OK'` rejected: blocked by policy\")" }
```

## 沙盒直測（無模型）
```
codex sandbox "C:/Users/user/AppData/Local/Microsoft/WindowsApps/pwsh.exe" -Command "7+7"
-> windows sandbox failed: CreateProcessAsUserW failed: 5 (access denied)

codex sandbox "<PW7_ROOT>/pwsh.exe" -NoProfile -NonInteractive -Command '$PSVersionTable.PSVersion.ToString(); 7+7'
-> 7.6.9
-> 14
```