# An example LLM chatbot using Cohere API and Streamlit that references a PDF
# Adapted from the StreamLit OpenAI Chatbot example - https://github.com/streamlit/llm-examples/blob/main/Chatbot.py

import streamlit as st
import cohere
import fitz # An alias for PyMuPDF

def pdf_to_documents(pdf_path):
    """
    Converts a PDF to a list of 'documents' which are chunks of a larger document that can be easily searched 
    and processed by the Cohere LLM. Each 'document' chunk is a dictionary with a 'title' and 'snippet' key
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries representing the documents. Each dictionary has a 'title' and 'snippet' key.
        Example return value: [{"title": "Page 1 Section 1", "snippet": "Text snippet..."}, ...]
    """

    doc = fitz.open(pdf_path)
    documents = []
    text = ""
    chunk_size = 1000
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        part_num = 1
        for i in range(0, len(text), chunk_size):
            documents.append({"title": f"Page {page_num + 1} Part {part_num}", "snippet": text[i:i + chunk_size]})
            part_num += 1
    return documents

# Add a sidebar to the Streamlit app
with st.sidebar:
    if hasattr(st, "secrets"):
        if "COHERE_API_KEY" in st.secrets.keys():
            cohere_api_key = st.secrets["COHERE_API_KEY"]
            # st.write("API key found.")
        else:
            cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
            st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    else:
        cohere_api_key = st.text_input("Cohere API Key", key="chatbot_api_key", type="password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    
    my_documents = []
    my_documents = pdf_to_documents('docs/Schedule.pdf')

    # st.write(f"Selected document: {selected_doc}")

# Set the title of the Streamlit app
st.title("💬 Schedule Manager")

# Initialize the chat history with a greeting message
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "text": "Hi! I'm your personal Study Schedule Manager. Lets start by telling me what classes you are taking and if you have any after school activities. Please let me know if the schedule provided needs to be tweaked for your benefit."}]

# Display the chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# Get user input
if prompt := st.chat_input():
    # Stop responding if the user has not added the Cohere API key
    if not cohere_api_key:
        st.info("Please add your Cohere API key to continue.")
        st.stop()

    # Create a connection to the Cohere API
    client = cohere.Client(api_key=cohere_api_key)
    
    # Display the user message in the chat window
    st.chat_message("user").write(prompt)

    preamble = """You are a Scheduling helper bot.
    You help people structure an after school schedule around the classes they take, the extracurricular activities they do, and allocate times for recreation.
    Your Goal is to allow the user to effectively structure a schedule for studying classes.
    You will try to provide a attiquite after school schedule for this person that can be tweaked at the user's request.
    This is primarily used to allocate time for studying and home learning for students and student atheletes.
    Finish with asking the user if they would like to tweak anything about their schedule, or if they need to study for a particular class more than another.
    Assume school starts from 8:35 AM and ends at 3:00 PM from monday to friday if the user does not specify the times"""
    

    # Send the user message and pdf text to the model and capture the response
    response = client.chat(chat_history=st.session_state.messages,
                           message=prompt,
                           documents=my_documents,
                           prompt_truncation='AUTO',
                           preamble=preamble)
    
    # Add the user prompt to the chat history
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    # Add the response to the chat history
    msg = response.text
    st.session_state.messages.append({"role": "assistant", "text": msg})

    # Write the response to the chat window
    st.chat_message("assistant").write(msg)