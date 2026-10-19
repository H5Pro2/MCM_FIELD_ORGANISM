"""Fresh synthetic provenance fixtures; never reads historical run records."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2uc_provenance_evaluation as ev
from tools import _s2uc_source_execution_binding as b
from tools import _s2uc_source_context_v9 as context
from tools import _s2uc_execution_v8 as core
from tools import _s2uc_source_execution as execution
from tools import _s2uc_record_codec as codec
from tools import _s2nu_private_source_binding as nu
from tests.test_s2uc_source_execution import fixture as bound_fixture


def seal(packet, record=None):
    value = dict(packet)
    if record is not None:
        value['record'] = codec.dumps(record)
    proof = json.loads(value['verification'])
    proof['record'] = ev._ref('record.json', value['record'])
    value['verification'] = b.old.canonical(proof)
    terminal = json.loads(value['terminal'])
    terminal.update(prestart_binding=ev._ref('execution-binding.json', value['binding']),
                    record=proof['record'], verification=ev._ref('verification.json', value['verification']))
    value['terminal'] = b.old.canonical(terminal)
    return value


def fresh_fixture(mapping):
    manifest = context.neutral_manifest()
    payloads = {f'neutral-v9-{i}': context.neutral_payload(f'neutral-v9-{j}') for i, j in enumerate(mapping)}
    for event in manifest['events']:
        if 'endpoint' in event:
            end = event['endpoint']
            end['pcm_sha256'] = b.discovery.sha(payloads[end['source_id']])
    bare = {k: v for k, v in manifest.items() if k not in ('binding_digest', 'binding_bytes')}
    manifest.update(binding_digest=context.science.digest(bare), binding_bytes=len(context.science.canonical(bare)))
    mbytes = b.old.canonical(manifest)
    binding = {'version': ev.FIXTURE_VERSION, 'contract_id': b.resources.CONTRACT_ID,
               'run_id': 'SYNTHETIC-PROVENANCE-' + ''.join(map(str, mapping)),
               'authorization': {'kind': 'SYNTHETIC_PROVENANCE_TEST', 'real_sources': False},
               'artifacts': {'manifest': ev._ref('manifest.json', mbytes)}}
    bbytes = b.old.canonical(binding)
    source = core._Source(context.endpoints(manifest, 'SYNTHETIC_PROVENANCE_TEST'), lambda e: payloads[e['source_id']])
    owners = core._Owners()
    try:
        record = core.connection.execute(manifest, source, owners=owners.create)
    finally:
        closed = owners.close()
    record.update(source_completion=source.snapshot(record), owner_cleanup=closed,
                  execution={'contract_id': b.resources.CONTRACT_ID, 'run_id': binding['run_id'],
                             'binding_sha256': b.discovery.sha(bbytes)})
    proof = {'version': 's2uc.verification-evaluation.v9', 'scope': 'NEUTRAL_DEVELOPMENT_ONLY',
             'technical': core.verify_materialized(record, manifest, record['source_completion'], closed),
             'evaluation': ev.legacy.evaluate(record)}
    terminal = {'version': 's2uc.neutral-integration.v9', 'scope': 'NEUTRAL_DEVELOPMENT_ONLY',
                'status': 'CLOSED_NEUTRAL_VERIFIED', 'evaluation_allowed': True,
                'primary_error': None, 'secondary_errors': []}
    return seal({'binding': bbytes, 'manifest': mbytes, 'record': codec.dumps(record),
                 'verification': b.old.canonical(proof), 'terminal': b.old.canonical(terminal)})


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.object(nu, 'pcm_window', side_effect=AssertionError('NO_REAL_SOURCE')) as guard:
            cls.distinct = fresh_fixture([0, 1, 2, 3, 4])
            cls.collision = fresh_fixture([0, 1, 1, 0, 2])
            cls.ambiguous = fresh_fixture([0, 1, 2, 1, 4])
            cls.flat = fresh_fixture([0, 0, 0, 0, 0])
            guard.assert_not_called()

    def evaluate(self, packet=None):
        value = ev.evaluate_neutral_fixture(self.distinct if packet is None else packet)
        self.assertEqual(value['status'], 'EVALUATED_NEUTRAL', value.get('reason'))
        return value, {r['key']: r for r in value['hints']}

    def unknown(self, packet):
        result = ev.evaluate_neutral_fixture(packet)
        self.assertEqual(result['status'], 'NOT_EVALUABLE')
        self.assertIsNone(result['gain_count'])
        self.assertIsNone(result['loss_count'])
        self.assertEqual(len(result['not_determinable']), 7)
        for row in result['hints']:
            self.assertIsNone(row['target_recall_gain'])
            self.assertIsNone(row['target_recall_loss'])
            for arm in row['arms'].values():
                self.assertEqual(arm['classification'], 'NICHT_BESTIMMBAR')
                self.assertIsNone(arm['correct_target_recall'])
        return result

    def test_n1_equal_values_do_not_change_stored_origin(self):
        result, rows = self.evaluate(self.collision)
        row = rows['g1/26']
        arm = row['arms']['candidate']
        self.assertEqual(arm['decision'], 'TRACE_MATCH')
        self.assertEqual(arm['classification'], 'ANDERER_ABRUF')
        self.assertEqual(arm['matches'][0]['stored_formation'], 'g1-p1')
        self.assertFalse(arm['correct_target_recall'])
        self.assertFalse(row['mechanism_details'])
        lineage = result['lineages'][arm['matches'][0]['lineage']]
        self.assertTrue(any(c['origin']['formation'] == 'g1-p3' and not c['same_bound_source_sequence']
                            for c in lineage['confirmations']))

    def test_n2_all_matches_kept_gain_is_not_preservation(self):
        _, rows = self.evaluate(self.ambiguous)
        row = rows['g3/60']
        tw = row['arms']['immediate']
        self.assertEqual(tw['classification'], 'MEHRDEUTIG')
        self.assertEqual(len(tw['matches']), 2)
        self.assertTrue(tw['target_in_matches'])
        self.assertTrue(tw['target_retained_present'])
        self.assertTrue(row['target_recall_gain'])
        self.assertFalse(row['preservation_gain'])
        self.assertEqual(row['gain_subtype'], 'UNIQUE_RECALL_WITH_TW_TARGET_RETAINED')
        self.assertEqual({m['stored_formation'] for m in tw['matches']}, {'g3-p1', 'g3-p3'})

    def test_n2_multiple_offsets_same_generation_remain_ambiguous(self):
        _, rows = self.evaluate(self.flat)
        arm = rows['g1/12']['arms']['candidate']
        self.assertEqual(arm['classification'], 'MEHRDEUTIG')
        self.assertEqual(len(arm['matches']), 3)
        self.assertEqual(len({m['generation'] for m in arm['matches']}), 1)
        self.assertEqual({m['offset'] for m in arm['matches']}, {0, 1, 2})
        self.assertFalse(arm['correct_target_recall'])

    def test_n3_missing_origin_despite_success_is_unknown(self):
        record = codec.loads(self.distinct['record'])
        self.assertEqual(record['stories'][0]['hints'][0]['candidate']['decision'], 'TRACE_MATCH')
        del record['stories'][0]['events'][0]['materialization']
        self.unknown(seal(self.distinct, record))

    def test_n4_owner_namespace_rejected_even_with_same_values_and_generation(self):
        record = codec.loads(self.distinct['record'])
        hint = record['stories'][0]['hints'][0]
        for suffix in ('before', 'after'):
            state = hint['candidate_' + suffix]
            gen, frames = state['retained']
            state['retained'] = (gen, tuple(replace(f, owner='s2uc-g2-candidate') for f in frames))
        result = self.unknown(seal(self.distinct, record))
        self.assertIn('PROVENANCE_FRAME_BINDING_INVALID', result['reason'])

    def test_n4_role_generation_namespace_not_interchangeable(self):
        result, rows = self.evaluate()
        row = rows['g3/60']['arms']['candidate']
        retained = result['lineages'][row['retained_lineages'][0]]
        candidate = result['lineages'][row['candidate_lineages'][0]]
        self.assertNotEqual(retained['id'], candidate['id'])
        self.assertEqual(retained['role'], 'retained')
        self.assertEqual(candidate['role'], 'candidate')
        self.assertEqual(retained['stored_origin']['formation'], 'g3-p1')
        self.assertEqual(candidate['stored_origin']['formation'], 'g3-p3')
        record = codec.loads(self.distinct['record'])
        record['stories'][2]['hints'][0]['candidate']['matches'] = ((candidate['generation'], 2),)
        self.unknown(seal(self.distinct, record))

    def test_n5_later_formation_cannot_repair_previous_hint(self):
        result, rows = self.evaluate()
        row = rows['g2/38']
        self.assertTrue(row['target_recall_loss'])
        self.assertFalse(row['arms']['candidate']['target_only_candidate'])
        self.assertEqual(row['mechanism_details'][0]['kind'], 'INTERRUPTION_BEFORE_PROMOTION')
        self.assertFalse(row['mechanism_details'][0]['previously_retained_loss'])
        self.assertFalse(row['loss_of_previously_demonstrated_ua_recall'])
        ids = row['arms']['candidate']['candidate_lineages']
        self.assertEqual([result['lineages'][k]['stored_origin']['frame_ordinals'] for k in ids], [[32, 33, 34, 35]])
        self.assertTrue(any(v['stored_origin']['frame_ordinals'] == [39, 40, 41, 42] for v in result['lineages'].values()))

    def test_n6_competition_loss_and_new_target_not_netted(self):
        result, rows = self.evaluate()
        a, b_row = rows['g3/67'], rows['g3/69']
        self.assertTrue(a['target_recall_loss'])
        self.assertTrue(a['loss_of_previously_demonstrated_ua_recall'])
        self.assertEqual(a['previous_ua_correct_recall'], 'g3/60')
        self.assertEqual(a['mechanism_details'][0]['kind'], 'RETAINED_REPLACED_BY_CONFIRMED_COMPETITION')
        self.assertEqual(b_row['comparison'], 'BOTH_CORRECT')
        self.assertFalse(b_row['target_recall_gain'])
        self.assertEqual(result['candidate_gains'], ['g1/24'])
        self.assertEqual(result['candidate_losses'], ['g1/26', 'g2/38', 'g3/67'])
        self.assertEqual((result['gain_count'], result['loss_count']), (1, 3))
        self.assertNotIn('net_gain', result)
        self.assertEqual(rows['g1/26']['mechanism_details'][0]['kind'], 'SINGLE_EXPERIENCE_REPLACED_BEFORE_CONFIRMATION')

    def test_g1_24_distinct_values_expectation_conflict_independent(self):
        _, rows = self.evaluate()
        row = rows['g1/24']
        self.assertEqual(row['arms']['immediate']['decision'], 'ABSTAIN_NO_RETAINED_TRACE')
        self.assertEqual(row['arms']['immediate']['matches'], [])
        self.assertEqual(row['arms']['immediate']['abstention_context'], 'OTHER_TRACES_PRESENT')
        self.assertEqual(row['legacy_expectation']['expected'][0], 'ABSTAIN_AMBIGUOUS_RETAINED_TRACE')
        self.assertFalse(row['legacy_expectation']['fulfilled'])
        self.assertFalse(row['legacy_expectation']['controls_provenance'])
        self.assertTrue(row['arms']['candidate']['correct_target_recall'])
        self.assertTrue(row['preservation_gain'])
        self.assertTrue(row['preservation_evidence'])

    def test_stored_and_confirming_origins_are_separate(self):
        result, rows = self.evaluate()
        for key, origin, confirmation in (('g1/12', 'g1-p1', 'g1-p2'), ('g3/69', 'g3-p3', 'g3-p4')):
            match = rows[key]['arms']['candidate']['matches'][0]
            lineage = result['lineages'][match['lineage']]
            self.assertEqual(lineage['stored_origin']['formation'], origin)
            self.assertEqual(match['confirmation_origins_before_hint'][0]['origin']['formation'], confirmation)
            self.assertIsNotNone(lineage['promoted_from'])
        self.assertEqual(rows['g3/60']['target']['formations'], ('g3-p1',))

    def test_record_manifest_hashes_and_every_pointer_resolve(self):
        result, _ = self.evaluate()
        record = codec.loads(self.distinct['record'])
        manifest = json.loads(self.distinct['manifest'])
        def resolve(tree, path):
            for part in path.strip('/').split('/'):
                tree = tree[int(part)] if isinstance(tree, (list, tuple)) else tree[part] if isinstance(tree, dict) else getattr(tree, part)
            return tree
        for name, data in self.distinct.items():
            self.assertEqual(result['inputs'][name], ev._ref(ev.FILENAMES[name], data))
        def visit(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.endswith('_path'):
                        self.assertIsNotNone(resolve(manifest if key == 'manifest_path' else record, value))
                    elif isinstance(value, (dict, list, tuple)):
                        visit(value)
            elif isinstance(obj, (list, tuple)):
                for value in obj:
                    visit(value)
        visit(result)

    def test_incomplete_failed_hash_and_real_scope_closures_unknown(self):
        for key in ev.FILENAMES:
            with self.subTest(missing=key):
                packet = dict(self.distinct)
                del packet[key]
                self.unknown(packet)
        for field, value in (('evaluation_allowed', False), ('primary_error', {'error': 'failed'}),
                             ('secondary_errors', ['late']), ('status', 'FAILED')):
            with self.subTest(terminal=field):
                packet = dict(self.distinct)
                terminal = json.loads(packet['terminal'])
                terminal[field] = value
                packet['terminal'] = b.old.canonical(terminal)
                self.unknown(packet)
        packet = dict(self.distinct)
        packet['record'] += b' '
        self.unknown(packet)
        packet = dict(self.distinct)
        binding = json.loads(packet['binding'])
        binding['authorization']['real_sources'] = True
        packet['binding'] = b.old.canonical(binding)
        self.unknown(seal(packet))
        self.unknown(None)

    def test_invalid_receipt_and_incomplete_owner_not_rescued_by_rehash(self):
        for mutation in ('receipt', 'owner', 'partial', 'boolean_generation'):
            with self.subTest(mutation=mutation):
                record = codec.loads(self.distinct['record'])
                if mutation == 'receipt':
                    record['stories'][0]['events'][0]['materialization']['raw_state_digest'] = '0' * 64
                elif mutation == 'owner':
                    record['owner_cleanup'][0]['closed'] = False
                elif mutation == 'partial':
                    record['status'] = 'NOT_EVALUABLE'
                else:
                    record['stories'][0]['hints'][0]['candidate']['matches'] = ((True, 1),)
                self.unknown(seal(self.distinct, record))

    def test_read_closed_fresh_v9_is_read_only_and_rejects_extra_error(self):
        with tempfile.TemporaryDirectory() as root, patch.object(nu, 'pcm_window', side_effect=AssertionError('NO_REAL_SOURCE')) as guard:
            path, rid, output = bound_fixture(Path(root), b.current())
            product = execution.run_neutral(path, lambda e: context.neutral_payload(e['source_id']), run_id=rid, output_directory=output)
            self.assertEqual(product['status'], 'CLOSED_NEUTRAL_VERIFIED')
            before = {p: p.read_bytes() for p in Path(root).rglob('*') if p.is_file()}
            result = ev.read_closed(path, output)
            self.assertEqual(result['status'], 'EVALUATED_NEUTRAL', result.get('reason'))
            self.assertEqual(before, {p: p.read_bytes() for p in Path(root).rglob('*') if p.is_file()})
            self.assertFalse(core.GATE)
            guard.assert_not_called()
            (output / 'error.json').write_bytes(b'{}')
            self.assertEqual(ev.read_closed(path, output)['status'], 'NOT_EVALUABLE')


if __name__ == '__main__':
    unittest.main()
