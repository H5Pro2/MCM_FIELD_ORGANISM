# S1-AY: Aktuelle Primaerquellen-Vorpruefung

## Status

Statische, begrenzte Quellenpruefung gegen S1-AW. Kein Substratkandidat,
keine Gleichung, keine Runtime, kein Test und keine Implementierungsfreigabe.

## Forschungsfrage

Gibt es in aktuellen Primaerquellen ein bereits beobachtetes Naturprinzip,
das gleichzeitig

1. durch lokale Teilnahme an einer Wechselwirkung veraendert wird,
2. eine endliche oder umverteilbare Ressource besitzt,
3. spaetere Wechselwirkung aus derselben Veraenderung beeinflusst,
4. im Nullkontakt eine pruefbare Eigenprognose liefert und
5. sich von leaky, P0, F3, CONST-V sowie einer bloss reversiblen
   Materialantwort unterscheidet?

Die Quellen werden nur als Mechanismusbelege gelesen. Begriffe wie Lernen,
Training oder Memory in einer Quelle gelten nicht als MCM-Nachweis.

## A: Lokaler epithelialer Spannungsumbau

Die Arbeit beschreibt ein aktives Vertexmodell, in dem lokale
mechanosensitive Spannungsanpassung die Gewebeelastizitaet veraendert. Die
langsame Spannungsvariable traegt Deformationsgeschichte und kann nach
zyklischer Belastung die globale mechanische Antwort veraendern.

S1-AW-Pruefung:

```text
eigene lokale Ursache:        teilweise vorhanden (lokale Dehnung)
endliche Ressource/Bilanz:    nicht ausgewiesen
konjugierte Rueckwirkung:     mechanisch vorhanden, aber modelliert
Gegenprognose:                nicht gegen adaptive Spannung/Gain getrennt
Nullkontakt/Freigabe:         keine ausreichende Ressourcenprognose
```

Urteil: Kein Kandidat. Die gesuchte Veraenderung wird durch eine entworfene
Anpassungsregel getragen. Ohne lokale endliche Bilanz bleibt sie eine
adaptive Material- oder Gain-Baseline.

Quelle: [Learning Epithelial Elasticity via Local Tension Remodeling](https://pubmed.ncbi.nlm.nih.gov/41446078/).

## B: Konstruktiver mechanochemischer Polymerumbau

Bei mechanisch belasteten Polymeren koennen Kettenbrueche reaktive
Zwischenprodukte erzeugen, aus denen neue Rueckgratbindungen entstehen. Das
liefert eine reale lokale Ursache, eine chemisch begrenzte Rolle und eine
Rueckwirkung auf spaetere mechanische Belastbarkeit.

S1-AW-Pruefung:

```text
eigene lokale Ursache:        vorhanden (Bruch und Radikalbildung)
endliche Ressource/Bilanz:    chemisch plausibel
konjugierte Rueckwirkung:     mechanisch plausibel
Gegenprognose:                konstruktiv gegen rein degradativ vorhanden
MCM-Uebertragung:             nicht hergeleitet
Freigabe/Wiederverwendung:    fuer das MCM-Substrat nicht bestimmt
```

Urteil: Kein neuer Kandidat. Diese Familie wurde bereits in W5-D geprueft.
Eine Uebertragung auf lokale MCM-Feldkopplung, spaetere konjugierte
Feldrueckwirkung und wiederverwendbare verteilte Kapazitaet wuerde die
fehlende Physik erfinden. S1-AY oeffnet W5-D daher nicht erneut.

Quelle: [The molecular mechanism of constructive remodeling of a mechanically-loaded polymer](https://www.nature.com/articles/s41467-022-30947-8).

## C: Belastungsinduzierte Phasentrennung in Hydrogelen

Die Arbeit beschreibt belastungsinduzierte makroskopische Phasentrennung,
reversible Ionenbindungs-Dissoziation und -Reassoziation sowie gerichtete
Energiedissipation. Damit existiert eine reale lokale Materialantwort mit
begrenzten Bindungs- und Domaenenrollen.

S1-AW-Pruefung:

```text
eigene lokale Ursache:        vorhanden (Dehnung/Spannung)
endliche Ressource/Bilanz:    Bindungen und Domaenen vorhanden
konjugierte Rueckwirkung:     aktuelle Mechanik wird veraendert
Nullkontakt-Praegung:         nicht ausreichend belegt
Gegenprognose:                nicht von reversibler Phase/Viscoelastik getrennt
```

Urteil: Kein Kandidat. Der berichtete Mechanismus erklaert adaptive
Belastungsantwort und Dissipation, aber keine eigenstaendige, spaeter
rekonstruierbare lokale Konfiguration nach kontrolliertem Nullkontakt.

Quelle: [Mechanically adaptive crack-resistant hydrogels based on strain-induced macroscopic phase separation and hierarchical energy dissipation](https://www.nature.com/articles/s41467-026-74084-y).

## Ergebnis

```text
gepruefte Mechanismusfamilien: 3
S1-AW-konforme Kandidaten:     0
neue Gleichungsfreigaben:      0
Wiederaufnahme von W5-D:       nein
```

Die Suche nach einem Substratkandidaten durch weitere offensichtliche
Materialanalogien ist an diesem Punkt nicht begruendet fortsetzbar. Das ist
kein Unmoeglichkeitsbeweis fuer MCM-Memory. Es ist ein negativer
Auswahlbefund: Keine gepruefte Quelle liefert die vollstaendige lokale
Ursache, Bilanz, MCM-Rueckwirkung, Gegenbaseline und Loeseprognose.

## Richtungsentscheid

**STOPP:** Die Substratlinie darf aus S1-AY weder eine neue Gleichung noch
eine Implementierung ableiten. Ein Neustart benoetigt eine eigenstaendig
formulierte Naturannahme, die vor einer Analogie alle sieben Punkte aus
S1-AW besteht.

Die kontrollierte AV-Feld-Engineeringlinie bleibt aktiv. Sie darf konkrete
technische Anforderungen an Rezeptorpfade, gemeinsames Feld,
Reproduzierbarkeit und Snapshot/Restore bearbeiten, ohne Memory-,
Organisations-, Semantik- oder KI-Claim.

