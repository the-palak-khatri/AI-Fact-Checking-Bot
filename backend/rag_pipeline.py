from data import documents
#from sentence_transformers import SentenceTransformer
import numpy as np
#import faiss
from groq import Groq
import os
from dotenv import load_dotenv
import json
import pandas as pd
from docx import Document
from pypdf import PdfReader
import io   

# Load Environment Variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load Embedding Model
#model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert Knowledge Base to Embeddings
#kb_embeddings = model.encode(documents)

# Convert to numpy array
#kb_embeddings = np.array(kb_embeddings)

# Create FAISS Index
#dimension = kb_embeddings.shape[1]

# Initialize Gemini Model
# llm = genai.GenerativeModel("gemini-2-flash")
MODEL_NAME = "llama-3.3-70b-versatile"

# L2 distance index (Euclidean distance)
#index = faiss.IndexFlatL2(dimension)

# Add embeddings to index
#index.add(kb_embeddings)

# Cache Definition
cache = {}

# Extract text from files
def extract_text_from_file(file_content, file_type):
    if file_type == "text/plain":
        return file_content.decode("utf-8")

    elif file_type == "application/pdf":
        pdf = PdfReader(io.BytesIO(file_content))
        return " ".join([page.extract_text() for page in pdf.pages])
    
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(io.BytesIO(file_content))
        return " ".join([p.text for p in doc.paragraphs])
    
    elif file_type == "text/csv":
        df = pd.read_csv(io.BytesIO(file_content))
        return df.to_string()     #  converts whole table to text for the AI

    return ""

# Fact Checking Function 
async def check_fact(user_input: str, custom_context: str = ""):
    # Check cache FIRST
    # if user_input in cache:
        # return cache[user_input]

    # Convert user query to embedding
    #query_vector = model.encode([user_input])
    #query_vector = np.array(query_vector)

    # Search top k similar results
    k = 2
    distances, indices = index.search(query_vector, k)
    
    # Step 1 : Retrieve relevant facts
    retrieved_facts = []

    for i in range(k):
        idx = indices[0][i]
        dist = distances[0][i]

        retrieved_facts.append({
            "fact": documents[idx],
            "score": float(dist)
        })
        # score = float("score")
        # print(score)

    # Step 2: Confidence Calculattion 
    confidence = sum(m["score"] for m in retrieved_facts) / len(retrieved_facts)
    # score  = 

    # # Step 3: Halluciantion Checking
    # if score > 0.8:
    #     risk = "Low"
    # elif score > 0.5:
    #     risk = "Medium"
    # else:
    #     risk = "High"

    # Step 4: Create LLM Prompt
    # Prompt improvement to request a strict JSON block and delimit it with markers
    prompt = f"""
You are a strict, robotic, literalist AI fact-checker. You have two sources of information.

User Claim:
"{user_input}"

User Uploaded Documents (Primary Source)
{custom_context if custom_context else "No documents uploaded by user."}

Relevant Verified Facts: (Secondary Source)
{retrieved_facts}

Based on the above facts, determine:
1. PRIORITIZE the PRIMARY SOURCE. If the answer is in the uploaded documents, use that first.
2. If the Primary Source is empty or irrelevant, use the SECONDARY SOURCE.
3. If neither contains the info, use your internal training data but state: 'Verified using general AI knowledge'.
4. Give a short explanation.
5. If facts are insufficient, say "Not Enough Information"
6. Do not assume units, currencies, or symbols (like $, £, or %) if they are not explicitly present in the provided text.

IMPORTANT: You must output your response exactly between these markers"
###BEGIN_JSON
<Your JSON object here>
###END_JSON

Do not include any conversational text. Respond strictly ONLY in JSON format like:
{{
    "verdict": "True" or "False" or "Not Enough Information",
    "confidence": confidence,
    "explanation": "...",
    "faithfulness_score": "score",
}}
 """
     
    # Step 5: Call LLM
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        top_p=1.0   
    )

    output_text = response.choices[0].message.content
    #print(f"DEBUG: Raw LLM Output: {output_text}")

    # Manual PARSING logic implementation
    try:
        # Extract the text b/w the markers
        if "###BEGIN_JSON" in output_text and "###END_JSON" in output_text:
            json_string = output_text.split("###BEGIN_JSON")[1].split("###END_JSON")[0].strip()
        else:
            # Fallback: if markers are missing, try to find the first '{' and last '}'
            start = output_text.find("{")
            end = output_text.rfind("}") + 1
            if start != -1:
                json_string = output_text[start:end]
            else:
                raise ValueError("No JSON found")   
        
        parsed_output = json.loads(json_string)

    except (IndexError, json.JSONDecodeError, ValueError):
        # Final Fallback if everything fails
        try:
            parsed_output = json.loads(output_text.strip())
        except: 
            parsed_output = {
            "verdict": "Not Enough Information",
            "confidence": 0,
            "explanation": "Could not parse the AI response correctly.",
            "faithfulness_score": 0
        }

    # Step 6: Final Result Preparation
    result = {
        "query": user_input,
        "top_matches": retrieved_facts[:3],     # less data, faster LLM reasoning
        "llm_response": parsed_output
    }

    # Step 7: Store in cache BEFORE returning
    cache[user_input] = result

    # Step 8: Return the final result
    return result