import os
import warnings
import asyncio

warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv(override=True)


async def index_document():

    # ==========================
    # Validate Environment
    # ==========================
    required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing required environment variable: {var}")

    # ==========================
    # Load PDF
    # ==========================
    PDF_PATH = "./dsa.pdf"

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")

    pdf_loader = PyPDFLoader(PDF_PATH)

    raw_docs = await pdf_loader.aload()

    print(f"PDF Loaded | Pages: {len(raw_docs)}")

    # ==========================
    # Chunking
    # ==========================
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )

    chunked_docs = text_splitter.split_documents(raw_docs)

    # Remove extremely small chunks
    chunked_docs = [
        doc for doc in chunked_docs
        if len(doc.page_content.strip()) > 100
    ]

    # Add metadata
    for i, doc in enumerate(chunked_docs):
        doc.metadata["chunk_id"] = i

    print(f"Total Chunks: {len(chunked_docs)}")

    # ==========================
    # Embedding Model
    # ==========================
    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-embedding-001"
    )

    print("Embedding Model Configured")

    # Test embedding
    test_vector = embeddings.embed_query("hello")
    print(f"Embedding Dimension: {len(test_vector)}")

    # ==========================
    # Store in Pinecone (batched to avoid rate limits)
    # Google free tier: ~1500 requests/min for embeddings
    # We use small batches + delay to stay safely under the limit
    # ==========================
    BATCH_SIZE = 10          # chunks per batch
    DELAY_SECONDS = 5        # wait between batches

    total = len(chunked_docs)
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Uploading to Pinecone in {total_batches} batches of {BATCH_SIZE}...")

    vector_store = None

    for batch_num in range(total_batches):
        start = batch_num * BATCH_SIZE
        end = min(start + BATCH_SIZE, total)
        batch = chunked_docs[start:end]

        print(f"  Batch {batch_num + 1}/{total_batches} — chunks {start + 1}–{end}...")

        try:
            if vector_store is None:
                # First batch: create the vector store
                vector_store = await PineconeVectorStore.afrom_documents(
                    documents=batch,
                    embedding=embeddings,
                    index_name=os.getenv("PINECONE_INDEX_NAME")
                )
            else:
                # Subsequent batches: add to existing store
                await vector_store.aadd_documents(batch)

        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"  ⚠️  Rate limit hit — waiting 30s before retrying batch {batch_num + 1}...")
                await asyncio.sleep(30)
                # Retry the same batch once
                if vector_store is None:
                    vector_store = await PineconeVectorStore.afrom_documents(
                        documents=batch,
                        embedding=embeddings,
                        index_name=os.getenv("PINECONE_INDEX_NAME")
                    )
                else:
                    await vector_store.aadd_documents(batch)
            else:
                raise

        # Delay between batches (skip after the last one)
        if batch_num < total_batches - 1:
            await asyncio.sleep(DELAY_SECONDS)

    print(f"✅ All {total} chunks stored successfully in Pinecone")


if __name__ == "__main__":
    asyncio.run(index_document())