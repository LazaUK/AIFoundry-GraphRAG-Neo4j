import streamlit as st
import os

# --- PAGE CONFIG (runs immediately - minimal imports) ---
st.set_page_config(
    page_title="Northwind Graph RAG Demo", 
    page_icon="🛒", 
    layout="wide"
)
st.title("Northwind Graph RAG Demo")
st.caption("Natural Language to Cypher with Azure AI Foundry, Langchain and Neo4j")

# --- SESSION STATE INITIALISATION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "graph" not in st.session_state:
    st.session_state.graph = None
if "chain" not in st.session_state:
    st.session_state.chain = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXAMPLE QUERIES ---
EXAMPLE_QUERIES = [
    "Which suppliers provide products ordered by customers in London?",
    "What categories has employee Nancy Davolio sold, with order counts?",
    "Show customers whose orders were handled by employees reporting to Andrew Fuller",
]

# --- SIDEBAR ---
with st.sidebar:
    st.header("Northwind Graph RAG Demo")
    st.markdown("**Graph Dataset**: *Northwind*")
    st.markdown("**Graph Database**: *Neo4j*")
    st.markdown("**AI Processing**: *Azure AI Foundry*")
    st.markdown("**AI Orchestration**: *Langchain*")

    st.divider()
    
    # Connection settings
    st.subheader("Neo4j Connection")
    NEO4J_URI = st.text_input("URI", value="bolt://localhost:7687")
    NEO4J_USER = st.text_input("Username", value="neo4j")
    NEO4J_PASSWORD = st.text_input("Password", value="northwind", type="password")
    
    st.divider()
    
    # Connect button
    if st.button("Connect", type="primary", use_container_width=True):
        # Get Azure OpenAI config from environment
        azure_endpoint = os.getenv("AZURE_OPENAI_API_BASE", "")
        azure_deployment = os.getenv("AZURE_OPENAI_API_DEPLOY", "")
        
        if not azure_endpoint or not azure_deployment:
            st.error("Missing environment variables: AZURE_OPENAI_API_BASE and/or AZURE_OPENAI_API_DEPLOY")
        else:
            with st.spinner("Loading packages and connecting..."):
                try:
                    # === LAZY IMPORTS - only when Connect is clicked ===
                    from langchain_openai import ChatOpenAI
                    from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
                    from langchain_core.prompts import PromptTemplate
                    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                    
                    # Connect to Neo4j
                    graph = Neo4jGraph(
                        url=NEO4J_URI, 
                        username=NEO4J_USER, 
                        password=NEO4J_PASSWORD
                    )
                    
                    # Connect to Azure OpenAI using v1 API
                    credential = DefaultAzureCredential()
                    token_provider = get_bearer_token_provider(
                        credential, "https://cognitiveservices.azure.com/.default"
                    )
                    
                    llm = ChatOpenAI(
                        model=azure_deployment,
                        base_url=azure_endpoint,
                        api_key=token_provider,
                    )
                    
                    # Create chain with Northwind-specific prompts
                    CYPHER_GENERATION_TEMPLATE = """
Task: Generate a Cypher statement to query a Northwind retail database.

Database Schema:
{schema}

Rules:
1. Use case-insensitive matching: WHERE toLower(n.property) CONTAINS toLower("value")
2. Use DISTINCT to avoid duplicates
3. LIMIT results to 50 unless user asks for more
4. Return meaningful properties (names, not just IDs)
5. CRITICAL: Always include the WHERE filter values in RETURN so results are self-explanatory

Example:
Question: Which suppliers provide products ordered by customers in London?
Cypher: MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)<-[:ORDERS]-(:Order)<-[:PURCHASED]-(c:Customer)
        WHERE toLower(c.city) CONTAINS toLower("London")
        RETURN DISTINCT s.companyName AS Supplier, p.productName AS Product, c.companyName AS Customer, c.city AS CustomerCity
        LIMIT 50

Question: {question}

Cypher Query:
"""
                    
                    QA_TEMPLATE = """
You are a helpful assistant analysing retail data from the Northwind database.

Context from Database:
{context}

Instructions:
1. Provide a clear, business-focused answer
2. Summarise key findings (counts, patterns, notable items)
3. Format lists with bullet points if there are multiple items
4. If no data found, say so clearly
5. Reference the specific entities from the query results in your answer

Question: {question}

Answer:
"""

                    cypher_prompt = PromptTemplate(
                        input_variables=["schema", "question"],
                        template=CYPHER_GENERATION_TEMPLATE
                    )
                    
                    qa_prompt = PromptTemplate(
                        input_variables=["context", "question"],
                        template=QA_TEMPLATE
                    )

                    chain = GraphCypherQAChain.from_llm(
                        llm=llm,
                        graph=graph,
                        verbose=True,
                        return_intermediate_steps=True,
                        cypher_prompt=cypher_prompt,
                        qa_prompt=qa_prompt,
                        allow_dangerous_requests=True,
                        top_k=50
                    )
                    
                    # Store in session state
                    st.session_state.graph = graph
                    st.session_state.chain = chain
                    st.session_state.connected = True
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Connection failed: {e}")
                    st.session_state.connected = False
    
    # Show connection status
    if st.session_state.connected:
        st.success("Status: Connected")
    else:
        st.warning("Status: Not connected")

# --- MAIN APP ---

# Check connection before showing main content
if not st.session_state.connected:
    st.info("👈 Configure connection settings in the sidebar and click **Connect**.")
    st.stop()

# === Functions defined here to avoid any module-level analysis ===

def display_schema(graph):
    """Display database schema."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Node Labels:**")
        try:
            result = graph.query("CALL db.labels() YIELD label RETURN label ORDER BY label")
            for row in result:
                st.markdown(f"- `{row['label']}`")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.markdown("**Relationship Types:**")
        try:
            result = graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
            for row in result:
                st.markdown(f"- `{row['relationshipType']}`")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    st.markdown("**Node Counts:**")
    try:
        result = graph.query("""
            MATCH (n) 
            RETURN labels(n)[0] AS label, count(*) AS count 
            ORDER BY count DESC
        """)
        cols = st.columns(min(len(result), 5))
        for i, row in enumerate(result[:5]):
            cols[i].metric(row['label'], row['count'])
        if len(result) > 5:
            cols2 = st.columns(min(len(result) - 5, 5))
            for i, row in enumerate(result[5:10]):
                cols2[i].metric(row['label'], row['count'])
    except Exception as e:
        st.error(f"Error: {e}")


def display_schema_as_table(graph):
    """Display schema relationships as a table."""
    st.markdown("**Schema Relationships:**")
    try:
        result = graph.query("""
            MATCH (n)-[r]->(m)
            WITH labels(n)[0] AS FromNode, type(r) AS Relationship, labels(m)[0] AS ToNode
            RETURN DISTINCT FromNode, Relationship, ToNode
            ORDER BY FromNode, Relationship
        """)
        if result:
            st.table(result)
    except Exception as e:
        st.error(f"Error: {e}")


def display_results_as_table(results):
    """Display query results as a Streamlit table."""
    if not results:
        st.info("No results found.")
        return
    
    import pandas as pd
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)


def display_results_as_graph_text(results):
    """Display results as a Graphviz graph using st.graphviz_chart()."""
    if not results or len(results) == 0:
        return
    
    sample = results[0] if results else {}
    columns = list(sample.keys())
    
    if len(columns) < 2:
        st.info("Need at least 2 columns to show relationships.")
        return
    
    nodes = {}
    edges = set()
    color_map = {0: "#1f77b4", 1: "#2ca02c", 2: "#ff7f0e", 3: "#d62728", 4: "#9467bd"}
    node_colors = {}
    
    for row in results[:30]:
        row_values = []
        for i, col in enumerate(columns):
            val = row.get(col)
            if val is not None and str(val).strip():
                val_str = str(val).strip()
                node_id = val_str.replace('"', '\\"').replace('\n', ' ')[:50]
                if node_id not in nodes:
                    nodes[node_id] = f"{col}:\\n{node_id}"
                    node_colors[node_id] = color_map.get(i % 5, "#888888")
                row_values.append(node_id)
        
        for i in range(len(row_values) - 1):
            edges.add((row_values[i], row_values[i + 1]))
    
    if not nodes:
        st.info("No data to visualise.")
        return
    
    dot_lines = ["digraph G {", "    rankdir=LR;", "    node [shape=box, style=filled, fontsize=10];", "    edge [fontsize=9];"]
    
    for node_id, label in nodes.items():
        color = node_colors.get(node_id, "#888888")
        safe_id = node_id.replace('"', '\\"')
        safe_label = label.replace('"', '\\"')
        dot_lines.append(f'    "{safe_id}" [label="{safe_label}", fillcolor="{color}", fontcolor="white"];')
    
    for source, target in edges:
        safe_source = source.replace('"', '\\"')
        safe_target = target.replace('"', '\\"')
        dot_lines.append(f'    "{safe_source}" -> "{safe_target}";')
    
    dot_lines.append("}")
    dot_string = "\n".join(dot_lines)
    
    try:
        st.graphviz_chart(dot_string, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render graph: {e}")
        with st.expander("DOT Source"):
            st.code(dot_string, language="dot")


# Tabs (only shown when connected)
tab1, tab2, tab3 = st.tabs(["Chat with Graph", "Schema", "Examples"])

# --- TAB 2: Schema ---
with tab2:
    st.subheader("Database Schema")
    display_schema(st.session_state.graph)
    st.markdown("---")
    display_schema_as_table(st.session_state.graph)

# --- TAB 3: Examples ---
with tab3:
    st.subheader("Example Queries")
    st.markdown("Click to copy, then paste in the Chat tab:")
    
    for query in EXAMPLE_QUERIES:
        st.code(query, language=None)

# --- TAB 1: Chat ---
with tab1:
    chat_container = st.container()
    prompt = st.chat_input("Ask about Northwind data...")
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("cypher"):
                    with st.expander("Cypher Query"):
                        st.code(msg["cypher"], language="cypher")
                if msg.get("results"):
                    with st.expander("Results Table"):
                        display_results_as_table(msg["results"])
                    if len(msg["results"]) >= 2:
                        with st.expander("Graph View"):
                            display_results_as_graph_text(msg["results"])

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Querying graph..."):
                    try:
                        response = st.session_state.chain.invoke(prompt)
                        result = response['result']
                        
                        cypher = None
                        evidence = []
                        
                        if 'intermediate_steps' in response:
                            steps = response['intermediate_steps']
                            if len(steps) >= 1:
                                cypher = steps[0].get('query', '')
                            if len(steps) >= 2:
                                evidence = steps[1].get('context', [])

                        st.markdown(result)
                        
                        if cypher:
                            with st.expander("Generated Cypher Query", expanded=False):
                                st.code(cypher, language="cypher")
                        
                        if evidence:
                            with st.expander("Query Results", expanded=True):
                                display_results_as_table(evidence)
                            
                            if len(evidence) >= 2:
                                with st.expander("Graph View", expanded=False):
                                    display_results_as_graph_text(evidence)
                        else:
                            st.info("No data returned from query.")

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result,
                            "cypher": cypher,
                            "results": evidence
                        })
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
