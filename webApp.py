import streamlit as st
import pandas as pd
from io import BytesIO
import os

# --- Page Config ---
st.set_page_config(
    page_title="Employee CSV Mapper",
    page_icon="🐼",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Style ---
st.markdown("""
<style>
    .stApp { background-color: #f4f6f8; font-family: 'Segoe UI', sans-serif; }
    .footer { color: #555; font-size: 12px; text-align: center; margin-top: 30px; }
    .stButton>button { border-radius: 8px; padding: 8px 20px; font-size: 14px; }
    .tab-header { font-size:20px; font-weight:bold; color:#333; }
</style>
""", unsafe_allow_html=True)

# --- Header Logo ---
try:
    st.image("panda.jpg", width=150)
except FileNotFoundError:
    st.warning("Logo image not found. Continuing without image...")

st.title("📊 Employee CSV Mapper")
st.markdown("H&E Department - Nethmini")
st.markdown("---")

# --- Database Path ---
db_path = "database.xlsx"

# --- Tabs ---
tab1, tab2 = st.tabs(["CSV Processing", "Database Management"])

# ================================
# TAB 1: CSV PROCESSING
# ================================
with tab1:
    st.subheader("⚙️ Process Daily CSV")

    # Load database if exists
    if os.path.exists(db_path):
        try:
            db_df = pd.read_excel(db_path)
            st.info(f"✅ Loaded database.xlsx ({len(db_df)} employees).")
        except Exception as e:
            st.error(f"Failed to load database.xlsx: {e}")
            db_df = None
    else:
        db_df = None

    # Upload daily CSV
    csv_file = st.file_uploader("Upload Daily CSV", type=["csv"])

    # Optional database upload
    uploaded_db = st.file_uploader("Upload Employee Database (Optional)", type=["xlsx"])
    if uploaded_db:
        db_df = pd.read_excel(uploaded_db)
        st.success(f"✅ Loaded uploaded database ({len(db_df)} employees).")

    # Process Button
    if st.button("Process CSV"):
        if not csv_file:
            st.warning("❌ Please upload the daily CSV file.")
        elif db_df is None:
            st.error("❌ No database found. Please upload database.xlsx or use uploaded file.")
        else:
            try:
                csv_df = pd.read_csv(csv_file)
                csv_df.rename(columns={"Username": "EmpNo"}, inplace=True)

                # Merge
                merged_df = pd.merge(csv_df, db_df, on="EmpNo", how="left")
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

                # Messages
                st.success("🎉 CSV processed successfully!")
                if missing:
                    st.warning(f"⚠️ Missing Employee Numbers: {', '.join(map(str, missing))}")

                # Download
                st.download_button(
                    label="⬇️ Download Processed Excel",
                    data=output,
                    file_name="processed.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

# ================================
# TAB 2: DATABASE MANAGEMENT
# ================================
with tab2:
    st.subheader("🛠️ Manage Employee Database")

    # Load database
    if os.path.exists(db_path):
        db_df = pd.read_excel(db_path)
    else:
        db_df = pd.DataFrame(columns=["EmpNo", "Name"])

    # Show current database
    with st.expander("View Current Database"):
        st.dataframe(db_df)

    # --- Insert new employee ---
    st.markdown("### ➕ Insert New Employee")
    new_emp_no = st.text_input("Employee Number (Insert)", key="insert_emp")
    new_name = st.text_input("Employee Name (Insert)", key="insert_name")
    if st.button("Insert Employee"):
        if new_emp_no and new_name:
            if new_emp_no in db_df["EmpNo"].astype(str).values:
                st.warning("Employee number already exists!")
            else:
                db_df = pd.concat([db_df, pd.DataFrame({"EmpNo":[new_emp_no],"Name":[new_name]})], ignore_index=True)
                db_df.to_excel(db_path, index=False)
                st.success(f"Inserted {new_name} ({new_emp_no}) successfully!")
        else:
            st.warning("Please enter both Employee Number and Name.")

    # --- Update existing employee ---
    st.markdown("### ✏️ Update Employee Name")
    upd_emp_no = st.text_input("Employee Number to Update", key="update_emp")
    upd_name = st.text_input("New Name", key="update_name")
    if st.button("Update Employee"):
        if upd_emp_no in db_df["EmpNo"].astype(str).values:
            db_df.loc[db_df["EmpNo"].astype(str) == upd_emp_no, "Name"] = upd_name
            db_df.to_excel(db_path, index=False)
            st.success(f"Updated Employee {upd_emp_no} to {upd_name}")
        else:
            st.warning(f"Employee number {upd_emp_no} not found.")

    # --- Delete an employee ---
    st.markdown("### ❌ Delete Employee")
    del_emp_no = st.text_input("Employee Number to Delete", key="delete_emp")
    if st.button("Delete Employee"):
        if del_emp_no in db_df["EmpNo"].astype(str).values:
            db_df = db_df[db_df["EmpNo"].astype(str) != del_emp_no]
            db_df.to_excel(db_path, index=False)
            st.success(f"Deleted Employee {del_emp_no} successfully!")
        else:
            st.warning(f"Employee number {del_emp_no} not found.")

# --- Footer Logo (optional) ---
try:
    st.image("panda.jpg", width=400)
except FileNotFoundError:
    pass

# --- Footer Text ---
st.markdown("<div class='footer'>© H&E Department - Nethmini</div>", unsafe_allow_html=True)
