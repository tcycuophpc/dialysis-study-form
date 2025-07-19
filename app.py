import streamlit as st
import pandas as pd
import io
# ➕ 輸出個人報告 Excel
        report_buffer = io.BytesIO()
        df.to_excel(report_buffer, index=False, engine='openpyxl')
        st.download_button(
            label="⬇️ 下載此筆個人報告 (Excel)",
            data=report_buffer.getvalue(),
            file_name=f"個人報告_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        from fpdf import FPDF
import os
from datetime import date

st.set_page_config("血液透析研究收案系統", layout="wide")
st.title("📝 血液透析病人研究收案系統")

DATA_FILE = "dialysis_data.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame().to_csv(DATA_FILE, index=False)

st.sidebar.title("🔐 模式選擇")
mode = st.sidebar.selectbox("選擇頁面模式", ["使用者填寫", "管理者後台"])

if mode == "管理者後台":
    password = st.sidebar.text_input("輸入管理者密碼", type="password")
    if password != "admin123":
        st.warning("密碼錯誤")
        st.stop()
    st.success("管理者登入成功")
    st.header("📊 已收資料總覽")
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df, use_container_width=True)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        
    else:
        st.info("尚無資料")
    st.stop()

with st.form("intake_form"):
    st.header("1️⃣ 基本資料")
    col1, col2, col3 = st.columns(3)
    age = col1.number_input("年齡 (歲)", 18, 120)
    sex = col2.radio("性別", ["男", "女"])
    height = col3.number_input("身高（cm）", 100.0, 250.0)
    weight = col1.number_input("體重（kg）", 30.0, 200.0)
    bmi = weight / ((height / 100) ** 2) if height > 0 else 0
    col2.metric("BMI", round(bmi, 2))
    edu = col2.selectbox("教育程度", ["國小以下", "國小", "國中", "高中/高職", "大專以上"])
    job = col3.text_input("職業")
    marital = col1.selectbox("婚姻狀況", ["未婚", "已婚", "離婚", "喪偶"])
    living = col3.selectbox("居住情形", ["與家人", "獨居", "機構", "其他"])

    st.header("2️⃣ 疾病狀態")
    dialysis_years = st.number_input("透析年資 (年)", 0.0, 50.0)
    cci = st.number_input("Charlson 合併症指數 (CCI)", 0, 20)
    med_count = st.number_input("目前服用藥物數量", 0, 50)
    sbp = st.number_input("收縮壓 (mmHg)", 80, 240)
    dbp = st.number_input("舒張壓 (mmHg)", 40, 140)

    st.header("3️⃣ 生化檢驗指標")
    creatinine = st.number_input("肌酸酐 (Creatinine)", 0.0, 20.0)
    hb = st.number_input("血色素 (Hb)", 0.0, 20.0)
    albumin = st.number_input("白蛋白 (Albumin)", 0.0, 10.0)
    phosphorus = st.number_input("血磷 (Phosphorus)", 0.0, 10.0)
    calcium = st.number_input("血鈣 (Calcium)", 0.0, 10.0)
    urr = st.number_input("尿素氮清除率 (URR, %)", 0.0, 100.0)

    st.header("4️⃣ BIA 肌肉質量測量")
    smi = st.number_input("四肢骨骼肌質量指數 (SMI, kg/m²)", 0.0, 15.0)
    smi_status = "低肌肉質量" if ((sex == "男" and smi < 7.0) or (sex == "女" and smi < 5.7)) else "正常"
    st.info(f"肌肉量狀態：{smi_status}")

    st.header("5️⃣ KCL 虛弱量表 (25 題)")
    kcl_answers = [st.selectbox(f"第 {i+1} 題", ["否", "是"], key=f"kcl_{i}") for i in range(25)]
    kcl_score = sum([1 for ans in kcl_answers if ans == "是"])
    if kcl_score <= 3:
        kcl_status = "健康"
    elif kcl_score <= 7:
        kcl_status = "虛弱前期"
    else:
        kcl_status = "虛弱"
    st.success(f"KCL 得分：{kcl_score}，分類：{kcl_status}")

    st.header("6️⃣ IPAQ-SS 身體活動量")
    vigorous = st.number_input("劇烈活動分鐘/週", 0)
    moderate = st.number_input("中等活動分鐘/週", 0)
    walk = st.number_input("步行分鐘/週", 0)
    met = vigorous*8 + moderate*4 + walk*3.3
    if met < 600:
        ipaqlvl = "低度活動"
    elif met < 1500:
        ipaqlvl = "中度活動"
    else:
        ipaqlvl = "高度活動"
    st.info(f"總 MET 分數：{int(met)}，活動分類：{ipaqlvl}")

    st.header("7️⃣ MNA-SF 營養評估")
    mna_scores = [st.slider(f"MNA-SF 第{i+1}題 (0-2分)", 0, 2, 1, key=f"mna_{i}") for i in range(6)]
    mna_total = sum(mna_scores)
    mna_status = "正常" if mna_total > 11 else "有營養不良風險"
    st.success(f"MNA-SF 總分：{mna_total}，分類：{mna_status}")

    submitted = st.form_submit_button("✅ 提交資料")
    if submitted:
        record = {
            "日期": date.today(), "年齡": age, "性別": sex, "身高": height, "體重": weight, "BMI": round(bmi, 2),
            "教育程度": edu, "職業": job, "婚姻狀況": marital, "居住情形": living,
            "透析年資": dialysis_years, "CCI": cci, "藥物數量": med_count, "SBP": sbp, "DBP": dbp,
            "Creatinine": creatinine, "Hb": hb, "Albumin": albumin, "血磷": phosphorus, "血鈣": calcium, "URR": urr,
            "SMI": smi, "SMI分類": smi_status, "KCL得分": kcl_score, "KCL分類": kcl_status,
            "IPAQ MET": int(met), "IPAQ分類": ipaqlvl, "MNA-SF得分": mna_total, "MNA-SF分類": mna_status
        }
        df = pd.DataFrame([record])
        df.to_csv(DATA_FILE, mode='a', index=False, header=not os.path.getsize(DATA_FILE))
        st.success("✅ 資料已成功儲存！")

        # ➕ 輸出個人報告 Excel
        report_buffer = io.BytesIO()
        df.to_excel(report_buffer, index=False, engine='openpyxl')
        from fpdf import FPDF

        # ➕ 輸出 PDF 報告
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", 'B', 12)
                self.cell(0, 10, "血液透析個人健康報告", ln=True, align="C")
                self.ln(10)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", '', 11)
        for key, value in record.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        st.download_button(
            label="⬇️ 下載此筆個人報告 (PDF)",
            data=pdf_buffer.getvalue(),
            file_name=f"個人報告_{date.today()}.pdf",
            mime="application/pdf"
        )
