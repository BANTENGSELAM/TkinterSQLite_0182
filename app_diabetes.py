import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "prediksi_diabetes.db"

def run_query(sql, params=()):
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            return conn.execute(sql, params).fetchall()
    finally:
        conn.close()
        
def init_db():
    run_query("""
        CREATE TABLE IF NOT EXISTS prediksi_diabetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            usia INTEGER,
            gula_darah REAL,
            bmi REAL,
            riwayat_ortu TEXT,
            hasil_prediksi TEXT
        )
    """)
    
def tambah_pasien(nama, usia, gula, bmi, riwayat, hasil):
    sql = """INSERT INTO prediksi_diabetes 
             (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi) 
             VALUES (?, ?, ?, ?, ?, ?)"""
    run_query(sql, (nama, usia, gula, bmi, riwayat, hasil))
    
def get_semua_pasien():
    return run_query("SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi FROM prediksi_diabetes ORDER BY id DESC")

def hitung_risiko(gula, bmi, riwayat):
    ada_ortu = (riwayat == "Ya")
    
    if gula >= 200:
        return ("Sangat Tinggi" if (bmi >= 30 or ada_ortu) else "Tinggi"), "#e74c3c"
    elif 140 <= gula < 200:
        return ("Tinggi" if (bmi >= 30 or ada_ortu) else "Sedang"), "#e67e22"
    else:  
        if bmi >= 30:
            return ("Sedang" if ada_ortu else "Waspada"), "#f1c40f" if ada_ortu else "#3498db"
        else:
            return ("Waspada" if ada_ortu else "Rendah"), "#3498db" if ada_ortu else "#2ecc71"
        
def read_form():
    nama = entry_nama.get().strip()
    usia = entry_usia.get().strip()
    gula = entry_gula.get().strip() 
    bmi = entry_bmi.get().strip()
    riwayat = combo_riwayat.get()

    if not nama or not usia or not gula or not bmi:
        messagebox.showwarning("Peringatan", "Semua kolom wajib diisi!")
        return None

    if not usia.isdigit():
        messagebox.showwarning("Peringatan", "Usia harus berupa angka bulat!")
        return None

    try:
        gula_val = float(gula)
        bmi_val = float(bmi)
    except ValueError:
        messagebox.showwarning("Peringatan", "Gula Darah dan BMI harus berupa angka!")
        return None

    return nama, int(usia), gula_val, bmi_val, riwayat

def clear_form():
    entry_nama.delete(0, tk.END)
    entry_usia.delete(0, tk.END)
    entry_gula.delete(0, tk.END)
    entry_bmi.delete(0, tk.END)
    combo_riwayat.set("Tidak")
    
def on_hitung_dan_simpan():
    data = read_form()
    if data:
        nama, usia, gula, bmi, riwayat = data
        risiko, warna = hitung_risiko(gula, bmi, riwayat)
        
        lbl_hasil.config(text=f"Hasil Risiko: {risiko}", bg=warna, fg="white")
        
        tambah_pasien(nama, usia, gula, bmi, riwayat, risiko)
        messagebox.showinfo("Sukses", f"Data {nama} disimpan!")
        clear_form()

def buka_jendela_tabel():
    top = tk.Toplevel(root)
    top.title("Riwayat Data Pasien")
    top.geometry("650x300")

    cols = ("id", "nama", "usia", "gula", "bmi", "riwayat", "hasil")
    tree = ttk.Treeview(top, columns=cols, show="headings")
    
    for c in cols:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=90, anchor="center")

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    for row in get_semua_pasien():
        tree.insert("", tk.END, values=row)
        
init_db()

root = tk.Tk()
root.title("Prediksi Risiko Diabetes")
root.geometry("400x520")

fields = [("Nama Pasien", 0), ("Usia (Tahun)", 1), ("Gula Darah (mg/dL)", 2), ("BMI", 3)]
entries = {}

for label_text, row_idx in fields:
    tk.Label(root, text=label_text).pack(pady=(5, 0))
    e = tk.Entry(root, width=35)
    e.pack(pady=2)
    entries[label_text] = e

entry_nama = entries["Nama Pasien"]
entry_usia = entries["Usia (Tahun)"]
entry_gula = entries["Gula Darah (mg/dL)"]
entry_bmi = entries["BMI"]

tk.Label(root, text="Riwayat Ortu Diabetes").pack(pady=(5, 0))
combo_riwayat = ttk.Combobox(root, values=["Ya", "Tidak"], state="readonly", width=32)
combo_riwayat.set("Tidak")
combo_riwayat.pack(pady=2)

btn_simpan = tk.Button(root, text="Hitung & Simpan", command=on_hitung_dan_simpan, bg="#2980b9", fg="white", font=("Arial", 10, "bold"))
btn_simpan.pack(pady=15)

lbl_hasil = tk.Label(root, text="Hasil Risiko: -", font=("Arial", 12, "bold"), width=30, bg="#bdc3c7", pady=5)
lbl_hasil.pack(pady=5)

btn_lihat = tk.Button(root, text="Lihat Data Pasien", command=buka_jendela_tabel)
btn_lihat.pack(pady=10)

root.mainloop()