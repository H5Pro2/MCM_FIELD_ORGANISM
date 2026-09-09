"""Independent direct arithmetic and a separately bounded offline check."""
import struct
from tools import _s2nu_private_comparison as c


def direct_ordered(ordered):
    c.require(type(ordered) is c.OrderedView,"VIEW_TYPE_INVALID")
    ordered.__post_init__()
    transitions = []
    for k in range(4):
        signed,absolute = [],[]
        for i in range(48):
            d = ordered.values[k+1][i]-ordered.values[k][i]
            signed.append(dict(original_index=i,value=d))
            absolute.append(-d if d < 0 else 0.0 if d == 0 else d)
        transitions.append(dict(transition=k,terms=signed,step=sum(absolute)/48))
    return dict(transitions=transitions,T=sum([r["step"] for r in transitions]))


def direct_endpoints(endpoints):
    c.require(type(endpoints) is c.EndpointView,"VIEW_TYPE_INVALID")
    endpoints.__post_init__()
    edge = []
    for i in range(48):
        d = endpoints.last_values[i]-endpoints.first_values[i]
        edge.append(dict(original_index=i,value=-d if d < 0 else 0.0 if d == 0 else d))
    return dict(profile_digest=endpoints.profile_digest,first_values=list(endpoints.first_values),
        last_values=list(endpoints.last_values),terms=edge,E=sum([r["value"] for r in edge])/48)


def direct_unordered(unordered):
    c.require(type(unordered) is c.UnorderedView,"VIEW_TYPE_INVALID")
    unordered.__post_init__()
    return dict(profile_digest=unordered.profile_digest,values_f64le_sorted=[x.hex() for x in unordered.values_f64le_sorted])


def direct_stream(ordered,endpoints,unordered):
    return dict(ordered=direct_ordered(ordered),endpoints=direct_endpoints(endpoints),unordered=direct_unordered(unordered))


def direct_controls(rows):
    a,z = rows[1]["measurement"],rows[2]["measurement"]
    edge,bag = [],[]
    for field in ("first_values","last_values"):
        for i in range(48):
            edge.append(a["endpoints"][field][i].hex() == z["endpoints"][field][i].hex())
    for k in range(5):
        left = a["unordered"]["values_f64le_sorted"][k]
        right = z["unordered"]["values_f64le_sorted"][k]
        for i in range(48):
            bag.append(left[16*i:16*(i+1)] == right[16*i:16*(i+1)])
    return dict(endpoint_bits=edge,multiset_bits=bag,endpoints_equal=all(edge),multiset_equal=all(bag),components_checked=336)


def verify_comparison(record,anchors):
    c.require(len(c.canonical(record)) <= c.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    c.check_root(record,"comparison_digest")
    c.require(record["schema"] == "s2nu.temporal-comparison.v1" and record["status"] == "RECORDING_COMPLETE"
        and record["evaluation"] is None,"RECORD_FORM_INVALID")
    inputs = record["inputs"]
    sources = c.bind_inputs(inputs["plan"],inputs["materialization"],inputs["verification"],anchors)
    work = dict(halvings=0,terms=0,equalities=0,sums=0,order_checks=0)
    for source in sources:
        for raw,half in zip(source.raw,source.half,strict=True):
            c.require(struct.pack("<d",raw*0.5) == struct.pack("<d",half),"HALVING_INVALID")
            work["halvings"] += 1
    c.require(len(record["primary"]) == len(record["direct"]) == 6,"STREAM_COUNT_INVALID")
    for arm in ("primary","direct"):
        for n,row in enumerate(record[arm]):
            c.check_root(row,"stream_digest")
            group = sources[n*5:(n+1)*5]
            c.require(row["stream_id"] == f"s{n+1:02d}" and row["source_ids"] == [s.source_id for s in group]
                and row["materialized_digests"] == [s.materialized_digest for s in group],"STREAM_BINDING_INVALID")
            # Independently project only the inputs allowed to each control.
            values = tuple(s.half for s in group)
            profile = inputs["plan"]["profiles"]["half_profile_digest"]
            ordered = c.OrderedView(profile,values)
            endpoints = c.EndpointView(profile,values[0],values[4])
            packed = [struct.pack("<48d",*v) for v in values]
            packed.sort()
            unordered = c.UnorderedView(profile,tuple(packed))
            expected = direct_stream(ordered,endpoints,unordered)
            c.require(c.canonical(row["measurement"]) == c.canonical(expected),"MEASUREMENT_INVALID")
            work["terms"] += 240
            work["sums"] += 6
        controls = direct_controls(record[arm])
        c.require(c.canonical(record["controls"][arm]) == c.canonical(controls),"CONTROL_EQUALITY_INVALID")
        work["equalities"] += 336
    c.require(c.canonical(record["primary"]) == c.canonical(record["direct"]),"BASELINE_DIFFERS")
    c.require(record["limits"] == c.LIMITS and record["work"] == dict(primary_differences=1440,direct_differences=1440,
        primary_equalities=336,direct_equalities=336),"WORK_BINDING_INVALID")
    c.require(work == dict(halvings=1440,terms=2880,equalities=672,sums=72,order_checks=0),"VERIFICATION_WORK_INVALID")
    result = c.sealed(dict(status="S2NU_COMPARISON_VERIFIED",comparison_digest=record["comparison_digest"],
        baseline_equal=True,read_only=True,evaluation_allowed=True,work=work,
        source_regenerations=0,receptor_calls=0,nj_calls=0),"verification_digest")
    c.require(len(c.canonical(result)) <= c.MAX_VERIFICATION_BYTES,"VERIFICATION_SIZE_EXCEEDED")
    return result
