# Passivität, Feldarbeit und Ende der Substratherleitung

## Status

Abschließender Architekturaudit auf `E2 / NEGATIVE_BOUNDARY`.

```text
passive Bilanz des vorhandenen Feldes:       bestätigt
physische Energie des Modells:               nicht definiert
Materialzustand aus Passivität ableitbar:     nein
Substratkandidat ausgewählt:                 nein
Runtime-Erweiterung:                          gesperrt
```

Der Audit wertet den
[Passivitäts-Nullbefund](../forschung/010_PASSIVITAET_DES_BESTEHENDEN_FELDES_NULLBEFUND.md)
aus und schließt die in Architektur 068 gesetzte letzte Prüffrage.

## Systemtheoretische Passivität

Passivität beziehungsweise Dissipativität wird nicht allein durch das Wort
„Energie“ bestimmt. Benötigt werden mindestens:

- ein Systemzustand;
- eine nichtnegative Speicherfunktion `S`;
- eine definierte Zufuhrrate `w`;
- eine Dissipationsungleichung.

Sinngemäß:

```text
S(t2) - S(t1) <= Integral w(t) dt
```

Die Speicherfunktion muss nicht die physische Energie eines realen Materials
sein. Sie kann eine mathematische Funktion des vorhandenen Zustands sein.

## Das MCM-Feld erfüllt bereits eine solche Bilanz

Für die vorhandene Aktivierung genügt:

```text
S(x) = 1/2 * x^T x
```

Die symmetrische positive Diffusion erzeugt nichtnegative
Nachbardissipation. Aktiver Rezeptorkontakt lässt sich als Zufuhr plus lokale
Randdissipation zerlegen.

Der passive Observer bestätigt für kontaktfreie und kontaktgetriebene Lage:

```text
dS/dt = Zufuhr - Dissipation
Bilanzfehler = 0
```

Damit ist Passivität bereits mit dem heutigen schnellen Feld vereinbar.

## Warum daraus kein Memory folgt

Die Bilanz liest ausschließlich:

```text
activation
+ feste Anatomie
+ feste Reaktionszeit
+ aktuellen Rezeptorkontakt
```

Sie benötigt keinen zusätzlichen Zustand. Sie bleibt nach Angleichung der
schnellen Feldlage ebenfalls angeglichen.

Damit gilt:

```text
Passivität vorhanden
und zugleich
kein geschichtlich fortwirkender Materialzustand vorhanden
```

Passivität ist deshalb keine hinreichende Herleitung von Memory.

## Passive Systeme können dennoch Memory besitzen

Die Gegenrichtung ist ebenfalls wichtig. Ein passives System darf innere
Zustände, Hysterese oder geschichtsabhängige Kennlinien besitzen.

Beispiele wie memristive oder Duhem-hysteretische Modelle zeigen, dass
Passivität und Memory vereinbar sind. Sie benötigen dafür jedoch eine
konkrete konstitutive Beziehung, interne Zustandsdynamik oder Hysteresefunktion.

Diese Struktur wird nicht durch die allgemeine Passivitätsungleichung
ausgewählt. Passivität prüft ein vorgeschlagenes Materialmodell; sie erzeugt
es nicht.

## Keine physische Feldarbeit im aktuellen Modell

Der vorhandene Diffusionsfluss ist kausal real innerhalb der Simulation. Das
bedeutet nicht, dass er bereits physikalische Arbeit misst.

Es fehlen:

- physikalische Einheiten der Aktivierung;
- ein experimentell begründetes konjugiertes Variablenpaar;
- eine kalibrierte Leistung oder Energiezufuhr;
- ein realer Materialträger;
- eine unabhängige Messung von gespeicherter und dissipierter Energie.

Die quadratische Bilanz darf daher nicht biologisch oder thermodynamisch
überinterpretiert werden.

## Was der Befund dennoch leistet

Die Passivitätsbilanz ist eine sinnvolle spätere Zulassungsbedingung:

- Eine hypothetische Materialrolle darf keine unbegründete Eigenenergie
  erzeugen.
- Ihre Nullstellung muss exakt auf die heutige Bilanz zurückfallen.
- Zugeführte, gespeicherte und dissipierte Anteile müssen explizit getrennt
  werden.
- Ein positiver Memory-Befund darf nicht nur eine umbenannte Speicherfunktion
  sein.

Diese Bedingungen kontrollieren einen Kandidaten. Sie begründen keinen.

## Primäre Vergleichsquellen

- J. C. Willems definiert Dissipativität über Speicherfunktion und
  Zufuhrrate, nicht über eine automatische Memory-Funktion:
  [Dissipative Dynamical Systems Part I](https://doi.org/10.1007/BF00276493)
- L. O. Chua führt den Memristor über eine konkrete konstitutive Beziehung
  zwischen Ladung und Flussverkettung ein:
  [Memristor - The Missing Circuit Element](https://doi.org/10.1109/TCT.1971.1083337)
- B. Jayawardhana, R. Ouyang und V. Andrieu zeigen Passivität für eine
  konkret spezifizierte Klasse von Duhem-Hystereseoperatoren samt
  Speicherfunktionen:
  [Stability of Systems with the Duhem Hysteresis Operator](https://doi.org/10.1016/j.automatica.2012.06.069)

Diese Quellen dienen nur der systemtheoretischen Abgrenzung. Sie belegen kein
MCM-Memory und wählen keinen technischen Kandidaten aus.

## Abschluss der Herleitungskette

Die bisherige Kette hat ausgeschlossen:

- zusätzliche Leaky-Spuren;
- feste Leser und Empfänglichkeiten;
- explizite oder implizite adaptive Kanten;
- Ressourcen- und Gewinnerregeln;
- Attraktor- und Hystereseautomaten;
- bloße räumliche Vervielfachung;
- Reziprozität als Scheinbegründung;
- Passivität als automatische Memory-Quelle.

Übrig bleibt keine aus der heutigen Feldgleichung zwingend folgende
Substratdarstellung.

Das ist ein methodischer Abschluss, kein Beweis der Unmöglichkeit digitalen
organischen Memorys.

## Freigabegrenze

```text
Passivität als Schutzbedingung brauchbar:       ja
Passivität als Memory-Herleitung brauchbar:     nein
physisches Materialmodell vorhanden:            nein
weitere abstrakte Kandidatensuche zulässig:      nein
Zustandsrolle oder Gleichung freigegeben:        nein
Runtime-Erweiterung freigegeben:                nein
```

## Erforderliche Richtungsentscheidung

Es folgt kein automatischer Versuch 011 und keine Architektur 070.

Vor weiterer Substratentwicklung muss zwischen zwei sauberen Wegen entschieden
werden:

### Weg A - Strenge Evidenzlinie

Die heutige Runtime bleibt unverändert. Forschung beobachtet reale Audio- und
Videoweltteilnahme, ohne einen Memory-Zustand zu ergänzen. Ein neuer Kandidat
darf erst aus einem unabhängig entdeckten Funktionsmangel und einer extern
begründeten Materialphysik entstehen.

### Weg B - Explizite Materialhypothese

Es wird bewusst genau ein konkretes passives Materialmodell als Hypothese
gewählt. Seine programmierte Physik, Parameter und Attraktorstruktur werden
offen ausgewiesen. Der Kandidat muss anschließend gegen alle bestehenden
Baselines, Lösung und Wiederprägung geprüft werden.

Weg B wäre keine aus der MCM zwingend entstandene Mechanik, sondern eine klar
deklarierte Forschungsannahme.

## Empfehlung

Die methodisch sauberste Fortsetzung ist zunächst **Weg A**. Das vorhandene
MCM-Feld sollte an längerer realer Weltteilnahme beobachtet werden, während
die Substrat-Runtime geschlossen bleibt. So wird nicht aus Forschungsdruck
eine gewünschte Memory-Physik programmiert.
