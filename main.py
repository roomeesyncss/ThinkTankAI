
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import json


client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="🔥 ThinkTankAI", page_icon="🔥", layout="wide")

st.title("ThinkTankAI")
st.subheader("Your AI-powered Hackathon Brainstorm Room")
st.write("Generate ideas, refine them, collaborate in real-time, and launch projects with us!")

with st.sidebar:
    st.header("Forge Settings")
    assistant_tone = st.selectbox("Assistant Tone", ["Creative", "Analytical", "Supportive", "Challenger"])
    max_tokens = st.slider("Max Tokens", 50, 500, 150, step=50)
    temperature = st.slider("Creativity Level", 0.0, 2.0, 1.5, step=0.1)

    if st.button("Clear Chat History"):
        st.session_state["chat_history"] = []
        st.session_state["ideas"] = []
        st.session_state["has_responded"] = False

# Tone-based prompts for the assistant
tone_prompts = {
    "Creative": "You are a highly imaginative assistant, generating outside-the-box ideas.",
    "Analytical": "You are a data-driven assistant who evaluates ideas critically.",
    "Supportive": "You are an encouraging assistant, reinforcing ideas with positive insights.",
    "Challenger": "You are a questioning assistant, pushing for stronger arguments and clarity."
}

# Initialize session states
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{"role": "system", "content": tone_prompts[assistant_tone]}]
if "ideas" not in st.session_state:
    st.session_state["ideas"] = []
if "has_responded" not in st.session_state:
    st.session_state["has_responded"] = False

st.markdown("### 💡 Idea Generation Zone")
user_input = st.text_input("Enter your theme, challenge, or idea:", placeholder="e.g., 'Eco-friendly solutions'")

if user_input and not st.session_state["has_responded"]:
    st.session_state["chat_history"].append({"role": "user", "content": user_input})

    # Generate idea using the Groq API
    completion = client.chat.completions.create(
        model="llama-3.2-1b-preview",
        messages=st.session_state["chat_history"],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )

    assistant_response = ""
    response_container = st.empty()
    progress_bar = st.progress(0)

    # Stream and display response
    for i, chunk in enumerate(completion):
        chunk_text = chunk.choices[0].delta.content or ""
        assistant_response += chunk_text
        response_container.markdown(f"**Llama’s Suggestion:** {assistant_response}")
        progress_bar.progress(min(i / max_tokens, 1.0))

    progress_bar.empty()

    # Save the generated idea
    st.session_state["ideas"].append({
        "user_idea": user_input,
        "assistant_response": assistant_response,
        "votes": 0,
        "comments": []
    })
    st.session_state["chat_history"].append({"role": "assistant", "content": assistant_response})
    st.session_state["has_responded"] = True

st.markdown("### Your Brainstorm Board")
sorted_ideas = sorted(st.session_state["ideas"], key=lambda x: x["votes"], reverse=True)

for idx, idea in enumerate(sorted_ideas):
    st.markdown(f"**Idea #{idx + 1}:** {idea['user_idea']}")
    st.write(f"**Llama’s Suggestion:** {idea['assistant_response']}")

    # Upvote Button
    if st.button(f"👍 Upvote ({idea['votes']})", key=f"vote_{idx}"):
        idea["votes"] += 1
        st.rerun()

    # Refinement Section
    if st.button("🔄 Refine Idea", key=f"refine_{idx}"):
        st.session_state["chat_history"].append(
            {"role": "user", "content": f"Refine the idea: {idea['assistant_response']}"})
        refine_completion = client.chat.completions.create(
            model="llama-3.2-3b-preview",
            messages=st.session_state["chat_history"],
            temperature=temperature,
            max_tokens=max_tokens
        )
        refined_response = refine_completion.choices[0].message["content"]
        idea["assistant_response"] = refined_response
        st.rerun()

    # Comment Section
    comment_input = st.text_input("Add a comment:", key=f"comment_input_{idx}")
    if st.button("Post Comment", key=f"post_comment_{idx}"):
        if comment_input:
            idea["comments"].append(comment_input)
            st.session_state[f"comment_input_{idx}"] = ""
            st.rerun()


    if idea["comments"]:
        st.markdown("**Comments:**")
        for comment in idea["comments"]:
            st.write(f"- {comment}")

# Export to JSON
st.markdown("### 📥 Export Options")
if st.button("Download Ideas as JSON"):
    st.download_button("Download JSON", data=json.dumps(st.session_state["ideas"]), file_name="ideas.json")

# Reset for new inputs
if not user_input:
    st.session_state["has_responded"] = False

# Footer
st.markdown("---")
st.caption("Powered by 🔥 ThinkTankAI")
