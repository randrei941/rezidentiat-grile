
import streamlit as st
import pandas as pd

st.title("Corectare grile Rezidențiat - Format ZipGrade")

uploaded_file = st.file_uploader("Încarcă fișierul CSV exportat din ZipGrade", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    df_raw.columns = df_raw.columns.str.strip()

    if not all(col in df_raw.columns for col in ["Quiz Name", "ZipGrade ID"] + [f"Q{i}" for i in range(1, 101)]):
        st.error("Fișierul trebuie să fie un export valid ZipGrade cu întrebările Q1–Q100 și coloana ZipGrade ID.")
    else:
        # Extragem datele esențiale
        df = pd.DataFrame()
        df["Varianta"] = df_raw["Quiz Name"].fillna("A").str.extract(r"(A|B|C|D)", expand=False).fillna("A")
        df["ID"] = df_raw["ZipGrade ID"]
        df["Nume"] = (
            df_raw.get("First Name", "").fillna("") + " " + df_raw.get("Last Name", "").fillna("")
        ).str.strip().replace("", "Anonim")

        # Răspunsuri 1–60 (complement simplu)
        def decode_simplu(row):
            litere = "ABCDE"
            return "".join([litere[int(row[f"Q{i}"])] if pd.notna(row[f"Q{i}"]) and 0 <= int(row[f"Q{i}"]) < 5 else "." 
                            for i in range(1, 61)])

        # Răspunsuri 61–100 (complement multiplu)
        def decode_cm(row):
            litere = "ABCDE"
            rasp = []
            for i in range(61, 101):
                val = row[f"Q{i}"]
                if pd.isna(val):
                    rasp.append("")
                else:
                    if isinstance(val, str):  # deja string tip "ACD"
                        rasp.append(val.upper())
                    elif isinstance(val, (int, float)):
                        binar = format(int(val), '05b')[-5:]
                        opt = "".join([litere[j] for j in range(5) if binar[j] == '1'])
                        rasp.append(opt)
                    else:
                        rasp.append("")
            return ";".join(rasp)

        df["Raspunsuri_1_60"] = df_raw.apply(decode_simplu, axis=1)
        df["Raspunsuri_61_100"] = df_raw.apply(decode_cm, axis=1)

        # Bareme demo (trebuie înlocuite cu cele reale)
        barem_1_60 = {v: ["A"] * 60 for v in "ABCD"}
        barem_61_100 = {v: [["A", "C"]] * 40 for v in "ABCD"}

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
                        0.2 for opt in "ABCDE"
                        if (opt in corect and opt in marcat) or
                           (opt not in corect and opt not in marcat)
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
