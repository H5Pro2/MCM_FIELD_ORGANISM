# 196 - Huerde D: Eingangs- und Quellenbindung mit statischem Sperrbefund

## 1. Zweck und Status

Dieses Dokument inventarisiert ausschliesslich statisch die Eingangs- und Integritaetsquellen eines moeglichen spaeteren Einmallaufs.

Es ist keine Implementierungs-, Test- oder Ausfuehrungsfreigabe. Kein Projektmodul wurde importiert oder ausgefuehrt, keine reale Bindung erzeugt, keine Handoff-Funktion aufgerufen, keine Fixierung ausgefuehrt und keine Runtime aktiviert.

Die Inventur ergibt einen Sperrbefund: Eine zur Laufzeit bytegepruefte Projektquelle liegt ausserhalb des in Dokument 193 gebundenen 37-Dateien-Umfangs. Huerde D kann deshalb auf dem aktuellen Umfang nicht positiv abgenommen werden.

## 2. Gebundene Vertragsgrundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/193_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_EINMALLAUF_PFAD_RUNTIME_FIXIERUNG.md` | `d002bc7832a0ef6cd36c2cc5ef481e0bb403cfede503c6ed6b22cd955c70974f` |
| `docs/forschung/194_HUERDE_B_EINMALIGER_AUSFUEHRUNGSVERTRAG_RUNTIME_FIXIERUNG.md` | `f4e2139aee4cc9f7cf95deb4cefc20881efe57aef1e17f8a9cad70b741e7274e` |
| `docs/forschung/195_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_EINMALLAUF_RUNTIME_FIXIERUNG.md` | `0154a6de7e80b5db8f373878af592855dfa6a0938bd7dedf5ebea927e5ae4ca3` |

## 3. Dateninputs

Der private Korridor sieht keine externe Eingabedatei vor. Die Anzahl erlaubter externer Daten-, Medien- oder Konfigurationsdateien ist exakt `0`.

Die einzigen fachlichen Eingangspayloads sind die in `_previous_state_minimal_runner.py` definierten Konstanten `_INPUT_A`, `_INPUT_B`, `_INPUT_C` und `_CONFIG_JSON`. Sie sind Bestandteil des bytegebundenen Quelltexts und werden kanonisch gehasht.

| Payload | SHA-256 laut gebundenem Quellvertrag |
|---|---|
| `A` | `2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998` |
| `B` | `66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31` |
| `C` | `81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3` |
| `config` | `fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a` |
| `bundle` | `2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0` |

Kein Parameter, Dateipfad, Standardinput, Umgebungswert oder externer Datenstrom darf diese Payloads ersetzen, erweitern oder beeinflussen.

## 4. Read-only-Integritaetsquellen

Die Adaptergrenze liest bei `verify_bound_source_bytes` genau acht Projektdateien zur SHA-256-Pruefung. Diese Lesezugriffe sind keine fachlichen Dateninputs, gehoeren aber zum realen Quellenumfang.

| Datei | SHA-256 |
|---|---|
| `mcm_field_organism/receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `mcm_field_organism/receptor_distributor.py` | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` |
| `mcm_field_organism/shared_mcm_field.py` | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` |
| `mcm_field_organism/field_step_time.py` | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` |
| `mcm_field_organism/neutral_local_field_substrate.py` | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` |
| `mcm_field_organism/mcm_neuron_layer.py` | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` |
| `mcm_field_organism/_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `mcm_field_organism/previous_state_contribution_hook.py` | `2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e` |

Spaeter zulaessig waere ausschliesslich ein byteweises Lesen dieser regulaeren, nicht symbolisch verlinkten Dateien innerhalb der gebundenen Projektwurzel. Schreiben, Pfadsubstitution und jede Nutzung ausser dem Digestvergleich bleiben verboten.

## 5. Umfangsabweichung gegen Huerde A

Sieben der acht Integritaetsquellen sind in Dokument 193 enthalten. `mcm_field_organism/previous_state_contribution_hook.py` ist dort nicht gebunden.

Das Hook-Modul wird nicht ueber einen relativen Python-Import erreicht. Sein Pfad steht als String in `_SOURCE_DIGESTS`, und `_verify_bound_source_bytes(...)` liest seine Bytes direkt. Eine reine AST-Importclosure erfasst diesen Dateizugriff nicht.

Dokument 193 bestimmt, dass jede Umfangserweiterung seine Bindung aufhebt und einen neuen ausdruecklichen Umfangsvertrag verlangt. Dokument 196 nimmt diese Erweiterung nicht selbst vor. Deshalb bleiben Huerde D, alle nachfolgenden Huerden und jede Ausfuehrung gesperrt. Huerde A muss fuer den realen Leseumfang neu gebunden werden.

## 6. Ausschluesse

Ausgeschlossen bleiben:

- alle externen Daten-, Medien- und Konfigurationsdateien;
- Standardinput, Kommandozeilenwerte und interaktive Eingaben;
- Umgebungsvariablen, Benutzerprofile und ungebundene Arbeitsverzeichnisse;
- Netzwerk, DNS, HTTP, Sockets und sonstige externe Verbindungen;
- Mikrofon, Kamera, Public-AV und andere Live-Sensoren;
- Uhrzeit, Zufall, Entropie und variable Systemmetadaten als fachlicher Input;
- Datenbanken, Caches, Rohdatenspeicher, Embeddings und persistente Memory-Artefakte;
- Symlinks, Junctions, Pfadtraversierung und Dateien ausserhalb der Projektwurzel;
- jede Projektdatei ausserhalb einer korrigierten, unabhaengig abgenommenen Umfangsbindung;
- Labels, Rewards, Zielantworten, Solltopologien und semantische Vorgaben.

## 7. Abbruchbedingungen

Ein spaeteres Vorabprotokoll muesste vor jeder Fixierungsfortsetzung fehlerhaft abbrechen, wenn:

- ein Payload- oder Quelldigest abweicht;
- eine Quelle fehlt, kein regulaeres File oder ein Symlink ist;
- ein Pfad die Projektwurzel verlaesst oder vom kanonischen Pfad abweicht;
- eine nicht gelistete Datei oder Quelle angefordert wird;
- externe, interaktive, variable oder live gelesene Eingaben angefordert werden;
- A, B, C oder die Konfiguration von ihren kanonischen Bytes abweichen;
- eine Quelle nicht vollstaendig gelesen oder gehasht werden kann;
- eine Umgebungs- oder Pfadabhaengigkeit nicht vorab gebunden ist;
- die korrigierte Umfangsbindung nicht unabhaengig abgenommen ist.

Danach duerfen kein Retry, kein zweiter Handoff, kein Teilergebnis, keine Teilfreigabe und keine Runtime-Fortsetzung erfolgen.

## 8. Keine Ausfuehrungsfreigabe

Dokument 196 erlaubt keine Implementierung, keinen Quellenlesetest, keinen Runner, keinen Executor, keinen CLI-Einstieg und keinen Ausfuehrungsbefehl.

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
orchestrator_handoff_release: false
minimal_test_release: false
```

`minimal_test_release_recommended: false`

## 10. Entscheidung zu Huerde D

Huerde D ist statisch inventarisiert, aber wegen der Umfangsabweichung nicht erfuellt. Eine positive Abnahme waere falsch, solange `previous_state_contribution_hook.py` nicht in einer korrigierten Huerde-A-Bindung enthalten ist.

Der einzige zulaessige naechste Schritt ist eine unabhaengige statische Review dieses Sperrbefunds. Erst danach darf ein korrigierter statischer Umfangsvertrag beauftragt werden. Huerde E und jede reale Ausfuehrung bleiben gesperrt.

## 11. Aussagegrenze

Kein Inhalt dieses Dokuments ist ein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 12. Zielbezug

Es besteht keine erkennbare Zielabweichung. Die Quellenbindung verhindert variable oder vorprogrammierte Zielinhalte und gibt weder Memory noch Bedeutung oder Topologie vor.

## 13. Auftrag fuer die unabhaengige statische Review

Die Review muss mindestens bestaetigen:

- alle zwoelf eingebetteten Datei-Digests stimmen;
- externe fachliche Eingabedateien sind auf exakt null begrenzt;
- die fuenf Payload-Digests stimmen mit `_previous_state_minimal_runner.py` ueberein;
- `_verify_bound_source_bytes(...)` liest genau acht Integritaetsquellen;
- genau eine dieser Quellen fehlt in Dokument 193;
- die fehlende Quelle ist `mcm_field_organism/previous_state_contribution_hook.py`;
- Huerde D bleibt gesperrt und Huerde A muss vor jeder Fortsetzung korrigiert werden;
- der Freigabeblock enthaelt genau zwoelf `false`- und kein `true`-Feld;
- `minimal_test_release_recommended: false` ist gesetzt;
- `git diff --check` meldet keine neuen Whitespace-Fehler.

Die Review darf keine Implementierungs-, Test-, Runtime- oder Exportdatei aendern, keine Projektmodule importieren oder ausfuehren und keine Bindungs-, Handoff-, Fixierungs- oder Runtime-Funktion aufrufen.
