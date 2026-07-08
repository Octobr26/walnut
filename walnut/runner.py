from __future__ import annotations

import copy
import importlib.util
import inspect
import math
import signal
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


@dataclass
class Failure:
    index: int
    kind: str
    note: str | None
    args: Any = None
    expected: Any = None
    got: Any = None
    error: str | None = None


@dataclass
class RunResult:
    passed: int
    total: int
    failures: list[Failure] = field(default_factory=list)
    elapsed_by_case: list[dict[str, Any]] = field(default_factory=list)
    slowest_case_sec: float | None = None

    @property
    def ok(self) -> bool:
        return self.passed == self.total and not self.failures


class CaseTimeout(TimeoutError):
    pass


def _tail_exception(exc: BaseException, frames: int = 3) -> str:
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    if len(tb) <= frames + 1:
        return "".join(tb).strip()
    return "".join(tb[-(frames + 1) :]).strip()


def _call_with_timeout(fn: Callable[[], Any], timeout_sec: float) -> Any:
    if hasattr(signal, "setitimer") and threading.current_thread() is threading.main_thread():
        previous = signal.getsignal(signal.SIGALRM)

        def handler(signum: int, frame: Any) -> None:
            raise CaseTimeout(f"timed out after {timeout_sec:g}s")

        signal.signal(signal.SIGALRM, handler)
        signal.setitimer(signal.ITIMER_REAL, timeout_sec)
        try:
            return fn()
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_sec)
    except FutureTimeout as exc:
        future.cancel()
        raise CaseTimeout(f"timed out after {timeout_sec:g}s") from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _load_module(path: Path, timeout_sec: float) -> ModuleType:
    def importer() -> ModuleType:
        name = f"walnut_user_{path.stem}_{time.time_ns()}"
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"could not import {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        previous_bytecode_setting = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous_bytecode_setting
            sys.modules.pop(name, None)
        return module

    return _call_with_timeout(importer, timeout_sec)


def _load_fixtures(problem_dir: Path) -> ModuleType | None:
    path = problem_dir / "fixtures.py"
    if not path.exists():
        return None
    return _load_module(path, 5)


def _materialize_case(problem_dir: Path, case: dict[str, Any], fixtures: ModuleType | None = None) -> dict[str, Any]:
    if "gen" not in case:
        out = dict(case)
        out.setdefault("kind", "example")
        return out

    fixtures = fixtures or _load_fixtures(problem_dir)
    if fixtures is None:
        raise RuntimeError("generated case requires fixtures.py")
    gen = case["gen"]
    fn = getattr(fixtures, gen["fn"])
    generated = fn(gen.get("seed"))
    out = dict(case)
    out.update(generated)
    out.setdefault("kind", "example")
    return out


def _compare_exact(got: Any, expected: Any) -> bool:
    return got == expected


def _compare_approx(got: Any, expected: Any, tol: float = 1e-6) -> bool:
    if isinstance(got, (int, float)) and isinstance(expected, (int, float)):
        return math.isclose(float(got), float(expected), abs_tol=tol)
    if isinstance(got, list) and isinstance(expected, list) and len(got) == len(expected):
        return all(_compare_approx(a, b, tol) for a, b in zip(got, expected))
    return got == expected


def compare(got: Any, expected: Any, mode: str) -> tuple[bool, str | None]:
    try:
        if mode == "exact":
            return got == expected, None
        if mode == "bool":
            return bool(got) == bool(expected), None
        if mode == "sorted":
            return sorted(got) == sorted(expected), None
        if mode == "groups":
            normalize = lambda value: sorted([sorted(group) for group in value])
            return normalize(got) == normalize(expected), None
        if mode == "approx":
            return _compare_approx(got, expected), None
    except TypeError as exc:
        return False, f"uncomparable output: {exc}"
    return got == expected, None


def _run_case(module: ModuleType, problem_dir: Path, runner: dict[str, Any], case: dict[str, Any]) -> Any:
    entry = runner.get("entry", "method")
    args = copy.deepcopy(case.get("args", {}))
    if entry == "method":
        sol = module.Solution()
        method = getattr(sol, runner["method"])
        return method(**args)
    if entry == "roundtrip":
        sol = module.Solution()
        encoded = getattr(sol, runner["encode"])(**args)
        return getattr(sol, runner["decode"])(encoded)
    if entry == "design":
        cls = getattr(module, runner["class"])
        ops = case["ops"]
        call_args = copy.deepcopy(case["args"])
        obj = cls(*call_args[0])
        outputs = [None]
        for op, op_args in zip(ops[1:], call_args[1:]):
            outputs.append(getattr(obj, op)(*op_args))
        return outputs
    if entry == "checker":
        sol = module.Solution()
        method = getattr(sol, runner["method"])
        output = method(**args)
        checker_path = problem_dir / "checker.py"
        checker = _load_module(checker_path, runner.get("timeout_sec", 10))
        return bool(checker.check(args, output))
    raise ValueError(f"unknown runner entry: {entry}")


def run(problem_dir: Path, problem_json: dict[str, Any], module_filename: str = "solution.py") -> RunResult:
    runner = problem_json["runner"]
    cases = problem_json.get("cases", [])
    module_path = problem_dir / module_filename
    if not module_path.exists():
        return RunResult(
            passed=0,
            total=len(cases),
            failures=[
                Failure(
                    index=0,
                    kind="error",
                    note=None,
                    error=f"{module_filename} not found; run walnut pick first",
                )
            ],
        )

    default_timeout = float(runner.get("timeout_sec", 10))
    try:
        module = _load_module(module_path, default_timeout)
        fixtures = _load_fixtures(problem_dir)
    except BaseException as exc:
        return RunResult(
            passed=0,
            total=len(cases),
            failures=[Failure(index=0, kind="error", note=None, error=_tail_exception(exc))],
        )

    passed = 0
    failures: list[Failure] = []
    elapsed: list[dict[str, Any]] = []

    for index, raw_case in enumerate(cases, start=1):
        try:
            case = _materialize_case(problem_dir, raw_case, fixtures)
        except BaseException as exc:
            failures.append(Failure(index=index, kind=raw_case.get("kind", "example"), note=raw_case.get("note"), error=_tail_exception(exc)))
            continue

        timeout_sec = float(case.get("timeout_sec", default_timeout))
        started = time.perf_counter()
        got: Any = None
        error: str | None = None
        ok = False
        try:
            got = _call_with_timeout(lambda: _run_case(module, problem_dir, runner, case), timeout_sec)
            if runner.get("entry") == "checker":
                ok = bool(got)
                compare_error = None
            else:
                ok, compare_error = compare(got, case.get("expected"), runner.get("compare", "exact"))
                if compare_error:
                    error = compare_error
        except CaseTimeout as exc:
            error = str(exc)
        except BaseException as exc:
            error = _tail_exception(exc)
        took = time.perf_counter() - started
        elapsed.append(
            {
                "index": index,
                "kind": case.get("kind", "example"),
                "note": case.get("note"),
                "elapsed": took,
                "timeout_sec": timeout_sec,
            }
        )
        if ok:
            passed += 1
        else:
            failures.append(
                Failure(
                    index=index,
                    kind=case.get("kind", "example"),
                    note=case.get("note"),
                    args=case.get("args"),
                    expected=case.get("expected"),
                    got=got,
                    error=error,
                )
            )

    slowest = max((item["elapsed"] for item in elapsed), default=None)
    return RunResult(passed=passed, total=len(cases), failures=failures, elapsed_by_case=elapsed, slowest_case_sec=slowest)


def _case_args_for_validation(problem_dir: Path, case: dict[str, Any], fixtures: ModuleType | None) -> dict[str, Any]:
    materialized = _materialize_case(problem_dir, case, fixtures)
    return materialized.get("args", {})


def _validate_args(signature: inspect.Signature, args: dict[str, Any]) -> list[str]:
    params = signature.parameters
    if any(p.kind in (p.VAR_POSITIONAL, p.POSITIONAL_ONLY) for p in params.values()):
        return []
    errors: list[str] = []
    unexpected = set(args) - set(params)
    if unexpected:
        errors.append(f"unexpected args: {', '.join(sorted(unexpected))}")
    for name, param in params.items():
        if param.kind in (param.VAR_KEYWORD, param.VAR_POSITIONAL):
            continue
        if param.default is inspect._empty and name not in args:
            errors.append(f"missing arg: {name}")
    return errors


def validate_problem(problem_dir: Path, problem_json: dict[str, Any], module_filename: str = "reference.py") -> list[str]:
    errors: list[str] = []
    required = ["id", "slug", "title", "difficulty", "seeded", "runner", "cases"]
    for field_name in required:
        if field_name not in problem_json:
            errors.append(f"missing field: {field_name}")
    if errors:
        return errors

    runner = problem_json["runner"]
    cases = problem_json.get("cases", [])
    entry = runner.get("entry", "method")
    if entry in {"method", "roundtrip"}:
        try:
            module = _load_module(problem_dir / module_filename, float(runner.get("timeout_sec", 10)))
            sol = module.Solution()
            method_name = runner["method"] if entry == "method" else runner["encode"]
            signature = inspect.signature(getattr(sol, method_name))
            fixtures = _load_fixtures(problem_dir)
            for index, case in enumerate(cases, start=1):
                args = _case_args_for_validation(problem_dir, case, fixtures)
                for error in _validate_args(signature, args):
                    errors.append(f"case {index}: {error}")
        except BaseException as exc:
            errors.append(_tail_exception(exc))
    elif entry == "design":
        for index, case in enumerate(cases, start=1):
            lengths = [len(case.get("ops", [])), len(case.get("args", [])), len(case.get("expected", []))]
            if len(set(lengths)) != 1:
                errors.append(f"case {index}: ops/args/expected lengths differ")
    elif entry == "checker":
        for index, case in enumerate(cases, start=1):
            if "args" not in case and "gen" not in case:
                errors.append(f"case {index}: checker case requires args")
    else:
        errors.append(f"unknown runner entry: {entry}")
    return errors
