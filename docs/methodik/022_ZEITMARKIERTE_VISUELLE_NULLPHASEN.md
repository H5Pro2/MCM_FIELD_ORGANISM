# Methodik 022: Zeitmarkierte visuelle Nullphasen

## 1. Forschungsfrage

Kann eine bereits vorhandene lokale Feldgröße reale Phasen von äußerer Ruhe,
kontrollierter Veränderung und erneuter Ruhe unterschiedlich tragen, wenn die
Phasen ausschließlich durch die gemessene Organismusuhr markiert werden?

Der Versuch prüft noch keine Bewegungserkennung und keine Persistenz.

## 2. Unveränderte Feldkette

```text
endlicher Kameraadapter
-> lokales visuelles Rezeptorraster
-> visuelle MCM-Neuronenschicht
-> Rezeptorprojektions-Baseline
-> passive lokale Feldbeobachtung
```

Es werden keine Frames, Bilder, Objekte oder Merkmale gespeichert. Die
Phasenhülle ist ein äußerer Observer und schreibt nicht in die Feldkette
zurück.

## 3. Äußere Phasenmarken

Die vorregistrierte Reihenfolge lautet:

```text
Ruhe 1 -> kontrollierte Veränderung -> Ruhe 2
```

`Ruhe` und `Veränderung` sind ausschließlich Bezeichnungen des menschlich
kontrollierten Versuchsablaufs. Sie sind keine erkannte Feldbedeutung und kein
Trainingslabel.

Jede Phase besitzt auf derselben monotonen Organismusuhr einen gemessenen
Beginn und ein gemessenes Ende. Ein Frame darf nur ausgewertet werden, wenn
sein vollständiges Leseintervall innerhalb genau einer Phase liegt.

Ein Frame, dessen Leseintervall eine Phasengrenze überschreitet, bleibt als
Grenzframe sichtbar, wird aber keiner Phase zugerechnet.

Der erste Wahrnehmungsframe folgt technisch auf den leeren Startzustand der
Neuronenschicht. Er bleibt als Initialisierungsframe sichtbar, geht aber nicht
in die Änderungsmittelwerte ein. Andernfalls würde Feldaufbau fälschlich als
Veränderung der ersten Ruhephase gezählt.

## 4. Zulässige Beobachtungsgrößen

Es werden nur bereits vorhandene lokale Eingänge zusammengefasst:

1. mittlere absolute Änderung zwischen aktuellem Rezeptorkontakt und eigener
   Aktivierung des vorherigen Takts;
2. mittlere absolute Aktivierungsdifferenz zu lokal benachbarten Neuronen aus
   dem vollständig abgeschlossenen vorherigen Takt.

Die Mittelwerte sind äußere Forschungsmaße. Sie sind weder Schwellen noch
Bewegungswerte und werden nicht in die Runtime zurückgegeben.

## 5. Nullkontrollen

- Zeitmarken und Feldlauf müssen dieselbe Uhridentität verwenden.
- Phasen müssen lückenlos und nicht überlappend sein.
- Grenzframes dürfen nicht nachträglich einer Phase zugeschlagen werden.
- Der Initialisierungsframe darf nicht als natürliche Änderung gelten.
- Der Observer darf weder Frames halten noch Feldzustände verändern.
- Eine synthetische Wiederholung muss die Zuordnung exakt reproduzieren.
- Der reale Lauf darf nur interpretiert werden, wenn jede Phase vollständig
  durch zugeordnete Frames vertreten ist.

## 6. Entscheidung

Ein Unterschied zwischen den äußeren Phasen ist nur ein Kandidat für eine
bereits vorhandene visuelle Feldreaktion. Er ist noch keine Invarianz, keine
Bewegungswahrnehmung, keine Beziehung und kein Memory.

Bleiben die vorhandenen Größen auch unter sauberer Zeitmarkierung gesättigt
oder überlappen die drei Phasen vollständig, ist der aktuelle visuelle
Feldzustand für diese Funktion nicht ausreichend.

Auch dieser Negativbefund erlaubt nicht automatisch:

- eine Rauschschwelle,
- Normalisierung oder Hintergrundsubtraktion,
- Glättung,
- Bewegungsklassen,
- visuelles Memory,
- Objekt- oder Syntaxbildung.

## 7. Evidenzgrenze

```text
Phasenhülle:                 passiver Methodenkandidat
Feldmechanik:                unverändert
Runtime-Rückwirkung:         keine
maximales Evidenzziel:       E2
Persistenzfreigabe:          keine
```

## 8. Bester nächster Schritt

Nach erfolgreicher synthetischer Nullkontrolle folgt genau ein endlicher realer
Lauf mit vorab festgelegter Phasendauer. Erst dessen gemessene Phasenabdeckung
entscheidet, ob die vorhandenen lokalen Feldgrößen vergleichbar sind.
