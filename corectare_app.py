import pandas as pd
import streamlit as st

st.title("🩺 Corectare Automatizată Grile Rezidențiat")

uploaded_file = st.file_uploader("Încarcă fișierul CSV exportat din ZipGrade", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    simple_range = range(1, 61)
    multi_range = range(61, 101)
    all_choices = set("ABCDE")

    def score_multiple(correct, selected):
        score = 0.0
        for c in all_choices:
            if c in selected and c in correct:
                score += 0.2
            elif c not in selected and c not in correct:
                score += 0.2
        return round(score, 2)

    results = []

    for index, row in df.iterrows():
        student_name = f"{row.get('FirstName', '')} {row.get('LastName', '')}".strip()
        student_id = row.get('StudentID', '')

        total_score = 0.0

        for q in simple_range:
            stu_col = f"Stu{q}"
            key_col = f"PriKey{q}"
            if stu_col in row and key_col in row:
                if str(row[stu_col]).strip().upper() == str(row[key_col]).strip().upper():
                    total_score += 1.0

        for q in multi_range:
            stu_col = f"Stu{q}"
            key_col = f"PriKey{q}"
            if stu_col in row and key_col in row:
                student_answer = str(row[stu_col]).strip().upper()
                correct_answer = str(row[key_col]).strip().upper()
                if student_answer and correct_answer:
                    total_score += score_multiple(set(correct_answer), set(student_answer))

        results.append({
            "Student Name": student_name if student_name else f"ID {student_id}",
            "Score": round(total_score, 2),
            "Grade (din 10)": round(total_score / 10, 2)
        })

    results_df = pd.DataFrame(results)
    st.success("✅ Corectare finalizată!")
    st.dataframe(results_df)

    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descarcă Rezultatele (CSV)",
        data=csv,
        file_name='Rezultate_Studenti_Calculat.csv',
        mime='text/csv'
    )
