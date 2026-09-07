# S2-NM: Subnormalverlust veraendert die A-Zulassung

Datum: 2026-09-07. Ausgangscommit: `b5e2752`.
Lauf-ID: `s2nm-subnormal-a-conflict-qualification-20260907-01`.

## Technische Qualifikation

Genau ein Aufruf aus dem Workspace-Root:

```powershell
C:/Python314/python.exe -B reports/s2nm/qualify_once.py
```

Dieser startete genau einmal `unittest` mit den drei vorgebundenen Testkoerpern,
`-v -f`, ohne Wiederholung der S2-NL-Tests. Ergebnis: **3/3**, Exit-Code **0**,
Testdauer **1,301 s**. Status: `S2NM_FOCUSED_QUALIFICATION_PASSED`.

Umfang: drei historische Zahlenpaare, zwei Profile, zwei Teilscanregeln,
zwoelf Primaerentscheidungen und zwoelf Direktbaselineentscheidungen.
Alle **24 Abrufbelege** wurden durch die vorhandene unabhaengige
`verify_arm`-Belegpruefung akzeptiert, ohne erneuten Abruf.
**12/12** Primaer-/Baselinevergleiche sind funktional exakt gleich.

Alle Scans vollstaendig `9/3/8`; jeweils Trefferzahlen **1/1/0** fuer B4/Fast/Slow.
Jeder Arm budgetiert 48 beobachtete Differenzen und 48 interne
Gleichheitspositionen: **96**, insgesamt **2304** Wertvergleiche in den
24 Abrufen. Die nachgelagerte lesende Verifikation ist darin nicht als
zusaetzlicher Abruf gezaehlt. Jeder gesamte Armbeleg bleibt unter **32768 Byte**;
der groesste innere KZ-Ergebnisbeleg hat **15170 Byte**. Die gesammelten
Beobachtungen umfassen **508256 Byte**, unter der vorgebundenen 1-MiB-Grenze.

## Verhaltensbefund

**`SEMANTIC_DEVIATION_CONFIRMED`**, nicht erhaltene Entscheidung.

Die einzige unterschiedliche Komponente liegt bei **47**, ausserhalb der
beobachteten Baender 0..23. Diese beobachteten Werte und beide Abstaende
sind in allen Konstellationen null. Beide Banken bleiben deshalb jeweils
eindeutig anwendbar, unabhaengig von Mittelwert- oder All-Bands-Regel.

| Gebundenes Paar an Position 47 | Nach NJ-Halbierung | Vollvektorgleichheit alt/neu |
| --- | --- | --- |
| `(s, 0)` | `(0, 0)` | falsch / wahr |
| `(3*s, 4*s)` | `(2*s, 2*s)` | falsch / wahr |
| `(m, nextafter(m,0))` | `(m/2, m/2)` | falsch / wahr |

`s` bezeichnet das kleinste positive Subnormal, `m` das kleinste normale
Binary64. Die exakten Hexwerte und Vektordigests sind im Beobachtungsbeleg
enthalten und gegen die unveraenderten S2-NL-Paare geprueft.

Fuer **jedes** Paar gilt unter **beiden** Regeln:

| Profil | Interne A-Aufloesung | Endentscheidung | Hypothese |
| --- | --- | --- | --- |
| Historisch | `A_RECENT_INTERNAL_CONFLICT` | `ABSTAIN_INTERNAL_CONFLICT` | keine |
| Halbprofil | `A_RECENT_APPLICABLE` | `ADMIT_SINGLE_CONTEXT` | genau `A_RECENT`, 24 Werte |

Damit wechseln **6/6** Paar-/Regelvergleiche von Konflikt/Enthaltung zu
Zulassung. Die unabhaengigen Direktbaselines reproduzieren alle sechs Wechsel.
Es handelt sich nicht bloss um andere Digests: Der numerische Informationsverlust
macht die vollstaendigen Kandidaten gleich und aendert dadurch die oeffentliche
Zulassungsentscheidung. Dies ist kein gemessener Abrufgewinn und keine Behauptung,
dass die beiden historischen Inhalte dieselbe Erfahrung seien.

Die technische Pruefung ist bestanden, weil die unveraenderte Logik auf den
jeweiligen Daten regelkonform arbeitet und die Belege konsistent sind.
**Die weitergehende Annahme semantischer Gleichheit der beiden Profile ist
dagegen fuer diese neutralen Konstellationen widerlegt.**

## Bindungen und Grenzen

- 22 vorab gebundene Datei-Hashes vor/nach dem Aufruf unveraendert; anschliessend
  lesend gegen die Dateien bestaetigt. Historische S2-NL-Beobachtung und Ergebnis
  sind eingeschlossen.
- Saemtliche State- und Cue-Daten vor/nach jedem Vergleich bytegleich;
  gespeicherte Pre-/Postzustandsdigests identisch.
- Sechs neutrale synthetische Konstellationen, keine reale Memorygeschichte.
  Null Formationen, PPB-Updates, PCM-Erzeugungen oder Rezeptoranalysen.
- Keine Feld-, Runtime- oder NH-Ausfuehrung und keine Hypothesenanwendung.
  NG-, NH- und NL-Gates vor/nach unveraendert `False`.
- Nur neue Test-/Qualifikationsdateien und dieser Befund. Keine Produktkorrektur,
  Toleranz, Ersatzdarstellung oder Erweiterung des Zahleninventars.
- Kein universeller Gleitkommabeweis. Keine Aussage zur Haeufigkeit dieser
  Konstellationen an realen Quellen und keine automatische Integrationsfreigabe.

Ergebnisdigest (kanonischer Payload ohne eigenes Digestfeld):
`67ac8b1a8eb510d1ce9c1056c49a1d4196c4d28b7ede13ad9ffe6e7308586981`.

SHA-256 `observations.json`:
`c79e3b42215d731c1a1d82af6336bd2853c3e76d85688a8fbbb52818635cf4a5`.

SHA-256 `stderr.txt` (vollstaendiges Testprotokoll):
`d88a2a4e09301f99679aa41f58e6cfe78d98a6d2d61309df705f921e0dd3d992`.

## Rueckmeldung an den Analysten

Die offene Verhaltensfrage ist beantwortet. Vor einer Systemintegration ist
explizit zu entscheiden, ob diese nachgewiesene semantische Abweichung fuer das
neue Profil akzeptiert werden kann. Sie darf nicht als vollstaendige
Bedeutungserhaltung deklariert werden. Kein weiterer Lauf und keine technische
Korrektur werden aus diesem Befund eigenstaendig abgeleitet.
