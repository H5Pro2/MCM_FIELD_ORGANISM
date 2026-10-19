# UH1 Profilklarstellung vor Umsetzung und Qualifikation

2026-10-04. Status: KONKRETE_VERTRAGSKORREKTUR_ZUR_ENTSCHEIDUNG.
Keine Änderung des gebundenen Vertrags oder des Produktionscodes vorgenommen.

## Nachgewiesener Widerspruch

Abschnitt 3 des abgenommenen UH1-Vertrags verlangt gleichzeitig:

> Das Profil ist unverändert der SHA256 des UTF-8-Strings
> `HX1-schema-48-float64` ohne Zeilenumbruch, wie im gebundenen HX1-Pfad;

Der unveränderte HX1-Pfad ruft tatsächlich
`source.digest('HX1-schema-48-float64')` auf. Diese Funktion hasht die kanonische
JSON-Serialisierung einschließlich Anführungszeichen und abschließendem LF.
Sie hasht nicht den nackten UTF-8-String.

| Variante | Eingangsbytes | SHA256 |
| --- | --- | --- |
| Tatsächlich gebundener HX1-Pfad | `"HX1-schema-48-float64"` gefolgt von LF | `4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b` |
| Wörtliche UH1-Textvorgabe | `HX1-schema-48-float64` ohne LF | `e613b0824a8578ba518576484b01634179895c814182f0dc7c978cb61ca61070` |

Beide Hashes wurden ausschließlich aus diesen statischen Zeichenfolgen berechnet.
Die Hashes der HX1-Dateien `_s2uc_hx1_engine.py` und `_s2uc_hx1_sources.py`
stimmen mit der ursprünglichen Codebindung überein. Kein Replay, kein Aufruf
einer Forschungsquelle und keine neue Bootstrapmatrix.

Dieser Widerspruch stammt aus meiner Vertragsformulierung. Er ist kein
beobachteter Defekt des HX1-Produktionscodes und hebt den HX1-Befund nicht auf.

## Konkrete vorgeschlagene Korrektur

Im UH1-Vertrag ausschließlich den Profilabsatz durch Folgendes ersetzen:

> Das Profil bleibt bitgleich zum gebundenen HX1-Pfad:
> `4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b`.
> Es ist SHA256 der UTF-8-Bytes der kanonischen JSON-Zeichenfolge
> `"HX1-schema-48-float64"` mit abschließendem LF, entsprechend der
> unveränderten HX1-Funktion `source.digest('HX1-schema-48-float64')`.
> Kein neuer fallabhängiger Profilwert und keine Änderung der U-Scope-Semantik.

Danach nur die UH1-Spezifikationsbindung für den korrigierten Vertrag erneuern;
die Quellenbindung, alle 64 Quellen, HX1-Bindungen, U, H-Regeln, Auswertung
und Ressourcenparameter bleiben unverändert. Alte Spezifikationsbindung vor
Ersetzung als historischen Stand erhalten. Noch keine Änderung daran ausgeführt.

## Betroffener Schritt und Fortsetzung

Die Vertragsentscheidung liegt beim Projektleiter. Betroffen sind die eindeutige
U-Integration und damit Code-/Vorstartbindung und formale neutrale Qualifikation.
Ein vollständiger neutraler Größenablauf auf einem eigenmächtig gewählten Profil
wäre nicht zulässig. Er wurde nicht gestartet; sein Kontingent ist unberührt.

Unabhängige H-Logik ist von diesem Profilwert nicht betroffen. Zur Vermeidung eines
unnötigen Vertragszweigs wird keine alternative U-Integration implementiert.
Empfehlung: den oben konkret formulierten Korrekturabsatz annehmen und den bereits
erteilten Entwicklungsauftrag auf dieser eindeutigen Grundlage fortführen.
Die spätere Forschungsfreigabe bleibt separat erforderlich; HX1 bleibt geschlossen.

Belege: [UH1-Vertrag](S2UC_UH1_PRUEFVERTRAG_20261004.md),
[bestehende Spezifikationsbindung](S2UC_UH1_SPEZIFIKATIONSBINDUNG_20261004.json),
[HX1-Aufruf](../tools/_s2uc_hx1_engine.py),
[HX1-Hashserialisierung](../tools/_s2uc_hx1_sources.py).
