# S2-BK: Private Audio-only-Probenhuelle

## Ergebnis

Der fehlende Eingabevertrag aus S2-BJ ist statisch geschlossen. Die spaetere
AVPC-1-Probe erhaelt genau einen reduzierten auditiven Frame und keinen
visuellen Eingang. Implementiert oder ausgefuehrt wurde noch nichts.

## Private Anatomie

Die Probenhuelle ist ein unveraenderliches, rein privates Wertobjekt. Sie
bindet:

- einen echten privaten Quellvertrag und dessen neu berechneten Digest;
- genau eine auditive `ReceptorTimeSequence` mit genau einem Zeitframe;
- Profil, Parameter und auditive Bankkonfiguration;
- eingefrorene auditive Bankidentitaet und Bankzustand;
- Quellzeit, Feldzeit und die Trennung von Relationsphase und Probe;
- die auditive Eingangsprojektion und den Digest der gesamten Huelle.

Der private Quellbeleg ist ebenfalls ein unveraenderliches Wertobjekt. Er
bindet Quellart, auditive Modalitaet, Geometrie, beide Uhren,
Sequenzdigest und die ausdrueckliche Rohdatenfreiheit. Lose extern
uebergebene IDs oder Digests koennen diesen Beleg nicht ersetzen.

Die Huelle enthaelt keine visuelle Sequenz, keinen visuellen Frame und keinen
visuellen Projektionsdigest. Ein leerer oder neutraler visueller Platzhalter
ist ebenfalls unzulaessig.

## Zeitgrenze

Auf der auditiven Quelluhr muss das Probeende spaeter liegen als das letzte
im eingefrorenen Bankzustand gebundene Quellfenster. Auf der gemeinsamen
Felduhr darf das halboffene Probefenster fruehestens am Ende aller
Relationsexpositionen beginnen. Uhrwerte verschiedener Uhren werden nicht
direkt verglichen oder nachtraeglich umgerechnet.

## Trennung von Validierung und Funktion

Die Validierungsschicht sieht die vollstaendige Provenienzhuelle. Der
read-only Matcher erhaelt danach ausschliesslich auditive Konfiguration,
eingefrorenen auditiven Bankzustand, reduzierten Audioframe und Probe-ID.

Quell-, Sequenz-, Feldzeit- und Relationsdigests duerfen nicht als
Matchingmerkmale dienen. Damit kann die neue Huelle keine versteckte
Zusatzinformation in die spaetere Funktionspruefung einschleusen.

## Fail-closed

Jede Abweichung bei Quelle, Anzahl, Modalitaet, Geometrie, Carrierreihenfolge,
Profil, Konfiguration, Zustand, Zeit oder Digest verwirft den gesamten
Bindungsversuch. Es gibt weder Teilausgabe noch Reparatur, Defaultwert oder
Retry-Fortsetzung.

## Einordnung

S2-BK schliesst nur die Spezifikationsluecke der Audio-only-Probe. Es liegt
noch keine AVPC-1-Relationsmechanik, Probeausfuehrung, Feldwirkung oder
MCM-Memory vor.

## Naechster Schritt

S2-BL prueft statisch, welche vorhandenen privaten Typen und Hilfsrollen ohne
Grenzverletzung wiederverwendet werden koennen. Erst danach kann eine kleine
private Implementierung gesondert freigegeben werden.
