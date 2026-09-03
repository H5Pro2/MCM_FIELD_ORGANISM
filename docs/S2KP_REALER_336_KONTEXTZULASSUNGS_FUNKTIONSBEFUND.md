# S2-KP - Realer 336-Werte-Kontextzulassungsbefund

## Status

`S2KP_FUNCTION_CONFIRMED`

Lauf-ID: `s2kp-real-context-admission-336-20260903-01`

Quellenstand:
`350ff1fdfa1008720af35d8a1e223761b35991d2`

Der einmalige Hauptlauf und die genau eine nachgelagerte unabhaengige
read-only Verifikation sind vollstaendig bestanden. Es gab keinen Retry,
keine Parameter-, Fixture- oder Schwellenaenderung. Das Quellgate war vor
und nach dem Lauf `False` und wurde nur fuer den einen Aufruf im laufenden
Prozess geoeffnet.

## Gebundener Umfang

- drei getrennte frische Memoryzustaende;
- Historylaengen `15/14/2`, zusammen exakt 31 reale Formationen;
- fuenf echte read-only Vollproben;
- sechs strikt spaetere maskierte Zulassungsproben;
- sechs S2-KN- und sechs unabhaengige Baselineentscheidungen;
- hoechstens 96 funktionale Top-Level-Arbeitseinheiten;
- keine Kontextfuellung, Feldwirkung oder automatische Maskenerkennung;
- keine gespeicherten RGB-, PCM- oder Rezeptorwertpayloads.

R1, R2, R5 und R6 wurden aus einer frisch rekonstruierten S2-JX-Geschichte
gebildet. R3 verwendete einen eigenen frischen B0/D1-D9/A0-Zustand, R4
einen eigenen frischen C0/C1-Zustand. Kein Zustand wurde aus einer alten
Ergebnisdatei geladen.

## Funktionsbefunde

| Fall | A-Befund | B-Befund | Entscheidung | Hypothese |
| --- | --- | --- | --- | --- |
| R1 | `A_RECENT_APPLICABLE`, B4/Fast wertgleich | `B_STABLE_ABSENT_VALID` | `ADMIT_SINGLE_CONTEXT` | `A_RECENT` |
| R2 | `A_RECENT_ABSENT_VALID` | `B_STABLE_APPLICABLE` | `ADMIT_SINGLE_CONTEXT` | `B_STABLE` |
| R3 | `A_RECENT_APPLICABLE` | `B_STABLE_APPLICABLE` | `ABSTAIN_AMBIGUOUS_CONTEXT` | keine |
| R4 | `A_RECENT_INTERNAL_CONFLICT` | `B_STABLE_ABSENT_VALID` | `ABSTAIN_A_RECENT_INTERNAL_CONFLICT` | keine |
| R5 | `A_RECENT_ABSENT_VALID` | `B_STABLE_ABSENT_VALID` | `ABSTAIN_NO_CONTEXT` | keine |
| R6 | `A_RECENT_NOT_APPLICABLE` | `B_STABLE_ABSENT_VALID` | `ABSTAIN_NO_APPLICABLE_CONTEXT` | keine |

Damit sind unter real erzeugten 336-Werte-Memoryzustaenden alle sechs
vorab gebundenen Zustaende entstanden: nutzbares A, nutzbares B,
oeffentliche Mehrdeutigkeit, interner A-Konflikt, gueltige Abwesenheit und
sichtbare Unvereinbarkeit.

Jeder Kandidat wurde ueber eine echte Vollprobe, den vorhandenen
S2-JW-read-only-Pfad, die S2-KJ-Wertebindung und die Zwei-Bereich-Projektion
gewonnen. B4 und Fast blieben interne Rollen von `A_RECENT`. Es wurde kein
Kandidatenvektor hinter dem Rezeptor eingesetzt.

## Baseline und Read-only-Grenze

Die unabhaengige Zwei-Bereich-Direktbaseline reproduzierte alle sechs
Entscheidungen und Hypothesenbindungen vollstaendig. Das ist der erwartete
Engineeringbefund und keine besondere MCM-Physik.

Bei allen Vollproben, Kontextprojektionen, maskierten Proben und
Zulassungsentscheidungen blieben die gebundenen Memoryzustandsdigests vor
und nach dem Zugriff identisch. Es erfolgte keine Kontextfuellung und keine
automatische Auswahl bei mehreren Kandidaten.

## Technische Verifikation

- technischer Status: `RECORDING_COMPLETE`;
- Funktionsstatus: `S2KP_FUNCTION_CONFIRMED`;
- Verifikationsprobleme: keine;
- Quellenhashabweichungen nach dem Lauf: `0`;
- Record-Digest:
  `cec6c4c881e8e94116ac5d8f585ca36fd46c24229f7bffef35a6c14446c6ff35`;
- SHA-256 der Ergebnisdatei:
  `dfe691f7da48f4bdc0b8a8340ee2f3c9dad867e528f34071ec00000ac056df82`.

Der maschinenlesbare Laufbeleg liegt unter
`reports/s2kp/s2kp-real-context-admission-336-20260903-01/result.json`.
Die getrennte Verifikationsnotiz liegt unter
`reports/s2kp/s2kp-real-context-admission-336-20260903-01-verification.json`.

## Aussagegrenze

S2-KP bestaetigt die kontrollierte Zwei-Bereich-Zulassung fuer sechs
konkret gebildete 336-Werte-Zustaende. Bestaetigt sind sichere Zulassung bei
genau einem anwendbaren Bereich sowie Enthaltung bei Mehrdeutigkeit,
internem A-Konflikt, Abwesenheit und sichtbarer Unvereinbarkeit.

Nicht bestaetigt sind Kontextfuellung, automatische Maskenerkennung,
Rangfolge, semantische Auswahl, Feldrueckwirkung oder eine allgemeine
Kontextentscheidung ausserhalb dieser gebundenen Geschichten.
