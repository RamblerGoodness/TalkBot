import chromadb
import os

def simple_db_test():
    """Simple ChromaDB test that outputs directly to console"""
    try:
        print("\n=== TESTING CHROMADB FUNCTIONALITY ===")
        
        # 1. Basic connection test
        print("\n[1] Testing basic ChromaDB connection...")
        client = chromadb.PersistentClient(path="test_db_chroma")
        print("✓ Successfully connected to ChromaDB")
        
        # 2. Collection creation
        print("\n[2] Testing collection creation...")
        test_collection = client.get_or_create_collection(name="test_collection")
        print(f"✓ Collection created: {test_collection.name}")
        
        # 3. Adding documents
        print("\n[3] Testing document addition...")
        test_collection.add(
            ids=["test1", "test2"],
            documents=[
                "This is a test document for ChromaDB verification",
                "This is another test document to make sure storage works"
            ],
            metadatas=[
                {"type": "test", "priority": "high"},
                {"type": "test", "priority": "low"}
            ]
        )
        print("✓ Added test documents to collection")
        
        # 4. Document retrieval by ID
        print("\n[4] Testing document retrieval by ID...")
        retrieved = test_collection.get(ids=["test1"])
        if retrieved and len(retrieved["documents"]) > 0:
            print(f"✓ Successfully retrieved document by ID: '{retrieved['documents'][0][:30]}...'")
        else:
            print("✗ Failed to retrieve document by ID")
        
        # 5. Document querying
        print("\n[5] Testing semantic search...")
        results = test_collection.query(
            query_texts=["verify database functionality"],
            n_results=2
        )
        if results and len(results["documents"]) > 0:
            print(f"✓ Successfully queried documents: Found {len(results['documents'][0])} results")
            print(f"  First result: '{results['documents'][0][0][:30]}...'")
        else:
            print("✗ Failed to query documents")
        
        # 6. Checking for existing Lyra database
        print("\n[6] Checking for existing character database...")
        lyra_path = "lyra_memories_chroma"
        if os.path.exists(lyra_path):
            print(f"✓ Character database exists at: {lyra_path}")
            
            lyra_client = chromadb.PersistentClient(path=lyra_path)
            lyra_collections = lyra_client.list_collections()
            print(f"✓ Found {len(lyra_collections)} collections in character database")
            
            for coll in lyra_collections:
                count = coll.count()
                print(f"  - Collection '{coll.name}' contains {count} memories")
                
                if count > 0:
                    peek = coll.peek(limit=1)
                    print(f"    Sample: '{peek['documents'][0][:50]}...'")
        else:
            print(f"! Character database not found at: {lyra_path}")
            print("  This is expected if you haven't had conversations with characters yet")
        
        # 7. Clean up test data
        print("\n[7] Cleaning up test data...")
        client.delete_collection(name="test_collection")
        print("✓ Test collection deleted")
        
        print("\n=== DATABASE TEST COMPLETE ===")
        print("✓ ChromaDB is functioning correctly!")
        print("✓ Your database setup is working as expected.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        print("\n=== DATABASE TEST FAILED ===")
        print("There is an issue with your ChromaDB setup.")
        return False

if __name__ == "__main__":
    simple_db_test()