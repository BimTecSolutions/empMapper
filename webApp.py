import streamlit as st
import pandas as pd
from io import BytesIO
import os

# --- Page Config ---
st.set_page_config(
    page_title="Employee CSV Mapper",
    page_icon="🐼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Style ---
st.markdown("""
<style>
    .stApp {
        background-color: #f4f6f8;
        font-family: 'Segoe UI', sans-serif;
    }
    .footer {
        color: #555;
        font-size: 12px;
        text-align: center;
        margin-top: 30px;
    }
    .stButton>button {
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Logo (optional) ---
try:
    st.image("panda.jpg", width=150)
except FileNotFoundError:
    st.warning("Logo image not found. Continuing without image...")

# --- Header Text ---
st.title("📊 Daily CSV Employee Mapper")
st.markdown("H&E Department - ANS")
st.markdown("---")

# --- Database ---
db_path = "database.xlsx"
db_df = None
if os.path.exists(db_path):
    try:
        db_df = pd.read_excel(db_path)
        st.info(f"✅ Loaded database.xlsx automatically ({len(db_df)} employees).")
    except Exception as e:
        st.error(f"Failed to load database.xlsx: {e}")

# --- CSV Upload ---
csv_file = st.file_uploader("Upload Daily CSV File", type=["csv"])

# --- Process Button ---
if st.button("⚙️ Process CSV"):
    if not csv_file:
        st.warning("❌ Please upload the daily CSV file.")
    else:
        try:
            # Read daily CSV
            csv_df = pd.read_csv(csv_file)
            csv_df.rename(columns={"Username": "EmpNo"}, inplace=True)

            # Use uploaded database if user uploads one
            uploaded_db = st.file_uploader("Upload Employee Database (Excel) [Optional]", type=["xlsx"])
            if uploaded_db:
                db_df = pd.read_excel(uploaded_db)
                st.success(f"✅ Loaded uploaded database ({len(db_df)} employees).")

            if db_df is None:
                st.error("❌ No database found. Please upload database.xlsx or use an uploaded file.")
            else:
                # Merge CSV and database
                merged_df = pd.merge(csv_df, db_df, on="EmpNo", how="left")

                # Detect missing employees
                missing = merged_df[merged_df["Name"].isna()]["EmpNo"].tolist()
                merged_df["Name"] = merged_df["Name"].fillna("")

                # Final DataFrame
                final_df = merged_df[["EmpNo", "Name", "Total Good Pieces", "Total Defect Pieces"]]
                final_df.columns = ["Employee No", "Employee Name", "Total Good Pcs", "Total Defects Pcs"]

                # Convert to Excel in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    final_df.to_excel(writer, index=False, sheet_name="Processed")
                    ws = writer.sheets["Processed"]
                    # Auto-fit columns
                    for col in ws.columns:
                        max_length = 0
                        column = col[0].column_letter
                        for cell in col:
                            try:
                                if cell.value:
                                    max_length = max(max_length, len(str(cell.value)))
                            except:
                                pass
                        ws.column_dimensions[column].width = max_length + 2
                output.seek(0)

                # Display messages
                st.success("🎉 CSV processed successfully!")
                if missing:
                    st.warning(f"⚠️ Missing Employee Numbers: {', '.join(map(str, missing))}")

                # Download button
                st.download_button(
                    label="⬇️ Download Processed Excel",
                    data=output,
                    file_name="processed.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

# --- Footer Logo (optional) ---
try:
    st.image("panda.jpg", width=400)
except FileNotFoundError:
    pass

# --- Footer Text ---
st.markdown("<div class='footer'>© H&E Department - ANS</div>", unsafe_allow_html=True)
