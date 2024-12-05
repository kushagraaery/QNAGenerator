import openai
import streamlit as st
import pandas as pd
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit UI Design Enhancements
st.set_page_config(page_title="Pharma Society QnA Report Generator", page_icon="💊")
st.title("💊 Pharma Society QnA Report Generator")
st.write("🔬 This Q&A generator allows users to fetch answers to predefined queries about pharmaceutical societies by entering the society name in the text box. It uses OpenAI to generate answers specific to the entered society and displays them in a tabular format. Users can download this report as an Excel file.")

# Step 1: Society Name Input with dropdown options
society_name = st.selectbox("Select the Pharmaceutical Society Name:", ["", "FLASCO", "GASCO"])

# Step 2: Define static pharma-specific questions for the society
questions = [
    "What is the membership count for society_name? Provide one word (number) only.",
    "Does society_name include opportunities in leadership for pharma professionals? Answer in one word ('yes' or 'no') only.",
    "Are there pharma sector committees like Drug Safety in society_name? Answer with one word ('yes' or 'no') only.",
    "Is society_name involved in therapeutic research collaborations? Provide one word ('yes' or 'no') only.",
    "Does society_name include top therapeutic area experts on its board? Respond with one word ('yes' or 'no') only."
]

# Initialize session state to track previous society name and report data
if "previous_society_name" not in st.session_state:
    st.session_state.previous_society_name = ""
if "report_data" not in st.session_state:
    st.session_state.report_data = pd.DataFrame(columns=["Society Name", "What is the membership count for society_name?",
                                                         "Does society_name include opportunities in leadership for pharma professionals?",
                                                         "Are there pharma sector committees like Drug Safety in society_name?",
                                                         "Is society_name involved in therapeutic research collaborations?",
                                                         "Does society_name include top therapeutic area experts on its board?"])

# Step 3: Generate the report only if a new society name is selected
if society_name and society_name != st.session_state.previous_society_name:
    st.session_state.previous_society_name = society_name

    # Prepare a list to store the answers for the selected society
    society_data = {
        "Society Name": society_name,
        "What is the membership count for society_name?": "",
        "Does society_name include opportunities in leadership for pharma professionals?": "",
        "Are there pharma sector committees like Drug Safety in society_name?": "",
        "Is society_name involved in therapeutic research collaborations?": "",
        "Does society_name include top therapeutic area experts on its board?": ""
    }

    # Replace the placeholder in questions with the selected society name
    modified_questions = [question.replace("society_name", society_name) for question in questions]

    # Fetch data from OpenAI API for each modified question
    with st.spinner("Retrieving data..."):
        for i, question in enumerate(modified_questions):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": question}]
                )
                answer = response["choices"][0]["message"]["content"].strip()
                society_data[list(society_data.keys())[i + 1]] = answer  # Add answer to corresponding column
            except Exception as e:
                st.error(f"Error with '{question}': {e}")
                society_data[list(society_data.keys())[i + 1]] = "Error"

    # Append new society data to the report
    st.session_state.report_data = pd.concat([st.session_state.report_data, pd.DataFrame([society_data])], ignore_index=True)

# Step 4: Display the report if data is available
if not st.session_state.report_data.empty:
    # Display the tabular report with static column names
    st.write("Consolidated Tabular Report:")
    st.dataframe(st.session_state.report_data)

    # Provide download option for the report
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Consolidated Report")
        return output.getvalue()

    excel_data = to_excel(st.session_state.report_data)

    st.download_button(
        label="Download Consolidated Report",
        data=excel_data,
        file_name="Consolidated_Pharma_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Chatbot Section
st.title("💬 Pharma Insights Chatbot")
st.caption("💡 The app features a chatbot powered by OpenAI for answering pharma-related queries, with quick prompts provided for easy testing.")

# Predefined Prompt Buttons in columns
st.write("**Quick Prompts for Pharma Insights**")
col1, col2, col3 = st.columns(3)

# Initialize prompt to None
prompt = None

with col1:
    if st.button("What are Genentech's top therapeutic areas?"):
        prompt = "What are Genentech's top therapeutic areas?"
with col2:
    if st.button("How is Genentech involved in drug safety initiatives?"):
        prompt = "How is Genentech involved in drug safety initiatives?"
with col3:
    if st.button("What is Roche's focus in therapeutic research?"):
        prompt = "What is Roche's focus in therapeutic research?"

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("Does Roche collaborate on oncology research?"):
        prompt = "Does Roche collaborate on oncology research?"
with col5:
    if st.button("What leadership opportunities does Roche offer in pharma?"):
        prompt = "What leadership opportunities does Roche offer in pharma?"
with col6:
    if st.button("Who are the leading experts at Genentech?"):
        prompt = "Who are the leading experts at Genentech?"

# Always show the chat input, allowing for further input even if a prompt is selected
user_input = st.chat_input("Ask a question or select a prompt...")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you with pharma insights?"}]

# Append user input or prompt to chat history
if prompt or user_input:
    user_message = prompt if prompt else user_input
    st.session_state["messages"].append({"role": "user", "content": user_message})

    # Query OpenAI API with the current messages
    with st.spinner("Generating response..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state["messages"]
            )
            bot_reply = response.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            bot_reply = f"Error retrieving response: {e}"
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

# Display chat history sequentially
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
