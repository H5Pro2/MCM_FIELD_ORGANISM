"""Private, fixed seven-event terminal experiment. No automatic user commands."""
import hashlib
import json
from pathlib import Path

from tools import _s2od_private_terminal_client as client
from tools import _s2od_budget_session as od
from reports.s2ob.run_caller_once import evaluate

s, b = client.s, client.b
RUN_ID = "caller-terminal-basic-20260911-01"
ROOT = b.ROOT / "reports/s2od/terminal-basic-final-binding"
OUTPUT = b.ROOT / "reports/s2od" / RUN_ID
QUAL_ID = "s2od-native-start-qualification-20260911-03"
TEST_COUNT = 12
CAPS = dict(evaluation=8192, dispatch=1536, balance=8192, release=3072)
ATTACHMENTS = (("metadata", "@evaluation", CAPS["evaluation"]),
               ("metadata", "@dispatch", CAPS["dispatch"]),
               ("metadata", "@balance", CAPS["balance"]),
               ("metadata", "@release", CAPS["release"]),
               ("metadata", "@common-reference", 512))
COMMANDS = ("open", "next", "status", "next", "status", "next", "status",
            "next", "status", "next", "status", "next", "status", "next",
            "status", "close")


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def independent_display(step, ordinal, total):
    """Independent field selection; never invokes the client renderer."""
    fields = {
        "progress": str(ordinal) + "/" + str(total),
        "perception": step["perception_status"],
        "memory": step["memory_status"],
        "context": step["context_status"],
        "hypothesis": step["hypothesis"],
        "errors": step["error_codes"],
    }
    return json.dumps(fields, ensure_ascii=True, separators=(",", ":"))


def preflight(common):
    od.validate_policy(common)
    rows = []
    for n in range(len(common["manifest"]["events"]) + 1):
        forms = client.verification.synthetic_forms(common, n)
        measured = {arm: od.ledger(*pair, common, attachments=ATTACHMENTS)
                    for arm, pair in zip(("success", "failure"), forms)}
        od.require_budget(measured, "BINDINGS", n, n)
        rows.append({"completed": n, **{arm: value["totals"] for arm, value in measured.items()}})
    return rows


def drive(terminal, commands, read, write):
    """One foreground command at a time, with no retry after a processing error."""
    position = 0
    opened = False
    display_hashes = []
    try:
        while not terminal.ended:
            try:
                command = read("mcm> ").strip()
            except (EOFError, KeyboardInterrupt):
                command = "abort"
            if command in ("abort", "quit"):
                if terminal.session is not None:
                    write(terminal.command("abort"))
                break
            if position >= len(commands) or command != commands[position]:
                write("COMMAND_ORDER_INVALID")
                continue
            if command == "open":
                client.need(not opened, "START_ALREADY_USED")
                opened = True
                try:
                    od.MAIN_GATE = True
                    shown = terminal.command(command)
                finally:
                    od.MAIN_GATE = False
            else:
                shown = terminal.command(command)
            if command == "next":
                client.need(len(display_hashes) < 7, "DISPLAY_COUNT_LIMIT")
                display_hashes.append(hash_text(shown))
            write(shown)
            position += 1
        return display_hashes
    except BaseException as primary:
        if terminal.session is not None and not terminal.ended:
            try:
                terminal.command("abort")
            except BaseException as closing:
                primary.add_note("Starter close: " + getattr(closing, "code", type(closing).__name__))
        raise
    finally:
        od.MAIN_GATE = False


def load_release():
    """A missing final binding or missing separate authorization fails closed."""
    release = s.read_json(ROOT / "release.json")
    b.check_root(release, "release_digest")
    client.need(release["run_id"] == RUN_ID and release["execution_authorized"] is True,
                "START_NOT_AUTHORIZED")
    client.need(not OUTPUT.exists(), "START_OUTPUT_EXISTS")
    current = s.file_reference("sources", Path(__file__))
    client.need(release["starter"] == current, "START_SOURCE_CHANGED")
    for reference in release["references"]:
        kind, path, size, digest = reference
        client.need(s.file_reference(kind, b.ROOT / path) == reference, "START_REFERENCE_CHANGED")
    qualification = s.read_json(b.ROOT / release["qualification_path"])
    b.check_root(qualification, "result_digest")
    client.need(qualification["result_digest"] == release["qualification_digest"]
                and qualification["status"] == "QUALIFIED"
                and qualification["starter"] == current
                and qualification["run_id"] == QUAL_ID
                and qualification["passed_tests"] == TEST_COUNT
                and qualification["native_complete"] is True
                and qualification["test_calls"] == 1, "START_NOT_QUALIFIED")
    common = s.read_json(ROOT / "common.json")
    client.need(s.sha(b.canonical(common)) == release["common_sha256"], "START_COMMON_CHANGED")
    client.need(common["manifest"]["run_id"] == RUN_ID, "START_RUN_MISMATCH")
    for ref in [current, *release["references"]]:
        client.need(ref in common["references"], "START_REFERENCE_UNBOUND")
    expected = s.read_json(ROOT / "evaluation-binding.json")
    b.check_root(expected, "evaluation_digest")
    client.need(expected["evaluation_digest"] == release["evaluation_digest"]
                and expected["manifest_digest"] == common["manifest"]["manifest_digest"]
                and tuple(expected["commands"]) == COMMANDS, "START_PLAN_CHANGED")
    client.need(len(b.canonical(release)) <= CAPS["release"], "START_RELEASE_LIMIT")
    preflight(common)
    return release, common, expected


def assess(common, expected, display_hashes, directory=OUTPUT):
    """Read the client's sole verification; never call a verifier or scan here."""
    proof = s.read_json(directory / "verification.json")
    b.check_root(proof, "verification_digest")
    record, session = s.unpack(s.read_json(directory / "record.json"),
                               s.read_json(directory / "session.json"), common)
    client.need(proof["common_sha256"] == s.sha(b.canonical(common))
                and proof["session_digest"] == session["session_digest"], "START_PROOF_CHANGED")
    if record["status"] != "RECORDING_COMPLETE" or not proof["evaluation_allowed"]:
        return None
    client.need(proof["core"]["record_digest"] == record["record_digest"], "START_RECORD_CHANGED")
    steps = [row["step"] for row in record["execution"]["rows"]]
    total = len(common["manifest"]["events"])
    client.need(len(steps) == len(display_hashes) == total, "DISPLAY_COUNT_INVALID")
    comparisons = [hash_text(independent_display(step, n, total)) == observed
                   for n, (step, observed) in enumerate(zip(steps, display_hashes), 1)]
    # Expectations are never passed to the runtime or used to authorize a scan.
    result = evaluate(record, proof["core"], expected)
    assessment = dict(functional=result, display_hashes=display_hashes,
                      display_equal=comparisons, verification_calls_by_starter=0)
    client.need(len(b.canonical(assessment)) <= CAPS["evaluation"], "ASSESSMENT_LIMIT")
    return assessment


def finish(common, directory, assessment, failure):
    """Count the full outer closure; the client has already closed and verified."""
    record, session = s.unpack(s.read_json(directory / "record.json"),
                              s.read_json(directory / "session.json"), common)
    dispatch = dict(status=record["status"], failure=failure, gates=False,
                    completed=record["failure"]["completed_events"] if record["execution"] is None
                    else len(record["execution"]["rows"]), verification_calls_by_starter=0)
    client.need(len(b.canonical(dispatch)) <= CAPS["dispatch"], "DISPATCH_LIMIT")
    reserved = od.ledger(record, session, common, attachments=ATTACHMENTS)
    client.need(not reserved["violations"], "START_CLOSURE_LIMIT")
    if assessment is not None:
        s.prior.save(directory / "evaluation.json", assessment)
    s.prior.save(directory / "dispatch.json", dispatch)
    proof_bytes = sum((directory / name).stat().st_size for name in
                      ("verification.json", "verification.claim") if (directory / name).exists())
    sizes = {name: (directory / name).stat().st_size if (directory / name).exists() else 0
             for name in ("evaluation.json", "dispatch.json", "common-reference.json")}
    release = ROOT / "release.json"
    release_bytes = release.stat().st_size if release.exists() else 0
    # Size-dependent balance is bounded by its fixed reserve and converges on bytes only.
    size = 0
    for _ in range(12):
        attachments = tuple(("metadata", name, n) for name, n in sizes.items()) + (
            ("metadata", "release.json", release_bytes), ("metadata", "final-balance.json", size))
        actual = od.ledger(record, session, common, attachments=attachments, proof_bytes=proof_bytes)
        balance = dict(reserved=reserved["totals"], actual=actual["totals"],
                       contributions=actual["contributions"], violations=actual["violations"])
        new_size = len(b.canonical(balance))
        if new_size == size:
            break
        size = new_size
    else:
        raise client.ClientError("BALANCE_SIZE_UNSTABLE")
    client.need(size <= CAPS["balance"] and not actual["violations"], "BALANCE_LIMIT")
    s.prior.save(directory / "final-balance.json", balance)
    return balance


def main():
    common = terminal = None
    assessment = failure = None
    try:
        release, common, expected = load_release()
        terminal = od.TerminalClient(ROOT / "common.json", release["common_sha256"],
            b.ROOT / release["inventory_path"], OUTPUT)
        hashes = drive(terminal, COMMANDS, input, print)
        if terminal.verified:
            assessment = assess(common, expected, hashes)
    except BaseException as exc:
        failure = dict(code=getattr(exc, "code", type(exc).__name__),
                       error_class=type(exc).__name__)
        raise
    finally:
        od.MAIN_GATE = False
        if common is not None and (OUTPUT / "record.json").exists():
            try:
                finish(common, OUTPUT, assessment, failure)
            except Exception:
                if failure is None:
                    raise


if __name__ == "__main__":
    main()
