# S2-NC: Prospektiver auditiver A-Anwendbarkeitsvergleich

## Ausgangspunkt und neue Gegenfrage

S2-NB ist abgeschlossen. Auf seinen Quellen liefern sowohl 24 als auch
48 Baender fuer jeden Hinweis neun B4- und drei Fast-Treffer. S2-MT Lauf 05
bleibt fachlich falsifiziert. Diese Quellen werden nicht erneut bewertet.

Die bestehende mittlere L1-Regel kann eine grosse Abweichung in wenigen
Baendern durch kleine Abweichungen in anderen Baendern ausgleichen.
S2-NB beweist nicht, dass dies die konkrete Ursache seiner Treffer ist.
Die folgende Gegenregel prueft diese Hypothese auf neuen Quellen.

Frage: Verringert eine komponentenweise Konsistenzanforderung falsche
A-Anwendbarkeit unter Konkurrenz, ohne den Nutzen durch verlorene
bekannte Treffer aufzuheben?

## Genau zwei vorab festgelegte Regeln

Beide Arme erhalten dieselben 24 beobachteten Baender `0..23`, dieselben
real erzeugten Rezeptorwerte und dieselben Kandidaten. Nicht beobachtete
Baender `24..47` bleiben fuer die Anwendbarkeit unzugaenglich.

```text
delta_i = abs(candidate_i - cue_i)
MEAN_L1_24:   statistics.mean(delta_i for i in 0..23) <= 0.2
ALL_BANDS_24: max(delta_i for i in 0..23)             <= 0.2
```

Numerische Praezisierung vor der Korpusauswertung: Die Differenzen werden
als Binary64-Werte gebildet. Der Mittelwertarm verwendet unveraendert die
bereits vor der neutralen Qualifikation gebundene `statistics.mean`-
Arithmetik. Diese wurde gegen eine rationale Referenz qualifiziert.
Sie ist nicht dieselbe Rechenfolge wie das historische `sum(...)/24`:
Zwischenrundungen koennen insbesondere an der inklusiven Grenze zu anderen
Entscheidungen fuehren. `MEAN_L1_24` ist daher keine bitidentische Reproduktion
des bisherigen Produktionspfads. Dieser bleibt unveraendert. Es gibt weder
einen dritten Vergleichsarm noch eine neue Schwelle, Dezimalrundung oder
Toleranz. Quellen, Erwartungen und Erfolgskriterien werden nicht geaendert.
Die historische Versiegelung bindet weiterhin die damalige Dokumentversion;
dieser ausdrueckliche Nachtrag wird separat versioniert, nicht neu versiegelt.

Die Zahl `0.2` wird vor der Auswertung fest uebernommen. Ihre unveraenderte
Schreibweise bedeutet keine unveraenderte Bedeutung: Der zweite Arm setzt
eine Grenze je Band statt fuer den Mittelwert und besitzt damit eine neue,
strengere Akzeptanzgeometrie. Er ist eine experimentelle Regel, keine
bereits qualifizierte Interpretation der bestehenden Fast-Schwelle.

Fuer nichtnegative Differenzen gilt `mean(delta) <= max(delta)`. Deshalb
ist jede Treffermenge von ALL_BANDS_24 eine Teilmenge von MEAN_L1_24.
Das begruendet die Richtung der Intervention, aber keinen Erfolg:
Eine kleinere Treffermenge kann auch den richtigen Kandidaten entfernen
oder einen falschen Kandidaten als einzigen uebrig lassen.

Keine Gewichtung, Rundung, relative Pegelnormierung, Quantilregel,
Schwellenreihe oder nachtraegliche Wahl eines Zwischenwerts.
Alle Vergleiche erfolgen inklusiv mit `<=`, ohne Toleranzzuschlag.

## Vorversiegelung eines neuen kleinen Quelleninventars

Vor Rezeptoranalyse und vor irgendeiner Distanzberechnung muss ein
vollstaendig literales Quelleninventar vorliegen. Es bindet:

- PCM-Rezepte beziehungsweise unveraenderte Aufnahmen, Seeds, Zeitfenster,
  Format und kanonische Payloaddigests;
- Referenz-/Hinweistrennung sowie feste neutrale Eingabeordinalzahlen;
- die beiden Regeln, das unveraenderte 48-Werte-Rezeptorprofil und
  den festen 24-Band-Plan;
- mindestens bekannte exakte Wiederholungen und unabhaengig festgelegte
  Varianten, mehrere konkurrierende Inhalte, unbekannte Hinweise sowie
  informationsarme oder mehrdeutige Hinweise;
- alle Referenzbelegungen vor und nach Entfernung des bekannten Inhalts.

Die Generatoren duerfen keine Rezeptoren, Distanzen, Schwellen oder
Auswertungsrollen importieren. Variationsstaerke, Pegel und Frequenzen
duerfen nicht aus S2-MT/S2-NB-Abstaenden auf erfolgreiche Trennung
zugeschnitten werden. Nach der Versiegelung gibt es keinen Quellenaustausch,
Seedwechsel, Clipping, Nachnormalisieren oder Anpassungsversuch.

Identitaets- und Variantenbeziehungen gelten nur als extern vorgebundene
Evaluationsrelationen. Sie beweisen keine semantische Klangidentitaet.
Der Rechenpfad sieht ausschliesslich Werte, Beobachtungsplan, Zeit- und
Quellenbindungen sowie neutrale Kandidatenindizes.

Das konkrete Inventar ist noch nicht erstellt oder versiegelt. Dieser
Vertrag ist daher noch keine ausfuehrbare Korpusfreigabe.

## Konkurrenz und Enthaltung

Die erste Stufe bleibt ein reiner Rezeptor-/Regelvergleich ohne
Memoryformation. Referenzbelegungen bilden maximal neun B4- und drei
Fast-Pruefpositionen ab; alle Werte stammen aus echten PCM-Analysen.
Solche Belegungen sind kontrollierte Referenzpanels, keine behaupteten
realen Memoryzustaende. Ihre Auswahl ist vor der Analyse festzulegen.

Jedes Panel muss bekannte Kandidaten und konkurrierende Inhalte enthalten;
eine zweite vorgebundene Belegung entfernt die bekannten Kandidaten und
erhaelt die Konkurrenz. Damit werden Annahme unter Konkurrenz und
Enthaltung bei fehlendem Inhalt getrennt gemessen.

Beide Arme pruefen stets saemtliche belegten Positionen. Mehrere Treffer
innerhalb einer Bank bleiben mehrdeutig. B4 und Fast bleiben intern;
die vorhandene A-Aufloesung und ihre vollstaendige 48-Werte-
Kandidatengleichheit werden nicht durch Rangfolge oder Deduplication
ersetzt. Eine reine direkte Entscheidungstabelle dient als Baseline.
Die vollstaendigen Werte duerfen ausschliesslich zur bestehenden internen
Kandidatengleichheitspruefung dienen, nicht zur Cue-Anwendbarkeit.

Es gibt keine Slow-Bevorzugung, keine neue B-Regel, keinen Kontextverbrauch
und keine Hypothesenfuellung. Aus leerer A-Treffermenge folgt hier nur
A-Enthaltung, niemals automatisch ein gueltiger B_STABLE-Abruf.

## Vorab festgelegte Messung und Entscheidung

Je Hinweis, Kandidat und Arm werden alle 24 Differenzen, Mittelwert,
Maximum, Grenzreserve und Trefferstatus dokumentiert. Vollstaendige
indexgeordnete Banktreffermengen und A-Entscheidungen bleiben getrennt
von den nachgelagerten Rollen und Sollrelationen.

Der Auswerter berichtet absolute Fallzahlen und Nenner fuer:

- korrekt eindeutige bekannte Treffer, getrennt nach exakt und variiert;
- Fehlzulassungen, insbesondere nach Entfernung des bekannten Inhalts;
- verlorene bekannte Treffer und verbleibende Mehrdeutigkeiten;
- Enthaltungen bei unbekannten und informationsarmen Hinweisen;
- Faelle mit verbessertem, verschlechtertem und unveraendertem Ergebnis.

Die Diagnosefrage erhaelt nur dann einen positiven Befund, wenn bei
unveraendertem Korpus mindestens eine Fehlzulassung oder bekannte
Mehrdeutigkeit in ein korrektes Ergebnis uebergeht, keine neue
Fehlzulassung entsteht und kein zuvor korrekt eindeutiger bekannter
Treffer verloren geht. Andernfalls wird der Befund als unveraendert,
negativ oder als expliziter Zielkonflikt berichtet. Reines Verwerfen aller
Kandidaten gilt nicht als Verbesserung. Ein Scheitern ist auswertbar.

Technische Quellen-, Zeit-, Typ-, Digest- oder Ressourcenfehler ergeben
`NOT_EVALUABLE`; eine unguenstige Geometrie oder Entscheidung nicht.
Kein Erfolgskriterium ist ein Startgate oder ein Quellenauswahlkriterium.

## Aktuelle Arbeitsgrenze

Nur statischer Vertrag: keine neue Auswertung, Implementierung oder
Korpuserzeugung. Das Quelleninventar samt festen Panels und exaktem
Arbeitsbudget muss vor einer spaeteren einmaligen Materialisierung
versiegelt sein. Eine kleine private Vergleichsfunktion genuegt danach;
neue Runner-/Recorder- oder Memoryinfrastruktur ist nicht erforderlich.

S2-KZ, S2-MR, Memorykerne, Quellen historischer Laeufe und Schwellen bleiben
unveraendert. Selbst ein positiver Referenzpanelvergleich wuerde eine
Produktintegration oder einen realen Memorylauf noch nicht qualifizieren.
