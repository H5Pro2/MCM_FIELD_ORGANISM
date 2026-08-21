# S1-TD: Implementierung nullable Rezeptorprovenienz und S1-TG-v2-Einmalpfad

## Ergebnis

S1-TD implementiert ausschliesslich die in S1-TC gebundene
Provenienzkorrektur. Feldmechanik, S/H-Profilachse, Kontraste, Paarmetrik,
Toleranzen und Ergebnisstatus bleiben unveraendert.

## Comparator- und Adaptergrenze

`FourNodeBaselineCheckpointVector.receptor_contact` traegt nun explizit
vier optionale Komponenten. Die Validatoren unterscheiden drei Faelle:

```text
vier endliche Zahlen                         = gueltige R-Provenienz
vier None bei C_GAP / POST_COMPETITION       = gueltige Kontaktabwesenheit
gemischt, nichtendlich oder andere Lage      = ungueltig
```

Boolwerte gelten nicht als Zahlen. S und H verlangen weiterhin jeweils
vier endliche numerische Komponenten und duerfen kein `None` enthalten.

Der passive Adapter prueft fuer das feste reale S1-SS-Artefakt zusaetzlich
die vollstaendige Achse: exakt eine all-null-R-Lage je Modellrolle, also
14 Records in registrierter Modellreihenfolge. Jede weitere, gemischte oder
fehlende nullable Lage stoppt fail-closed.

R bleibt aus allen numerischen Profil-, Kontrast- und Distanzoperationen
ausgeschlossen. Die 320-Komponenten-S/H-Achse wurde nicht veraendert.

## Artefakt und neue Laufidentitaet

Der Parser trennt jetzt numerische Vierervektoren von nullable
Rezeptorprovenienz. Vollstaendige R-Abwesenheit wird als vier JSON-`null`
kanonisch erhalten. Der Resultatvalidator prueft die Profilprovenienz vor
Kontrast- und Paarvalidierung erneut.

Gebundene v2-Identitaet:

```text
schema_id       = mcm.s1tc.baseline-reference-atlas-artifact.v2
source_contract = S1-TC
execution_id    = mcm.s1tg.baseline-reference-atlas.once.v2
authorization   = S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2
```

Der Einmalrunner verwendet nur die neuen S1-TG-v2-Pfade. Vorhandene
S1-TB-Belege werden nicht gelesen, veraendert oder als neuer Laufpfad
behandelt.

## Angepasster synthetischer Testkatalog

Der bestehende Katalog bleibt auf genau 20 Testmethoden begrenzt. Neu oder
gezielt angepasst sind insbesondere:

- vollstaendig numerisches R bleibt gueltig;
- gebundenes all-null R erzeugt einen computable synthetischen Atlas;
- JSON-`null` bleibt im kanonischen Roundtrip erhalten;
- gemischtes R wird abgewiesen;
- all-null R an anderer Lage wird abgewiesen;
- `None` in S oder H wird abgewiesen;
- all-null R und explizites Null-R zwischen Modellen sind nicht
  provenienzaequivalent;
- erhaltene S1-TB-Belege blockieren die getrennten S1-TG-Pfade nicht;
- neue Schema-, Autorisierungs- und Pfadidentitaet gilt.

Weiterhin enthalten sind Einmalschutz, genau ein synthetisch ersetzter
Comparatoraufruf, gestarteter Fehlerbeleg, Quell- und Eingabedrift,
Hardlinkfehler, CLI-Grenze und fehlende direkte Modellproducerimporte.

Die 20 Tests wurden in S1-TD nicht ausgefuehrt. Statisch geprueft wurden
nur Python-Syntax, AST-Testanzahl, Comparator-Aufrufstelle,
Diffsauberkeit und Laufpfade.

## Unveraenderte Altbelege und freie Neupfade

```text
S1-TB attempt sha256
  e746f02cb0cfaa219a59ae2a1d7a8768925a52710ba0316aacd8bddd7eb795e5
S1-TB lock sha256
  42a66cbd8e32bfba04655617cb56f53220029f155a7b320c57239261b409600e

S1-TG result  = absent
S1-TG attempt = absent
S1-TG lock    = absent
S1-TG staging = absent
```

## Methodische Grenze

Mini-DIO und Biocomputing begruenden durch diese Korrektur keine neue
Mechanik. Der relevante Schnittstellenabgleich ist bereits erfuellt:
Kontaktabwesenheit und gemessener Nullkontakt bleiben getrennt. Es entsteht
kein Feld-, Memory- oder Funktionsbefund.

## Entscheidung und naechster Schritt

```text
NULLABLE_RECEPTOR_PROVENANCE_AND_V2_ONE_SHOT_PATH_IMPLEMENTED
S_H_PROFILE_METRICS_UNCHANGED
TWENTY_SYNTHETIC_TESTS_ADAPTED_NOT_EXECUTED
S1_TB_BELEGE_PRESERVED_NO_REAL_COMPARATOR
```

Der einzige naechste Schritt ist S1-TE: genau ein unveraenderter Lauf nur
der 20 synthetischen Tests aus
`tests/test_four_node_baseline_reference_artifact_and_single_run.py`.
Kein anderer Test, kein reales S1-SS-Comparing und kein Modellproducer sind
dabei zulaessig.
