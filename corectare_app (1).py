
import streamlit as st
import pandas as pd

st.title("Corectare grile Rezidențiat")

uploaded_file = st.file_uploader("Încarcă fișierul CSV cu răspunsurile studenților", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Verificare coloane obligatorii
    expected_cols = {"ID", "Nume", "Raspunsuri_1_60", "Raspunsuri_61_100", "Varianta"}
    if not expected_cols.issubset(df.columns):
        st.error(f"Fișierul trebuie să conțină coloanele: {expected_cols}")
    else:
        # Încarcă baremele pentru toate cele 4 variante
        barem_1_60 = {
            "A": ["A"] * 60,
            "B": ["B"] * 60,
            "C": ["C"] * 60,
            "D": ["D"] * 60
        }

        barem_61_100 = {
            "A": [["A", "C"]] * 40,
            "B": [["B", "D"]] * 40,
            "C": [["C", "E"]] * 40,
            "D": [["A", "B", "E"]] * 40
        }

        def scor_rezidentiat(raspunsuri_simplu, raspunsuri_cm, varianta):
            scor = 0.0
            rasp_simplu = list(raspunsuri_simplu.strip().upper())
            barem_simplu = barem_1_60.get(varianta)
            if barem_simplu:
                for i in range(min(len(barem_simplu), len(rasp_simplu))):
                    if rasp_simplu[i] == barem_simplu[i]:
                        scor += 0.2

            # Scor complement multiplu (simplificat pentru demo)
            rasp_cm = raspunsuri_cm.strip().split(";")
            barem_cm = barem_61_100.get(varianta)
            if barem_cm and len(rasp_cm) == 40:
                for i in range(40):
                    corect = set(barem_cm[i])
                    marcat = set(rasp_cm[i].replace(" ", "").upper())
                    if marcat == corect:
                        scor += 1
                    elif corect.issuperset(marcat):
                        scor += 0.2 * len(marcat)
            return round(scor, 2)

        # Aplică scorul pe fiecare rând
        df["Punctaj"] = df.apply(
            lambda row: scor_rezidentiat(
                row["Raspunsuri_1_60"], row["Raspunsuri_61_100"], row["Varianta"]
            ),
            axis=1
        )

        # Afișează rezultatul inclusiv cu ID-ul studentului
        st.subheader("Rezultate corectare:")
        st.dataframe(df[["ID", "Nume", "Punctaj"]])
