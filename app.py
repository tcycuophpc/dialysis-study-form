import streamlit as st
import pandas as pd
import io
import os
from datetime import date
from fpdf import FPDF

st.set_page_config("血液透析研究收案系統", layout="wide")
st.title("📝 血液透析病人研究收案系統")

DATA_FOLDER = "all_records"
os.makedirs(DATA_FOLDER, exist_ok=True)

st.sidebar.title("🔐 模式選擇")
mode = st.sidebar.selectbox("選擇頁面模式", ["使用者填寫", "管理者後台"])

if mode == "管理者後台":
    password = st.sidebar.text_input("輸入管理者密碼", type="password")
    if password != "20040815":
        st.warning("密碼錯誤")
        st.stop()
    st.success("管理者登入成功")
    st.header("📊 已收資料總覽")

    all_dfs = []
    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".xlsx"):
            df = pd.read_excel(os.path.join(DATA_FOLDER, file))
            all_dfs.append(df)

    if all_dfs:
        df_all = pd.concat(all_dfs, ignore_index=True)
        st.dataframe(df_all, use_container_width=True)

        excel_buffer = io.BytesIO()
        df_all.to_excel(excel_buffer, index=False, engine='openpyxl')
        st.download_button(
            label="⬇️ 匯出全部資料 (Excel)",
            data=excel_buffer.getvalue(),
            file_name="總報表彙整.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("尚無任何資料")
    st.stop()

with st.form("intake_form"):
    st.header("基本資料")
    mrn = st.text_input("病歷號碼")
    age = st.number_input("年齡", 18, 120)
    sex = st.radio("性別", ["男", "女"])
    height = st.number_input("身高（cm）", 100.0, 250.0)
    weight = st.number_input("體重（kg）", 30.0, 200.0)
    bmi = round(weight / ((height / 100) ** 2), 2) if height > 0 else 0
    st.metric("BMI", bmi)
    edu = st.selectbox("教育程度", ["國小以下", "國小", "國中", "高中/高職", "大專以上"])
    job = st.text_input("職業")
    marital = st.selectbox("婚姻狀況", ["未婚", "已婚", "離婚", "喪偶"])
    living = st.selectbox("居住情形", ["與家人", "獨居", "機構", "其他"])

    st.header("生理與實驗室數據")
    dialysis_years = st.number_input("透析年資 (年)", 0.0, 50.0)
    cci = st.number_input("Charlson 合併症指數 (CCI)", 0, 20)
    med_count = st.number_input("目前服用藥物數量", 0, 50)
    sbp = st.number_input("收縮壓 SBP", 80, 240)
    dbp = st.number_input("舒張壓 DBP", 40, 140)
    creatinine = st.number_input("肌酸酐 (Creatinine)", 0.0, 20.0)
    hb = st.number_input("血色素 (Hb)", 0.0, 20.0)
    albumin = st.number_input("白蛋白 (Albumin)", 0.0, 10.0)
    phosphorus = st.number_input("血磷 (Phosphorus)", 0.0, 10.0)
    calcium = st.number_input("血鈣 (Calcium)", 0.0, 10.0)
    urr = st.number_input("尿素氮清除率 URR (%)", 0.0, 100.0)
    smi = st.number_input("四肢骨骼肌質量 SMI (kg/m²)", 0.0, 15.0)
    smi_status = "低肌肉質量" if ((sex == "男" and smi < 7.0) or (sex == "女" and smi < 5.7)) else "正常"

    st.header("KCL 虛弱量表 (25 題)")
    kcl_answers = [st.selectbox(f"第 {i+1} 題", ["否", "是"], key=f"kcl_{i}") for i in range(25)]
    kcl_score = sum([1 for a in kcl_answers if a == "是"])
    if kcl_score <= 3:
        kcl_status = "健康"
    elif kcl_score <= 7:
        kcl_status = "虛弱前期"
    else:
        kcl_status = "虛弱"

    st.header("IPAQ 身體活動")
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

    st.header("MNA-SF 營養風險")
    mna_scores = [st.slider(f"MNA-SF 第{i+1}題 (0-2 分)", 0, 2, 1, key=f"mna_{i}") for i in range(6)]
    mna_total = sum(mna_scores)
    mna_status = "正常" if mna_total > 11 else "有營養不良風險"

    submitted = st.form_submit_button("✅ 提交資料")

if submitted:
    record = {
        "病歷號碼": mrn, "日期": date.today(), "年齡": age, "性別": sex, "身高": height, "體重": weight,
        "BMI": bmi, "教育程度": edu, "職業": job, "婚姻": marital, "居住": living,
        "透析年資": dialysis_years, "CCI": cci, "藥物數量": med_count,
        "SBP": sbp, "DBP": dbp, "Creatinine": creatinine, "Hb": hb,
        "Albumin": albumin, "Phosphorus": phosphorus, "Calcium": calcium, "URR": urr,
        "SMI": smi, "SMI分類": smi_status, "KCL得分": kcl_score, "KCL分類": kcl_status,
        "IPAQ MET": int(met), "IPAQ分類": ipaqlvl, "MNA得分": mna_total, "MNA分類": mna_status
    }
    df = pd.DataFrame([record])
    file_path = os.path.join(DATA_FOLDER, f"{mrn}_{date.today()}.xlsx")
    df.to_excel(file_path, index=False, engine='openpyxl')
    st.success("✅ 資料已儲存並建立個人報告")

    # 顯示報告下載按鈕
    report_buffer = io.BytesIO()
    df.to_excel(report_buffer, index=False, engine='openpyxl')
    st.download_button(
        label="⬇️ 下載個人報告 (Excel)",
        data=report_buffer.getvalue(),
        file_name=f"{mrn}_個人報告.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
