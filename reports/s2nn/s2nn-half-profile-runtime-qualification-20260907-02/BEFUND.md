# S2-NN: vollstaendige neutrale Neuqualifikation bestanden

Datum: 2026-09-07. Ausgangscommit `734ae99`.
Lauf-ID: `s2nn-half-profile-runtime-qualification-20260907-02`.
Status: **S2NN_HALF_RUNTIME_QUALIFIED**. **14/14**, Exit-Code **0**.

## Eng begrenzte Korrektur

Ausschliesslich Testgruppe 3 wurde fachlich korrigiert. Die beiden direkten
Zustandsmischungspruefungen erwarten nun `TSPM1Error` mit genau
`TSPM1_COMPOSITE_OR_FAST_STATE_INVALID`. Sie stehen in getrennten benannten
`subTest`-Bloecken fuer beide Mischrichtungen. Beide Kontrollen wurden erreicht
und bestanden. Die oeffentliche NN-Konfigurationspruefung erwartet weiterhin
`S2NNError`. Keine allgemeine Exception-Akzeptanz.

Der bestehende reportlokale Aufruf erhielt die neue Lauf-ID und die Bindung
an `QUALIFIKATIONSBINDUNG_02.md`. Produktcode, Profile, Regeln, Fixtures und
Ressourcenlimits wurden nicht veraendert. Vor Ausfuehrung entsprachen alle
**1179 Produktmodulhashes** den Bindungen der ersten Qualifikation.

## Genau ein Aufruf

Aus dem Workspace-Root:

```powershell
C:/Python314/python.exe -B reports/s2nn/qualify_once.py
```

Der Aufruf band vor Testbeginn Inventar, Interpreter, Quellhashes und Budgets
in `preregistration.json`. Genau ein vollstaendiger `unittest`-Aufruf mit den
unveraenderten 14 Testkoerpern, `-v -f`; Testdauer **9,741 Sekunden**, terminal
`OK`. Kein Retry, keine Wiederholung der NL-/NM-Suiten.

## Beobachtete Qualifikation

Alle 14 Pruefgruppen bestanden, einschliesslich der beim ersten Aufruf nicht
erreichten Gruppen 4..14:

- Vollstaendige Halbprofil-/Regelbindung, halbierte Audiogrenzen und feste
  Audio-Rangumrechnung; Ablehnung alter Konfigurationen und gemischter Zustaende.
- Drei gueltige NJ-Projektionen: jeweils 48 x 0.5 auf 48 x 0.25, einmal vor
  der gemeinsamen Bindung. Feld und Memory erhalten dieselben neuen Werte;
  Visualwerte bleiben unveraendert. Bereits projizierte Eingaenge werden als
  falscher Rohzustandstyp abgewiesen; lesende Validierung projiziert nicht erneut.
- Getrennte Runtime-, Prozessor-, Feld- und Memoryinstanzen, MR-Ereignisowner,
  konsistenter Lifecycle und geschlossene Endzustaende.
- Fortsetzung der Formation ueber den fruehen read-only Audiohinweis hinweg;
  auditive und visuelle PPB-Bank werden bei der zweiten Formation gemeinsam
  erzeugt. Beide Hinweisformen bleiben read-only.
- Vollstaendige Scans, unabhaengige Direktbaselines, gueltige Enthaltung sowie
  unveraenderte visuelle Verarbeitung und identische Slow-Belege beider Regelarme.
- Quellen-/Zeit-/Projektionsmanipulationen und fehlende Belege werden abgewiesen;
  unveraenderliche Eingaben und bestehende Ressourcenlimits sind geprueft.

| Neutraler Ablauf | Ereignisse je Arm | Feldkontakte gesamt | Scanbelege | Technischer Belegstatus |
| --- | --- | --- | --- | --- |
| Formation, Audiohinweis, Fortsetzung, Visualhinweis | 4 | 2016 | 8 | RECORDING_COMPLETE |
| Praefix mit injizierten Scanfehlern | 2 | 768 | 0 | NOT_EVALUABLE, erwartete Fehlerkontrolle |
| Praefix mit injiziertem zweitem PPB-Fehler | 3 | 1440 | 4 | NOT_EVALUABLE, erwartete Fehlerkontrolle |

Gesamt: **18 neutrale Runtimeereignisse**, **10 Formationsversuche**,
**4224 transiente Feldkontakte**, **12 vollstaendige Scanbelege**.
Die zwoelf Belege umfassen sechs Primaer-/Direktbaselinepaare. Alle drei
Aufzeichnungen wurden unabhaengig lesend geprueft, ohne erneute Formation
oder Runtimeausfuehrung. Die gespeicherten erfolgreichen Scans weisen zusammen
**1152** Wertvergleiche aus, innerhalb der gebundenen Obergrenze 7424;
Verifikationsarbeit wird davon getrennt gezaehlt.

Die beiden absichtlichen Fehlerpraefixe sind neutrale Sicherheitskontrollen,
keine fachlich gescheiterten Hauptlaeufe und keine Wiederholungen einer
Transfergeschichte. Bei Scanfehlern blieben Memory und gueltiger Feldkontakt
erhalten. Im PPB-Fehlerfall wurde der auditive Zwischenvorschlag berechnet,
bevor der visuelle Zweig scheiterte: **kein B4-/Fast-/Slow-Teilcommit**.
Beide Arme blieben beim jeweiligen vollstaendigen Memoryvorzustand;
der Feldschritt wurde unabhaengig fortgeschrieben.

## Integritaet und Ressourcen

Alle **1185** vorab gebundenen Dateihashes waren vor/nach dem Aufruf identisch
und wurden anschliessend lesend gegen die Dateien kontrolliert. Auch die
gespeicherten Artefakthashes stimmen. Keine erneute Test- oder Projektberechnung
bei dieser Dateipruefung.

Die drei Runtimeaufzeichnungen sind **179902**, **45379** und **115654 Byte**
gross, jeweils unter dem unveraenderten Limit von 4194304 Byte. Eingangs-,
Zustands-, Ereignis- und Scanlimits wurden vom bestehenden Code und den Tests
geprueft; keine Grenzerhoehung.

NG-, NH-, NL- und NN-Gates sind weiterhin `False`. Keine NH-Quellen,
PCM-/RGB-Erzeugung oder Rezeptoranalyse. Der erste S2-NN-Fehlbefund bleibt
unveraendert `NOT_QUALIFIED`; historische Belege, fremde Aenderungen und
Bootstrap wurden nicht geaendert.

Ergebnisdigest:
`6825f44ef741c59a8432a03a73cb2546d75ce758d0b206b2a8ed4527cca72a8c`.

Neutraler Vierereignisbeleg-Digest:
`e45eed5165686615d28a3dbf3263ab995b73d81e2e032093a5183523718208b3`.

Zugehoeriger read-only Pruefbeleg-Digest:
`fe2bf90c9460d31d2b953f1ca038b5f7b1f6af98c049ed301d6358d8d77987ac`.

## Aussagegrenze und Rueckmeldung

Die private Halbprofil-Runtime-Anbindung ist fuer diesen neutralen Umfang
technisch qualifiziert. **Kein realer Quellen-/Transferbefund**, keine
NH-Wiederoeffnung, keine Produktionsumstellung und kein universeller
Gleitkommanachweis. Es wurde keine Alt-/Neu-Feldgleichheit verlangt oder
nachgewiesen. Die in S2-NM belegte Konfliktaufloesung bleibt eine akzeptierte
semantische Profilabweichung, kein automatisch richtiger Abruf oder Gewinn.

Naechster Vorschlag an den Analysten: ueber einen einzelnen, separat
gebundenen Funktionsversuch mit der qualifizierten privaten Halbprofil-Anbindung
entscheiden. Ohne diese Freigabe keine weitere Ausfuehrung und insbesondere
kein erneuter NH-Lauf.
