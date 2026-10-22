You are a sandboxed Codex CLI worker on a governed evidence round. Work ONLY inside the current
directory. Do not run git. Do not modify any file that already exists.

Do exactly three things, in order, and print each result on its own line:
1. Print the single line: HGK_EXEC_LANE_OK
2. Run the shell command  echo SHELL_GATE_OK  and print only its output.
3. Read the file STATUS_R15_2.md and print its first 3 lines prefixed with 'LINE:'.
