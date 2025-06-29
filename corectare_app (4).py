
import streamlit as st
import pandas as pd

st.title("Corectare grile Rezidențiat")

uploaded_file = st.file_uploader("Încarcă fișierul CSV cu răspunsurile studenților", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()  # elimină spațiile inutile

    expected_cols = ["Varianta", "ID", "Nume", "Raspunsuri_1_60", "Raspunsuri_61_100"]
    if tuple(df.columns) != tuple(expected_cols):
        st.error(f"Fișierul trebuie să conțină coloanele exact în această ordine: {expected_cols}")
    else:
        # Barem de test demo (trebuie înlocuit cu baremul real)
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

            # Complement multiplu
            rasp_cm = raspunsuri_cm.strip().split(";")
            barem_cm = barem_61_100.get(varianta)
            if barem_cm and len(rasp_cm) == 40:
                for i in range(40):
                    corect = set(barem_cm[i])
                    marcat = set(rasp_cm[i].replace(" ", "").upper())
                    scor += sum([
                        0.2 for optiune in "ABCDE"
                        if (optiune in corect and optiune in marcat) or
                           (optiune not in corect and optiune not in marcat)
                    ])
            return round(scor, 2)

        df["Punctaj"] = df.apply(
            lambda row: scor_rezidentiat(
                row["Raspunsuri_1_60"], row["Raspunsuri_61_100"], row["Varianta"]
            ),
            axis=1
        )

        st.subheader("Rezultate corectare:")
        st.dataframe(df[["ID", "Nume", "Punctaj"]])
