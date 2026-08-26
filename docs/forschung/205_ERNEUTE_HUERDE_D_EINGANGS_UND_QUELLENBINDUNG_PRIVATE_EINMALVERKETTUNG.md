# Erneute Huerde D: Eingangs- und Quellenbindung der privaten Einmalverkettung

## 1. Status und Zweck

Dieses Dokument bewertet Huerde D auf der Bytebasis aus Dokumenten 202 bis 204 erneut. Die Pruefung ist ausschliesslich statisch. Projektmodule, Tests und Laufpfade werden nicht ausgefuehrt.

## 2. Gebundene Pruefgrundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/198_ERNEUTE_HUERDE_D_EINGANGS_UND_QUELLENBINDUNG_RUNTIME_FIXIERUNG.md` | `46b4793e0baf73dda025f5475c5ed06335b4d8b12838fb7a4220dccdeaf64878` |
| `docs/forschung/202_ERNEUTE_HUERDE_A_UMFANGSBINDUNG_PRIVATE_EINMALVERKETTUNG_RUNTIME_FIXIERUNG.md` | `8365dbf825962d10acd11a9422b507e412bda19f71a0613ad1d7bf7e84674bfd` |
| `docs/forschung/203_ERNEUTE_HUERDE_B_EINMALLAUFVERTRAG_PRIVATE_VERKETTUNG_RUNTIME_FIXIERUNG.md` | `53456fb230bc3a4eb7d45a9464abaefc8c7eec7d20fcfbec030a88930ecd4a52` |
| `docs/forschung/204_ERNEUTE_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | `ec0cead77a18d2b3ca0ba1caca43c0baf96d5af269ea8512fe72ff4823018671` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/_runtime_fixation_single_use_path.py` | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |

Jede Digest- oder Umfangsabweichung sperrt Huerde D erneut.

## 3. Reproduzierte Integritaetsquellen

Die in `_runtime_fixation_structure.py` statisch deklarierte `_SOURCE_DIGESTS`-Menge enthaelt weiterhin exakt acht Eintraege:

| Integritaetsquelle | SHA-256 |
|---|---|
| `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `mcm_field_organism/receptor_distributor.py` | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` |
| `mcm_field_organism/shared_mcm_field.py` | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` |
| `mcm_field_organism/field_step_time.py` | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` |
| `mcm_field_organism/neutral_local_field_substrate.py` | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` |
| `mcm_field_organism/mcm_neuron_layer.py` | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` |
| `mcm_field_organism/_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `mcm_field_organism/previous_state_contribution_hook.py` | `2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e` |

Alle acht Digests stimmen mit den aktuellen Dateien ueberein und alle acht Quellen sind in Dokument 202 bytegebunden. Die Hook-Datei wird ausschliesslich als Integritaetsquelle gelesen; Hook-Ausfuehrung bleibt gesperrt.

## 4. Eingangsgrenze der neuen Verkettung

`_run_private_runtime_fixation_once()` nimmt keine Parameter an und enthaelt nur drei private Importe, einen Bindungsaufbau und einen Handoff-Aufruf. Die Datei oeffnet keine zusaetzliche Eingangsquelle und enthaelt insbesondere keinen:

- Datei- oder Verzeichniszugriff;
- Hook-, Public-AV- oder Sensoreingang;
- Netzwerk-, Socket- oder IPC-Zugriff;
- Kamera-, Mikrofon- oder sonstigen Geraetezugriff;
- Umgebungs-, CLI-, Standard- oder Konfigurationseingang;
- dynamischen Import oder dynamische Symbolaufloesung.

Externe fachliche Eingabedateien bleiben auf exakt null begrenzt. Die bereits fixierten internen Kontakt-Payloads und deren Digestgrenzen bleiben unveraendert; die neue Verkettung erzeugt oder ersetzt keine Payload.

## 5. Ausschluss- und Abbruchgrenze

Nicht gebundene Quellen, veraenderte Digests, zusaetzliche Eingaben oder nicht eindeutig zuordenbare Bytes muessen einen spaeteren Lauf vor fachlicher Ergebnisuebernahme abbrechen. Retry, Weiterlauf, Teilresultat und Teilfreigabe bleiben verboten.

Die neue Funktion darf weder Quellenpruefung umgehen noch eine alternative Bindung, einen alternativen Handoff oder einen zweiten Aufruf herstellen.

## 6. Freigabeblock

```yaml
byte_scope_release: false
single_execution_release: false
resource_boundary_release: false
input_source_release: false
output_side_effect_release: false
failure_abort_release: false
observation_evidence_release: false
independent_final_review_release: false
real_binding_release: false
handoff_release: false
runtime_fixation_release: false
minimal_test_release: false
minimal_test_release_recommended: false
```

## 7. Statische Entscheidung

Huerde D ist auf der Bytebasis 202 bis 204 dokumentarisch konsistent vorbereitet. Eine unabhaengige statische Review ist erforderlich, bevor Huerde E erneut bewertet werden darf.

Huerden E bis G und jede reale Ausfuehrung bleiben gesperrt.

## 8. Aussagegrenze und Zielbezug

Kein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI. Keine Erinnerung, Bedeutung, Zielwirkung oder Topologie wird vorprogrammiert.

Keine Zielabweichung ist erkennbar. Bewertet werden ausschliesslich technische Eingangs- und Quellenbindungen.
