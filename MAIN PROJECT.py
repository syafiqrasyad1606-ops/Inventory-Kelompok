#HAL APA SAJA YANG KAMI IMPORT
import tkinter as tk                         #<-----CODE INI BERTUJUAN MENGAMBIL TKINTER, BERGUNA UNTUK GUI PADA PYTHON
from tkinter import messagebox, simpledialog #<-----CODE INI BERGUNA UNTUK MENGAMBIL FITUR DARI TKINTER
import json                                  #<-----CODE INI AKAN BERGUNA SEBAGAI PENYIMPANAN YANG AKAN MAASUK KE LOCAK DRIVE
import os                                    #<-----CODE INI AKAN MENJADI SEBUAH AKSES LAYAKNYA KABEL YANG DAPAT MENGAKSES DRIVE
import datetime                              #<-----SESUAIKAN DENGAN NAMANYA

#INI ADALAH BAGIAN VARIABLE
INVENTORY = "inventory.json" #INI SEBAGAI ALAMAT PENYIMPANAN
TRANSAKSI = "transaksi.json" #INI SEBAGAI ALAMAT UNTUK TRANSAKSI
inventori_gudang = {}        #INI ADALAH TEMPAT PENYIMPANANNYA
transaksi_history = []       #INI ADALAH TEMPAT HISTORY TRANSAKSI
MAX_HISTORY_LIMIT = 5        #INI ADALAH MAX HISTORY YANG BISA DI TAMPUNG IALAH 5
GARIS = "-"*50

#INI BAGIAN SELURUH LOGIKA YANG TERDAPAT PADA PROGRAM KAMI
# --- FUNGSI LOGIKA INVENTORI ---
def tambah_stok_gui():
    # Dipanggil oleh tombol "Input Barang (Masuk)"
    kode = entry_kode.get().strip().upper()         #GET = AMBIL DATA DARI KOTAK YANG DI ISI #UPPER = MENGUBAH SELURUH KATA MENJADI KAPITAL
    jumlah_str = entry_jumlah.get().strip()         #STRIP = MEMBERSIHKAN SPASI DI AWAL KOTAK
    
    if not kode or not jumlah_str:
        messagebox.showwarning("Warning", "Kode dan Jumlah wajib diisi!") #SEBUAH MASSAGEBOX KETIKA KODE ATAU JUMLAH BLM TERISI
        return
    
    try:
        jumlah = int(jumlah_str)
        if jumlah <= 0: raise ValueError #NIALI TIDAK BOLEH KURANG SAMA DENGAN 0
    except ValueError:
        messagebox.showerror("Error", "Jumlah harus Bilangan Bulat Positif!") #INI TANDA BAHWA NILAI ITU BUKAN BILANGAN BULAT
        return

    if kode in inventori_gudang:                                    #TAHAP PENYIMPANAN KODE UNIK KE BAGIAN INVENTORY DAN JUGA HISTORY
        # Barang sudah ada
        inventori_gudang[kode]["stok"] += jumlah                    #MASUK KE INVENTORY GUDANG, NANTI INVENTORY GUDANG AKAN DI ARAHKAN KE ALAMAT INVENTORY.JSON
        nama_barang = inventori_gudang[kode]["nama"]
        pesan = f"Stok '{nama_barang}' ({kode}) ditambah {jumlah}. Total: {inventori_gudang[kode]['stok']}" #INI SUSUANANNYA
    else:
        # Barang baru, minta nama barang
        nama_barang = simpledialog.askstring("Input Nama", f"Masukkan NAMA barang untuk kode {kode}:", parent = window) 
        if not nama_barang:
             messagebox.showwarning("Warning", "Barang baru wajib punya nama!") #PESAN ERROR NONGOL KETIKA ENTRY BOX BELUM TERISI
             return
             
        inventori_gudang[kode] = {"nama": nama_barang.title(), "stok": jumlah}
        pesan = f"Barang baru '{nama_barang.title()}' ({kode}) ditambahkan dengan stok: {jumlah}"

    catat_transaksi(kode, inventori_gudang[kode]["nama"], "MASUK ", jumlah)
    simpan_data()
    update_gui()
    messagebox.showinfo("Sukses", pesan)

def kurangi_stok_gui():
    # Dipanggil oleh tombol "Output Barang (Keluar)"
    kode = entry_kode.get().strip().upper()
    jumlah_str = entry_jumlah.get().strip()

    if not kode or not jumlah_str:
        messagebox.showwarning("Warning", "Kode dan Jumlah wajib diisi!")
        return
    
    try:
        jumlah = int(jumlah_str)
        if jumlah <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Jumlah harus angka bulat positif!")
        return

    if kode not in inventori_gudang:
        messagebox.showerror("Error", f"Barang dengan kode '{kode}' tidak terdaftar!")
        return
    
    stok_sekarang = inventori_gudang[kode]["stok"]
    if jumlah > stok_sekarang:
        messagebox.showwarning("Warning", f"Stok tidak cukup! Stok '{inventori_gudang[kode]['nama']}' hanya {stok_sekarang}.")
    else:
        inventori_gudang[kode]["stok"] -= jumlah
        nama_barang = inventori_gudang[kode]["nama"]
        pesan = f"{jumlah} unit '{nama_barang}' dikeluarkan. Stok sisa: {inventori_gudang[kode]['stok']}"

        # Catat dan simpan
        catat_transaksi(kode, nama_barang, "KELUAR", jumlah)
        simpan_data()
        update_gui()
        messagebox.showinfo("Sukses", pesan)

def ubah_data_gui():
    # Dipanggil oleh tombol "Ubah Data Master"
    kode_lama = simpledialog.askstring("Ubah Data", "Masukkan KODE Barang yang ingin diubah:")
    if not kode_lama: return

    kode_lama = kode_lama.strip().upper()
    if kode_lama not in inventori_gudang:
        messagebox.showerror("Error", f"Barang dengan kode '{kode_lama}' tidak terdaftar!")
        return

    data_lama = inventori_gudang[kode_lama]

    # Ambil input baru
    nama_baru = simpledialog.askstring("Ubah Nama", f"Nama Lama: {data_lama['nama']}\nMasukkan NAMA BARU (Kosongkan jika tidak diubah):")
    kode_baru = simpledialog.askstring("Ubah Kode", f"Kode Lama: {kode_lama}\nMasukkan KODE BARU (Kosongkan jika tidak diubah):")

    nama_baru = nama_baru.strip().title() if nama_baru else ""
    kode_baru = kode_baru.strip().upper() if kode_baru else ""

    perubahan = False

    if nama_baru:
        data_lama['nama'] = nama_baru
        perubahan = True

    if kode_baru and kode_baru != kode_lama:
        if kode_baru in inventori_gudang:
            messagebox.showerror("Error", "Kode baru sudah digunakan!")
            return

        # Pindahkan data dan hapus yang lama
        inventori_gudang[kode_baru] = data_lama
        del inventori_gudang[kode_lama]
        perubahan = True

    if perubahan:
        simpan_data()
        update_gui()
        messagebox.showinfo("Sukses", "Data master berhasil diubah!")
    else:
        messagebox.showinfo("Info", "Tidak ada perubahan data dilakukan.")

def hapus_barang_gui():
    # Dipanggil oleh tombol "Hapus Barang"
    kode = simpledialog.askstring("Hapus Barang", "Masukkan KODE Barang yang ingin dihapus:")
    if not kode: return

    kode = kode.strip().upper()
    if kode not in inventori_gudang:
        messagebox.showerror("Error", f"Barang dengan kode '{kode}' tidak terdaftar!")
        return

    # Konfirmasi penghapusan
    nama_barang = inventori_gudang[kode]["nama"]
    stok = inventori_gudang[kode]["stok"]
    konfirmasi = messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus barang '{nama_barang}' ({kode}) dengan stok {stok} unit?")
    if not konfirmasi:
        return

    # Catat transaksi hapus
    catat_transaksi(kode, nama_barang, "HAPUS ", stok)

    # Hapus dari inventori
    del inventori_gudang[kode]

    # Simpan dan update GUI
    simpan_data()
    update_gui()
    messagebox.showinfo("Sukses", (f"Barang {nama_barang} '{kode}' berhasil dihapus!"))

# --- FUNGSI UTILITY (Pencatatan Transaksi) ---
def catat_transaksi(kode, nama, tipe, jumlah):
    global transaksi_history
    waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Tambahkan transaksi baru
    transaksi_history.append({
        "waktu": waktu,
        "kode": kode,
        "nama": nama,
        "tipe": tipe, 
        "jumlah": jumlah
     }) 
    # 2. Cek dan hapus transaksi terlama jika batas terlampaui (LOGIKA BARU)
    # Ini memastikan history hanya menyimpan 5 transaksi terbaru
    if len(transaksi_history) > MAX_HISTORY_LIMIT:
        del transaksi_history[0]
        
    simpan_data() # Langsung simpan setelah ada transaksi baru# Langsung simpan setelah ada transaksi baru

# --- FUNGSI UNTUK TAMPILAN (GUI) ---
def update_stok_list():
    # Update area teks untuk menampilkan Stok
    list_stok.config(state=tk.NORMAL) 
    list_stok.delete(1.0, tk.END) 
    
    if not inventori_gudang:
        list_stok.insert(tk.END, "Inventori kosong.")
    else:
        list_stok.insert(tk.END, "Kode\t| Nama Barang\t\t| Stok\n")
        list_stok.insert(tk.END, f"{GARIS}\n")
        for kode, detail in sorted(inventori_gudang.items()):
            list_stok.insert(tk.END, f"{kode}\t| {detail['nama']}\t\t| {detail['stok']} unit\n")
            
    list_stok.config(state=tk.DISABLED) 

def update_history_list():
    # Update area teks untuk menampilkan History Transaksi
    list_history.config(state=tk.NORMAL) 
    list_history.delete(1.0, tk.END) 

    if not transaksi_history:
        list_history.insert(tk.END, "Belum ada transaksi tercatat.")
    else:
        list_history.insert(tk.END, "Waktu\t\t\t| Kode\t | Tipe\t | Jumlah| Nama Barang\n")
        list_history.insert(tk.END,f"{GARIS}\n")
        # Tampilkan 10 transaksi terakhir
        for t in transaksi_history[-10:]:
            list_history.insert(tk.END, f"{t['waktu']}\t\t\t| {t['kode']}\t| {t['tipe']}\t| {t['jumlah']:^1} \t | {t['nama']}\n")

    list_history.config(state=tk.DISABLED)

def update_gui():
    # Dipanggil setiap kali ada perubahan data
    update_stok_list()
    update_history_list()
    
def refresh_history():
    """Memperbarui history transaksi dan menjadwalkan refresh 5 detik kemudian."""
    update_history_list()
    # Panggil fungsi ini lagi setelah 5000 milidetik (5 detik)
    window.after(5000, refresh_history)

# --- FUNGSI PERSISTENCE (Simpan dan Muat) ---
def muat_data():
    # 1. Muat data Master Inventori
    global inventori_gudang
    if os.path.exists(INVENTORY):
        try:
            with open(INVENTORY, 'r') as f:
                inventori_gudang = json.load(f)
        except:
            inventori_gudang = {}

    # 2. Muat data History Transaksi
    global transaksi_history
    if os.path.exists(TRANSAKSI):
        try:
            with open(TRANSAKSI, 'r') as f:
                transaksi_history = json.load(f)
        except:
            transaksi_history = []

def simpan_data():
    # Fungsi ini yang menjamin data lo gak hilang saat program ditutup!
    # Simpan Master Inventori
    with open(INVENTORY, 'w') as f:
        json.dump(inventori_gudang, f, indent=4)
        
    # Simpan History Transaksi
    with open(TRANSAKSI, 'w') as f:
        json.dump(transaksi_history, f, indent=4)


#INI BAGIAN WINDOW
window = tk.Tk()                        #BAGIAN MENAMPILKAN WINDOW
window.title("INVENTORY KELOMPOK 2")    #INI ADALAH BAGIAN NAMA PADA WINDOW
window.config(bg="#3e3e3e")           #BAGIAN WARNA DARI BACKGROUND
window.geometry("600x600")              #BAGIAN UNTUK MENENTUKAN UKURAN


#BAGIAN FRAM KE 1 YANG BERISI BAGIAN INPUT
framepertama = tk.LabelFrame(window, text="Transaksi Cepat", padx=10, pady=10, bg='#e4e4e4')            #BAGIAN INI ADALAH FRAME PERTAMA
framepertama.pack(padx=10, pady=10, fill="x")                                                             #BAGIAN FRAME PERTAMA UNTUK MENENTUKAN POSISI
tk.Label(framepertama, text="Kode Barang:", bg='#e4e4e4').grid(row=0, column=0, sticky="w", pady=5)     #BAGIAN INI ADALAH LABEL PADA FRAMEPERTAMA DENGAN TEKS KODE BARANG
entry_kode = tk.Entry(framepertama, width=15)                                                             #BAGIAN INI ADALAH TEMPAT UNTUK MENGISI
entry_kode.grid(row=0, column=1, padx=5, pady=5)                                                          #BERFUNGSI SEBAGAI POSISI DENGAN GRID
entry_kode.bind("<Return>", lambda event: entry_jumlah.focus_set())                                       #CODE YANG BERFUNGSI UNTUK LANGSUNG KELUAR DENGAN MENEKAN BUTTON "ESC"
tk.Label(framepertama, text="Jumlah:", bg='#e4e4e4').grid(row=1, column=0, sticky="w", pady=5)          #BAGIAN INI ADALAH LABEL PADA FRAMEPERTAMA DENGAN JUMLAH
entry_jumlah = tk.Entry(framepertama, width=15)                                                           #BAGIAN INI ADALAH TEMPAT UNTUK MENGISI
entry_jumlah.grid(row=1, column=1, padx=5, pady=5)                                                        #BERFUNGSI SEBAGAI POSISI DENGAN GRID
entry_jumlah.bind("<Return>", lambda event: tambah_stok_gui())                                            #Enter untuk langsung input masuk
entry_jumlah.bind("<Shift_R>", lambda event: kurangi_stok_gui())                                          #right shift untuk output keluar

#BAGIAN INI ADALAH BAGIAN TRANSAKSI, SEPERTI BUTTON CONTOHNYA
btn_input = tk.Button(framepertama, text="➕ Input Masuk", command=tambah_stok_gui, bg='#0F8558')      #CODE YANG AKAN MENAMPILAKN BUTTON DAN BERFUNGSI LAYAKNYA BUTTON, DAN AKAN BERAKSI DENGAN LOGIKA TAMBA STOCK
btn_input.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

btn_output = tk.Button(framepertama, text="➖ Output Keluar", command=kurangi_stok_gui, bg='#E22718')  #CODE YANG AKAN MENAMPILAKN BUTTON DAN BERFUNGSI LAYAKNYA BUTTON, DAN AKAN BERAKSI DENGAN LOGIKA KURANG STOCK
btn_output.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

btn_ubah = tk.Button(framepertama, text="✏️ Ubah Data Master", command=ubah_data_gui, bg='#81c4ff')    #CODE YANG AKAN MENAMPILAKN BUTTON DAN BERFUNGSI LAYAKNYA BUTTON, DAN AKAN BERAKSI DENGAN LOGIKA UBAH DATA
btn_ubah.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

btn_hapus = tk.Button(framepertama, text="🗑️ Hapus Barang", command=hapus_barang_gui, bg='#E22718')    #CODE YANG AKAN MENAMPILAKN BUTTON DAN BERFUNGSI LAYAKNYA BUTTON, DAN AKAN BERAKSI DENGAN LOGIKA HAPUS BARANG
btn_hapus.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

#BAGIAN FRAME KE-2 YANG BERFUNSGI MENAMPILKAN SELURUH BARANG YANG MASUK
framekedua = tk.LabelFrame(window, text="Stok Barang Saat Ini (Cek Stok)", padx=10, pady=10)              #BAGIAN INI ADALAH FRAME KEDUA
framekedua.pack(padx=10, pady=(0, 10), fill="both", expand=True)                                          #BAGIAN FRAME KEDUA UNTUK MENENTUKAN POSISI
list_stok = tk.Text(framekedua, height=10, width=60, bg="#e4e4e4")                                      #AKAN MENAMPILKAN LIST BERUPA TEKS PADA BAGIAN FRAME KEDUA
list_stok.pack(fill="both", expand=True)                                                                  #POSISI LAH INTINYA

#BAGIAN FRAME KE-3 YANG BERFUNGSI HISTORY TRANSAKSI
frameketiga = tk.LabelFrame(window, text="History 5 Transaksi Terakhir", padx=10, pady=10)                #BAGIAN INI ADALAH FRAME KETIGA
frameketiga.pack(padx=10, pady=(0, 10), fill="both", expand=True)                                         #BAGIAN FRAME KETIGA UNTUK MENENTUKAN POSISI

list_history = tk.Text(frameketiga, height=10, width=63, bg="#e4e4e4")                                  #AKAN MENAMPILKAN LIST BERUPA TEKS PADA BAGIAN FRAME KETIGA
list_history.pack(fill="both", expand=True)                                                               #POSISI LAH INTINYA

#BAGIAN UNTUK MENJALANKAN PROGRAM
if __name__ == "__main__":
    muat_data()
    update_gui()
    refresh_history()
    window.mainloop()
