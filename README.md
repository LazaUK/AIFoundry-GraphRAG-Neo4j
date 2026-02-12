# Northwind: Graph RAG with Neo4, Azure AI Foundry and Langchain

This repo demonstrates how to deploy a **Neo4j** graph database pre-loaded with the _Northwind_ dataset and use it as a knowledge base for Graph RAG workflows.

The solution includes a containerised **Neo4j** backend and a **Streamlit** frontend powered by **Azure AI Foundry** and **Langchain**.

> [!NOTE]
> This project utilises the _Northwind_ dataset, kindly shared by Martin O'Hanlon and the Neo4j team on this [repository](https://github.com/neo4j-graph-examples/northwind). All CSV data files used in the graph import are derived directly from this original work.

## 📑 Table of Contents:
- [Part 1: Environment & Authentication]
- [Part 2: Backend - Neo4j Deployment]
- [Part 3: Frontend - Streamlit App Deployment]
- [Part 4: Graph RAG Samples]

## Part 1: Environment & Authentication

### 1.1. Prerequisites
The solution uses Microsoft **Entra ID** authentication via the `azure-identity` package. Please, ensure that you:

- loged in using `az login` command to retrieve Entra ID tokens,
- have relevant RBAC (role-based access control) role assigned to access Azure AI Foundry's deployment.

### 1.2. Setup & Dependencies
Install all required libraries, including those for Azure identity and Neo4j orchestration, using the provided `requirements.txt`:

``` PowerShell
pip install -r requirements.txt
```

### 1.3. Configuration
The app uses `DefaultAzureCredential()`, so no static API keys are required. Simply configure these variables:

| Variable                | Description                                       |
| ----------------------- | ------------------------------------------------- |
| AZURE_OPENAI_API_BASE   | Your Azure AI Foundry project endpoint            |
| AZURE_OPENAI_API_DEPLOY | Your model deployment name (e.g., `gpt-4.1-mini`) |

> [!TIP]
> Provided Neo4j backend is set with `neo4j` as a user account, and `northwind` as its password.
