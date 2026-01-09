import chromadb
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection(name="corruption_complaints")
print(f"Total Vectors Stored: {collection.count()}")
print("Recent Metadata:", collection.peek(limit=5)['metadatas'])