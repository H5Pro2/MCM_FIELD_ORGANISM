"""Neutral evidence and runtime-permission contracts."""

from __future__ import annotations

from enum import Enum


class EvidenceLevel(str, Enum):
    E0 = "e0"
    E1 = "e1"
    E2 = "e2"
    E3 = "e3"
    E4 = "e4"
    E5 = "e5"
    E6 = "e6"


class RuntimePermission(str, Enum):
    PASSIVE_AVAILABLE = "passive_available"
    CONTRACT_ONLY = "contract_only"
    RESEARCH_CLOSED = "research_closed"

