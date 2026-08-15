# Teilpaket 213A: Statische lokale Python-Korridor-Datei- und Importkarte

## Einordnung, Forschungsfrage und Auftrag

Dies ist statische Dokumentation und **kein Forschungslauf**. Deshalb wird keine
Laufnummer vergeben. Der freigegebene Auftrag 213A lautet, lokale Dateien sowie
statische Import- und Dateiverweise des privaten Python-Korridors zu kartieren.

Nicht Gegenstand dieses Teilpakets sind Windows-AppContainer, ACL-Klassen, SID/DACL-
Annahmen, Temp-, Profil-, Cache- oder Diagnosepfade. Diese Punkte gehoeren getrennt
zu 213B. Es wurden keine Module importiert, Tests gestartet oder Projektpfade
ausgefuehrt.

## Tatsaechlich verwendete Quellen

- aktueller Abschnitt `Ergebnis / Auftrag` mit der Korrektur und Freigabe von 213A;
- `docs/forschung/212_LAUF_STATISCHE_APPCONTAINER_KOMPATIBILITAETSANALYSE_PYTHON_KORRIDOR.md`;
- die in dieser Karte aufgefuehrten lokalen Python-Dateien;
- statische Ausgaben von `Get-Content`, `Get-Item`, `Get-FileHash` und `rg`.

Externe Quellen und MCM-Grundlagenquellen wurden fuer dieses lokale Dateiteilpaket
nicht verwendet.

## Verwendete Dateien und Schnittstellen

Ausgangspunkt war
`mcm_field_organism/_runtime_fixation_single_use_path.py`. Relative Imports wurden
zeilenbasiert aus dem Quelltext gelesen und rekursiv verfolgt. Literale Dateiverweise
wurden separat mit Textsuche erfasst. SHA-256-Werte wurden mit `Get-FileHash`
berechnet.

Kein Python-Interpreter, Projektmodul, Test, Runner, Hook oder privater Runtimepfad
wurde aufgerufen. Es gab keine Code-, ACL- oder Systemaenderung.

## Durchgefuehrte Schritte

1. Einstiegspunkt und rekursive relative `from .modul import ...`-Kanten gelesen.
2. Alle erreichbaren lokalen `.py`-Dateien auf Existenz, Bytegroesse und SHA-256
   geprueft.
3. Nichtrelative Importwurzeln als Namen erfasst, ohne ihre Module aufzuloesen.
4. Direkte Datei-API-Verweise (`Path`, `read_bytes`, `__file__`) gesucht.
5. Die acht in `_SOURCE_DIGESTS` festgeschriebenen Dateiverweise gegen den aktuellen
   Workspace verglichen.
6. Den normalen Paketimport als Gegenbaseline betrachtet, weil ein Untermodulimport
   grundsaetzlich die Paketdatei `__init__.py` einbezieht.

## Privater statischer Importabschluss

Der rekursive relative Importgraph ab dem privaten Einstieg umfasst 20 lokale
Projektdateien:

| Modul | Bytes | SHA-256 |
| --- | ---: | --- |
| `_previous_state_minimal_runner` | 8655 | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `_runtime_fixation_adapters` | 11458 | `422f511c54da7cecce541313ab23bcb37d5d8edab6a97a5cfe04768f111048fc` |
| `_runtime_fixation_binding` | 2226 | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `_runtime_fixation_handoff` | 1086 | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |
| `_runtime_fixation_single_use_path` | 482 | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `_runtime_fixation_structure` | 15549 | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `auditory_baselines` | 8538 | `1bd6a5f22181ef0af345509cfbf25195dd97c66e4137f11fefc7f629a9c35731` |
| `broadband_hearing_path` | 7754 | `4dea43d16110444dc2408137361740c5b4a0cca24ac627b715f409ceff0c6535` |
| `carrier_baselines` | 3572 | `dc891f4f263b17acf7b7b50c7c135d9a3d028cb1b9bdb72c342d72d24f1337ab` |
| `field_step_time` | 1790 | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` |
| `finite_video_path` | 10943 | `d09cb6ba35fd061e4a243b7ed2112597a194e75abd026d7cc3ab7aa89922c07a` |
| `live_audio_adapter` | 13852 | `c37ab44ded2678a3d0a664044390bdced5de7a4c10174935e1b0025bb286a676` |
| `log_spectral_receptor` | 7024 | `26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0` |
| `mcm_neuron` | 7702 | `79cf8f8aa79d8c336c5d3fd57303a9f618e2840217c7786688112d0b7c66783a` |
| `mcm_neuron_layer` | 18322 | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` |
| `neutral_local_field_substrate` | 28183 | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` |
| `receptor_contract` | 7853 | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` |
| `receptor_distributor` | 7563 | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` |
| `shared_mcm_field` | 31578 | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` |
| `transient_neuron_input` | 9799 | `1ee10351fbe97811211aa08099cd967072b9ad1bbe24e151faefd2e64cfc7546` |

Alle 20 erwarteten Dateien waren vorhanden. Es fehlte keine durch den Textresolver
erkannte relative Projektdatei.

## Importkanten

Es wurden 44 eindeutige relative Importkanten erfasst. Nach Quelle gruppiert:

| Quelle | direkte relative Ziele |
| --- | --- |
| `_runtime_fixation_single_use_path` | `_runtime_fixation_binding`, `_runtime_fixation_handoff`, `_runtime_fixation_structure` |
| `_runtime_fixation_handoff` | `_previous_state_minimal_runner`, `_runtime_fixation_binding`, `_runtime_fixation_structure` |
| `_runtime_fixation_binding` | `_previous_state_minimal_runner`, `_runtime_fixation_adapters`, `_runtime_fixation_structure` |
| `_runtime_fixation_structure` | `_previous_state_minimal_runner` |
| `_runtime_fixation_adapters` | `_previous_state_minimal_runner`, `_runtime_fixation_structure`, `field_step_time`, `neutral_local_field_substrate`, `receptor_contract`, `receptor_distributor`, `shared_mcm_field` |
| `auditory_baselines` | `carrier_baselines` |
| `broadband_hearing_path` | `carrier_baselines`, `live_audio_adapter`, `log_spectral_receptor` |
| `field_step_time` | `receptor_contract` |
| `live_audio_adapter` | `auditory_baselines`, `carrier_baselines` |
| `log_spectral_receptor` | `carrier_baselines` |
| `mcm_neuron_layer` | `field_step_time`, `mcm_neuron`, `transient_neuron_input` |
| `neutral_local_field_substrate` | `field_step_time`, `mcm_neuron_layer`, `receptor_distributor`, `shared_mcm_field`, `transient_neuron_input` |
| `receptor_contract` | `broadband_hearing_path`, `finite_video_path` |
| `receptor_distributor` | `receptor_contract` |
| `shared_mcm_field` | `field_step_time`, `mcm_neuron`, `mcm_neuron_layer`, `receptor_contract`, `receptor_distributor`, `transient_neuron_input` |
| `transient_neuron_input` | `field_step_time`, `receptor_contract` |

Die nichtrelativen Importwurzeln lauten: `__future__`, `dataclasses`, `enum`,
`hashlib`, `hmac`, `json`, `math`, `numpy`, `pathlib`, `queue`, `re`, `time` und
`typing`. Ihre Standardbibliotheks-, Drittbibliotheks- oder DLL-Abhaengigkeiten sind
nicht Bestandteil von 213A.

## Statische Dateiverweise ausserhalb des Importgraphen

`_runtime_fixation_adapters.py` bestimmt ueber
`Path(__file__).resolve().parent.parent` den Projektwurzelpfad und liest die in
`_runtime_fixation_structure.py::_SOURCE_DIGESTS` genannten Dateien mit
`resolved.read_bytes()`.

`_SOURCE_DIGESTS` nennt acht Dateien. Sieben davon liegen bereits im 20-Dateien-
Importgraphen. Der achte Verweis ist
`mcm_field_organism/previous_state_contribution_hook.py`; diese Datei wird in diesem
Pfad statisch nicht importiert, aber als zu lesende Digestquelle referenziert.

| Dateiverweis | festgeschriebener SHA-256 | aktueller SHA-256 | passt |
| --- | --- | --- | --- |
| `_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` | gleich | ja |
| `field_step_time.py` | `2fba95b49768fcbfb01253ef20b7574a6f4df868fb51d0c0229791d0d523d3dd` | gleich | ja |
| `mcm_neuron_layer.py` | `ea699158096d35be62bfc308691325d4408ca491b5d456928509f52c1a554277` | gleich | ja |
| `neutral_local_field_substrate.py` | `df5fb99d653963b83990315f5d3b70ff7feb00bd518a6a192a9fd06523bd4f13` | gleich | ja |
| `receptor_contract.py` | `af565ce442aa56ade4b3b5d028692cccc93b481c299f1ff2d87ba840fdb6ee71` | gleich | ja |
| `receptor_distributor.py` | `649bb3eb49e43f039fe525bdcbdfe5a0a1d06e67f25e5c88a10471fc546f1dad` | gleich | ja |
| `shared_mcm_field.py` | `2ddb013a049a13897af5e1e506a739410bf1579843799c4d6bf86d10e610a5ec` | gleich | ja |
| `previous_state_contribution_hook.py` | `2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e` | `42f98fe9beab7f71900135524693fc7e3be898fdc16c1696057c95a0fad8a648` | **nein** |

Der aktuelle Hook ist 4568 Bytes gross. Beobachtetes Ergebnis ist damit aktuell
`7/8` passende festgeschriebene Dateidigestwerte. Der in Dokument 212 gepruefte Stand
`8/8` beschreibt dessen damalige Bytebasis; er darf nicht auf den inzwischen
abweichenden Workspace uebertragen werden.

Es wurden innerhalb der 20 Importdateien keine statischen Verweise auf `tempfile`,
`NamedTemporaryFile`, `TemporaryDirectory`, `importlib`, `__import__`, `exec` oder
`eval` gefunden. Dies ist nur ein Textbefund und kein Laufzeitnachweis.

## Gegenbaseline normaler Paketimport

`mcm_field_organism/__init__.py` ist 64463 Bytes gross und hat aktuell SHA-256
`c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0`.

Eine gleichartige statische Verfolgung ab `__init__.py` plus privatem Einstieg ergab
118 vorhandene Projektmodule, 19 nichtrelative Importwurzeln und 0 fehlende relative
Dateien. Diese Gegenbaseline zeigt: Die 20-Dateien-Karte beschreibt nur die direkten
privaten Quellkanten. Sie ist **kein Nachweis**, dass ein normaler Python-Paketimport
nur diese 20 Dateien beruehren wuerde.

## Messergebnisse und Gegenbaselines

Es wurden keine dynamischen Messwerte erzeugt. Statische Zaehlergebnisse:

- 20 lokale Module im privaten relativen Importabschluss;
- 44 eindeutige relative Importkanten;
- 13 nichtrelative Importwurzeln im privaten Abschluss;
- 1 zusaetzlicher, nicht importierter Dateiverweis durch `_SOURCE_DIGESTS`;
- 7 von 8 festgeschriebenen Dateidigestwerten passen aktuell;
- 118 Projektmodule in der normalen Paketimport-Gegenbaseline;
- 0 erkannte fehlende relative Projektdateien in beiden Graphen.

Gegenbaselines:

| Baseline | Ergebnis |
| --- | --- |
| nur private relative Imports | 20 Module; blendet Paketinitialisierung aus |
| normaler Paketimport | 118 Module; erheblich breiterer lokaler Abschluss |
| nur Importdateien betrachten | uebersieht den zusaetzlichen Hook-Dateiverweis |
| Dokument-212-Bytebasis ungeprueft fortschreiben | falsch fuer aktuellen Workspace; Hook-Digest weicht ab |

## Fortbestehende Freigabegrenzen

Die zwoelf Freigabefelder aus Dokument 212 bleiben `false`; insbesondere gilt
`minimal_test_release_recommended: false`. 213A erteilt keine Implementierungs-,
Import-, Test- oder Ausfuehrungsfreigabe. Huerde G bleibt gesperrt.

## Grenzen und nicht gepruefte Annahmen

- Der zeilenbasierte Resolver ist kein vollstaendiger Python-AST- oder Importlib-
  Resolver.
- Bedingte und dynamische Importe, `.pth`-Dateien, Pluginmechanismen sowie native
  Bibliothekskanten wurden nicht aufgeloest.
- Kein Befund belegt, welche Dateien ein realer Prozess tatsaechlich oeffnen wuerde.
- Der Hook-Digestunterschied wurde nicht inhaltlich bewertet oder korrigiert.
- ACL-, AppContainer-, Profil-, Temp-, Cache- und Diagnosethemen sind absichtlich
  nicht Teil dieses Teilpakets.
- Es gibt keinen Befund zu Laufverhalten, Feldwirkung, Kontaktgeschichte, Memory,
  Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Der lokale private Korridor besitzt statisch 20 Importmodule, 44 relative Kanten und
einen zusaetzlichen Hook-Dateiverweis. Fuer einen normalen Paketimport ist die
20-Dateien-Annahme nicht ausreichend; die statische Gegenbaseline umfasst 118 Module.
Ausserdem ist die festgeschriebene Hook-Bytebindung im aktuellen Workspace nicht mehr
erfuellt, sodass aktuell nur 7/8 Digestverweise passen.

Diese Befunde sind reine Dateidokumentation. Sie weisen weder Lauffaehigkeit noch
AppContainer-Kompatibilitaet nach und aendern keine Sperre.

## Naechster begrenzter Schritt

Teilpaket 213A ist unabhaengig statisch durch die statische Gegenpruefung zu pruefen. Zu
reproduzieren sind die 20 Dateien, 44 Kanten, 13 externen Namen, der zusaetzliche
Hook-Dateiverweis, der aktuelle `7/8`-Digeststand, die 118-Modul-Gegenbaseline und die
vollstaendige Trennung von 213B. Das Ergebnis ist mit `FREIGABE`, `KORREKTUR` oder
`STOPP` zu bewerten; daraus folgt keine Ausfuehrungsfreigabe.

## Zielabweichung

Keine erkennbare Zielabweichung. Teilpaket 213A bleibt technische statische Vorarbeit
und behauptet keine MCM-Forschungswirkung.
