# DSA RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers Data Structures and Algorithms questions from a PDF document using Google Gemini Embeddings, Pinecone Vector Database, and Gemini LLM.

## Features

* PDF document ingestion
* Intelligent text chunking
* Gemini Embeddings (`gemini-embedding-001`)
* Pinecone Vector Database
* Semantic Search
* Context-Aware Question Answering
* Query Rewriting
* Conversational Chat Interface
* Source-based Responses

## Architecture

```text
PDF Document
      ↓
Document Loader
      ↓
Text Chunking
      ↓
Gemini Embeddings
      ↓
Pinecone Vector DB
      ↓
User Question
      ↓
Query Embedding
      ↓
Vector Search
      ↓
Relevant Context Retrieval
      ↓
Gemini LLM
      ↓
Final Answer
```

## Tech Stack

* Python
* Google Gemini API
* LangChain
* Pinecone
* PyPDFLoader
* Python Dotenv

## Project Structure

```text
.
├── rag.py              # PDF indexing pipeline
├── query.py            # RAG chatbot
├── dsa.pdf             # Knowledge source
├── .env                # Environment variables
├── requirements.txt
└── README.md
```

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/dsa-rag-chatbot.git
cd dsa-rag-chatbot
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key

PINECONE_API_KEY=your_pinecone_api_key

PINECONE_INDEX_NAME=your_index_name
```

## Create Pinecone Index

Configuration:

```text
Dimension: 3072
Metric: Cosine
```

## Index Documents

```bash
python rag.py
```

Output:

```text
PDF Loaded
Chunking Completed
Embedding Model Configured
Uploading to Pinecone...
Data Stored Successfully
```

## Start Chatbot

```bash
python query.py
```

Example:

```text
You: What is AVL Tree?

Bot: AVL Tree is a self-balancing Binary Search Tree in which the difference between the heights of left and right subtrees cannot exceed 1.
```

## Challenges Solved

* API key management
* Pinecone vector dimension mismatch
* Embedding model integration
* Retrieval quality optimization
* Chunking strategy improvements
* Query rewriting for follow-up questions
* Context-based answer generation

## Future Improvements

* Hybrid Search (BM25 + Vector Search)
* Reranking
* Metadata Filtering
* Source Citations
* Streamlit UI
* Multi-PDF Support
* Agentic RAG
* Conversation Memory

## Learning Outcomes

This project helped in understanding:

* Retrieval-Augmented Generation (RAG)
* Vector Embeddings
* Semantic Search
* Vector Databases
* Pinecone Indexing
* LangChain Integration
* Large Language Models
* End-to-End GenAI Application Development

## Author

Arjit Gupta

B.Tech Final Year | AI, GenAI & Software Development Enthusiast
