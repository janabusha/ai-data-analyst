import streamlit as st
import analysis

st.title("Intelligent Data Analysis Assistant")
st.write("Upload a CSV or Excel file to inspect and analyze your data.")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"],
)

try:
    if uploaded_file is not None:
        dataset = analysis.load_dataset(uploaded_file)
        st.write("Uploaded file:", uploaded_file.name)
        st.dataframe(dataset)
except FileNotFoundError as error:
    st.error(str(error))
except ValueError as error:
    st.error(str(error))
except st.errors.EmptyDataError as error:
    st.error(str(error))
except st.errors.ParserError as error:
    st.error(str(error))

    


