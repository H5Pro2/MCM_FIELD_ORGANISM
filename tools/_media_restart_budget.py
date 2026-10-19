"""Pre-test physical upper envelope. No project imports or media processing."""
VERSION = "media.restart-envelope.v1"
TOTAL_LIMIT = 4194304
FIELD_BOUND = 426580


def record_parts(n):
    if type(n) is not int or not 0 <= n <= 20:
        raise ValueError("MEDIA_BUDGET_POSITION")
    return dict(native=(n+1)*98304+n*32768, nj=n*1024,
                formations=n*1536, generations=n*1536, field=0)


def combine(items):
    return {key: sum(number*row[key] for number, row in items) for key in record_parts(0)}


def preflight():
    """Early/late and every intermediate cut, before adding administrative bytes.

    One reference plus one save/restore comparison. Tests repeating comparisons
    in the same artifact directory would additionally require their retained files.
    Two publication names are counted conservatively while link publication runs.
    """
    rows = []
    full = record_parts(20)
    for cut in range(1, 20):
        checkpoint = dict(record_parts(cut), field=FIELD_BOUND)
        for completed in range(cut, 21):
            prefix = record_parts(completed)
            for ending in ("success_publication", "failure_prefix_publication"):
                parts = combine(((1, full), (1, checkpoint), (2, prefix)))
                total = sum(parts.values())
                rows.append(dict(cut=cut, completed=completed, ending=ending,
                    parts=parts, body_upper=total, limit=TOTAL_LIMIT,
                    excess=max(0, total-TOTAL_LIMIT)))
    return dict(version=VERSION, ready=False, test_calls=0, rows=rows,
        peak=max(rows, key=lambda row: row["body_upper"]),
        excluded_not_zero=["metadata", "sources", "verification", "qualification", "report"],
        scope="Upper reservation for explicit full-prefix copies, not measured sizes or a minimum.",
        reason="BODY_RESERVATION_EXCEEDS_TOTAL_BEFORE_ADMINISTRATION")
