
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
        df = pd.DataFrame()
        df["Varianta"] = df_raw["Quiz Name"].fillna("A").str.extract(r"(A|B|C|D)", expand=False).fillna("A")
        df["ID"] = df_raw["ZipGrade ID"]
        df["Nume"] = (
            df_raw.get("First Name", "").fillna("") + " " + df_raw.get("Last Name", "").fillna("")
        ).str.strip().replace("", "Anonim")

        def decode_simplu(row):
            litere = "ABCDE"
            return "".join([litere[int(row[f"Q{i}"])] if pd.notna(row[f"Q{i}"]) and 0 <= int(row[f"Q{i}"]) < 5 else "." 
                            for i in range(1, 61)])

        def decode_cm_bin(row):
            litere = "ABCDE"
            rasp = []
            for i in range(61, 101):
                val = row[f"Q{i}"]
                opt = ""
                if pd.isna(val):
                    rasp.append("")
                    continue
                if isinstance(val, str):
                    opt = val.upper()
                elif isinstance(val, (int, float)):
                    binar = format(int(val), '05b')[-5:]
                    opt = "".join([litere[j] for j in range(5) if binar[j] == '1'])
                rasp.append(opt)
            return rasp

        df["Raspunsuri_1_60"] = df_raw.apply(decode_simplu, axis=1)
        df["Raspunsuri_61_100"] = df_raw.apply(decode_cm_bin, axis=1)

        # Barem demonstrativ (toate A la simplu, AC la multiplu)
        barem_1_60 = {v: ["A"] * 60 for v in "ABCD"}
        barem_61_100 = {v: [["A", "C"]] * 40 for v in "ABCD"}

        def scor_complement_simplu(raspunsuri, barem):
            punctaj = 0.0
            for i, rasp in enumerate(raspunsuri):
                corect = barem[i]
                if rasp == corect:
                    punctaj += 1.0
            return punctaj

        def scor_complement_multiplu(raspunsuri, barem):
            punctaj = 0.0
            for i in range(40):
                corect = set(barem[i])
                dat = set(raspunsuri[i])
                for litera in "ABCDE":
                    if (litera in corect and litera in dat) or (litera not in corect and litera not in dat):
                        punctaj += 0.2
            return punctaj

        def scor_total(r1_60, r61_100, varianta):
            barem_s = barem_1_60[varianta]
            barem_m = barem_61_100[varianta]
            rasp_1_60 = list(r1_60)
            rasp_61_100 = r61_100
            punctaj = scor_complement_simplu(rasp_1_60, barem_s)
            punctaj += scor_complement_multiplu(rasp_61_100, barem_m)
            return round(punctaj, 2)

        df["Punctaj"] = df.apply(
            lambda row: scor_total(
                row["Raspunsuri_1_60"], row["Raspunsuri_61_100"], row["Varianta"]
            ),
            axis=1
        )

        st.subheader("Rezultate corectare:")
        st.dataframe(df[["ID", "Nume", "Punctaj"]])
