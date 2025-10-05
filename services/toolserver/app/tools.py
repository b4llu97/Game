import chromadb
from chromadb.config import Settings
import os
import time
from typing import List, Dict

CHROMA_HOST = os.getenv("CHROMA_HOST", "http://chroma:8000")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "jarvis_docs")

def get_chroma_client():
    host = CHROMA_HOST.replace("http://", "").replace("https://", "").split(":")[0]
    port_str = CHROMA_HOST.split(":")[-1]
    port = int(port_str) if port_str.isdigit() else 8000
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            client.heartbeat()
            return client
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Chroma connection attempt {attempt + 1} failed, retrying in {retry_delay}s: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"Failed to connect to Chroma after {max_retries} attempts: {e}")
                raise

def get_or_create_collection():
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=CHROMA_COLLECTION)
    except Exception as e:
        print(f"Collection not found, creating new one: {e}")
        collection = client.create_collection(
            name=CHROMA_COLLECTION,
            metadata={"description": "Jarvis document collection"}
        )
    return collection

def search_docs(query: str, n_results: int = 5) -> List[Dict]:
    try:
        collection = get_or_create_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        documents = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return documents
    except Exception as e:
        return [{"error": str(e)}]

def add_document(text: str, metadata: Dict = None) -> bool:
    try:
        collection = get_or_create_collection()
        import uuid
        doc_id = str(uuid.uuid4())
        
        collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        return True
    except Exception as e:
        print(f"Error adding document: {e}")
        return False

def get_tool_definitions() -> List[Dict]:
    return [
        {
            "name": "get_fact",
            "description": "Ruft einen gespeicherten Fakt aus der Datenbank ab",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Der Schlüssel des Fakts (z.B. 'versicherung.gebaeude.summe')"
                    }
                },
                "required": ["key"]
            }
        },
        {
            "name": "set_fact",
            "description": "Speichert einen neuen Fakt in der Datenbank",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Der Schlüssel des Fakts"
                    },
                    "value": {
                        "type": "string",
                        "description": "Der Wert des Fakts"
                    }
                },
                "required": ["key", "value"]
            }
        },
        {
            "name": "search_docs",
            "description": "Durchsucht die Dokumentensammlung semantisch nach relevanten Informationen",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Die Suchanfrage"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Anzahl der Ergebnisse (Standard: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    ]
