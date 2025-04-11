import chromadb

class ShortTermMemory:
    def __init__(self, max_length=20):
        self.max_length = max_length
        self.entries = []

    def add(self, message, time_delta, day, time_of_day):
        self.entries.append({
            "message": message,
            "time_delta": time_delta,
            "day": day,
            "time_of_day": time_of_day
        })
        if len(self.entries) > self.max_length:
            self.entries.pop(0)

    def get_recent(self, n=8):
        return [item["message"] for item in self.entries[-n:]]

    def clear(self):
        self.entries.clear()

class LongTermMemory:
    def __init__(self, db_path, collection_name="memories"):
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    def add(self, memory_id, summary, day, time_of_day):
        self.collection.add(
            ids=[memory_id],
            metadatas=[{"day": day, "time_of_day": time_of_day}],
            documents=[summary]
        )

    def query(self, prompt, n_results=2):
        results = self.collection.query(query_texts=[prompt], n_results=n_results)
        return results.get("documents", [])
