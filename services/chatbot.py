from typing import List, Dict
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# ================= Embeddings =================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ================= Vector DB =================
vectorstore = FAISS.load_local(
    "./vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

# ================= LLM =================
llm = ChatGroq(
    model="groq/compound-mini",
    temperature=0
)

# ================= Prompt =================
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful restaurant assistant."
        "Answer strictly using the provided context. "
        "If the answer is not in the context, say you do not have that information."
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion:\n{question}"
    )
])

# ================= Runnable Chain =================
chatbot_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)



# ================= Chat Function =================
from typing import List
from datetime import datetime
from datetime import datetime, timezone

datetime.now(timezone.utc).isoformat()

def chat(new_message: str, history: List) -> dict:
    reply_text = chatbot_chain.invoke(new_message)

    last_id = history[-1].id if history else 0

    return {
    "id": last_id + 1,
    "role": "bot",
    "message": reply_text,
    "time": datetime.now(timezone.utc).isoformat()
}


