# S2-NS: Quellen-, Zeit- und Gesamtlaufanbindung neutral qualifiziert

Status: **S2NS_RUN_BINDING_QUALIFIED**.
Qualifikations-ID: `s2ns-run-binding-qualification-20260908-01`.
Genau ein Testprozess, **20/20**, Exit-Code **0**, kein Retry.

## Aufruf und Bindungen

Aus dem Workspace-Root:

```powershell
& C:/Python314/python.exe -m reports.s2ns.qualify_run_binding_once
```

Der vorregistrierte Kindprozess lautete:
`C:/Python314/python.exe -m unittest tests.test_s2ns_private_run_binding -v -f`.
Testinventar, Umgebung, Arbeitsbudgets und vollstaendige Quellhashlisten
stehen in `preregistration.json`. Alle Vorher-/Nachher-Quellhashes sind gleich.

- Ergebnisdigest: `fef4b44b7a5189797a151238767e7d32ba97465b384a18e46e57fd3aa0ce319f`
- Ergebnisdatei SHA-256: `adcf957f7151f3d92ce646f9b5d40854b271fa8328d22d78c766770c746de3ab`
- Testprotokoll SHA-256: `e36fd6eb250a80e7d6a2c1335e682f35cacaf6bbf30e728a7a35c7127d9a2a27`
- Neutraler Recording-Digest: `0b7049e28c3ad20037072c58807e8821e850c2247dc10b50e74c2e9e152b8373`
- Unabhaengiger Verifikationsdigest: `46bd4d5be27eb646a9aac229208d508ffea177cdf49354659f4c23c9f2e415d3`

Der alte 24/24-Logikbeleg wird unveraendert referenziert:
`cf4f75d03a409b0a5801b8bb2835e4b68c61008d2ee6cf03bac72cfc9d9dae7f`.
Diese Tests wurden nicht erneut ausgefuehrt. 24 historische Logiktests und
20 neue Anschlusspruefungen sind keine behauptete neue 44-Test-Serie.

## Beobachtete Anschlusspruefung

Der historische `endpoint_snapshot_index` bleibt unveraendert versiegelt.
Die neue V2-Bindung fuehrt daneben den exakt geprueften nativen NJ-Index.
e01/e02 und spaetere Metadatenfenster bis e31 sind abgedeckt. Falscher Index,
Nichtteilbarkeit und manipulierte Plan-/Ereignis-/Fensterbindung wurden
typisiert abgewiesen. Der direkte Analyzer hat selbst keinen Indexparameter;
die V2-Pruefung liegt vor dem Aufruf, die einzige Rohzustandskonstruktion
verwendet danach den nativen Index. Keine nachtraegliche Umetikettierung.

Die eine synthetische, reduzierte Neutralfolge erzeugte 16 echte atomare
Memoryformationen und vier read-only Hinweise, keine NS-Geschichte.
Der auditive PPB-Slot 000 entstand bei n02, erhielt bei n03/n04 MATCHED mit
Support 2/3 und wurde bei n13 ersetzt. Slot 001 wurde bei n18 ersetzt.
Die unabhaengige Nachrechnung bestaetigte Auswahl, Updates und Generationen;
MATCHED erhaelt die Geburt, REPLACED erzeugt eine andere aktuelle Bindung.
Manipulierte Herkunft und Transaktionen wurden abgewiesen.

Alle acht gespeicherten Zwei-Sichten-Resultate der neutralen Folge stimmen
mit ihrer Direktbaseline ueberein. Die Gesamtpruefung akzeptiert gueltige
Enthaltung unabhaengig von der Erwartung. Formationswerte, Kandidatenabweichung
und Rezeptorvariation bleiben getrennt; fehlende Referenzen bleiben null.

Fehlende/vertauschte Ereignisse, fremde Quellenbindung, visueller Cue-Fremdbeleg,
Schreibkonflikt und erneute Verifikation wurden abgewiesen. Ein eigener,
frueh abbrechender neutraler Quellenfehler hinterliess den phasengenauen
`NOT_EVALUABLE`-Beleg. Kein teilweiser Funktionsbefund daraus.

## Beobachteter Umfang

| Arbeit im gesamten Qualifikationsprozess | Anzahl |
| --- | ---: |
| Echte neutrale Memoryformationen | 16 |
| Echte neutrale Audioanalysen | 2 |
| NJ-Projektionen (20 reduzierte Fixtures plus 2 echte Endpunkte) | 22 |
| Echte neutrale Videoanalyse | 1 |
| Ausfuehrungsscans / Banddifferenzen | 16 / 3840 |
| Lesende Scans / Banddifferenzen | 8 / 1920 |
| Formationspruefaufrufe inkl. abgewiesener Manipulationen | 21 |
| NS-Payloads, reale NS-Hauptgeschichten | 0 / 0 |

Der gueltige neutrale Gesamtbeleg umfasst **651396 Byte**. Die vollstaendig
bestueckte, nicht ausgefuehrte 31/16/15-Serialisierungsform umfasst
**1776635 Byte**. Sie verwendet echte Quellen-/Formations-/Zustandsformen
und vollstaendige numerische Scantermfelder, keine Platzhalterhuelle.
Die vorab additive und zur Laufzeit abschnittsweise gepruefte Grenze liegt
bei **4127744 Byte**, unter unveraendert **4194304 Byte**.
`size-witness.json` bindet Form, Digest und gemessene Groesse; es ist kein
funktionaler 31-Ereignis-Beleg und keine Behauptung universeller Numerik.

## Quellhashes des neuen Anschlusses

- Quellen/Zeit: `61de047a1f7c1a8b9b9ef303eada5387c39510ac5f1e6fe6a2e7e7a9d4bdc858`
- Einmaleinstieg: `355fa65464238c8630a40ef76e83d04ccb03f515619583bdddc09182ec4e45fa`
- Gesamtverifikation: `33f15b43f772a72db66525e51931a506f3107ef7f3d1e678c778b4fbca2e1102`
- Auswertung: `94fd303e9dd795d0c27a6c46116ec2158dc487d61671247004a6c040aac412d1`
- Tests: `63617f69176e704776cf3dd72aee78c5a65ce8af95ba79019ac4a225df0dc7a9`

## Verbleibende Grenze

Der eigene `run_main_once` ist vorbereitet und an den neuen Anschlussbeleg
sowie die unveraenderte Logikqualifikation gebunden. Historische Haupteinstiege
werden nicht umetikettiert. Quellenversiegelung und statischer Zeitblocker
bleiben als historische Belege unveraendert.

Keine NS-PCM-/RGB-Quelle wurde in dieser Qualifikation erzeugt oder analysiert.
Keine reale NS-Geschichte und keine Feld-/Runtimeintegration. Alle Hauptgates
bleiben False. Rezeptorgueltigkeit und Funktionsnutzen des NS-Korpus sind
weiterhin offen; unerwartete Speicherverlaeufe und Enthaltungen bleiben
spaeter regulaer fachlich auswertbar.

Offline werden gespeicherte Rohwerte direkt gegen NJ-Werte geprueft, nicht
rueckrekonstruiert. PCM/RGB-Erzeugung und Rezeptorreduktion werden nicht
wiederholt. Deren Herkunft bleibt hashgebunden; der native innere TSPM-Receipt
wird nicht neu erzeugt. Diese Grenze ist keine vollstaendige Reproduktion
aller vorgelagerten numerischen Rechnungen.

WEITER: Am besten geht es jetzt mit der lesenden Analystenpruefung dieser
Gesamtanbindung und der separaten Entscheidung ueber genau einen realen
31-Ereignis-NS-Lauf weiter.
