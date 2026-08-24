# S2-AF: Statischer PPB-1-Aktivbatch-Bindungsvertrag

## Gegenstand

S2-AF bindet ausschliesslich die private technische Verbindung zwischen
einem validierten `BrowserReceptorSequenceBatch` und den getrennten
auditiven und visuellen PPB-1-Eingabestroemen. Der Vertrag fuehrt keine neue
Speicherregel und keine Feldursache ein.

Vorgesehene spaetere Funktionssignatur:

```text
bind_ppb1_active_receptor_batch(
    binding_id,
    BrowserReceptorSequenceBatch,
    PPB1ReceptorProfileBinding,
) -> PPB1ActiveReceptorBatchEnvelope
```

In S2-AF werden diese Typen und die Funktion noch nicht implementiert.

## Eingangsbindung

Zulaessig ist genau ein vollstaendiger Browserbatch mit auditiver und
visueller Sequenz in dieser Reihenfolge. Beide Sequenzen muessen denselben
gemeinsamen Feldtakt verwenden und nichtleer sein. Innerhalb jeder
Modalitaet bleiben Snapshotidentitaeten eindeutig, Feldintervalle geordnet
und Quellfenster fortschreitend.

Das Profil muss `browser` sein. Modalitaet, Geometrie und geordnete
Traegeridentitaeten jedes Frames muessen exakt zur jeweiligen PPB-1-
Konfiguration passen. Es gibt keine Reparatur, Umsortierung oder
Dimensionsanpassung.

## Provenienzhuelle

Die spaetere unveraenderliche Huelle bindet:

- Weltvertrags-ID und -Digest;
- Batchdigest;
- Profil-, Parameter- und beide Konfigurationsdigests;
- gemeinsamen Feldtakt;
- zwei weiterhin getrennte Modalitaetsstroeme;
- Framezahl, Geometrie und Traegerreihenfolge;
- Snapshot-ID;
- Quellfenster und gemeinsames Feldintervall;
- bestehenden PPB-Eingabedigest und erweiterten Framedigest.

Der vorhandene PPB-Eingabedigest umfasst bereits Werte, Geometrie, Traeger
und Quellfenster. Er umfasst jedoch nicht Snapshot-ID und gemeinsames
Feldintervall. Diese Rollen werden deshalb in der Huelle zusaetzlich
gebunden, ohne den vorhandenen PPB-Kern oder Frame zu veraendern.

Die Huelle darf nur die bereits unveraenderlichen reduzierten Frames tragen.
Sie speichert keine Audio-/Videorohdaten, keinen Feldsnapshot und keine
semantischen Rollen.

## Atomaritaet und Fail-Closed-Verhalten

Der spaetere Binder darf weder PPB-Zustand fortschreiben noch eine Probe,
Feldfunktion oder Dateioperation aufrufen. Batch, Profil, Frames, Werte und
Reihenfolge muessen vor und nach der Bindung identisch sein. Es entsteht
entweder eine vollstaendige Zwei-Modalitaeten-Huelle oder kein Ergebnis.

Der Vertrag definiert elf endliche Fehlerrollen fuer ungueltige Identitaet,
Rohpayloadbindung, Digestdrift, falsches Profil, Modalitaets-, Geometrie-,
Traeger-, Snapshot- und Zeitfehler, Mutation sowie Teilausgabe.

## Fairness

Jeder spaetere Vergleichsarm erhaelt denselben Huelldigest, dieselben Frames
in derselben Reihenfolge und dieselbe Trennung von Bildung, Aktualisierung
und Probe. Kapazitaet, Zustandsbudget und Aufrufzahl muessen vor der
Ausfuehrung angeglichen werden. Beim Abruf steht keine Rohhistorie bereit.

Vergleichsarme:

- PPB-1 als adaptive Online-Prototypkomponente;
- kein Zustand;
- registriertes Replay reduzierter Eingaben als diagnostische Obergrenze;
- statische Prototypbank;
- gleitende Statistik oder Nachhall;
- Attraktor-basierte Mustervervollstaendigung;
- begrenzter Reservoirzustand.

Das Replay darf nur die registrierten reduzierten Eingaben verwenden, keine
Audio- oder Videorohdaten.

## Mess- und Falsifikationsgrenze

Die Anschlussabnahme darf nur Frame-, Digest-, Identitaets- und
Zeitkonservierung, fehlende Mutation, fehlende Rohdaten und atomaren Fehler
messen. Ein bestandener Anschluss ist noch keine Speicherfunktion.

Die Richtung wird gestoppt, wenn der Browserbatch fuer das Browserprofil
transformiert, resampelt oder modalitaetsuebergreifend fusioniert werden
muesste, Provenienz nicht exakt bindbar ist, ein Zustands-/Probe-/Feldaufruf
fuer die Bindung erforderlich waere oder Vergleichsarme unterschiedliche
Eingaben oder Budgets erhielten.

Bildung, Stabilisierung, Wiedererkennung, Distanz, Fehlzuordnung, Kapazitaet
und Verdraengung werden erst in einem spaeteren Funktionsvertrag bewertet.

## Grenze und naechster Schritt

Nicht freigegeben sind Implementierung, Tests, Fixtures, Zustands- oder
Probeaufrufe, Baselines, Feldrueckwirkung, API, Snapshot, Produktion, Live-
Eingabe und Semantik.

S2-AG soll ausschliesslich statisch Vollstaendigkeit, Nichtzirkularitaet und
Materialisierbarkeit pruefen. Insbesondere muss geklaert werden, ob das
vorhandene Browserprofil ohne neue Parameter exakt zum kontrollierten Batch
passt. Erst danach kann eine private Implementierung erwogen werden.

Maschinenlesbarer Vertrag:
[S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json](S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json).
