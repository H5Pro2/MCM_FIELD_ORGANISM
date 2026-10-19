"""Qualification-only binding to the unchanged OC lossless evidence package."""
import hashlib
import json
from pathlib import Path

from tools import _s2oc_private_evidence_package as package
from tools import _s2oc_private_caller_session as old

FILES = ("preregistration.json", "stdout.txt", "stderr.txt", "metrics.json",
         "result.json", "final-balance.json")
QUAL_LIMIT = 6607
RECEIPT_LIMIT = 768
INDEX_STORED_LIMIT = 2048


def measure(path, originals=None):
    measured = package.verify_package(path, originals)
    # Every byte, including ZIP members, the index and central directory, is
    # already assigned by the existing independent package verifier.
    return measured


def violations(measured, receipt_bytes=RECEIPT_LIMIT):
    result = []
    if measured["stored"]["qualification"] + receipt_bytes > QUAL_LIMIT:
        result.append("QUALIFICATION_LIMIT")
    if measured["stored"]["metadata"] > INDEX_STORED_LIMIT:
        result.append("INDEX_METADATA_LIMIT")
    if receipt_bytes > RECEIPT_LIMIT:
        result.append("QUALIFICATION_RECEIPT_LIMIT")
    return result


def read_qualification(directory):
    directory = Path(directory)
    stamp = json.loads((directory/"package.json").read_bytes())
    measured = measure(directory/"qualification.zip")
    package.require(stamp["status"] == "QUALIFIED" and not stamp["violations"]
        and stamp["sha256"] == measured["sha256"]
        and measured["files"] == len(FILES)
        and not violations(measured, (directory/"package.json").stat().st_size),
        "QUALIFICATION_PACKAGE_INVALID")
    q = json.loads(old.packed_file(directory/"qualification.zip", "result.json"))
    package.require(set(q["evidence"]) == set(FILES)-{"result.json"}, "QUALIFICATION_FILES_INVALID")
    for name, digest in q["evidence"].items():
        raw = old.packed_file(directory/"qualification.zip", name)
        package.require(hashlib.sha256(raw).hexdigest() == digest, "QUALIFICATION_CONTENT_CHANGED")
    return q
