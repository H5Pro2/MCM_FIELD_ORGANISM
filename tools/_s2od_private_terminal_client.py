"""Command-driven display around the qualified OC session; never grants a gate."""
import argparse
import hashlib
import json
from pathlib import Path

from tools import _s2oc_bound_session as entry
from tools import _s2oc_shared_verification as verification

s, b = entry.shared, entry.b
VERSION = "s2od.terminal.v1"
QUAL_ID = "s2od-terminal-qualification-20260911-01"
OWN = ("tools/_s2od_private_terminal_client.py", "tests/test_s2od_terminal_client.py",
       "reports/s2od/qualify_terminal_once.py")
DISPLAY_LIMIT = 16384
QUAL_LIMIT = 6607
TEST_COUNT = 16


class ClientError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise ClientError(code)


def sources():
    return {p: [hashlib.sha256((b.ROOT / p).read_bytes()).hexdigest(),
                (b.ROOT / p).stat().st_size] for p in OWN}


def validate_client(common, inv):
    own = sources()
    for p, (h, n) in own.items():
        need(["sources", p, n, h] in common["references"], "CLIENT_SOURCE_UNBOUND")
    root = b.ROOT / "reports/s2od" / QUAL_ID
    q = s.read_json(root / "result.json")
    b.check_root(q, "result_digest")
    need(q["version"] == VERSION and q["run_id"] == QUAL_ID and
         q["status"] == "QUALIFIED" and q["test_calls"] == 1 and
         q["passed_tests"] == q["expected_tests"] == TEST_COUNT and q["exit_code"] == 0 and
         q["client_sources"] == own and q["base_inventory_digest"] == b.digest(inv)
         and q["hashes_unchanged"] is True and q["gates"] is False,
         "CLIENT_NOT_QUALIFIED")
    total = 0
    for name in ("preregistration.json", "stdout.txt", "stderr.txt", "result.json"):
        ref = s.file_reference("metadata", root / name)
        need(ref in common["references"], "CLIENT_QUALIFICATION_UNBOUND")
        total += ref[2]
        if name != "result.json":
            need(q["evidence"].get(name) == ref[3], "CLIENT_EVIDENCE_CHANGED")
    need(total <= QUAL_LIMIT, "CLIENT_QUALIFICATION_LIMIT")


def render_step(raw, ordinal, total):
    need(type(raw) is bytes and len(raw) <= DISPLAY_LIMIT, "CLIENT_RESULT_INVALID")
    value = json.loads(raw)
    need(b.canonical(value) == raw, "CLIENT_RESULT_INVALID")
    shown = dict(progress=f"{ordinal}/{total}", perception=value["perception_status"],
                 memory=value["memory_status"], context=value["context_status"],
                 hypothesis=value["hypothesis"], errors=value["error_codes"])
    text = json.dumps(shown, ensure_ascii=True, separators=(",", ":"))
    need(len(text.encode("utf-8")) <= DISPLAY_LIMIT, "CLIENT_DISPLAY_LIMIT")
    return text


class TerminalClient:
    def __init__(self, common_path, trusted_sha256, inventory_path, output):
        self.common_path = Path(common_path)
        self.common = s.read_json(self.common_path)
        need(s.sha(b.canonical(self.common)) == trusted_sha256, "CLIENT_PIN_INVALID")
        self.inv = s.read_json(inventory_path)
        manifest = s.validate_common(self.common, self.inv, qualified=True)
        validate_client(self.common, self.inv)
        self.events = manifest.events
        self.output = Path(output)
        self.session = None
        self.attempted = self.ended = self.verified = False
        self.completed = 0

    def _verify(self):
        if self.verified:
            return None
        # Claim before calling: a failing verifier must never be retried here.
        self.verified = True
        proof, _ = verification.verify_once(self.output, self.inv, qualified=True)
        return proof

    def command(self, command):
        need(type(command) is str, "CLIENT_COMMAND_INVALID")
        command = command.strip()
        if command == "status":
            return f"{self.completed}/{len(self.events)} " + (
                "CLOSED" if self.ended else "OPEN" if self.session else "NOT_OPEN")
        if command == "open":
            if self.attempted or self.ended:
                entry.MAIN_GATE = False
                raise ClientError("CLIENT_ALREADY_USED")
            need(entry.MAIN_GATE is True, "MAIN_GATE_CLOSED")
            self.attempted = True
            try:
                self.session = entry.open_session(self.common, self.inv, self.output,
                    neutral=False, common_path=self.common_path)
            except Exception as primary:
                self.ended = True
                if (self.output / "record.json").is_file():
                    try:
                        self._verify()
                    except Exception as closure:
                        primary.add_note("Client verification: " + getattr(closure, "code", type(closure).__name__))
                raise
            finally:
                entry.MAIN_GATE = False
            return "OPEN 0/" + str(len(self.events))
        need(self.session is not None and not self.ended, "CLIENT_NOT_OPEN")
        if command == "next":
            need(self.completed < len(self.events), "CLIENT_EXHAUSTED")
            try:
                raw = self.session.process(self.events[self.completed])
            except Exception as primary:
                self.ended = True
                entry.MAIN_GATE = False
                try:
                    self.session.close()
                    self._verify()
                except Exception as closure:
                    # Preserve the original exception, including its bound diagnostic.
                    primary.add_note("Client closure: " + getattr(closure, "code", type(closure).__name__))
                raise
            self.completed += 1
            return render_step(raw, self.completed, len(self.events))
        if command in ("close", "abort", "quit"):
            self.ended = True
            try:
                raw = self.session.close()
                proof = self._verify()
                result = json.loads(raw)
                return json.dumps(dict(status=result["status"],
                    progress=f"{self.completed}/{len(self.events)}",
                    failure=result.get("failure"),
                    evaluation_allowed=proof["evaluation_allowed"]), ensure_ascii=True)
            except Exception as primary:
                if not self.verified and (self.output / "record.json").is_file():
                    try:
                        self._verify()
                    except Exception as closure:
                        primary.add_note("Client verification: " + getattr(closure, "code", type(closure).__name__))
                raise
            finally:
                entry.MAIN_GATE = False
        raise ClientError("CLIENT_COMMAND_INVALID")

    def interact(self, read=input, write=print):
        write("Commands: open, next, status, close, abort, quit")
        try:
            while not self.ended:
                try:
                    command = read("mcm> ")
                except (EOFError, KeyboardInterrupt):
                    command = "abort" if self.session else "quit"
                if command == "quit" and self.session is None:
                    self.ended = True
                    break
                try:
                    write(self.command(command))
                except ClientError as exc:
                    write(exc.code)
        finally:
            entry.MAIN_GATE = False
            if self.session is not None and not self.ended:
                self.command("abort")


def main():
    parser = argparse.ArgumentParser(description="Private OC terminal; requires separate in-process gate authorization")
    for flag in ("common", "sha256", "inventory", "output"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    try:
        TerminalClient(args.common, args.sha256, args.inventory, args.output).interact()
    finally:
        entry.MAIN_GATE = False


if __name__ == "__main__":
    main()
