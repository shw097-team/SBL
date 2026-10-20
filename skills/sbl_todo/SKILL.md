---
name: sbl-todo
description: Create and list local todo items through the sbl-todo CLI
---

# sbl-todo

Use this skill when the user wants to track local work items: adding a task,
listing open tasks, or removing a finished one. Tasks live in a local store;
nothing is sent over the network and no repository files are written.

## When to use

- The user says "todo", "task list", or "待辦".
- The request is about capturing or reviewing small local work items.
- The request is not about editing product code or repository contents.

## Planned CLI surface

The executable CLI is built in the next slice (Slice B2). The planned commands
are:

```text
sbl-todo init
sbl-todo add "<title>"
sbl-todo list
sbl-todo remove <id>
sbl-todo uninstall
```

- `init` prepares the local todo store.
- `add` appends one item with a generated id.
- `list` prints the stored items.
- `remove` deletes one item by id.
- `uninstall` removes skill-owned local state.

## Boundaries

- Permitted actions: `todo.read`, `todo.write`.
- Forbidden actions: `repo.write`, `net.call`.
- If the host provider is off, the skill refuses to load or invoke.

Until Slice B2 lands, treat these commands as the documented contract rather
than a working surface.
