"""15 node của graph photo-sort — mỗi node ở 1 file, làm 1 việc. Xem sơ đồ ở
:mod:`pipeline.graph`.
"""
from steps.agent_repair import agent_repair
from steps.apply import apply
from steps.canonicalize import canonicalize
from steps.check import check
from steps.classify import classify
from steps.conservation import conservation
from steps.delete_empty import delete_empty
from steps.dot_range import dot_range
from steps.even_four import even_four
from steps.normalize import normalize
from steps.plan import plan
from steps.scaffold import scaffold
from steps.scan import scan
from steps.validate import validate
from steps.vision import vision

__all__ = [
    "scan", "normalize", "check", "classify", "vision", "dot_range", "canonicalize", "scaffold", "even_four",
    "validate", "agent_repair", "plan", "conservation", "apply", "delete_empty",
]
