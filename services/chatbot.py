from collections import deque
from typing import Dict
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
        "You are a helpful restaurant assistant. "
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

# ================= Memory =================
chat_history = deque(maxlen=5)
message_id = 0


def chat(query: str) -> Dict:
    global message_id

    user_message = {
        "id": message_id,
        "role": "user",
        "message": query
    }
    message_id += 1

    reply_text = chatbot_chain.invoke(query)

    bot_message = {
        "id": message_id,
        "role": "bot",
        "reply": reply_text
    }
    message_id += 1

    chat_history.append(user_message)
    chat_history.append(bot_message)

    return {
        "user": user_message,
        "bot": bot_message,
        "last_5_messages": list(chat_history)
    }
