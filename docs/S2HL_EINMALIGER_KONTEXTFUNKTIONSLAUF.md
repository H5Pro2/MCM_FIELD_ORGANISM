# S2-HL: Einmaliger Kontextfunktionslauf

Status: `S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS`

## Laufabschluss

Der Lauf `s2hl-context-function-20260831-01` wurde mit frischem
Ergebnisverzeichnis genau einmal ausgefuehrt. Es gab keinen Retry und keine
Parameter- oder Codeaenderung.

- `run_main_once`: genau ein Aufruf, Exit-Code `0`;
- Aufzeichnung: `139` Operationen und `278` START-/RESULT-Ereignisse;
- terminaler Laufstatus: `COMPLETE`;
- unabhaengige read-only Verifikation: genau ein Aufruf;
- Verifikationsstatus: `RECORDING_COMPLETE`, keine Fehler;
- aufgezeichneter Umfang: `564.399` Byte;
- alle zehn Quellhashes vor und nach dem Lauf identisch;
- versioniertes Hauptgate nach dem Lauf weiterhin `False`.

S2-HC bleibt unveraendert `NOT_EVALUABLE`.

## Funktionsbefunde

| Fall | Ergebnis |
|---|---|
| `CURRENT_PERCEPTION_ONLY` | keine Ergaenzung, `INSUFFICIENT_INFORMATION` |
| korrekter `B_STABLE`-Kontext | exakt neun Maskenwerte ergaenzt, Maskenfehler `0,0` |
| direkte B-Stable-Baseline | zur Kontextfunktion funktional gleichwertig |
| fremder Kontext | neun Werte ergaenzt, Maskenfehler `1,0`; vorab gebundene Grenze beobachtet |
| fehlender Kontext | `CONTEXT_ABSENT`, keine Fuellung |
| sichtbarer Konflikt | `CONTEXT_CONFLICT`, keine Teilfuellung |

In allen vier Auswertungsfaellen blieben die neun sichtbaren Werte erhalten.
Die Probezugriffe veraenderten die gebundenen Speicher- und Bundlezustaende
nicht.

## A-RECENT-Grenze

Die Geschichten enthalten nach der Stabilisierung jeweils neun juengste
Distraktorzustaende. Bei der spaeteren vollstaendigen Zielprobe liefert die
oeffentliche A-Projektion jedoch `A_RECENT = ABSENT_VALID` und
`TSPM_FAST = ABSENT_VALID`, weil keiner dieser Distraktoren zur Zielprobe
passt.

Der Lauf bestaetigt damit, dass die internen juengsten Distraktoren nicht
verdeckt fuer die Vervollstaendigung verwendet werden. Er prueft aber keine
Situation, in der gleichzeitig ein oeffentlich verfuegbarer konkurrierender
`A_RECENT`-Kandidat vorliegt. Diese Grenze wird nicht als bestaetigte
Interferenzrobustheit ausgegeben.

## Einordnung

Ein bereitgestellter stabiler perzeptiver Kontext kann fehlende visuelle Werte
technisch ergaenzen. Die konkrete Funktion wird bei gleichem Kontext und
Budget vollstaendig durch direkte Maskenfuellung erklaert. Das ist ein
brauchbarer Engineeringbefund fuer Kontextverwendung, aber kein
MCM-spezifischer Memory-Mechanismus, keine automatische Kontextauswahl und
keine semantische Verarbeitung.

## Naechster fachlicher Schritt

Vor einer Feldintegration ist nun zu entscheiden, ob die direkte transparente
Maskenfuellung als einfacher Kontextverbraucher genuegt. Eine spaetere
eigenstaendige Untersuchung kann einen tatsaechlich verfuegbaren,
konkurrierenden `A_RECENT`-Kandidaten gegen den ausdruecklich benannten
`B_STABLE`-Kontext stellen. Diese Zusatzfrage ist durch S2-HL nicht
vorweggenommen und benoetigt einen eigenen begrenzten Auftrag.
