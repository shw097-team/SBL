"""Line-length check for the proposed error line against the repo's ruff limit (100)."""
p = r"C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py"
lines = open(p, "rb").read().decode("utf-8").replace("\r\n", "\n").split("\n")
one_line = ('                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: '
            '{open_rows} required workorders open (refused at {to_state})")')
split_1 = ('                    f"ERR_PENDING_WORK_CANNOT_DELIVER {project_id}: '
           '{open_rows} required workorders open "')
split_2 = '                    f"(refused at {to_state})")'
over100 = [(i + 1, len(l)) for i, l in enumerate(lines) if len(l) > 100]
print("one_line_len", len(one_line), "exceeds_100", len(one_line) > 100)
print("split_lens", len(split_1), len(split_2))
print("existing_over_100", len(over100), over100[:10])
print("max_existing_len", max(len(l) for l in lines))
