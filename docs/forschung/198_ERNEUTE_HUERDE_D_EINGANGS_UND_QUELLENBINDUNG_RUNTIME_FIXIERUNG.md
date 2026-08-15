# 198 - Erneute Huerde-D-Entscheidung zur Eingangs- und Quellenbindung

## 1. Zweck und Status

Dieses Dokument bewertet Huerde D erneut auf Grundlage der korrigierten und unabhaengig statisch abgenommenen Umfangsbindung aus Dokument 197.

Es ist keine Implementierungs-, Test- oder Ausfuehrungsfreigabe. Kein Projektmodul wurde importiert oder ausgefuehrt, keine reale Bindung erzeugt, keine Handoff-Funktion aufgerufen, keine Fixierung ausgefuehrt und keine Runtime aktiviert.

## 2. Gebundene Grundlage

| Datei | SHA-256 |
|---|---|
| `docs/forschung/196_HUERDE_D_EINGANGS_UND_QUELLENBINDUNG_SPERRBEFUND_RUNTIME_FIXIERUNG.md` | `cd5ed958821bc6b67334ab133aee88a207c14f388590331968f1deae593b72f6` |
| `docs/forschung/197_KORRIGIERTE_HUERDE_A_BYTE_UND_UMFANGSBINDUNG_RUNTIME_FIXIERUNG.md` | `644b71731a8bd539deb83b00b9e8cd38872ff8fb572711306e9ad642447644c1` |
| `mcm_field_organism/_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/_runtime_fixation_adapters.py` | `422f511c54da7cecce541313ab23bcb37d5d8edab6a97a5cfe04768f111048fc` |

Dokument 197 ersetzt fuer die Umfangsfrage Dokument 193. Die uebrigen Sperren aus Dokumenten 192, 194, 195 und 196 bleiben bestehen.

## 3. Fachliche Eingangsbindung

Der private Fixierungskorridor verwendet keine externe fachliche Eingabedatei. Die erlaubte Anzahl externer Daten-, Medien- und Konfigurationsdateien bleibt exakt `0`.

Die einzigen fachlichen Payloads sind die in `_previous_state_minimal_runner.py` fest definierten und kanonisch gehashten Werte:

| Payload | SHA-256 |
|---|---|
| `A` | `2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998` |
| `B` | `66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31` |
| `C` | `81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3` |
| `config` | `fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a` |
| `bundle` | `2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0` |

Diese Payloads duerfen nicht durch Parameter, Dateien, Standardinput, Umgebungswerte, Zufall oder externe Datenstroeme ersetzt oder erweitert werden.

## 4. Vollstaendige Integritaetsquellenbindung

`_SOURCE_DIGESTS` benennt genau acht Read-only-Integritaetsquellen:

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

Alle acht Quellen sind in Dokument 197 enthalten. Die in Dokument 196 festgestellte Umfangsluecke ist damit fuer den statisch gebundenen Stand geschlossen.

Die Aufnahme von `previous_state_contribution_hook.py` erlaubt ausschliesslich seine Bytepruefung. Sie erteilt keine Hook-Ausfuehrungsfreigabe.

## 5. Erlaubte Leseoperation

Als spaetere Quellenoperation waere ausschliesslich der bereits vorhandene Digestvergleich ueber `_verify_bound_source_bytes(...)` zulaessig, sofern alle spaeteren Huerden gesondert erfuellt und freigegeben wuerden.

Dabei muessten fuer jede der acht Quellen gelten:

- kanonischer relativer Pfad innerhalb der gebundenen Projektwurzel;
- regulaere Datei, kein Symlink und keine Pfadtraversierung;
- ausschliesslich byteweises Lesen zur SHA-256-Pruefung;
- keine inhaltliche Verwendung als fachlicher Input;
- keine Schreiboperation und keine Pfadsubstitution;
- Abbruch bei fehlender Datei, Lesefehler oder Digestabweichung.

## 6. Ausschluesse

Weiterhin ausgeschlossen bleiben:

- externe Daten-, Medien- und Konfigurationsdateien;
- Standardinput, CLI-Parameter und interaktive Eingaben;
- Umgebungsvariablen und ungebundene Pfade;
- Netzwerk, IPC, Mikrofon, Kamera, Public-AV und Live-Sensoren;
- Uhrzeit, Zufall und variable Systemmetadaten als fachlicher Input;
- Datenbanken, Caches, Rohdatenspeicher, Embeddings und Memory-Artefakte;
- Symlinks, Junctions, Pfadtraversierung und Quellen ausserhalb der Projektwurzel;
- Projektdateien ausserhalb des 42-Dateien-Umfangs aus Dokument 197;
- Labels, Rewards, Zielantworten, Solltopologien und semantische Vorgaben.

## 7. Abbruchbedingungen

Vor jeder Fixierungsfortsetzung muesste fehlerhaft abgebrochen werden, wenn:

- ein Payload- oder Quelldigest abweicht;
- eine erwartete Quelle fehlt, kein regulaeres File oder ein Symlink ist;
- ein Pfad ausserhalb der Projektwurzel liegt oder vom kanonischen Pfad abweicht;
- eine nicht gebundene Datei oder Quelle angefordert wird;
- externe, interaktive, variable oder live gelesene Eingaben angefordert werden;
- A, B, C oder die Konfiguration von ihren kanonischen Bytes abweichen;
- eine Quelle nicht vollstaendig gelesen oder gehasht werden kann;
- Dokument 197 nicht mehr bytegleich ist oder sein Umfang erweitert wurde.

Nach einem solchen Abbruch duerfen kein Retry, kein zweiter Aufruf, kein Teilergebnis, keine Teilfreigabe und keine Runtime-Fortsetzung erfolgen.

## 8. Erneute Entscheidung zu Huerde D

Auf Grundlage der positiv geprueften korrigierten Umfangsbindung aus Dokument 197 ist die in Dokument 196 festgestellte Quellenluecke geschlossen. Huerde D ist damit statisch konsistent vorbereitet.

Huerde D gilt erst nach unabhaengiger statischer Review von Dokument 198 als dokumentarisch abgenommen. Daraus folgt keine Freigabe fuer Huerde E, eine Implementierung, einen Test oder eine reale Ausfuehrung.

## 9. Fortbestehende Sperren

Gesperrt bleiben:

- reale Bindung und Handoff;
- Ablaufkoordinator und Fixierung;
- Minimaltest und Runtime;
- Runner, Integrator, Hook und Executor;
- Public-AV und realer Weltkontakt;
- Produktionsschalter und automatische Ausfuehrung;
- persistente Zustandsaenderung und Ausdruckskanaele.

## 10. Freigabefelder

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

## 11. Aussagegrenze

Kein Inhalt dieses Dokuments ist ein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 12. Zielbezug

Es besteht keine erkennbare Zielabweichung. Die Eingangsbindung verhindert variable oder vorprogrammierte Zielinhalte und gibt weder Memory noch Bedeutung oder Topologie vor.

## 13. Auftrag fuer die unabhaengige statische Review

Die Review muss mindestens bestaetigen:

- alle dreizehn eingebetteten Datei-Digests stimmen;
- die fuenf Payload-Digests stimmen mit `_previous_state_minimal_runner.py` ueberein;
- externe fachliche Eingabedateien sind auf exakt null begrenzt;
- `_SOURCE_DIGESTS` enthaelt genau acht Quellen;
- alle acht Quellen sind in Dokument 197 gebunden;
- `previous_state_contribution_hook.py` ist nur zur Bytepruefung, nicht zur Ausfuehrung freigegeben;
- Ausschluesse und Abbruchbedingungen bleiben vollstaendig;
- Huerde E und reale Ausfuehrung bleiben gesperrt;
- der Freigabeblock enthaelt genau zwoelf `false`- und kein `true`-Feld;
- `minimal_test_release_recommended: false` ist gesetzt;
- `git diff --check` meldet keine neuen Whitespace-Fehler.

Die Review darf keine Implementierungs-, Test-, Runtime- oder Exportdatei aendern, keine Projektmodule importieren oder ausfuehren und keine Bindungs-, Handoff-, Fixierungs- oder Runtime-Funktion aufrufen.
