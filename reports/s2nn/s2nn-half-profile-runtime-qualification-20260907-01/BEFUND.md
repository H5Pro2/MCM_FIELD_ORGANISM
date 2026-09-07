# S2-NN: neutrale Runtime-Anbindung, Qualifikation gestoppt

Datum: 2026-09-07. Ausgangscommit `5bef4ec`.
Lauf-ID: `s2nn-half-profile-runtime-qualification-20260907-01`.
Gesamtstatus: **NOT_QUALIFIED**, Exit-Code **1**. Kein Retry.

## Umsetzung und einmaliger Aufruf

Die akzeptierte semantische Profilabweichung ist als Nachtrag in S2-NK
festgehalten. Die neue private Datei
`tools/_s2nn_private_half_runtime_binding.py` bindet die NJ-Ausgangsprojektion
vor der gemeinsamen Ereignisprojektion an NL-Konfiguration und NG-Komposition.
MR, NG, LO, Memorykerne, Rezeptoren und Defaultadapter wurden nicht veraendert.
Die Anbindung hat nur einen neutralen Einstieg, das Hauptgate bleibt geschlossen.

Genau ein Aufruf aus dem Workspace-Root:

```powershell
C:/Python314/python.exe -B reports/s2nn/qualify_once.py
```

Dieser startete einmal `unittest` mit den 14 vorgebundenen Pruefgruppen,
`-v -f`. **Zwei Tests bestanden; Test 3 endete mit ERROR; Tests 4..14 liefen
nicht.** Das Protokoll meldet drei aufgerufene Tests in 4,113 Sekunden.
Kein zweiter Aufruf, keine nachtraegliche Produkt- oder Testkorrektur.

## Konkrete Abbruchstelle

In `test_03_mixed_profile_and_state_rejected`, Zeile 133, wird ein alter
Nullzustand unmittelbar mit dem internen JW-Validator unter der neuen
Konfiguration geprueft:

```python
ng.memory._validate_state(self.config, ng.memory.initial_s2jv_composite_state(old))
```

Der Test erwartet dort `S2JWCoordinatorError`. `_validate_state` delegiert
jedoch in Zeile 315 ohne Ausnahmeumformung an
`tspm1._validate_composite_state`. Dieser verwirft das gemischte Profil mit:

```text
TSPM1Error
TSPM1_COMPOSITE_OR_FAST_STATE_INVALID: composite identity or generation mismatch
```

Die Ablehnung ist erfolgt; es wurde kein gemischter Zustand akzeptiert.
Fehlerhaft ist an dieser direkt aufgerufenen internen Pruefstelle die
vorausgesetzte Ausnahmeklasse der neutralen Assertion. Die vorherige
oeffentliche NN-Pruefung einer alten Konfiguration wurde bereits mit
`S2NNError` korrekt abgewiesen. Die folgende umgekehrte Zustandsmischung im
selben Test wurde wegen des Fehlers **nicht mehr erreicht**.

Dies ist weder ein Beleg fuer eine fehlende Profiltrennung noch eine bestandene
Gesamtqualifikation. Aus diesem Befund wurde keine Kernkorrektur abgeleitet.

## Bereits aufgezeichnete neutrale Teilbefunde

Das gemeinsame `setUpClass` hat die vier gebundenen Ereignisse vorher einmal
je neuer Regelruntime verarbeitet und den Gesamtbeleg einmal mit der bestehenden
unabhaengigen NG-Pruefung verifiziert. Deren Status ist `RECORDING_COMPLETE`:

| Ereignis | Feld, beide Arme | Memory, beide Arme | Kontext, beide Arme |
| --- | --- | --- | --- |
| 1: Formation | Kontakt aufgezeichnet | Formation committed | nicht angefordert |
| 2: Audiohinweis | Kontakt aufgezeichnet | read-only unveraendert | A-Kandidat verfuegbar |
| 3: Fortsetzung | Kontakt aufgezeichnet | Formation committed | nicht angefordert |
| 4: Visualhinweis | Kontakt aufgezeichnet | read-only unveraendert | interne Mehrdeutigkeit, Enthaltung |

- Drei gueltige NJ-Aufrufe: rohe synthetische 48 x 0.5 werden jeweils einmal
  zu 48 x 0.25. Dieselben neuen Materialisate gehen in beide Regelarme.
- Acht Runtimeereignisse, vier erfolgreiche Formationen, **2016 Feldkontakte**,
  **acht Scanbelege**. Die lesende Pruefung bestaetigt Baselinegleichheit und
  identische korrespondierende Feld-/Memoryzustaende innerhalb des neuen Profils.
- **768** im Beleg erfasste Scan-Wertvergleiche. Gesamtbeleg **179902 Byte**,
  unter dem bestehenden Limit von 4194304 Byte.
- Test 1 bestaetigte Profil-/Regelbindung und geschlossenes Hauptgate.
  Test 2 bestaetigte gemeinsame halbierte Werte und wies einen bereits
  projizierten Eingang als falschen Rohzustandstyp ab.
- Die nachfolgenden ausdruecklichen Instanz-, Lifecycle-, Ressourcen-,
  Fehlerisolations- und Teilcommit-Kontrollen sind **nicht qualifiziert**.
  Insbesondere wurden die beiden geplanten Fehlerinjektionspraefixe nicht ausgefuehrt.

Das ist eine neutrale technische Teilbeobachtung, keine reale Transfergeschichte
und keine vollstaendige S2-NN-Freigabe. Es wird keine Alt-/Neu-Feldgleichheit
behauptet. S2-NM bleibt akzeptierte semantische Abweichung, kein Abrufgewinn.

## Bindungsbelege und Grenzen

Die vorab protokollierten **1184** Projektmodul-/Test-/Dokumenthashes sind vor
und nach dem Aufruf unveraendert und wurden anschliessend lesend gegen die
Dateien geprueft. Die gespeicherten Artefakthashes stimmen ebenfalls.
Diese Hashpruefung fuehrte keine Projektfunktion oder Testwiederholung aus.

NG-, NH-, NL- und NN-Hauptgates sind `False`. Keine NH-Quellen,
PCM-/RGB-Erzeugungen oder Rezeptoranalysen. Keine Quellenanpassung, neue
Genauigkeitsmechanik, Toleranz, Feld-Rueckverstaerkung oder Produktumstellung.
Historische Belege, fremde Aenderungen und Bootstrap bleiben unberuehrt.

Gesamtergebnisdigest:
`03bb63a716ff4a3267a87c8183e0e80bcf6503b3521935f5b9bb7a6419a9863a`.

Neutraler Runtimebeleg-Digest:
`e45eed5165686615d28a3dbf3263ab995b73d81e2e032093a5183523718208b3`.

Read-only-Pruefbeleg-Digest:
`fe2bf90c9460d31d2b953f1ca038b5f7b1f6af98c049ed301d6358d8d77987ac`.

## Rueckmeldung

Der kleinste naechste Vorschlag ist eine Analystenfreigabe zur exakten
Korrektur der neutralen Ausnahmenerwartung an den beiden direkten
Kernvalidatoraufrufen, mit Pruefung des konkreten TSPM-Fehlercodes und ohne
Lockerung auf beliebige Exceptions. Danach waere genau eine neue neutrale
Qualifikation unter eigener ID erforderlich. Bis dahin keine System- oder
Hauptlauffreigabe aus diesen Teilbefunden ableiten.
