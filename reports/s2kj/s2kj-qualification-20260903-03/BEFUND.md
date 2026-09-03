# S2-KJ Qualifikationsabschluss

## Status

`PRIVATE_TWO_AREA_PERCEPTUAL_CONTEXT_336_VALID`

Die enge Korrektur trennt Laufzeitdatenform und kanonische
Serialisierungsform in `_make_av_candidate` und `_make_stable_candidate`.
Kandidaten erhalten ausschliesslich die urspruenglichen Tupel; die
Digestpayloads verwenden weiterhin Listen. Datentypen, Validatoren, Rollen
und Digestregeln wurden nicht geaendert.

## Einmalqualifikation

```text
Qualifikations-ID: s2kj-qualification-20260903-03
python -m unittest tests.test_s2kj_two_area_perceptual_context_336 -v
Ausgefuehrte Tests: 12/12
Exit-Code: 0
Terminal: OK
Retry: keiner
```

Qualifiziert wurden:

- stabiler auditiver und visueller B-Kontext;
- ausschliesslich visueller stabiler Kontext bei auditivem
  `NO_FUNCTIONAL_MATCH`;
- getrennte abweichende B4- und Fast-Kandidaten;
- vollstaendige gueltige Abwesenheit als `NO_CONTEXT`;
- einmalige Same-Probe-Wertebindung ohne zweite Memoryprobe;
- unveraenderliche und ressourcenbegrenzte A/B-Projektion;
- Fail-Closed-Verhalten bei Dimensions-, Digest-, Rollen-, Stabilitaets-,
  Zustands-, Probe- und Slotmanipulationen.

## Quellhashes

| Datei | SHA-256 vor und nach dem Lauf |
| --- | --- |
| `tools/_s2kj_validated_perceptual_finding_336.py` | `920762c4a29d2baf579829fdb896526c5a2901ffd3629d52ab1658b0436a0b6c` |
| `tools/_s2kj_two_area_perceptual_context_336.py` | `5e2510eb6dd58ffef27901fc545ad700d1f8a5e4d5b3363d09811fe11c0a1d17` |
| `tests/test_s2kj_two_area_perceptual_context_336.py` | `22f67096bbdf7522b1dd043a78ec6a7eae76326a40d21f1d2976202677620f74` |

## Historie und Grenze

Die Qualifikationen `s2kj-qualification-20260903-01` und
`s2kj-qualification-20260903-02` bleiben unveraendert als fehlgeschlagene
Fixture- beziehungsweise Binderdiagnosen erhalten.

S2-KJ bestaetigt eine private, read-only und modalitaetsgetrennte
`TwoAreaPerceptualContext336`-Darstellung. Es liegt noch kein realer
Kontextnutzungsbefund vor. Ein solcher Versuch benoetigt eine neue
prospektive Geschichte mit Kandidatenwerten; historische S2-KG-Belege werden
weder ergaenzt noch neu interpretiert.
