# Jarvis AI - Persönlicher KI-Assistent

Ein intelligenter persönlicher Assistent basierend auf einer Microservices-Architektur mit LLM-Integration.

## Übersicht

Jarvis ist ein modulares KI-System, das folgende Hauptfunktionen bietet:
- 📚 Fakten-Verwaltung und semantische Dokumentensuche
- 🗣️ Spracherkennung (ASR) und Sprachausgabe (TTS) auf Deutsch
- 📄 Automatische Dokumentenverarbeitung (NAS, E-Mails)
- 🤖 LLM-gestützte Konversation (Ollama)
- ⏰ Proaktive Erinnerungen und Benachrichtigungen

## Architektur (PR1: Basis-Infrastruktur)

Das System wird in mehreren Phasen implementiert. Diese erste Phase (PR1) umfasst die Basis-Infrastruktur:

1. **llama**: Ollama LLM Service (Port 11434)
2. **chroma**: ChromaDB Vector Database (Port 8001)
3. **toolserver**: Facts Database + Vector Search API (Port 8002)

Weitere Services folgen in späteren PRs.

## Schnellstart

### Voraussetzungen

- Docker und Docker Compose
- Mind. 8GB RAM

### Installation

1. Repository klonen:
```bash
git clone https://github.com/b4llu97/Jarvis.git
cd Jarvis
```

2. Umgebungsvariablen konfigurieren:
```bash
# Die config/.env Datei ist bereits vorhanden
# Bei Bedarf anpassen (z.B. IMAP-Zugangsdaten)
```

3. Services starten:
```bash
docker-compose up -d
```

4. LLM-Modell herunterladen:
```bash
docker exec jarvis-llama ollama pull llama3.1
```

### Verwendung

#### Toolserver API

Facts speichern und abrufen:
```bash
# Fakt speichern
curl -X PUT http://localhost:8002/v1/facts/versicherung.gebaeude.summe \
  -H "Content-Type: application/json" \
  -d '{"value":"980000 CHF"}'

# Fakt abrufen
curl http://localhost:8002/v1/facts/versicherung.gebaeude.summe

# Alle Facts auflisten
curl http://localhost:8002/v1/facts
```

Dokument hinzufügen:
```bash
curl -X POST http://localhost:8002/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"text":"Dies ist ein Testdokument über Versicherungen", "metadata":{"source":"test"}}'
```

Semantische Suche:
```bash
curl -X POST http://localhost:8002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Versicherung", "n_results":5}'
```

## Konfiguration

### config/.env

Hauptkonfigurationsdatei mit allen Umgebungsvariablen:
- LLM-Einstellungen (Ollama Host, Modell)
- Chroma DB Einstellungen
- Platzhalter für zukünftige Features (IMAP, Telegram)

### config/system_prompt.txt

System-Prompt für das LLM mit Anweisungen und Richtlinien (in Deutsch).

### config/persona_prompt.txt

Persönlichkeitsdefinition für Jarvis (Kommunikationsstil, Tonfall).

## Entwicklung

### Service-Struktur

```
services/toolserver/
├── Dockerfile
├── requirements.txt
└── app/
    ├── main.py
    ├── database.py
    ├── models.py
    └── tools.py
```

### Logs anzeigen

```bash
# Alle Services
docker-compose logs -f

# Einzelner Service
docker-compose logs -f toolserver
```

### Services neu bauen

```bash
docker-compose up -d --build
```

## Tests

### Verfügbare Test-Befehle

```bash
# Toolserver Health-Check
curl http://localhost:8002/health

# Chroma Health-Check
curl http://localhost:8001/api/v1/heartbeat

# Ollama Health-Check
curl http://localhost:11434/api/tags

# Fakt-Speicherung testen
curl -X PUT http://localhost:8002/v1/facts/test.key \
  -H "Content-Type: application/json" \
  -d '{"value":"test_value"}'

# Fakt abrufen
curl http://localhost:8002/v1/facts/test.key

# Dokument hinzufügen und durchsuchen
curl -X POST http://localhost:8002/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"text":"Testdokument", "metadata":{"source":"test"}}'

curl -X POST http://localhost:8002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Test", "n_results":5}'
```

### Verifizierte Funktionalität (PR1)

✅ **Llama Service**
- Ollama läuft auf Port 11434
- Modell llama3.1:latest (8B Parameter, 4.9 GB) erfolgreich geladen

✅ **Chroma Service**  
- ChromaDB läuft auf Port 8001
- Vector Database ist erreichbar und funktional

✅ **Toolserver Service**
- API läuft auf Port 8002
- Fakten-Speicherung (SQLite): ✅ Funktioniert
- Fakten-Abruf: ✅ Funktioniert  
- Dokument-Hinzufügen (Chroma): ✅ Funktioniert
- Semantische Suche: ✅ Funktioniert (Distanz: 0.72)
- Tool-Definitionen API: ✅ Liefert 3 Tools (get_fact, set_fact, search_docs)

**Test-Beispiel:**
```bash
# Versicherungssumme speichern
curl -X PUT http://localhost:8002/v1/facts/versicherung.gebaeude.summe \
  -H "Content-Type: application/json" \
  -d '{"value":"980000 CHF"}'

# Dokument über Gebäudeversicherungen hinzufügen
curl -X POST http://localhost:8002/v1/documents \
  -H "Content-Type: application/json" \
  -d '{"text":"Dies ist ein Testdokument über Gebäudeversicherungen. Die Versicherungssumme beträgt 980000 CHF für das Hauptgebäude.", "metadata":{"source":"test", "type":"insurance"}}'

# Semantische Suche nach "Versicherung Gebäude"
curl -X POST http://localhost:8002/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Versicherung Gebäude", "n_results":3}'

# Antwort: Dokument gefunden mit Distanz 0.72
```

## Roadmap

- [x] Phase 1: Basis-Infrastruktur (docker-compose, toolserver, chroma, llama) - **PR1**
- [ ] Phase 2: ASR/TTS Services - PR2
- [ ] Phase 3: Orchestrator mit LLM-Integration - PR3
- [ ] Phase 4: Ingestion-Pipeline - PR4
- [ ] Phase 5: Proaktiv-Engine - PR5

## Sicherheit

- Alle Services sind nur auf localhost verfügbar
- Sensible Daten werden in `.env` gespeichert (nicht in Git)
- Docker-Container laufen mit minimalen Berechtigungen
- Verschlüsselte Volumes für sensible Daten

## Autor

Mario Hunziker (@b4llu97)

---

**Link zur Devin Session**: https://app.devin.ai/sessions/299414aacd4143aab9f366e2a23f8d7e
