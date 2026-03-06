"""
Compatibility shim.

Use `love_core` package instead:
`from love_core import router, init_p0_tables`
"""

from love_core import init_p0_tables, router

__all__ = ["router", "init_p0_tables"]
