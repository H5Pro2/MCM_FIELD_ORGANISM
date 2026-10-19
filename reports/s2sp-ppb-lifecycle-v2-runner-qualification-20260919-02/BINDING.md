# S2-SP: PPB-Lebenszyklus V2 – korrigierte Runner-Qualifikation

Qualifikations-ID: `S2SP-PPB-LIFECYCLE-V2-RUNNER-QUAL-20260919-02`.

Die fehlgeschlagene Vorqualifikation `...-01` bleibt unverändert. Dieser
einmalige Aufruf führt ausschließlich die vier nicht erreichten
Runnerprüfungen aus:

```text
python -B -m unittest tests.test_s2sp_ppb_lifecycle_v2_runner -v
```

## Native Bindungszuordnung

| Bindung | Nativer Träger | Geprüfte Felder |
|---|---|---|
| AV-Paar | `S2JVBoundAVPairV1` | Paar-ID, Profil, PCM-/RGB-Digest |
| gemeinsame Feldzeit | `S2LOFieldInputV1` | `start_tick`, `end_tick`, `timed_frames` |
| Audio-/Videozeiten | `OrganismTimedReceptorFrame` | `field_time` |
| visueller Cue | `MaskedMemoryCue336V1` | sichtbare Positionen und Werte |
| PPB-Übergang | `PPB1Readout` | Readoutdigest oder `None` |

Der Adapter verwendet keine Ersatzzeit und keinen Fallback. Die gemeinsame
Feldzeit stammt aus `S2LOFieldInputV1.start_tick/end_tick` und muss mit beiden
gebundenen Frame-Endzeiten übereinstimmen.

| Datei | SHA-256 |
|---|---|
| `tools/_s2sp_oa_materialization_adapter.py` | `47101c39df0ff8efb4cc6935ce1b24ede1f4ad5482f2f2cbd459b43a9e19169b` |
| `tools/_s2sp_ppb_lifecycle_v2_runner.py` | `b923bc8af77a3a31a3d3dcba8e55084abded11a9ac7764bb3e7f4bcd33b36e16` |
| `tests/test_s2sp_ppb_lifecycle_v2_runner.py` | `fe34e273781a43dd02fafed55b90929b3be0039080a8768dc0cb068c87c0ab1a` |

Die vier Kontrollen decken nativen Abschluss mit Verifikation und Auswertung,
unvollständige Hülle, falsche Cue-/Formationsbindung und falschen
`S2LOFieldInputV1` ab. OA-Payloads bleiben ausgeschlossen.
