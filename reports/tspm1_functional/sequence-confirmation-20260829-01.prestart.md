# Ausfuehrungsstand vor der unabhaengigen Folgenbestaetigung

Basis ist Commit `2482d9d`. Der private Runner wird vor dem Start ausschliesslich
auf die vorregistrierte Lauf-ID, die N1-N4-Fixtures, den unabhaengigen Plan und
den bereits abgeschlossenen Validatorbeleg gebunden. B4, Folgenpruefer,
Distanzfunktion, Schwelle `44/765`, Kapazitaet und Auswertungsregeln bleiben
unveraendert.

Der Validatorbeleg
`sequence-confirmation-validator-20260829-01/result.json` ist versiegelt mit
Digest `93f7e63ac6c1be57da279ec93530e5937a31b27098a1fe1600ab097178d18089`.
Er enthaelt genau einen bestandenen Korrekturtest, Exit-Code 0, einen
vollstaendigen Mini-Abschluss und keine verbotenen Aufrufe.

Der neue Lauf verwendet zwei frische Banken und die Folgen N1-N2-N3-N4 sowie
N1-N3-N2-N4. N1-N4 besitzen je drei Zellen mit 40 und 200. Der kleinste
konstruktive Abstand unterschiedlicher Bilder ist `160/765`; die globale
Intensitaetskontrolle liegt bei `8/255`. Beide Seiten liegen vorab getrennt um
die unveraenderte Schwelle `44/765`.

Erwarteter Umfang: 56 Bildanalysen, acht Bildungen, zwoelf Folgeproben,
24 read-only Entscheidungen, 152 Ereignisse, 232 funktionale Schreibwoerter
sowie je 4992 funktionale und validierende L1-Terme. Das neue Laufverzeichnis
muss fehlen. Seine Erzeugung verbraucht die Freigabe auch bei Fehlern. Keine
Wiederholung, Fortsetzung, Reparatur oder Parameteranpassung.
