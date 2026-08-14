# S1-EB20: Unabhaengige Prueferentscheidung

## Entscheidung

```text
FREIGABE
```

Der organisatorisch getrennte Forschungshelfer hat den S1-EB19-
Releasevertragsentwurf fachlich geprueft und freigegeben.

## Begruendung des Forschungshelfers

Der Releasevertrag schliesst die in S1-EB18 benannten Korrekturluecken fuer
den naechsten organisatorischen Schritt ausreichend:

- Forschungsfrage und Aussagegrenze bleiben eng und claimfrei.
- AB/BA-, Identitaets-, Bildungs-, Probe-, Fixed-Adapter-, Ressourcen-,
  Support- und `r2/r4/r8`-Restkontrollen bleiben erhalten.
- Die strikte Achtfachregel wird nicht aufgeweicht.
- 23800 Feldschritte, 30 Minuten und 4 GiB sind als harte Obergrenzen
  vertretbar.
- No-Retry nach einem gestarteten Fehler bleibt verbindlich.

## Reichweite der Freigabe

Die Entscheidung gilt nur fuer den S1-EB19-Releasevertragsentwurf als
naechsten organisatorischen Schritt. Sie ist keine Autorisierung zum Start
des kanonischen Laufs.

Weiterhin offen und vor jeder Ausfuehrung zwingend:

```text
project_owner_one_shot_authorization = PENDING
same_session_preflight               = PENDING
runtime_limit_enforcement            = PENDING
memory_limit_enforcement             = PENDING
execution_permitted                  = false
persistence_permitted                = false
```

## Rollenabgrenzung

Der Forschungshelfer hat nur geprueft. Er hat nicht geforscht, nichts
implementiert, keinen Vertrag technisch geoeffnet und keinen Lauf gestartet.

## Bester naechster Schritt

Der Projekteigner muss den genau einen S1-EB-Einmallauf ausdruecklich
autorisieren oder ablehnen. Erst nach einer Autorisierung duerfen die
technischen Zeit- und Speicher-Abbruchgates gebunden und danach der
Same-session-Preflight ausgefuehrt werden. Bis dahin bleibt der Lauf
gesperrt.
