# Abschlussprojekt_BA_MECH_25_IBK_WaiJ_WirF
# E-Bike Simulator

## Projektbeschreibung

Dieses Projekt wurde im Rahmen des Abschlussprojekts der Lehrveranstaltung Programmieren I von Jonas Waid und Fabian Wirnsberger entwickelt. Ziel ist die Auswertung realer GPS-Daten einer Fahrradfahrt sowie die Simulation eines E-Bikes. Aus den GPS-Daten werden verschiedene Fahrgrößen berechnet, die anschließend zur Bestimmung des Leistungsbedarfs und zur Simulation unterschiedlicher Batterietypen verwendet werden. Die Aufgabenstellung orientiert sich an den Vorgaben des Abschlussprojekts. :contentReference[oaicite:0]{index=0}

---

# Installation

## Voraussetzungen

Folgende Software muss installiert sein:

- Python 3.14.3
- Git
- MiKTeX (für die automatische Erstellung des PDF-Berichts)

## Python-Abhängigkeiten installieren

Repository klonen:

```bash
git clone <Repository-URL>
cd <Projektordner>
```
oder mit STRG + Shift + P und den URL-Link einfügen

Virtuelle Umgebung erstellen:

```bash
python -m venv .venv
```
auf python oder py achten.

Aktivieren:

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Pakete installieren:
Wichtig, prüfen ob man im selben Ordner wie die requirements Datei ist.

```bash
pip install -r requirements.txt
```

---

# Projekt starten

Das Programm wird über

```bash
python main.py
```

gestartet.

Nach erfolgreicher Ausführung werden automatisch

- sämtliche Diagramme
- die Folium-Karte
- der PDF-Bericht

erstellt.

---

# Projektstruktur

```
main.py
│
├── RouteData
├── GPSPoint
├── GeoUtils
├── EBikePhysics
├── BatterySizing
├── BatteryBase
├── BatteryPack
├── BatteryLiPo
├── BatteryNMC
├── Motor
├── EBike
├── EBikeSimulator
├── PlotGenerator
└── ReportGenerator
```

---

# Funktionsumfang

Folgende Funktionen wurden umgesetzt:

- Einlesen der GPS-Daten
- Distanzberechnung (Haversine)
- Geschwindigkeitsberechnung
- Beschleunigungsberechnung
- Steigungsberechnung
- Leistungsberechnung
- Motorleistungsberechnung
- Batteriekapazitätsberechnung
- Simulation eines LiPo-Akkus
- Simulation eines NMC-Akkus
- SoC-Berechnung
- Spannungsberechnung
- Motorstromberechnung
- Motordrehmomentberechnung
- Höhenmeter Anstieg und Abstieg
- Maximalleistung
- Logging
- Fehlerbehandlung

---

# Umgesetzte Erweiterungen

Zusätzlich zu den Mindestanforderungen wurden folgende Erweiterungen umgesetzt:

- Berücksichtigung einer konstanten Fahrerleistung
- Berechnung der notwendigen Batteriekapazität mit Reserve
- Luftdichteberechnung aus Höhe und Temperatur
- Berechnung der Orientierung (Nord, Ost, Süd, West)
- Darstellung der Route auf einer interaktiven Folium-Karte, mit Anzeige der Orientierung (.html kann im Explorer in einem Browser geöffnet werden)
- Automatische Erstellung eines PDF-Berichts mit LaTeX (unter output/report)
- UML-Klassendiagramm (unter out/Diagramme)
- Drei UML-Aktivitätsdiagramme (unter out/Diagramme)
- Verwendung von Conventional Commits für die Versionsverwaltung
- Speicherung sämtlicher Diagramme als Bilddateien

---

# Erzeugte Diagramme

Neben den geforderten Diagrammen werden zusätzlich folgende Grafiken erstellt:

- Geschwindigkeit
- Beschleunigung
- Höhenprofil
- Motorleistung
- Fahrerleistung
- Gesamtleistung
- Motormoment
- Motorstrom
- Ladezustand (SoC) LiPo
- Ladezustand (SoC) NMC
- Batteriespannung LiPo
- Batteriespannung NMC
- Luftdichte
- Interaktive Folium-Karte der gefahrenen Strecke

Alle Diagramme werden automatisch im entsprechenden Ausgabeordner gespeichert.

---

# PDF-Bericht

Nach jeder Simulation wird automatisch ein PDF-Bericht erzeugt.

Der Bericht enthält unter anderem:

- Zusammenfassung der Simulation
- wichtigste Fahrdaten
- Batteriedaten
- sämtliche erzeugten Diagramme

Der Bericht befindet sich im Ordner

```
output/report/
```
beziehungsweise im Explorer unter output/report kann die PDF-Version gesichtet werden.

---

# UML-Dokumentation

Die Software wurde mit UML dokumentiert.

Folgende Diagramme wurden erstellt:

- Klassendiagramm
- Aktivitätsdiagramm Gesamtprogramm
- Aktivitätsdiagramm Simulation
- Aktivitätsdiagramm Batteriesimulation

Die Diagramme wurden mit **PlantUML** erstellt und zusätzlich als **SVG-Dateien** exportiert. Sie befinden sich im Projektordner Diagramme und die SVG-Dateien sind im ordner out zu finden.

---

# Bekannte Einschränkungen

Die berechnete maximale Motorleistung überschreitet stellenweise **1000 W**. Für einen durchschnittlichen Radfahrer ist dieser Wert nicht realistisch.

Die Ursache liegt darin, dass die Leistung ausschließlich aus den gemessenen GPS-Daten (Geschwindigkeit, Beschleunigung und Steigung) berechnet wird. Insbesondere kurze Messintervalle und starke Beschleunigungen führen zu hohen Leistungsspitzen. Im Rahmen dieses Projekts konnte keine geeignete Methode gefunden werden, diese Spitzenwerte physikalisch sinnvoll zu begrenzen, ohne die tatsächlichen Messdaten zu verfälschen. Eine Begrenzung der Beschleunigung auf ein vertretbares Maß wurde implemtiert.

Die Luftdichte wird bereits aus Temperatur und Höhe berechnet und grafisch dargestellt und anschließend an den Simulator übergeben. Falls die Luftdichte nicht berechnet werden kann, wird ein Fixwert angenommen.

---

# Verwendete Quellen

Für die Umsetzung des Projekts wurden unter anderem folgende Quellen verwendet:

- Vorlesungsunterlagen der Lehrveranstaltung *Programmieren*
- https://www.conventionalcommits.org/en/v1.0.0/
- https://python4data.science/de/latest/workspace/pandas/data-structures.html
- https://python4data.science/de/latest/workspace/numpy/intro.html
- Dokumentation der verwendeten Python-Bibliotheken (NumPy, Pandas, Matplotlib, Folium, SciPy und pathlib)

Zusätzlich wurden die im Rahmen der Aufgabenstellung bereitgestellten Batteriekennlinien und Simulationsparameter verwendet. :contentReference[oaicite:1]{index=1}

---

# Hinweise

Für die Entwicklung wurde Git zur Versionsverwaltung eingesetzt. Die Commit-Nachrichten orientieren sich am Standard der **Conventional Commits**, wodurch die Entwicklungsschritte nachvollziehbar dokumentiert werden.

Eine Rekuperation wurde nicht implementiert, da sie bei herkömmlichen E-Bikes in der Praxis nur selten eingesetzt wird und aufgrund der geringen rückgewinnbaren Bremsenergie nur einen geringen Einfluss auf die Reichweite hat.
---

# KI-Unterstützung

KI-gestützte Werkzeuge wurden ausschließlich unterstützend zur Ideenfindung, für Formulierungsvorschläge sowie zur Diskussion möglicher Lösungsansätze eingesetzt. Die Umsetzung, Anpassung und Überprüfung des Programmcodes erfolgte eigenständig.

Die UML-Diagramme wurden mit PlantUML erstellt und als SVG-Vektorgrafiken exportiert. Die SVG-Dateien befinden sich im Ordner out und können ohne zusätzliche Software betrachtet werden. Eine Installation von PlantUML oder Graphviz ist daher für die Ausführung des Projekts nicht erforderlich.