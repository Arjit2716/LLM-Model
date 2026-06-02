import os
from dotenv import load_dotenv

from pinecone import Pinecone
from google import genai
from google.genai import types
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# =========================
# Load Environment Variables
# =========================
load_dotenv(override=True)

# =========================
# Validate Environment
# =========================
required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# =========================
# Gemini Client
# =========================
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# =========================
# Embedding Model
# =========================
embeddings = GoogleGenerativeAIEmbeddings(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    model="models/gemini-embedding-001"
)

# Test Embeddings
try:
    test_vec = embeddings.embed_query("hello")
    print(f"Embedding Model Ready | Dimension = {len(test_vec)}")
except Exception as e:
    print("Embedding Error:", e)
    exit()

# =========================
# Pinecone Setup
# =========================
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

print("Pinecone Connected Successfully")

# =========================
# Chat History
# Store as types.Content objects for compatibility with new google-genai SDK
# =========================
history: list[types.Content] = []

# =========================
# Query Rewriter
# =========================
def transform_query(question: str) -> str:
    """Rewrite a follow-up question into a standalone question using chat history."""

    # Build contents: history + new user question
    contents = history + [types.UserContent(question)]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a query rewriting expert.\n\n"
                "Based on the provided chat history, "
                "rephrase the follow-up user question into a "
                "complete standalone question.\n\n"
                "Only return the rewritten question. "
                "Do not explain anything."
            )
        )
    )

    return response.text.strip()


# =========================
# Retrieve Context
# =========================
def retrieve_context(question: str) -> str:
    """Embed the question and retrieve top-k matching chunks from Pinecone."""

    query_vector = embeddings.embed_query(question)

    search_results = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )

    print("\n========== RETRIEVED CHUNKS ==========\n")

    context_chunks = []

    for i, match in enumerate(search_results["matches"], start=1):
        print(f"Chunk {i}")
        print(f"Score: {match['score']:.4f}")
        print("-" * 50)

        text = match["metadata"].get("text", "")
        print(text[:500])
        print()

        context_chunks.append(text)

    print("=====================================\n")

    return "\n\n".join(context_chunks)


# =========================
# Main Chat Function
# =========================
def chatting(question: str) -> None:

    try:
        # Rewrite follow-up questions into standalone queries
        rewritten_question = transform_query(question)
        print(f"\nRewritten Query: {rewritten_question}")

        # Retrieve relevant context from Pinecone
        context = retrieve_context(rewritten_question)

        if not context.strip():
            print("\n🤖: I could not find relevant information in the document.")
            return

        # Add original user question to history BEFORE generating answer
        history.append(types.UserContent(question))

        # Generate answer grounded in retrieved context
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a Data Structure and Algorithm Expert.\n\n"
                    "Answer ONLY from the provided context.\n\n"
                    "If the answer is not available in the context, "
                    'say exactly: "I could not find the answer in the provided document."\n\n'
                    f"Context:\n\n{context}"
                )
            )
        )

        answer = response.text

        # Add model response to history
        history.append(types.ModelContent(answer))

        print(f"\n🤖: {answer}")

    except Exception as e:
        print(f"\nError: {e}")
        # Remove the user message if answer generation failed
        # to keep history consistent
        if history and history[-1].role == "user":
            history.pop()


# =========================
# Main Loop
# =========================
def main() -> None:

    print("\nDSA RAG Chatbot Started")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not question:
            continue

        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        chatting(question)


if __name__ == "__main__":
    main()