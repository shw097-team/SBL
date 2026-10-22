from __future__ import annotations

from dataclasses import dataclass

from .errors import InvariantViolation


@dataclass(frozen=True)
class DelegatedTask:
    task_id: str
    owner: str
    dependencies: tuple[str, ...]
    writable_root: str | None
    checker_only: bool = False


class TaskDAG:
    def __init__(self, tasks: list[DelegatedTask]) -> None:
        self.tasks = {task.task_id: task for task in tasks}
        if len(self.tasks) != len(tasks):
            raise InvariantViolation("ERR_TASK_DAG_DUPLICATE_ID")
        self._validate()

    def _validate(self) -> None:
        for task in self.tasks.values():
            unknown = set(task.dependencies) - self.tasks.keys()
            if unknown:
                raise InvariantViolation(f"ERR_TASK_DAG_UNKNOWN_DEP:{task.task_id}:{sorted(unknown)}")
            if task.checker_only and task.writable_root:
                raise InvariantViolation(f"ERR_CHECKER_WRITE_SCOPE:{task.task_id}")
        writers: dict[str, str] = {}
        for task in self.tasks.values():
            if not task.writable_root:
                continue
            key = task.writable_root.casefold()
            if key in writers:
                raise InvariantViolation(f"ERR_SHARED_WRITABLE_WORKTREE:{writers[key]}:{task.task_id}")
            writers[key] = task.task_id
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise InvariantViolation(f"ERR_TASK_DAG_CYCLE:{task_id}")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in self.tasks[task_id].dependencies:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in self.tasks:
            visit(task_id)

    def ready(self, completed: set[str], cancelled: set[str] | None = None) -> list[str]:
        cancelled = cancelled or set()
        return sorted(
            task.task_id
            for task in self.tasks.values()
            if task.task_id not in completed | cancelled and set(task.dependencies) <= completed
        )

    def join(self, results: dict[str, str]) -> str:
        missing = self.tasks.keys() - results.keys()
        if missing:
            raise InvariantViolation(f"ERR_TASK_DAG_JOIN_MISSING:{sorted(missing)}")
        failed = {task_id: verdict for task_id, verdict in results.items() if verdict != "PASS"}
        return "PASS" if not failed else "NACK:" + ",".join(f"{key}={value}" for key, value in sorted(failed.items()))

