import streamlit as st

def main():
    st.set_page_config(
        page_title="Multi-Agent Healthcare System",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Multi-Agent Healthcare System")
    st.write("Welcome to the Multi-Agent Healthcare Platform")
    
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Upload Documents", "X-Ray Analysis", "Therapy Recommendations"])
    
    if page == "Home":
        st.header("Home")
        st.write("This is a multi-agent healthcare system for:")
        st.write("- Document ingestion and PII masking")
        st.write("- X-ray image classification")
        st.write("- OTC therapy recommendations")
        st.write("- Pharmacy matching and inventory")
        st.write("- Doctor escalation and tele-consult")
    
    elif page == "Upload Documents":
        st.header("Upload Documents")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_file:
            st.success(f"File uploaded: {uploaded_file.name}")
    
    elif page == "X-Ray Analysis":
        st.header("X-Ray Analysis")
        st.write("Upload X-ray images for classification")
    
    elif page == "Therapy Recommendations":
        st.header("Therapy Recommendations")
        st.write("Get OTC therapy recommendations")

        # python -m streamlit run app.py 

if __name__ == "__main__":
    main()
