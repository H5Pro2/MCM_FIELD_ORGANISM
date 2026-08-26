# 197 - Korrigierte Huerde A: Vollstaendige Byte- und Umfangsbindung der Runtime-Fixierung

## 1. Zweck und Status

Dieses Dokument ersetzt die Umfangsbestimmung aus Dokument 193. Es bindet neben der relativen AST-Importclosure auch die in `_SOURCE_DIGESTS` als Strings benannten Read-only-Integritaetsquellen.

Es ist keine Implementierungs-, Test- oder Ausfuehrungsfreigabe. Kein Projektmodul wurde importiert oder ausgefuehrt, keine reale Bindung erzeugt, keine Handoff-Funktion aufgerufen, keine Fixierung ausgefuehrt und keine Runtime aktiviert.

## 2. Ermittlung des korrigierten Umfangs

Der Umfang wird aus zwei statisch ermittelten Produktionsmengen gebildet:

- relative AST-Importclosure ab den vier privaten Fixierungsmodulen: 23 Dateien;
- stringgebundene Quellenliste `_SOURCE_DIGESTS`: 8 Dateien.

Sieben der acht Stringquellen liegen bereits in der AST-Closure. Die Vereinigung umfasst daher genau 24 Produktionsdateien. Neu gegenueber Dokument 193 ist `mcm_field_organism/previous_state_contribution_hook.py` enthalten.

Der vollstaendige gebundene Umfang besteht aus genau 42 Dateien:

- 13 Vertragsdokumente 184 bis 196;
- 24 Produktionsdateien der vereinigten Abhaengigkeitsclosure;
- `mcm_field_organism/__init__.py` als Exportgrenze;
- 4 private Fixierungstests.

Dokument 197 kann seinen eigenen finalen Digest nicht selbst enthalten. Dieser muss in der nachfolgenden unabhaengigen Review erhoben werden.

## 3. Bytebindung der Vertragslinie

| Datei | SHA-256 |
|---|---|
| `docs/forschung/184_IMPLEMENTIERUNGSVORABNAHME_PRIVATE_ADAPTERGRENZE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `984ea0f8323ca57e70502b62d99543f68103d7f6e2a58f0362ec5d46981be83f` |
| `docs/forschung/185_TECHNISCHE_ABSCHLUSSABNAHME_PRIVATE_ADAPTERGRENZE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `2e33efa8db66cdd7d0eadf7e10304999237fb642f9f5be2fb57b5ba7ffbe06fb` |
| `docs/forschung/186_STATISCHE_VORABNAHME_PRIVATE_BINDUNGSBRUECKE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `1dcfa46e5be53071e5fdc864dcf3be1018e194281e422c47f2e1637828858fb5` |
| `docs/forschung/187_IMPLEMENTIERUNGSVORABNAHME_PRIVATE_BINDUNGSBRUECKE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `14538c261919816cb2146b62fde47b8741ece5aeec8bd15348e69637a60535f9` |
| `docs/forschung/188_TECHNISCHE_ABSCHLUSSABNAHME_PRIVATE_BINDUNGSBRUECKE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `90b371dbd551df8363c39a31650be5e18807a6461dc41b3db87d06b42e23cda6` |
| `docs/forschung/189_STATISCHE_VORABNAHME_PRIVATE_ABLAUFKOORDINATOR_UEBERGABE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `2ab72a64f3911224241c4ed48e9daf42cc4194c1f47f3685de3a467df1f2cfbd` |
| `docs/forschung/190_IMPLEMENTIERUNGSVORABNAHME_PRIVATE_ABLAUFKOORDINATOR_UEBERGABE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `14b60309c38dd40a5200ba1a8d717b7a712a51371cb47a7a8936d1a7649ca2c9` |
| `docs/forschung/191_TECHNISCHE_ABSCHLUSSABNAHME_PRIVATE_ABLAUFKOORDINATOR_UEBERGABE_RUNTIME_FIXIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `29da4baecc5088f5b38da64e9bea1642189fe2054fd5c89aea8bed3fda227608` |
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/193_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_EINMALLAUF_PFAD_RUNTIME_FIXIERUNG.md` | `d002bc7832a0ef6cd36c2cc5ef481e0bb403cfede503c6ed6b22cd955c70974f` |
| `docs/forschung/194_HUERDE_B_EINMALIGER_AUSFUEHRUNGSVERTRAG_RUNTIME_FIXIERUNG.md` | `f4e2139aee4cc9f7cf95deb4cefc20881efe57aef1e17f8a9cad70b741e7274e` |
| `docs/forschung/195_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_EINMALLAUF_RUNTIME_FIXIERUNG.md` | `0154a6de7e80b5db8f373878af592855dfa6a0938bd7dedf5ebea927e5ae4ca3` |
| `docs/forschung/196_HUERDE_D_EINGANGS_UND_QUELLENBINDUNG_SPERRBEFUND_RUNTIME_FIXIERUNG.md` | `cd5ed958821bc6b67334ab133aee88a207c14f388590331968f1deae593b72f6` |

## 4. Bytebindung der vereinigten Produktionsclosure

| Datei | SHA-256 |
|---|---|
| `mcm_field_organism/_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `mcm_field_organism/_runtime_fixation_adapters.py` | `422f511c54da7cecce541313ab23bcb37d5d8edab6a97a5cfe04768f111048fc` |
| `mcm_field_organism/_runtime_fixation_binding.py` | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `mcm_field_organism/_runtime_fixation_handoff.py` | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/asynchronous_receptor_events.py` | `d2c9fc155c364af20d5f119c267dfb60857a668c65969254ad674389a7e0f4e2` |
| `mcm_field_organism/auditory_baselines.py` | `1bd6a5f22181ef0af345509cfbf25195dd97c66e4137f11fefc7f629a9c35731` |
| `mcm_field_organism/broadband_hearing_path.py` | `4dea43d16110444dc2408137361740c5b4a0cca24ac627b715f409ceff0c6535` |
| `mcm_field_organism/carrier_baselines.py` | `dc891f4f263b17acf7b7b50c7c135d9a3d028cb1b9bdb72c342d72d24f1337ab` |
| `mcm_field_organism/field_step_time.py` | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` |
| `mcm_field_organism/finite_video_path.py` | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| `mcm_field_organism/live_audio_adapter.py` | `c37ab44ded2678a3d0a664044390bdced5de7a4c10174935e1b0025bb286a676` |
| `mcm_field_organism/log_spectral_receptor.py` | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `mcm_field_organism/mcm_neuron.py` | `79cf8f8aa79d8c336c5d3fd57303a9f618e2840217c7786688112d0b7c66783a` |
| `mcm_field_organism/mcm_neuron_layer.py` | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` |
| `mcm_field_organism/neutral_local_field_substrate.py` | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` |
| `mcm_field_organism/previous_state_contribution_hook.py` | `2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e` |
| `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `mcm_field_organism/receptor_distributor.py` | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` |
| `mcm_field_organism/receptor_proposal_handoff_audit.py` | `40fd37b306ec6d41b85980c5cd498db555e4567fe1cfea957366194db7ee42d6` |
| `mcm_field_organism/receptor_time_alignment.py` | `af88766136848e0aea0e2bc1f09b689cf5748a46f4cdcc907c4ff6b5c70b643f` |
| `mcm_field_organism/shared_mcm_field.py` | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` |
| `mcm_field_organism/transient_dock_trajectory.py` | `22e24e719238181f8a3e57870d59794f2fa955aa46642482c2d5a4a5bf7a18a3` |
| `mcm_field_organism/transient_neuron_input.py` | `1ee10351fbe97811211aa08099cd967072b9ad1bbe24e151faefd2e64cfc7546` |

## 5. Bytebindung der Export- und Testgrenzen

| Datei | SHA-256 |
|---|---|
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |
| `tests/test_runtime_fixation_structure.py` | `78753a9baec8885482f295e62d92133211fef4e56c9e072ebb29ed05ebd38c6c` |
| `tests/test_runtime_fixation_adapters.py` | `31a73be9717a536c691d17d0b0e08dc919adcd7f9821971aebb592441e6d3966` |
| `tests/test_runtime_fixation_binding.py` | `de2d9f312a20d4fa0aa3237644402f0c8b74888552c8ed927d93c790cf4d9e58` |
| `tests/test_runtime_fixation_handoff.py` | `0ea123bd8b9c8aeeb719952058ddddd06aa22a0a29265029169bce0d48fdf53c` |

## 6. Ausdrueckliche Stringquellenbindung

Die acht Pfade aus `_SOURCE_DIGESTS` muessen in jeder spaeteren Umfangspruefung als Abhaengigkeiten behandelt werden, auch wenn sie nicht importiert werden:

- `mcm_field_organism/receptor_contract.py`;
- `mcm_field_organism/receptor_distributor.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/field_step_time.py`;
- `mcm_field_organism/neutral_local_field_substrate.py`;
- `mcm_field_organism/mcm_neuron_layer.py`;
- `mcm_field_organism/_previous_state_minimal_runner.py`;
- `mcm_field_organism/previous_state_contribution_hook.py`.

Eine Umfangspruefung nur anhand von Importkanten ist fuer diesen Korridor unzureichend. Auch statische Pfade in Digestlisten und alle anderen direkten Dateilesezugriffe muessen erfasst werden.

## 7. Umfangs- und Aenderungssperre

Die 42 Dateien aus Abschnitten 3 bis 5 bilden den vollstaendigen gebundenen Projektumfang fuer die weitere statische Vorbereitung.

- Jede Digestabweichung hebt diese Bindung auf.
- Keine der 42 Dateien darf im Rahmen dieser Neubindung geaendert werden.
- Keine Produktions-, Test-, Runtime-, Konfigurations- oder Exportdatei ausserhalb dieses Umfangs darf fuer den Pfad verwendet werden.
- Neue Import-, Stringpfad-, Datei-, Umgebungs- oder Laufzeitabhaengigkeiten sind verboten.
- Eine spaetere Umfangserweiterung verlangt erneut eine vollstaendige Bytebindung und unabhaengige Review.

Dokument 197 ersetzt nur die Umfangsbindung aus Dokument 193. Die Sperren und Bedingungen aus Dokumenten 192, 194, 195 und 196 bleiben bestehen. Insbesondere wird Huerde D erst nach positiver Review dieser korrigierten Bindung erneut entscheidbar.

## 8. Private Import-, Export- und Ausfuehrungsgrenzen

- Alle Fixierungs-, Bindungs-, Handoff- und Ablaufkoordinatorsymbole bleiben privat.
- Kein solches Symbol darf ueber `mcm_field_organism/__init__.py` oder eine andere oeffentliche Fassade exportiert werden.
- Dynamische Aufloesung und alternative Aufrufstellen bleiben verboten.
- Runner-, Integrator-, Hook-, Executor-, Runtime- und Public-AV-Module duerfen den Handoff nicht aufrufen.
- Die Aufnahme von `previous_state_contribution_hook.py` ist nur eine Byte- und Leseumfangsbindung; sie erteilt keine Hook-Ausfuehrungsfreigabe.
- Reale Bindung, Handoff, Ablaufkoordinator, Fixierung, Minimaltest und Runtime bleiben gesperrt.

## 9. Freigabefelder

```text
real_operations_binding_release: false
real_fixation_execution_release: false
runtime_release: false
runner_release: false
integrator_release: false
hook_release: false
executor_release: false
public_av_release: false
production_switch_release: false
automatic_execution_release: false
coordinator_handoff_release: false
minimal_test_release: false
```

`minimal_test_release_recommended: false`

## 10. Entscheidung

Die korrigierte Huerde A ist mit Dokument 197 vorbereitet, aber erst nach unabhaengiger statischer Review abgenommen. Bis dahin bleiben Huerde D, Huerde E und jede reale Ausfuehrung gesperrt.

Der einzige zulaessige naechste Schritt ist die unabhaengige statische Review von Dokument 197.

## 11. Aussagegrenze

Kein Inhalt dieses Dokuments ist ein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 12. Zielbezug

Es besteht keine erkennbare Zielabweichung. Die korrigierte Bytebindung schliesst einen technischen Quellenumfang und programmiert keine Erinnerung, Bedeutung, Zielantwort oder Topologie vor.

## 13. Auftrag fuer die unabhaengige statische Review

Die Review muss mindestens bestaetigen:

- 42/42 eingebettete SHA-256-Digests stimmen;
- Vertragslinie 184 bis 196: 13/13 Dokumente;
- relative AST-Importclosure: genau 23 Produktionsdateien;
- `_SOURCE_DIGESTS`: genau acht Stringquellen;
- Vereinigung beider Produktionsmengen: genau 24 Dateien;
- `previous_state_contribution_hook.py` ist enthalten;
- Exportgrenze und vier private Fixierungstests sind enthalten;
- keine weitere statische Projektdatei-Lesequelle im Fixierungskorridor bleibt ausserhalb des Umfangs;
- der Freigabeblock enthaelt genau zwoelf `false`- und kein `true`-Feld;
- `minimal_test_release_recommended: false` ist gesetzt;
- `git diff --check` meldet keine neuen Whitespace-Fehler.

Die Review darf keine Implementierungs-, Test-, Runtime- oder Exportdatei aendern, keine Projektmodule importieren oder ausfuehren und keine Bindungs-, Handoff-, Fixierungs- oder Runtime-Funktion aufrufen.
