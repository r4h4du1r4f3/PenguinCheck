"""RAM statistics collected via psutil.

Structured helpers (:func:`get_ram_stats`, :func:`get_swap_stats`) expose
raw numbers for programmatic use, while :func:`ram_check` returns a
human-readable multi-line summary suitable for console diagnostics
(parent issue: run all hardware checks together and print a summary).
"""

from __future__ import annotations

import psutil

__all__ = ["get_ram_stats", "get_swap_stats", "ram_check"]


def _format_bytes(num_bytes: int | float) -> str:
    """Format a byte count as a human-readable string (1024-based).

    Examples:
        0 -> "0 B", 1536 -> "1.50 KB", 14531268608 -> "13.53 GB".
    """
    num = float(num_bytes)
    if num < 0:
        num = 0.0
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    value = num
    unit = units[0]
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            break
        value /= 1024.0
    if unit == "B":
        return f"{int(value)} B"
    return f"{value:.2f} {unit}"


def get_ram_stats() -> dict[str, int | float]:
    """Return current physical memory stats as a plain dict.

    Wraps :func:`psutil.virtual_memory` and returns its fields
    (``total``, ``available``, ``used``, ``free``, ``percent``, plus any
    platform-specific fields such as ``active``/``inactive``/``buffers``/
    ``cached``/``shared``/``slab`` where available).

    Raises:
        RuntimeError: If the stats cannot be read.
    """
    try:
        return dict(psutil.virtual_memory()._asdict())
    except Exception as exc:
        raise RuntimeError(f"Unable to read RAM stats: {exc}") from exc


def get_swap_stats() -> dict[str, int | float]:
    """Return current swap memory stats as a plain dict.

    Wraps :func:`psutil.swap_memory` and returns its fields
    (``total``, ``used``, ``free``, ``percent``, ``sin``, ``sout``).

    Raises:
        RuntimeError: If the stats cannot be read.
    """
    try:
        return dict(psutil.swap_memory()._asdict())
    except Exception as exc:
        raise RuntimeError(f"Unable to read swap stats: {exc}") from exc


def ram_check() -> str:
    """Return a human-readable summary of RAM and swap usage.

    Never raises: on failure a ``"RAM check failed: ..."`` string is
    returned so combined hardware diagnostics can continue.
    """
    try:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
    except Exception as exc:
        return f"RAM check failed: {exc}"

    lines = [
        "RAM Stats:",
        f"  Total: {_format_bytes(vm.total)}",
        f"  Used: {_format_bytes(vm.used)} ({vm.percent:.1f}%)",
        f"  Available: {_format_bytes(vm.available)}",
        f"  Free: {_format_bytes(vm.free)}",
    ]

    if sm.total == 0:
        lines.append("Swap: not configured")
    else:
        lines += [
            "Swap Stats:",
            f"  Total: {_format_bytes(sm.total)}",
            f"  Used: {_format_bytes(sm.used)} ({sm.percent:.1f}%)",
            f"  Free: {_format_bytes(sm.free)}",
        ]

    return "\n".join(lines)
