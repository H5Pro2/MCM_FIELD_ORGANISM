# S1-BL: E1 ressourcenbegrenzte lokale Kopplungsplastizitaet

## Status

Statischer Engineeringkandidatenvertrag unter S1-BK. Keine Gleichung, keine
Runtime, kein Testlauf und kein Memory-, Lern-, Organismus- oder KI-Befund.

Kandidatenkennung:

```text
E1_RESOURCE_CONSERVING_LOCAL_EDGE_PLASTICITY
```

## Technische Frage

Kann eine endliche, lokal umverteilbare Kopplungsressource auf den bereits
vorhandenen MCM-Nachbarschaftskanten wiederholte Feldteilnahme technisch
erhalten, spaetere Feldfortsetzung beeinflussen, unter Nullkontakt freigeben
und unter konkurrierender Geschichte anders wiederverwendet werden?

Diese Frage untersucht konstruierte Feldplastizitaet. Sie sucht kein neues
Naturgesetz.

## Zustandsrollen

Jeder Feldort besitzt eine freie nichtnegative Ressourcenmenge. Jede bereits
vorhandene lokale ungerichtete MCM-Kante kann einen nichtnegativen gebundenen
Anteil derselben Ressource tragen.

```text
freie lokale Ressource       = fuer neue lokale Bindung verfuegbar
kantengebundene Ressource    = an bestehender Feldkopplung beteiligt
Gesamtressource              = endlich und erhalten
```

Es werden keine neuen Kanten erzeugt. Die bestehende MCM-Geometrie bleibt
unveraendert. Nur die Verteilung einer endlichen Kopplungsressource auf dieser
Geometrie darf sich entwickeln.

## Lokale Ursache

Ursache ist ausschliesslich die bereits vorhandene lokale Feldteilnahme auf
einer Kante: Feldunterschied und der daraus entstehende lokale Austausch.

Die spaetere Gleichung muss stetig und fuer alle Kanten gleich sein. Sie darf
keine Ereignisklasse, Modalitaet, Objektkennung oder Schwelle abfragen.

Wiederholte aehnliche Feldteilnahme kann dadurch dieselbe lokale
Ressourcenverteilung mehrfach beeinflussen. Ein Speicherkommando existiert
nicht.

## Konjugierte Rueckwirkung

Die gebundene Ressource ist kein getrenntes Leseregister. Sie ist Teil der
lokalen Kopplung, durch die derselbe Feldtransfer laeuft.

```text
lokaler Feldtransfer
-> veraendert Ressourcenbindung
-> dieselbe Ressourcenbindung bestimmt spaeteren lokalen Feldtransfer
```

Schreib- und Lesepfad duerfen nicht als zwei unabhaengige Regeln
implementiert werden.

## Bilanz

Die spaetere Zustandsform muss eine exakte endliche Bilanz besitzen:

```text
Summe freie Ressource
+ Summe kantengebundene Ressource
= konstantes Gesamtbudget Q
```

Zulaessig sind nur bilanzierte lokale Transfers. Clipping, nachtraegliche
Normierung oder unbilanzierte Erzeugung ersetzen die Erhaltung nicht.

## Freigabe und Wiederverwendung

Ohne neuen Feldtransfer darf gebundene Ressource kontinuierlich in den freien
lokalen Anteil zurueckkehren. Diese Freigabe ist eine allgemeine
Materialdynamik und kein Loeschkommando.

Konkurrierende spaetere Feldgeschichte greift auf dasselbe endliche Budget
zu. Neue Bindung muss deshalb freie oder zuvor gebundene Kapazitaet
beanspruchen. Dadurch wird Wiederverwendung technisch moeglich, aber nicht als
Erfolgsphase vorgeschrieben.

## Vorhersagen vor einem Memorytest

E1 muss vor jeder Interpretation mindestens folgende technische Prognosen
erfuellen:

1. Gleiches raeumliches Kontaktmuster bei Wiederholung verschiebt Ressource
   reproduzierbar auf dieselben vorhandenen lokalen Kanten.
2. Die Gesamtressource bleibt in jedem Schritt numerisch erhalten.
3. Nach Angleichung von S und H kann eine unterschiedliche
   Ressourcenverteilung einen identischen Probeverlauf unterschiedlich
   fortsetzen.
4. Nullkontakt fuehrt ohne Reset zu bilanziertem Rueckfluss in freie
   Ressource.
5. Eine konkurrierende orthogonale Geschichte kann gebundene Ressource
   umlagern, sodass die alte technische Probeabweichung sinkt und eine andere
   entstehen kann.
6. Eine Kantenpermutation bei gleicher Werteverteilung veraendert die
   Feldfortsetzung nur entsprechend der permutierten Geometrie.

## Pflichtbaselines

E1 wird nicht nur gegen den Nullpfad verglichen. Verbindlich sind:

```text
P0 / heutiges neutrales S/H-Feld
lokale leaky Spur
lokaler Integrator
fester Gain mit gleichem Wertebereich
F3 mit erhaltener M-Ressource
CONST-V / feste Kopplungskoeffizienten
gleicher E1-Zustand ohne Rueckwirkung
gleiche Rueckwirkung bei eingefrorenem E1-Zustand
```

Adaptive Gain- und bekannte Plastizitaetsmodelle bleiben Erklaerungsbaselines.
Sie sperren die Implementierung nicht mehr, begrenzen aber jede spaetere
Aussage.

## Nullpfad

Bei ausgeschalteter E1-Kopplung muss die heutige neutrale S/H-Runtime exakt
reproduziert werden:

```text
E1 opt-in aus
-> kein E1-Zustand im Schema-1-Snapshot
-> identischer Feldverlauf und identischer Digest
```

E1 darf nicht implizit durch `current_api` oder einen bestehenden Consumer
aktiviert werden.

## Erfolgsstufen

```text
E0: Bilanz und Nullpfad technisch korrekt
E1: wiederholungsabhaengige Ressourcenverteilung
E2: kausale spaetere Rueckwirkung nach S/H-Angleichung
E3: Nullkontaktfreigabe und konkurrierende Wiederverwendung
E4: R1 bis R4 unter Pflichtbaselines
```

Keine Stufe heisst automatisch Memory. Bis E4 lautet die hoechste zulaessige
Bezeichnung `ressourcenbegrenzte lokale Feldplastizitaet`.

## Offene Punkte vor einer Gleichung

Vor Implementierung muessen noch statisch festgelegt werden:

1. exakte diskrete Ressourcenanatomie auf Knoten und vorhandenen Kanten;
2. eine einzige kontinuierliche lokale Transferursache;
3. Vorzeichen und Wertebereich der Rueckwirkung auf den Feldgenerator;
4. eine erhaltende Integrationsform ohne Clipping oder Nachnormierung;
5. exakte E0-Abschaltung und Snapshotgrenze;
6. kleinste Gegenprognose gegen festen Gain und F3.

## Aussagegrenze

E1 ist bewusst konstruiert und daher kein emergent gefundenes Naturprinzip.
Selbst bei erfolgreicher Funktion waere zunaechst nur gezeigt, dass das
MCM-Feld mit einer allgemeinen lokalen Plastizitaet gekoppelt werden kann.

## Bester naechster Schritt

S1-BM bestimmt die minimale Ressourcenanatomie und die exakte
Erhaltungsidentitaet von E1, weiterhin ohne Dynamikgleichung. Erst danach darf
eine lokale Transferform vorgeschlagen werden.

