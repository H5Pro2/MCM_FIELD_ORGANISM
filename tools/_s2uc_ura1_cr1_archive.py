"""CR1 archive semantics and independent C/U replay, using unchanged wire guards."""
import json
from tools._s2uc_ura1_delta_fast_decode import Reader, verify as integrity
from tools._s2uc_ura1_cr1_fused import finish, archive_sequences
from tools._s2uc_ura1_cr1_reference import Reference


def need(ok, message):
    if not ok: raise ValueError(message)


def verify(blob, proof, expected=None):
    result = integrity(blob, proof, expected)
    reader = Reader(blob)
    record = reader.value(reader.doc['root'])
    envelope, paired = finish(record, archive_sequences(reader, record))
    need(envelope == {k: reader.doc[k] for k in ('original_bytes', 'original_sha256')}, 'CR1_ARCHIVE_ENVELOPE')
    for mode in ('C', 'U'):
        ref = Reference(mode)
        forecasts = iter(reader.records(record[mode]['forecasts']['$sequence']))
        rows = iter(reader.records(record[mode]['rows']['$sequence']))
        for index, values in enumerate(record['source'], 1):
            if ref.pending:
                feedback = ref.feedback(index, values)
                row = json.loads(next(rows))
                need(row == json.loads(json.dumps(dict(target=index, error=feedback['error'], updates=feedback['updates']))), 'CR1_ARCHIVE_FEEDBACK')
            forecast = ref.perceive(index, values)
            if forecast:
                actual = json.loads(next(forecasts))
                receipt = actual['receipt']
                need(actual['output'] == list(forecast['output']), 'CR1_ARCHIVE_OUTPUT')
                need(actual['selected'] == (None if forecast['chosen'] is None else list(forecast['chosen'])), 'CR1_ARCHIVE_CHOICE')
                need(receipt['decision'] == forecast['decision'], 'CR1_ARCHIVE_DECISION')
                hs = forecast['hypotheses']
                choice = 0 if forecast['chosen'] is None else next(i+1 for i,h in enumerate(hs) if h['key']==forecast['chosen'])
                need(receipt['choice'] == choice, 'CR1_ARCHIVE_CHOICE_INDEX')
                need(actual['originals'] == [dict(key=list(h['key']),ordinal=h['original']) for h in hs], 'CR1_ARCHIVE_ORIGINALS')
        need(next(rows, None) is None and next(forecasts, None) is None, 'CR1_ARCHIVE_COMPLETE')
        ref.finish()
    return result | dict(cr1_reference_equal=True, cr1_paired_equal=paired['paired_equal'])
