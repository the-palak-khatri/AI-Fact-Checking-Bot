import streamlit as st
import requests
import sys
import os
import warnings

# Suppress Deprecation Warnings from transformers/streamlit
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false" 
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message="Accessing __path__ from")

# Add the project root (parent dir of `frontend`) so `backend` is importable
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from .rag_pipeline import extract_text_from_file

BACKEND_URL = "https://ai-fact-checking-bot.onrender.com/fact-check"

def call_fact_checker(input_text):
    try:
        # Sending the data to your deployed backend
        response = requests.post(
            BACKEND_URL,
            json={"text": input_text},
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return None 

# Page config
st.set_page_config(page_title="AI Fact Checker", layout="centered")

# Title
st.title("AI Fact Checker")
st.markdown("**Verify claims using AI + document-based reasoning**")

# Sidebar
st.sidebar.title("About")
st.sidebar.info(
    "This system uses Retrieval-Augmented Generation (RAG) "
    "to verify claims and detect hallucinations in AI responses."
)

# Sidebar File Upload
st.sidebar.subheader("Upload Reference Documents")
uploaded_files = st.sidebar.file_uploader(
    "Choose files for the AI to read:",
    type=["txt", "csv", "docx", "pdf"],
    accept_multiple_files=True
)

# Example queries
st.markdown("*Try these example claims:*")

# Category 1: Document-Specific (Testing Larry Stewart & Specs)
st.write("**Document Analysis:**")
st.write("- Larry Stewart's company was founded after a Thanksgiving accident.")
st.write("- The Glow-Watch battery lasts for 500 hours.")

# Category 2: Data & Tables (Testing CSV logic)
st.write("**Data Verification:**")
st.write("- The price of Widget B is exactly 25.50.")
st.write("- Widget A is cheaper than Widget B.")

# Category 3: General Knowledge (Testing FAISS/Vector DB)
st.write("**General Knowledge:**")
st.write("- Nuclear energy is one of the safest forms of energy production.")
st.write("- You can still get a sunburn on a cloudy day.")

# Input Box FIRST
query = st.text_input(
    "Enter a claim:",
    placeholder="Does hot water shower cure COVID-19?"
)

# Button
if st.button("Check Fact"):
    
    files_data = []
    if uploaded_files:
        pass

    all_extracted_text = ""
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        extracted_content = extract_text_from_file(file_bytes, uploaded_file.type) 
        all_extracted_text += extracted_content + "\n"

    with st.expander("View Raw Extracted Text (Debug)"):
        st.text(all_extracted_text)

    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Analyzing..."):

            try:
                response = requests.post(
                    "https://ai-fact-checking-bot.onrender.com/fact-check",
                    json={
                        "text": query,
                        "custom_context": all_extracted_text
                    }
                )

                # st.write(response)

                data = response.json()
                # st.write("Full API response:", data)
                # st.write("API keys", data.keys())
                
                llm_data = data.get("llm_response", {})

            except Exception as e:
                st.error("Backend not running or connection failed.")
                st.stop()

        # Verdict Section
        verdict = llm_data.get("verdict","Unknown")
        # st.write(f"{verdict}")
        confidence = llm_data.get("confidence",0)
        # st.write(f"{confidence}")
        score = llm_data.get("faithfullness_score",0)
        
        st.subheader("Verdict")
        if verdict.lower() == "true":
            st.success(verdict)
        elif verdict.lower() == "false":
            st.error(verdict)
        else:
            st.info(verdict)
        
        # Confidence Section
        st.subheader("Confidence")
        st.write(f"{round(confidence * 100, 2)}%")
        st.progress(int(confidence * 100))

        # Score Section
        # st.subheader("Faithfulness Score")
        # st.write(f"{score}")

        # Explanation Section
        st.subheader("Explanation")
        st.write(llm_data.get("explanation", "No explanation available"))
        # # Hallucination Section
        # st.subheader("Hallucination Analysis")

        # faithfulness = llm_data.get("faithfulness_score", 0)
        # risk = llm_data.get("hallucination_risk", "Unknown")

        # # if faithfulness is not None:
        # st.write(f"Faithfulness Score: {round(faithfulness, 2)}")

        # if risk.lower() == "low":
        #     st.success(f"Hallucination Risk: {risk}")
        # elif risk.lower() == "medium":
        #     st.warning(f"Hallucination Risk: {risk}")
        # else:
        #     st.error(f"Hallucination Risk: {risk}")

        # unsupported = data.get("unsupported_claims", [])

        # if unsupported:
        #     st.markdown("Unsupported Claims")
        #     for claim in unsupported:
        #         st.markdown(f"- {claim}")

        # Sources Section
        st.subheader("Sources")

        matches = data.get("top_matches", [])

        for i, match in enumerate(matches):
            with st.expander(f"Source {i+1}"):
                st.write(match["fact"])
                st.caption(f"Similarity Score: {round(match['score'], 3)}")

        # Debug View
        with st.expander("Debug (Raw Response)"):
            st.json(data)
     
