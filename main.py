from src.neo4j_setup import setup_neo4j_database, Neo4jSetup
from src.agent import generate_lineage_response
from src.nasa_cmr_catalog_poc import fetch_nasa_cmr_catalog

# Toggle flags for ingestion source
USE_NASA_CATALOG = False
USE_JSON_MOCK = True


def main():
    print("="*80)
    print("BANK DATA CATALOG - TEXT-TO-CYPHER POC")
    print("="*80)
    
    print("\n[STEP 1] Setting up Neo4j database with mock bank data...")

    # Initialize Neo4j connection wrapper
    setup = Neo4jSetup()
    try:
        setup.clear_database()

        if USE_JSON_MOCK:
            print("Ingesting mock JSON files into Neo4j...")
            try:
                setup.ingest_json_files(directory='data')
                print("\nCreating schema metadata nodes and relationships...")
                setup.create_schema_from_sqlalchemy()
            except Exception as e:
                print(f"JSON ingestion failed: {e}. Falling back to synthetic data.")
                setup.populate_database()
        elif USE_NASA_CATALOG:
            print("Fetching NASA CMR catalog and ingesting into Neo4j...")
            try:
                catalog = fetch_nasa_cmr_catalog()
                if not catalog:
                    print("Warning: NASA catalog fetch returned no entries. Falling back to Citibank synthetic data.")
                    setup.populate_database()
                else:
                    setup.ingest_catalog_data(catalog)
            except Exception as e:
                print(f"Error fetching or ingesting NASA catalog: {e}")
                print("Falling back to Citibank synthetic data ingestion.")
                setup.populate_database()
        else:
            print("Using built-in Citibank metadata graph...")
            setup.populate_database()

        setup.verify_setup()
    finally:
        setup.close()
    
    print("\n" + "="*80)
    print("[STEP 2] Running example queries...")
    print("="*80)
    
    example_queries = [
        "Show lineage and join key for the DEPOSIT_SUMMARY table.",
        "Which tables are linked to CDE_00145 and what region are they for?",
        "What are the source tables loading into the FINAL_REPORT table?"
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}: {query}")
        print(f"{'='*80}")
        
        explanation, cypher = generate_lineage_response(query)
        
        print(f"\n[Generated Cypher Query]:")
        print(cypher)
        
        print(f"\n[Natural Language Explanation]:")
        print(explanation)
        
        print(f"\n{'='*80}\n")
    
    print("\n" + "="*80)
    print("POC EXECUTION COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
