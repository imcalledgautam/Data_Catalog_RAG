import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://6cd2c310.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "u6hVOOQET9s7fvC11DIpx9JZAEVVNK3fQUGkmKSzBqY")


class Neo4jSetup:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared successfully.")
    
    def populate_database(self):
        with self.driver.session() as session:
            session.run("""
                CREATE (cust:Table {name: 'CUSTOMER_MASTER', description: 'Main customer information table'})
                CREATE (trans:Table {name: 'TRANSACTION_DATA', description: 'Daily transaction records'})
                CREATE (dep:Table {name: 'DEPOSIT_SUMMARY', description: 'Summary of customer deposits'})
                CREATE (loan:Table {name: 'LOAN_ACCOUNTS', description: 'Loan account details'})
                CREATE (final:Table {name: 'FINAL_REPORT', description: 'Consolidated reporting table'})
                CREATE (risk:Table {name: 'RISK_METRICS', description: 'Risk assessment metrics'})
                
                CREATE (c1:Column {name: 'customer_id', data_type: 'VARCHAR(20)'})
                CREATE (c2:Column {name: 'account_number', data_type: 'VARCHAR(30)'})
                CREATE (c3:Column {name: 'transaction_id', data_type: 'VARCHAR(50)'})
                CREATE (c4:Column {name: 'amount', data_type: 'DECIMAL(15,2)'})
                CREATE (c5:Column {name: 'deposit_date', data_type: 'DATE'})
                CREATE (c6:Column {name: 'loan_id', data_type: 'VARCHAR(25)'})
                CREATE (c7:Column {name: 'risk_score', data_type: 'DECIMAL(5,2)'})
                
                CREATE (cde1:CDE {name: 'CDE_00145', description: 'Customer Identification Number'})
                CREATE (cde2:CDE {name: 'CDE_00289', description: 'Account Balance Amount'})
                
                CREATE (r1:Region {name: 'APAC', description: 'Asia Pacific region'})
                CREATE (r2:Region {name: 'EMEA', description: 'Europe, Middle East, Africa'})
                CREATE (r3:Region {name: 'NAM', description: 'North America'})
                
                CREATE (cust)-[:HAS_COLUMN]->(c1)
                CREATE (cust)-[:HAS_COLUMN]->(c2)
                CREATE (trans)-[:HAS_COLUMN]->(c3)
                CREATE (trans)-[:HAS_COLUMN]->(c4)
                CREATE (dep)-[:HAS_COLUMN]->(c1)
                CREATE (dep)-[:HAS_COLUMN]->(c5)
                CREATE (loan)-[:HAS_COLUMN]->(c6)
                CREATE (loan)-[:HAS_COLUMN]->(c1)
                CREATE (final)-[:HAS_COLUMN]->(c4)
                CREATE (final)-[:HAS_COLUMN]->(c7)
                
                CREATE (cust)-[:LOADS_INTO {lineage_type: 'ETL'}]->(dep)
                CREATE (trans)-[:LOADS_INTO {lineage_type: 'ETL'}]->(dep)
                CREATE (cust)-[:LOADS_INTO {lineage_type: 'ETL'}]->(final)
                CREATE (dep)-[:LOADS_INTO {lineage_type: 'ETL'}]->(final)
                CREATE (loan)-[:LOADS_INTO {lineage_type: 'ETL'}]->(final)
                CREATE (risk)-[:LOADS_INTO {lineage_type: 'ETL'}]->(final)
                
                CREATE (cust)-[:JOINS {join_key: 'customer_id'}]->(dep)
                CREATE (cust)-[:JOINS {join_key: 'customer_id'}]->(loan)
                CREATE (dep)-[:JOINS {join_key: 'customer_id'}]->(final)
                CREATE (loan)-[:JOINS {join_key: 'customer_id'}]->(final)
                
                CREATE (cde1)-[:IS_CDE_FOR]->(c1)
                CREATE (cde2)-[:IS_CDE_FOR]->(c4)
                
                CREATE (dep)-[:BELONGS_TO_REGION]->(r1)
                CREATE (final)-[:BELONGS_TO_REGION]->(r2)
                CREATE (cust)-[:BELONGS_TO_REGION]->(r3)
                CREATE (loan)-[:BELONGS_TO_REGION]->(r1)
            """)
            print("Database populated with Citibank metadata graph.")
    
    def verify_setup(self):
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            print(f"Setup verified: {node_count} nodes, {rel_count} relationships created.")

    def create_schema_from_sqlalchemy(self):
        """
        Create Table and Column nodes with relationships that match the bank data SQLAlchemy schema.
        Tables: clients, bank_accounts, account_types, card_details, etc.
        Relationships: LOADS_INTO (ETL flows), JOINS (foreign keys), HAS_COLUMN
        """
        with self.driver.session() as session:
            # Create Table nodes for each table in the schema
            tables = {
                'clients': ('Client information', ['client_id', 'first_name', 'last_name', 'date_of_birth', 'home_address', 'contact_number', 'email_address', 'registered_on']),
                'bank_accounts': ('Bank account details', ['account_id', 'account_no', 'routing_no', 'balance_amount', 'date_created', 'account_category', 'client_id']),
                'account_types': ('Account categories and rules', ['account_category', 'min_balance_req', 'interest_rate']),
                'card_details': ('Credit/Debit card information', ['card_id', 'card_number', 'expiry_date', 'limit_amount', 'card_type', 'card_status', 'client_id']),
                'card_transactions': ('Card transaction records', ['transaction_id', 'card_id', 'merchant_name', 'transaction_date', 'transaction_amount', 'transaction_type', 'transaction_status']),
                'branches': ('Bank branch information', ['branch_id', 'branch_name', 'branch_city', 'branch_state', 'branch_contact']),
                'employees': ('Employee records', ['employee_id', 'emp_first_name', 'emp_last_name', 'emp_role', 'phone_ext', 'branch_id', 'supervisor_id']),
                'client_accounts': ('Client-Account relationships', ['client_id', 'account_id', 'relationship_type']),
                'loan_records': ('Loan account details', ['loan_id', 'client_id', 'loan_amount', 'loan_start_date', 'loan_due_date', 'interest_rate', 'loan_status']),
                'branch_employees': ('Branch-Employee assignments', ['branch_id', 'employee_id', 'start_date', 'end_date']),
                'online_transactions': ('Online transaction records', ['online_txn_id', 'account_id', 'txn_timestamp', 'txn_amount', 'payment_method', 'destination_account', 'txn_description']),
                'customer_support': ('Customer support tickets', ['ticket_id', 'client_id', 'issue_category', 'issue_description', 'reported_date', 'resolved_date', 'support_agent_id', 'ticket_status'])
            }

            # Create Table nodes
            for table, (desc, columns) in tables.items():
                session.run(
                    "MERGE (t:Table {name: $name}) SET t.description = $desc",
                    name=table, desc=desc
                )
                # Create Column nodes and HAS_COLUMN relationships
                for col in columns:
                    session.run("""
                        MATCH (t:Table {name: $table})
                        MERGE (c:Column {name: $col})
                        MERGE (t)-[:HAS_COLUMN]->(c)
                    """, table=table, col=col)

            # Create LOADS_INTO relationships for ETL flows
            etl_flows = [
                # Transaction flows
                ('card_transactions', 'card_details'),  # Card txns load into card details
                ('online_transactions', 'bank_accounts'),  # Online txns update account balances
                ('loan_records', 'bank_accounts'),  # Loan disbursements affect accounts
                # Aggregation flows
                ('bank_accounts', 'account_types'),  # Accounts roll up to types
                ('card_details', 'clients'),  # Cards roll up to client view
                ('loan_records', 'clients'),  # Loans roll up to client view
            ]
            for src, dst in etl_flows:
                session.run("""
                    MATCH (src:Table {name: $src}), (dst:Table {name: $dst})
                    MERGE (src)-[:LOADS_INTO {lineage_type: 'ETL'}]->(dst)
                """, src=src, dst=dst)

            # Create JOINS relationships based on foreign keys
            joins = [
                ('bank_accounts', 'clients', 'client_id'),
                ('card_details', 'clients', 'client_id'),
                ('loan_records', 'clients', 'client_id'),
                ('customer_support', 'clients', 'client_id'),
                ('bank_accounts', 'account_types', 'account_category'),
                ('employees', 'branches', 'branch_id'),
                ('card_transactions', 'card_details', 'card_id'),
                ('online_transactions', 'bank_accounts', 'account_id'),
                ('customer_support', 'employees', 'support_agent_id'),
            ]
            for src, dst, key in joins:
                session.run("""
                    MATCH (src:Table {name: $src}), (dst:Table {name: $dst})
                    MERGE (src)-[:JOINS {join_key: $key}]->(dst)
                """, src=src, dst=dst, key=key)

            print("Created schema metadata (Table nodes, Column nodes, and relationships).")

    def ingest_json_files(self, directory='.', file_list=None):
        """
        Ingest JSON files from `directory` (or provided file_list) into Neo4j.

        Each JSON file should be an array of objects. The node label will be derived
        from the filename (e.g., `clients.json` -> `Client`). For properties that
        look like foreign keys (ending with '_id'), the method will try to create
        a relationship from the source node to the target node where the target
        label matches the foreign key name (e.g., client_id -> :Client).
        """
        import json
        import glob
        import os

        files = file_list or glob.glob(os.path.join(directory, '*.json'))
        if not files:
            print("No JSON files found to ingest.")
            return

        with self.driver.session() as session:
            for fp in files:
                try:
                    name = os.path.splitext(os.path.basename(fp))[0]
                    # naive singular label: drop trailing 's' if present
                    raw_label = name.capitalize()
                    label = raw_label[:-1] if raw_label.endswith('s') else raw_label

                    with open(fp, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)

                    if not isinstance(data, list):
                        data = [data]

                    if not data:
                        continue

                    # Batch create nodes. Prefer an explicit id property if present.
                    # Determine id key: prefer keys ending with '_id' or 'id'
                    sample = data[0]
                    id_key = None
                    for k in sample.keys():
                        if k.endswith('_id'):
                            id_key = k
                            break
                    if not id_key:
                        for k in sample.keys():
                            if k == 'id':
                                id_key = 'id'
                                break

                    rows = data
                    if id_key:
                        cypher = f"UNWIND $rows AS row MERGE (n:{label} {{ {id_key}: row.{id_key} }}) SET n += row"
                    else:
                        cypher = f"UNWIND $rows AS row CREATE (n:{label}) SET n += row"

                    session.run(cypher, rows=rows)
                    print(f"Ingested {len(rows)} nodes for label :{label} from {fp}")

                except Exception as e:
                    print(f"Failed to ingest {fp}: {e}")
            
            print("JSON ingestion completed.")
            
            # After all nodes are created, create relationships between them based on foreign keys
            print("Creating relationships based on foreign keys...")
            relationship_mappings = [
                # Format: (source_label, source_key, target_label, target_key, relationship_type)
                # Direction: Parent -> Child (e.g., Client HAS_ACCOUNT Bank_account)
                ('Client', 'client_id', 'Bank_account', 'client_id', 'HAS_ACCOUNT'),
                ('Client', 'client_id', 'Card_detail', 'client_id', 'HAS_CARD'),
                ('Client', 'client_id', 'Loan_record', 'client_id', 'HAS_LOAN'),
                ('Client', 'client_id', 'Customer_support', 'client_id', 'SUBMITTED_TICKET'),
                ('Card_detail', 'card_id', 'Card_transaction', 'card_id', 'HAS_TRANSACTION'),
                ('Bank_account', 'account_id', 'Online_transaction', 'account_id', 'HAS_TRANSACTION'),
                ('Branche', 'branch_id', 'Employee', 'branch_id', 'HAS_EMPLOYEE'),
                ('Account_type', 'account_category', 'Bank_account', 'account_category', 'APPLIES_TO'),
            ]
            
            for src_label, src_key, tgt_label, tgt_key, rel_type in relationship_mappings:
                try:
                    result = session.run(f"""
                        MATCH (a:{src_label}), (b:{tgt_label})
                        WHERE a.{src_key} = b.{tgt_key}
                        MERGE (a)-[:{rel_type}]->(b)
                        RETURN count(*) as created
                    """)
                    count = result.single()['created']
                    if count > 0:
                        print(f"  Created {count} {rel_type} relationships ({src_label} -> {tgt_label})")
                except Exception as e:
                    print(f"  Failed to create {rel_type} relationships: {e}")

            print("JSON ingestion completed.")

    def ingest_catalog_data(self, catalog_data):
        """
        Ingests NASA CMR catalog data (a list of dicts) into the Neo4j database.

        Each entry in catalog_data is expected to contain keys like:
        Catalog_Entry_Name, Concept_ID, Short_Name, Metadata_Source_URL, Summary_Snippet
        """
        if not catalog_data:
            print("No catalog data provided to ingest_catalog_data(). Skipping ingestion.")
            return

        with self.driver.session() as session:
            # Create Dataset nodes and simple RELATED_TO relationships to allow
            # downstream lineage-type queries to run without errors.
            for i, entry in enumerate(catalog_data):
                try:
                    session.run(
                        """
                        MERGE (d:Dataset {concept_id: $concept_id})
                        SET d.catalog_entry_name = $catalog_entry_name,
                            d.short_name = $short_name,
                            d.metadata_source_url = $metadata_source_url,
                            d.summary_snippet = $summary_snippet
                        """,
                        concept_id=entry.get('Concept_ID') or entry.get('ConceptId') or f"unknown-{i}",
                        catalog_entry_name=entry.get('Catalog_Entry_Name') or entry.get('Name') or 'N/A',
                        short_name=entry.get('Short_Name') or entry.get('ShortName') or 'N/A',
                        metadata_source_url=entry.get('Metadata_SourcE_URL') or entry.get('Metadata_Source_URL') or entry.get('Metadata_Source') or entry.get('Metadata_Source_Url') or entry.get('Metadata_Source_Url') or entry.get('Metadata_Source_Url') or entry.get('Metadata_Source_URL'),
                        summary_snippet=entry.get('Summary_Snippet') or entry.get('Summary') or entry.get('summary') or ''
                    )
                except Exception as e:
                    print(f"Failed to ingest catalog entry {i} ({entry.get('Concept_ID', 'unknown')}): {e}")

            # Create lightweight RELATED_TO relationships between consecutive datasets
            # to simulate lineage paths so that agent queries that expect LOADS_INTO
            # or RELATED relationships still have connectivity to traverse.
            try:
                session.run(
                    """
                    MATCH (a:Dataset), (b:Dataset)
                    WHERE id(a) < id(b)
                    WITH a, b LIMIT 100
                    MERGE (a)-[:RELATED_TO {source: 'nasa_cmr_ingest'}]->(b)
                    RETURN count(*) as created
                    """
                )
            except Exception as e:
                print(f"Failed to create RELATED_TO relationships: {e}")

            print("NASA catalog ingestion completed.")


def setup_neo4j_database():
    setup = Neo4jSetup()
    try:
        setup.clear_database()
        setup.populate_database()
        setup.verify_setup()
    finally:
        setup.close()


if __name__ == "__main__":
    setup_neo4j_database()
