# Kandidatenfamilien für feldgetragene Beziehungswirkung

## Status

Konzeptioneller Familienaudit auf `E0 / NO_CANDIDATE_ADMITTED`.

```text
Funktionsgrenze aus Architektur 061:   übernommen
offensichtliche Kandidatenfamilien:    ausgesiebt
bedingt prüfbare Familie:              lokales hysteretisches Feldmedium
konkreter Kandidat:                    nicht zugelassen
Zustandsrolle oder Gleichung:          nicht gewählt
Runtime-Erweiterung:                   gesperrt
```

Dieser Audit setzt die
[feldgetragene Beziehungswirkungsgrenze](061_FELDGETRAGENE_BEZIEHUNGSWIRKUNGSGRENZE.md)
um und berücksichtigt den früheren
[C2-Familienvergleich](044_KANDIDATENFAMILIEN_UND_C2_BASELINEGRENZE.md)
sowie die
[K6-Vorprüfung](046_K6_VORPRUEFUNG_UND_MEMORY_SUBSTRATFRAGE.md).

Er enthält keine Implementierung und keine Updategleichung.

## 1. Prüffrage

Gesucht wird keine Mechanik, die den L4-Ausgang nachbildet.

Geprüft wird nur:

> Welche allgemeine lokale Substratfamilie könnte aus realer Feldbeanspruchung
> vor jeder Leserfunktion eine Zustandsdifferenz bilden, dieselbe spätere
> Feldtransition kausal mitprägen, funktional vollständig lösbar bleiben und
> danach erneut anders geprägt werden?

Jede Familie muss K1 bis K7 aus Architektur 061 beantworten.

## 2. F1: zusätzliche schnelle oder langsame Nachhallspuren

### Idee

Jeder Feldort erhält weitere Leaky-Zustände mit anderen Zeitkonstanten.

### Prüfung

```text
K1  lokale Aktivierung oder Rezeptorwirkung
K2  zusätzlicher Zustand vorhanden
K3  nur über festen Leser oder additive Modulation
K4  vollständig Leaky-Spur
K5  Lösung nur durch Zeitablauf
K6  erneute Prägung nur erneutes Aufladen
K7  B1 bis B4 tragen die Familie
```

### Entscheidung

**Verworfen.**

Mehr Zeitkonstanten erweitern die Reichweite, nicht die Organisationsform.
Sie wiederholen die bereits vermessene Nachhallgrenze.

## 3. F2: explizite Kontaktpaar- oder Pfadablage

### Idee

Ein Kontakt an `x` und ein späterer Kontakt an `y` erzeugen eine gespeicherte
Verbindung, einen Pfad oder eine Brücke zwischen beiden Feldorten.

### Prüfung

Die Familie kann die Deformationswelt unmittelbar tragen. Sie muss dafür aber
bereits festlegen:

- welche zwei Ereignisse ein Paar bilden;
- wo die Verbindung gespeichert wird;
- wie sie bei einer späteren Abfrage gelesen wird;
- wann sie ersetzt oder gelöscht wird.

### Entscheidung

**Verworfen.**

Sie schreibt Beziehung und Topologie als Datenstruktur vor und wiederholt die
statische Kanten- und Interpolatorsackgasse.

## 4. F3: unabhängige lokale Empfänglichkeit

### Idee

Ein skalarer oder vektorieller Zustand verändert die spätere Aufnahme eines
einzelnen Neurons.

### Prüfung

Bleibt jeder Feldort unabhängig, zerfällt die Familie in lokale Spuren plus
festen Leser. Sie kann Amplitude und Dauer verändern, aber keine verteilte
Beziehungsform begründen.

Wird die Empfänglichkeit gezielt auf den erwarteten Austrittsort projiziert,
ist die Beziehung bereits durch den Projektor eingebaut.

### Entscheidung

**In unabhängiger Form verworfen.**

Sie fällt unter B1 bis B4 beziehungsweise die frühere K2-Grenze.

## 5. F4: adaptive Kante oder Leitfähigkeit

### Idee

Lokale Nachbarschaftsverbindungen ändern ihre Leitfähigkeit abhängig von
gemeinsamer oder aufeinanderfolgender Aktivität.

### Prüfung

Diese Familie liegt nahe an biologischer Plastizität, setzt digital aber
bereits voraus:

- eine explizite Kante;
- einen persistenten Kantenwert;
- eine feste Koinzidenz- oder Reihenfolgeregel;
- eine Schwächungs- oder Löschregel.

Damit wäre die gesuchte Feldtopologie nicht Befund, sondern Speicherformat.

### Entscheidung

**Verworfen.**

Eine feste oder adaptive Kantenmatrix wird nicht als erstes organisches
Substrat übernommen.

## 6. F5: lokale Normalisierung oder konservierte Ressource

### Idee

Feldorte teilen eine begrenzte Summe, Energie, Kapazität oder einen Stoff.
Beanspruchung an einer Stelle verändert dadurch andere Stellen.

### Prüfung

Lösung und Wiederbindung entstehen scheinbar natürlich, weil Ressource
freigegeben und neu verteilt wird. Die zentrale Funktion folgt aber direkt
aus der programmierten Erhaltung oder Norm.

### Entscheidung

**Verworfen.**

Ressourcenfreigabe darf später beobachtbare Beschreibung sein, aber keine
vorgegebene Zustandsvariable oder Gewinnerregel.

## 7. F6: Oszillator-, Phasen- oder Interferenzmedium

### Idee

Weltkontakte regen lokale Schwingungen an. Wiederholte Kontaktfolgen bilden
Phasen- oder Interferenzlagen, die spätere Feldwirkung verändern.

### Prüfung

Die Familie kann reichhaltige Geschichte tragen, führt aber zusätzlich ein:

- Phase oder Frequenz als neue Zustandsrolle;
- feste Kopplungs- und Resonanzskalen;
- häufig einen nachgeschalteten Phasenleser;
- schwer kontrollierbare permanente Restdynamik.

Eine feste lokale Rekurrenz oder ein Reservoir kann dieselben Muster
erzeugen. Natürliche vollständige Lösung ist nicht begründet.

### Entscheidung

**Für den kleinsten Kandidaten verworfen.**

Die Familie überlädt den präzisen Funktionsmangel.

## 8. F7: Musterarchiv, Reservoir oder lokale Projektionsbank

### Idee

Frühere Feldformen oder verdichtete Projektionen werden bewahrt und unter
späterem Kontakt verglichen.

### Prüfung

Auch eine komprimierte Projektionsbank bleibt ein Historienbestand. Ihre
Wirkung benötigt eine Such-, Vergleichs- oder Leserfunktion. Lösung erfolgt
durch Überschreiben, Vergessen oder Speicherverwaltung.

L8 und L9 sind bereits starke äußere Gegenmodelle dieser Familie.

### Entscheidung

**Verworfen.**

Sie verlagert die L4-Rekonstruktion in den Organismus, ohne eine
feldgetragene Bildung zu erklären.

## 9. F8: lokales hysteretisches Feldmedium

### Grundidee

Jeder gleichartige Feldort besitzt eine noch nicht festgelegte lokale
konstitutive Zustandsrolle. Reale Feldbeanspruchung kann den gegenwärtigen
Zustand des Mediums verändern. Dieser Zustand verändert anschließend die
weitere lokale Feldtransition desselben Mediums.

```text
lokale Feldbeanspruchung
-> veränderter lokaler Mediumzustand
-> veränderte weitere Feldfortsetzung
```

Es werden zunächst keine Partner, Kanten, Kontaktpaare, Form-IDs oder
Austrittsziele bezeichnet.

### Warum die Familie nicht sofort in F1 bis F7 fällt

Im Unterschied zu einer unabhängigen Spur wäre die Zustandsrolle nicht nur
später gelesener Inhalt. Sie müsste die lokale Feldtransition selbst
mitbestimmen.

Im Unterschied zur adaptiven Kante läge die Rolle am lokalen Feldmedium und
nicht auf einer bezeichneten Verbindung.

Im Unterschied zum Archiv würde keine frühere Feldform abgefragt.

### K1 bis K7

```text
K1  mögliche Quelle: reale lokale Feldbeanspruchung oder lokaler Feldfluss
K2  Mediumzustand läge vor jeder Leserfunktion im Neuronenzustand
K3  Wirkung müsste in derselben atomaren Feldtransition liegen
K4  Abgrenzung zu Leaky-Spur und fester Rekurrenz noch offen
K5  vollständige funktionale Lösung noch nicht begründet
K6  erneute andersartige Prägung prinzipiell möglich, aber nicht gezeigt
K7  B5 mit gleichem Zustands- und Radiusbudget bleibt Pflichtbaseline
```

### Kritischer Punkt

„Hysterese“ darf nicht als gewünschte Memoryeigenschaft programmiert werden.
Eine feste Hysteresekurve wäre selbst nur eine feste lokale Zustandsmaschine.

Ebenso wäre unzulässig:

- eine vorgegebene positive oder negative Prägungsrichtung;
- ein Schwellwert für Bindung oder Lösung;
- ein Mediumwert pro erwarteter Beziehung;
- eine eingebaute Annäherung an L4;
- eine adaptive Kopplung mit versteckter Kantenbedeutung.

### Entscheidung

**Als einzige Familie bedingt weiter prüfbar, aber nicht zugelassen.**

Vor jeder Gleichung muss gezeigt werden, ob die heutige Runtime überhaupt
eine lokale intrinsische Beanspruchungsgröße besitzt, die diese Rolle ohne
Observerprodukt kausal speisen könnte.

## 10. Zusammenfassung

| Familie | Entscheidung | Hauptgrund |
|---|---|---|
| F1 weitere Nachhallspuren | verworfen | feste Zeitspur |
| F2 Kontaktpaar oder Pfad | verworfen | Beziehung vorgegeben |
| F3 lokale Empfänglichkeit | verworfen | unabhängige Spur plus Leser |
| F4 adaptive Leitfähigkeit | verworfen | Kante als Speicherformat |
| F5 Ressource oder Norm | verworfen | Konkurrenz programmiert |
| F6 Phase oder Interferenz | verworfen | unnötige Zusatzdynamik |
| F7 Archiv oder Reservoir | verworfen | Historienbank plus Leser |
| F8 hysteretisches Feldmedium | bedingt prüfbar | lokale Quelle und Lösung offen |

Der Audit wählt F8 nicht aus. Er zeigt nur, dass F8 nicht bereits durch eine
explizite Beziehungsdatenstruktur ausgeschlossen ist.

## 11. Verhältnis zur früheren K6-Familie

F8 ist keine nachträgliche Freigabe von K6.

K6 beschrieb allgemein eine gekoppelte lokale Feldverformung. Die
[K6-Vorprüfung](046_K6_VORPRUEFUNG_UND_MEMORY_SUBSTRATFRAGE.md) schloss eine
vorschnelle Gleichung, weil lokale Naturquelle, Lösung und Wiederbindung
fehlten.

F8 verengt die verbleibende Frage auf ein lokales Medium, das von realer
Feldbeanspruchung geprägt und in derselben Feldtransition kausal gelesen
würde. Die drei alten Lücken bleiben vollständig bestehen.

## 12. Stärkste Gegenbaseline

Für F8 ist B5 aus dem
[operationalen C2-Baselinevertrag](045_OPERATIONALE_C2_BASELINEKLASSEN.md)
die primäre Gegenbaseline:

```text
fester lokaler Zustand
+ konstante lokale Kopplung
+ feste punktweise Nichtlinearität
-> komplexe geschichtsabhängige Feldtrajektorie
```

Zusätzlich bleiben bindend:

- B1 bis B3 gegen unabhängige Spuren;
- B4 gegen eine reine Leserwirkung;
- B6 gegen feste Normalisierung;
- L4 gegen die vollständige äußere Rekonstruktionsfunktion;
- L8 und L9 gegen Reservoir und Archiv.

Eine F8-Implementierung, die nur B5 mit anderer Schreibweise reproduziert,
trägt keinen eigenen Befund.

## 13. Noch fehlende Zulassungsnachweise

Vor einem konkreten F8-Kandidaten fehlen mindestens:

1. eine bereits kausal vorhandene lokale Beanspruchungsquelle;
2. ihre Verfügbarkeit vor Observer und ohne abgeleitetes Kontaktpaar;
3. eine Begründung, warum ein Mediumzustand statt weiterer Nachhallspur nötig
   wäre;
4. eine vorab prüfbare vollständige funktionale Lösung;
5. erneute Prägung durch dieselbe unveränderte lokale Naturbedingung;
6. ein endlicher fairer B5-Budgetvergleich;
7. eine Nullgrenze, in der exakt die heutige Runtime entsteht.

Ohne diese Nachweise bleibt jede Gleichung eine programmierte
Memorybehauptung.

## 14. Aussagegrenze

Dieser Audit trägt:

- die erneute Verwerfung der bekannten statischen Sackgassen;
- F8 als engste noch untersuchbare Substratfamilie;
- die unveränderte Bindung an B1 bis B6 und L4, L8, L9;
- die konkrete offene Frage nach einer intrinsischen lokalen Feldquelle.

Er trägt nicht:

- einen F8-Kandidaten;
- Hysterese als notwendige MCM-Eigenschaft;
- eine Zustandsvariable oder Gleichung;
- natürliche Lösung oder Wiederprägung;
- organisches Memory;
- Feldintelligenz.

## Freigabegrenze

```text
Kandidatenfamilien ausgesiebt:          ja
bekannte statische Familien verworfen: ja
bedingt prüfbare Familie:              F8
F8 als Kandidat zugelassen:            nein
lokale Beanspruchungsquelle bestätigt: nein
Zustandsrolle freigegeben:             nein
Runtime-Erweiterung freigegeben:       nein
```

## Nächster Schritt

Als Nächstes wird ausschließlich die heutige atomare Feldtransition auf eine
intrinsische lokale Beanspruchungs- oder Flussgröße auditiert. Es wird weder
ein Mediumzustand noch Hysterese implementiert.
