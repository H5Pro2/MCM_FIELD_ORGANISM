# Vergleich notwendiger Organismusfunktionen

## Status

```text
Weg B konzeptionell geprüft:              ja
biologische Mechanik übernommen:          nein
notwendige digitale Erhaltungsfunktion:   nicht gefunden
Zustands- oder Variablenkandidat gewählt: nein
Runtime-Erweiterung:                      gesperrt
organisches Memory:                       gesperrt
```

Dieser Vergleich folgt aus dem
[darstellungsoffenen Erhaltungsfunktionsvertrag](089_DARSTELLUNGSOFFENER_ERHALTUNGSFUNKTIONSVERTRAG.md).
Er sucht keine Speicherform und keine Variable. Er prüft, welche unabhängig
begründeten Funktionen einen Organismusprozess tragen könnten und ob eine
davon in der bestehenden Architektur bereits notwendig ist.

## Methodische Abgrenzung

Biologische Begriffe werden nicht als Bauanleitung verwendet. Ein Stoffwechsel,
eine Zellmembran, Homöostase oder neuronale Ermüdung dürfen nicht allein wegen
ihrer biologischen Rolle digital nachgebildet werden.

Eine übertragbare Funktion müsste:

1. auch ohne Memory-Ziel notwendig sein;
2. aus dem bestehenden System-Welt-Verhältnis folgen;
3. einen observerunabhängigen möglichen Verlust besitzen;
4. durch eigene Weltteilnahme beansprucht oder erhalten werden;
5. die weitere Feldfähigkeit kausal verändern;
6. ohne vorgegebenes Überlebensziel, Reward oder Sollintervall auskommen.

## Externe Funktionsrahmen

### Organisatorische Selbstaufrechterhaltung

Theorien biologischer Autonomie beschreiben lebende Organisation nicht nur
als stabilen Zustand. Entscheidend ist die wechselseitige Abhängigkeit von
Prozessen oder Einschränkungen, die zur Erhaltung anderer Bedingungen
beitragen und selbst durch das System erhalten werden.

Die abstrakte Funktion lautet:

```text
eigene Prozesse ermöglichen die Bedingungen ihrer weiteren Wirksamkeit
und hängen zugleich von diesen Bedingungen ab
```

Diese Funktion ist unabhängig von Memory sinnvoll. Im aktuellen MCM-System
ist sie jedoch nicht vorhanden:

- Feldanatomie und Docks werden nicht durch Feldprozesse erzeugt;
- Feldparameter werden nicht durch Feldprozesse erhalten;
- Rezeptoraufnahme erhält keine Bedingung ihrer eigenen Fortsetzung;
- kein Bestandteil der Runtime ist durch den Feldprozess selbst gefährdet.

Eine digitale Selbstproduktion jetzt einzuführen würde die gewünschte
Organismusrolle programmieren, nicht entdecken.

### Regulation eigener Existenzbedingungen

Adaptivität wird in organismischen Ansätzen als Regulation gegenüber den
eigenen Bedingungen der Lebensfähigkeit gefasst. Der wichtige Punkt ist nicht
ein vorgegebener Optimalwert, sondern dass Abweichungen für das System selbst
Folgen besitzen.

Diese Funktion setzt jedoch bereits voraus:

- einen eigenständigen Organismusprozess;
- eine nicht vom Observer gewählte Erhaltungsbedingung;
- reale Folgen ihrer Verletzung;
- eine Möglichkeit eigener Gegenwirkung.

Das MCM-Feld besitzt keine solchen Bedingungen. Ein nachträglich gewählter
Aktivitätsbereich, Kapazitätswert oder Stabilitätsscore wäre eine externe Norm.
Die Regulation würde genau das voraussetzen, was sie begründen soll.

### Eigenständige Weltbeteiligung

Arbeiten zur Agency unterscheiden passive Reaktion von einem System, das
selbst Quelle von Aktivität in seiner Umwelt ist und diese Aktivität in Bezug
auf eigene Bedingungen reguliert.

Die bestehende Architektur trägt reale Audio- und Videowahrnehmung, aber keine
autonome Weltwirkung. Die vorhandene simulierte Effektorwelt:

- trennt externe und als Effektor bezeichnete Interventionen;
- prüft Weltfolge und Rezeptorrückkehr;
- schreibt nicht in das MCM-Feld;
- wählt keine Handlung aus dem Feld;
- beansprucht ausdrücklich keine Autonomie.

Eigenständige Weltwirkung ist deshalb eine reale offene Architekturgrenze.
Sie ist aber allein keine Erhaltungsfunktion. Ohne eigene gefährdete
Organisationsbedingung wäre ein geschlossener Sensor-Effektor-Kreis nur ein
technischer Regelkreis mit extern gesetztem Zweck.

### Stabilität und Homöostase

Stabilitäts- und ultrastabile Modelle zeigen, wie ausgewählte wesentliche
Größen trotz Störungen in einem zulässigen Bereich gehalten werden können.

Für das Projekt liefern sie eine wichtige Gegenprüfung: Sobald der Forscher
die wesentliche Größe, ihren zulässigen Bereich und die Korrekturrichtung
festlegt, entsteht ein programmiertes Erhaltungsziel.

Ohne bereits unabhängig begründete Organismusfunktion sind daher nicht
zulässig:

- Aktivierung innerhalb eines Sollbereichs halten;
- Last automatisch ausgleichen;
- Ruhe als Erholung definieren;
- bei Grenzverletzung Parameter umstellen;
- Erfolg als Rückkehr in einen festgelegten Bereich werten.

## Funktionsvergleich

| Funktionsfamilie | ohne Memory sinnvoll | in organismischen Theorien eigenständig begründet | im heutigen MCM intrinsisch notwendig | derzeit übertragbar |
|---|---:|---:|---:|---:|
| wechselseitige Selbstaufrechterhaltung | ja | als Rahmen ja | nein | nein |
| Regulation eigener Existenzbedingungen | ja | als Rahmen ja | nein, Bedingungen fehlen | nein |
| eigenständige Weltbeteiligung | ja | als Rahmen ja | nein, Effektorpfad fehlt | nur als offene Grenze |
| Stabilisierung vorgegebener Größen | technisch ja | bedingt | nein | nein |

Keine Familie begründet derzeit eine digitale Zustandsgröße.

## Der entscheidende Kausalpfad

Für einen späteren Organismusprozess müsste ohne Memory-Ziel gelten:

```text
notwendige eigene Organismusfunktion
-> reale weltbezogene Beanspruchung
-> beeinträchtigte zukünftige Feldfähigkeit
-> eigene weltbezogene Erhaltung oder Erneuerung
-> erneut wirksame Feldteilnahme
```

Im heutigen System bricht diese Kette bereits am ersten Übergang ab. Es gibt
keine eigene dynamische Organismusfunktion, deren Verlust die Feldmechanik
gefährdet.

## Stärkster Gegenbefund

Das gemeinsame Feld kann beliebig viele technisch zulässige Schritte
fortgesetzt werden, solange Rechner, Prozess, feste Konfiguration und
Rezeptorquellen von außen verfügbar bleiben.

Der Feldprozess:

- stellt seine Anatomie nicht her;
- erhält seine Docks nicht;
- erzeugt seine Zeitbasis nicht;
- erhält seine Sensorquellen nicht;
- erzeugt keine Weltwirkung, von der seine weitere Wahrnehmung abhängt;
- verliert bei neutralem Schnellzustand keine spätere Aufnahmefähigkeit.

Damit ist seine Fortsetzung technisch ermöglicht, aber nicht durch eine eigene
Organisationsleistung getragen.

## Ergebnis

```text
gemeinsames Wahrnehmungsfeld:              vorhanden
technisch fortsetzbare Feldmechanik:       vorhanden
eigene Weltwirkung:                        nicht vorhanden
eigene gefährdete Organisationsbedingung: nicht vorhanden
eigene Erhaltungsleistung:                 nicht vorhanden
Organismusprozess im gewünschten Sinn:     nicht begründet
```

Weg B liefert damit keinen zulässigen Kandidaten. Er zeigt stattdessen die
präzise Grenze:

> Das MCM-Feld nimmt an einer Welt wahrnehmend teil, trägt aber die Bedingungen
> seiner eigenen weiteren Teilnahme nicht selbst mit.

Organisches Memory bleibt geschlossen. Nicht Memory ist gescheitert, sondern
die Annahme, aus der bestehenden passiven Feldmechanik bereits eine
organismische Erhaltungsfunktion ableiten zu können.

## Keine direkte Übernahme biologischer Mechanik

Aus dem Vergleich folgen ausdrücklich nicht:

- digitaler Stoffwechsel;
- künstliche Energie oder Nahrung;
- Lebenspunkte oder Überlebensscore;
- Zellgrenze oder digitale Membran;
- Homöostasevariable;
- Aktivitäts-Sollbereich;
- Ermüdung und Regeneration;
- autonomer Effektor;
- Reward, Selbsterhaltungsziel oder Todesbedingung.

Jede dieser Festlegungen wäre ein neuer Kandidat und benötigt eine eigene,
vom gewünschten Ergebnis unabhängige Begründung.

## Quellen und Aussagegrenze

- Montévil und Mossio beschreiben biologische Organisation als wechselseitige
  Abhängigkeit erhaltener Einschränkungen in offenen Prozessen:
  [Biological organisation as closure of constraints](https://doi.org/10.1016/j.jtbi.2015.02.029).
- Di Paolo unterscheidet bloße Selbsterhaltung von Adaptivität als Regulation
  gegenüber eigenen Lebensfähigkeitsbedingungen:
  [Autopoiesis, adaptivity, teleology, agency](https://doi.org/10.1007/s11097-005-9002-y).
- Barandiaran, Di Paolo und Rohde benennen Individualität, eigenständige
  Umweltaktivität und Normativität als gemeinsame Bedingungen von Agency:
  [Defining Agency](https://doi.org/10.1177/1059712309343819).
- Froese und Ziemke grenzen für enaktive künstliche Systeme konstitutive
  Autonomie und Adaptivität als getrennte Anforderungen ab:
  [Enactive artificial intelligence](https://doi.org/10.1016/j.artint.2008.12.001).
- Ashbys Stabilitätsrahmen dient hier nur als Gegenprüfung gegen extern
  festgelegte wesentliche Variablen und Sollbereiche:
  [Design for a Brain](https://doi.org/10.1007/978-94-015-1320-3).

Diese Quellen begründen Funktionsunterschiede in organismischen Theorien. Sie
belegen weder einen digitalen MCM-Organismus noch die Übertragbarkeit einer
konkreten Mechanik.

## Stopplinie

Weg B wird als unmittelbarer Implementierungsweg geschlossen. Es wird kein
Organismuszustand erfunden, nur um die offene Erhaltungsfunktion zu besetzen.

## Wie es am besten weitergeht

Vor weiterer Entwicklung ist eine Architekturentscheidung nötig:

1. Das Projekt bleibt vorläufig ein gemeinsames Wahrnehmungsfeld und erforscht
   dessen reale Feldreaktionen ohne Organismus- oder Memory-Anspruch.
2. Das Projekt öffnet später einen getrennten Grundlagenzweig zur Frage, ob
   ein digitaler Prozess die Bedingungen seiner eigenen Weltteilnahme
   tatsächlich mit hervorbringen und erhalten kann.

Für das langfristige Ziel ist der zweite Weg relevant. Er darf aber nicht als
Fortsetzung der heutigen Memory-Mechanik behandelt werden und beginnt ohne
Zustandsvariable, Effektorfreigabe oder Organismuslabel.
