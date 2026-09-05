# S2-MQ: Vorversiegelter Bewegungskorrespondenz-Korpusvergleich

Status: verbindlicher, ergebnisoffener Funktionsvertrag  
Datum: 2026-09-05

## 1. Frage und Aussagegrenze

S2-MQ prueft, ob die in S2-MP qualifizierte bildgetriebene Sparse-LK-Korrespondenz auf einem neuen, vor jeder Pixelanalyse versiegelten Korpus Fortsetzung, Formwechsel, Teilverdeckung und Szenensprung besser unterscheidet als statische Bild-, Pose- und Formvergleiche.

Die Ausgabe ist Bewegungskorrespondenzevidenz. Sie behauptet weder Objektidentitaet noch eine semantische Klasse. Memory, Kontext und Feld sind ausgeschlossen.

## 2. Unveraenderte Messung

Der Lauf verwendet `tools._s2mp_private_feature_sparse_correspondence.measure_sparse_pair` ohne Parameter- oder Quellaenderung. Gebunden bleiben:

- Shi-Tomasi-Punkte aus dem ersten Bild auf einem `12 x 8`-Raster;
- hoechstens 16 Punkte je Zelle und 1.536 Punkte insgesamt;
- unveraenderter Sparse PyrLK-Vorwaerts-/Rueckwaertspfad;
- ausschliessliche Interpretation gueltiger, nach Gitterindex geordneter Tracks;
- `MOTION_EVIDENCE_AVAILABLE` ab 32 gueltigen Tracks in mindestens vier Zellen;
- `INSUFFICIENT_MOTION_EVIDENCE` als regulaerer Wahrnehmungsbefund.

Es gibt keine neue Matchschwelle, Parametersuche, Toleranz oder nachtraegliche Korpuskorrektur.

## 3. Korpus und Vorversiegelung

Der Korpus enthaelt exakt acht neue Paare und 16 kanonische `1920 x 1080 RGB8`-Frames:

| neutraler Paarbeleg | Evaluationsrolle | Strukturstratum |
| --- | --- | --- |
| `s2mq-pair-001` | `CONTINUATION` | `STRUCTURE_RICH` |
| `s2mq-pair-002` | `CONTINUATION` | `EDGE_POOR` |
| `s2mq-pair-003` | `FORM_CHANGE` | `STRUCTURE_RICH` |
| `s2mq-pair-004` | `FORM_CHANGE` | `EDGE_POOR` |
| `s2mq-pair-005` | `PARTIAL_OCCLUSION` | `STRUCTURE_RICH` |
| `s2mq-pair-006` | `PARTIAL_OCCLUSION` | `EDGE_POOR` |
| `s2mq-pair-007` | `SCENE_CUT` | `STRUCTURE_RICH` |
| `s2mq-pair-008` | `SCENE_CUT` | `EDGE_POOR` |

Vor dem ersten Rezeptor-, Pose-, Form-, Shi-Tomasi- oder LK-Aufruf werden getrennt und atomar erzeugt:

1. eine Quellenwurzel mit literalem Rendererplan und allen 16 Payloaddigests;
2. eine rollenfreie Ausfuehrungswurzel mit acht neutralen Paaren, Zeitfenstern und S2-MP-Bindung;
3. eine Evaluationswurzel mit den oben genannten Rollen und Strata;
4. ein Vorversiegelungsbeleg, der die drei Wurzeln, Vertrags- und Quellcodehash bindet.

Die Ausfuehrungswurzel enthaelt keine Evaluationsrolle. Die Evaluationswurzel wird erst nach abgeschlossener Messung geoeffnet. Frames werden je Paar erzeugt, digestgeprueft, ausgewertet und anschliessend verworfen. Rohframes und Trackarrays erscheinen in keinem Ergebnisbeleg.

## 4. Messwerte

Je Paar werden separat gebunden:

- Kandidaten- und gueltige Trackzahl;
- Kandidaten- und gueltige Zellabdeckung;
- S2-MP-Evidenzstatus;
- Bewegungszusammenfassung;
- Zyklusresiduum;
- bewegungskompensiertes RGB-Residuum;
- direkte mittlere RGB8-Frame-Differenz;
- mittlere 288-Rezeptor-L1-Differenz;
- alle 16 kanonischen Pose-Komponentendifferenzen;
- mittlere Pose-Komponentendifferenz als reine Vergleichszusammenfassung;
- mittlere Formdeskriptor-L1-Differenz;
- Vor-/Nach-Digests beider Eingabeframes.

Die statischen Baselines erhalten exakt dieselben zwei Frames wie S2-MP und verwenden keine Evaluationsrolle.

## 5. Vorab gebundener ordinaler Vergleich

Pro Strukturstratum werden fuer jede verfuegbare Metrik drei Beziehungen ausgewertet:

1. `CONTINUATION < FORM_CHANGE`;
2. `CONTINUATION < SCENE_CUT`;
3. `CONTINUATION < PARTIAL_OCCLUSION`.

Fuer S2-MP werden Zyklusmittel und RGB-Residuenmittel getrennt bewertet. Fuer die statischen Baselines werden direkte Frame-Differenz, Pose-Zusammenfassung und Formdeskriptor getrennt bewertet. Gleichheit erfuellt keine strikte Beziehung.

Ist ein beteiligtes Paar `INSUFFICIENT_MOTION_EVIDENCE`, lautet die betroffene zeitliche Beziehung `INSUFFICIENT_EVIDENCE`; sie wird weder als technischer Fehler noch als bestandene Beziehung gezaehlt. Die Baselines bleiben trotzdem auswertbar.

`S2MQ_TEMPORAL_ADDITIONAL_VALUE_OBSERVED` ist nur zulaessig, wenn:

- alle acht Paare `MOTION_EVIDENCE_AVAILABLE` liefern;
- sowohl Zyklus- als auch RGB-Residuum in beiden Strata jeweils alle drei Beziehungen erfuellen;
- die normierte gemeinsame S2-MP-Erfuellungsrate strikt ueber jeder einzelnen statischen Baseline liegt.

Andernfalls lautet der fachliche Abschluss entweder `S2MQ_MIXED_OR_NO_TEMPORAL_ADVANTAGE` oder, falls kein Paar verwertbare Bewegungsevidenz liefert, `S2MQ_INSUFFICIENT_MOTION_EVIDENCE`. Negative und gemischte Abschluesse sind regulaere Funktionsbefunde.

## 6. Technischer Abschluss

`NOT_EVALUABLE` ist ausschliesslich fuer Quellen-, Zeit-, Form-, Digest-, Laufzeit-, Ressourcen- oder Ausfuehrungsfehler zulaessig. Ein gueltiger Lauf erzeugt genau einen atomaren Ergebnisbeleg und wird danach genau einmal read-only verifiziert.

Der Lauf darf weder Objektidentitaet noch Memory-, Kontext- oder Feldwirkung behaupten. Ein positiver Zusatznutzen wuerde lediglich begruenden, die Korrespondenzevidenz spaeter am Rezeptor-/Formationuebergang zu untersuchen.
