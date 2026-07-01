
import streamlit as st
import pandas as pd

st.title("Corectare Teste - Model Rezidențiat")

uploaded_file = st.file_uploader("Încarcă fișierul CSV exportat din ZipGrade", type="csv")

def calculeaza_nota(row):
    nota = 0.0
    for i in range(1, 60):
        student_col = f"#{i} Student Response"
        corect_col = f"#{i} Primary Answer"
        if pd.isna(row[student_col]) or pd.isna(row[corect_col]):
            continue
        if row[student_col].strip() == row[corect_col].strip():
            nota += 1.0

    for i in range(61, 100):
        student_col = f"#{i} Student Response"
        corect_col = f"#{i} Primary Answer"
        if pd.isna(row[student_col]) or pd.isna(row[corect_col]):
            continue
        student_ans = ''.join(sorted(row[student_col].strip().upper()))
        corect_ans = ''.join(sorted(row[corect_col].strip().upper()))
        if len(student_ans) < 2 or len(student_ans) > 4:
            continue  # nu se punctează răspunsurile cu 0, 1 sau 5 litere

        puncte = 0.0
        for litera in 'ABCDE':
            if (litera in student_ans and litera in corect_ans) or                (litera not in student_ans and litera not in corect_ans):
                puncte += 0.2
        nota += puncte
    return round(nota, 2)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    rezultate = pd.DataFrame()
    rezultate["Numar Matricol"] = df.iloc[:, 0]  # prima coloană e Student ID
    rezultate["Nota"] = df.apply(calculeaza_nota, axis=1)
    st.success("Corectare finalizată!")
    st.dataframe(rezultate)
    st.download_button("Descarcă rezultate CSV", rezultate.to_csv(index=False), file_name="note_rezultate.csv")
