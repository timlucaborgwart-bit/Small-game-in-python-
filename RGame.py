import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
import string

USERS_DATEI = "users.json"
MONEY_DATEI = "money.json"
START_GELD = 1000
SYMBOLE = ["🍒", "🍋", "🔔", "⭐", "💎", "7"]

def lade_users():
    if not os.path.exists(USERS_DATEI):
        return {}
    with open(USERS_DATEI, "r", encoding="utf-8") as f:
        return json.load(f)

def speichere_users(users):
    with open(USERS_DATEI, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4, sort_keys=True)

def lade_money():
    if not os.path.exists(MONEY_DATEI):
        return {}
    with open(MONEY_DATEI, "r", encoding="utf-8") as f:
        return json.load(f)

def speichere_money(money):
    with open(MONEY_DATEI, "w", encoding="utf-8") as f:
        json.dump(money, f, ensure_ascii=False, indent=4, sort_keys=True)

class LoginApp:
    def __init__(self, master):
        self.master = master
        master.title("Login / Registrierung")
        master.geometry("600x400")

        self.users = lade_users()
        self.money = lade_money()

        # Admin Account (settings)
        if "admin" not in self.users:
            self.users["admin"] = {"pass": "admin123"} 
            self.money["admin"] = START_GELD
            speichere_users(self.users)
            speichere_money(self.money)

        self.label_user = tk.Label(master, text="Benutzername:", font=("Arial", 14))
        self.label_user.pack(pady=10)
        self.entry_user = tk.Entry(master, font=("Arial", 14))
        self.entry_user.pack()

        self.label_pass = tk.Label(master, text="Passwort:", font=("Arial", 14))
        self.label_pass.pack(pady=10)
        self.entry_pass = tk.Entry(master, show="*", font=("Arial", 14))
        self.entry_pass.pack()

        self.login_button = tk.Button(master, text="Anmelden", font=("Arial", 14), command=self.login)
        self.login_button.pack(pady=10)

        self.register_button = tk.Button(master, text="Registrieren", font=("Arial", 14), command=self.register)
        self.register_button.pack()

    def login(self):
        user = self.entry_user.get()
        pw = self.entry_pass.get()

        if user in self.users and self.users[user]["pass"] == pw:
            messagebox.showinfo("Erfolg", f"Willkommen, {user}!")
            self.master.destroy()
            if user == "admin":
                admin_screen(self.users, self.money)
            else:
                spiel_screen(self.money, user)
        else:
            messagebox.showerror("Fehler", "Benutzername oder Passwort falsch!")

    def register(self):
        user = self.entry_user.get()
        pw = self.entry_pass.get()

        if user in self.users:
            messagebox.showerror("Fehler", "Benutzername existiert schon!")
            return
        if not user or not pw:
            messagebox.showerror("Fehler", "Benutzername und Passwort dürfen nicht leer sein!")
            return

        self.users[user] = {"pass": pw}
        self.money[user] = START_GELD

        speichere_users(self.users)
        speichere_money(self.money)

        messagebox.showinfo("Erfolg", "Registrierung erfolgreich! Du kannst dich jetzt anmelden.")

def admin_screen(users, money):
    # Timer id zum Cancellen
    timer_id = {"id": None}

    def logout():
        # Timer stoppen, falls aktiv
        if timer_id["id"] is not None:
            try:
                admin_fenster.after_cancel(timer_id["id"])
            except Exception:
                pass
            timer_id["id"] = None
        admin_fenster.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()

    def refresh_listbox():
        listbox.delete(0, tk.END)
        for user in sorted(users.keys()):
            listbox.insert(tk.END, user)

    def löschen():
        auswahl = listbox.curselection()
        if not auswahl:
            return
        user = listbox.get(auswahl)
        if user == "admin":
            messagebox.showwarning("Warnung", "Admin kann nicht gelöscht werden!")
            return
        if messagebox.askyesno("Bestätigen", f"Benutzer {user} wirklich löschen?"):
            del users[user]
            if user in money:
                del money[user]
            speichere_users(users)
            speichere_money(money)
            refresh_listbox()
            messagebox.showinfo("Erfolg", f"Benutzer {user} gelöscht.")

    def passwort_ändern():
        auswahl = listbox.curselection()
        if not auswahl:
            return
        user = listbox.get(auswahl)
        neues_pw = simpledialog.askstring("Passwort ändern", f"Neues Passwort für {user}:", show='*')
        if neues_pw:
            users[user]["pass"] = neues_pw
            speichere_users(users)
            messagebox.showinfo("Erfolg", f"Passwort für {user} geändert.")

    def geld_ändern():
        auswahl = listbox.curselection()
        if not auswahl:
            return
        user = listbox.get(auswahl)
        neues_geld = simpledialog.askinteger("Geld ändern", f"Neues Spielgeld für {user}:", minvalue=0)
        if neues_geld is not None:
            money[user] = neues_geld
            speichere_money(money)
            messagebox.showinfo("Erfolg", f"Spielgeld für {user} auf {neues_geld} gesetzt.")

    # FAQ-Fenster (Messenger-Stil)
    def faq_fenster():
        faq_win = tk.Toplevel(admin_fenster)
        faq_win.title("📩 FAQ / Aufträge")
        faq_win.geometry("520x420")

        fragen_liste = tk.Listbox(faq_win, font=("Arial", 12))
        fragen_liste.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        beispiel_fragen = [
            "Bitte ändern Sie das Passwort von user123.",
            "Ein neuer Benutzer möchte Spielgeld erhöhen.",
            "Melden Sie verdächtige Aktivitäten im Spiel.",
            "Fügen Sie einen neuen Sonderbonus hinzu.",
            "Löschen Sie inaktive Benutzer.",
            "Bitte überprüfe Login-Versuche von IP 192.168.0.5",
            "Backup von users.json anlegen."
        ]

        def frage_hinzufügen():
            fragen_liste.insert(tk.END, random.choice(beispiel_fragen))

        def frage_abschließen():
            auswahl = fragen_liste.curselection()
            if not auswahl:
                messagebox.showwarning("Hinweis", "Bitte wählen Sie eine Frage aus.")
                return
            index = auswahl[0]
            inhalt = fragen_liste.get(index)
            fragen_liste.delete(index)
            messagebox.showinfo("Erledigt", f"Auftrag abgeschlossen:\n{inhalt}")

        def frage_löschen():
            auswahl = fragen_liste.curselection()
            if not auswahl:
                messagebox.showwarning("Hinweis", "Bitte wählen Sie eine Frage aus.")
                return
            index = auswahl[0]
            fragen_liste.delete(index)
            messagebox.showinfo("Gelöscht", "Frage wurde entfernt.")

        # Buttons unten
        btn_frame = tk.Frame(faq_win)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Neue Frage hinzufügen", command=frage_hinzufügen).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Abschließen", command=frage_abschließen).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Löschen", command=frage_löschen).grid(row=0, column=2, padx=5)

        # Start mit ein paar Fragen
        for _ in range(3):
            frage_hinzufügen()

    # NEUES FEATURE: KI-Fragen & Auto-User-Erstellung
    def ki_fragen_und_user_erstellen():
        # Falls Fenster geschlossen wurde, nicht weiter planen
        if not admin_fenster.winfo_exists():
            timer_id["id"] = None
            return

        fragen = [
            "Können Sie mir sagen, wie mein Passwort ist?",
            "Bitte ändern Sie Ihr Passwort.",
            "Sicherheitswarnung: Ihr Passwort läuft bald ab.",
            "Neuer Benutzerantrag steht aus – wollen Sie genehmigen?",
            "Passwort zu schwach, bitte neu setzen.",
            "Prüfen Sie die letzten Login-Versuche.",
            "Bitte erhöhe Startguthaben für Promo-Test."
        ]
        frage = random.choice(fragen)
        # Kleine Info an den Admin
        try:
            messagebox.showinfo("KI-Frage", frage)
        except Exception:
            pass  # falls Fenster bereits geschlossen während Popup geplant war

        # Zufälligen, eindeutigen Benutzernamen erstellen
        for _ in range(50):  # Versuchsschleife, falls Namenskonflikt
            neuer_user = "user_" + ''.join(random.choices(string.ascii_lowercase, k=5))
            if neuer_user not in users:
                break
        else:
            # Falls alle Versuche fehlschlagen, hänge Random-Zahl an
            neuer_user = "user_" + ''.join(random.choices(string.ascii_lowercase, k=3)) + str(random.randint(1000,9999))

        neues_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Benutzer anlegen
        users[neuer_user] = {"pass": neues_pw}
        money[neuer_user] = START_GELD
        speichere_users(users)
        speichere_money(money)
        refresh_listbox()

        # Optional: nur printen (damit nicht jedes Mal ein Messagebox mit Passwort kommt)
        print(f"[KI] Neuer Benutzer erstellt: {neuer_user} / {neues_pw}")

        # Nächsten Timer setzen (60 Sekunden)
        try:
            timer_id["id"] = admin_fenster.after(60000, ki_fragen_und_user_erstellen)
        except Exception:
            timer_id["id"] = None

    # Admin GUI aufbauen
    admin_fenster = tk.Tk()
    admin_fenster.title("Admin Panel")
    admin_fenster.geometry("700x500")

    label = tk.Label(admin_fenster, text="Admin: Benutzerverwaltung", font=("Arial", 16))
    label.pack(pady=10)

    listbox = tk.Listbox(admin_fenster, font=("Arial", 12))
    listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

    refresh_listbox()

    btn_frame = tk.Frame(admin_fenster)
    btn_frame.pack(pady=8)

    löschen_button = tk.Button(btn_frame, text="Benutzer löschen", command=löschen)
    löschen_button.grid(row=0, column=0, padx=5)

    passwort_button = tk.Button(btn_frame, text="Passwort ändern", command=passwort_ändern)
    passwort_button.grid(row=0, column=1, padx=5)

    geld_button = tk.Button(btn_frame, text="Spielgeld ändern", command=geld_ändern)
    geld_button.grid(row=0, column=2, padx=5)

    faq_button = tk.Button(btn_frame, text="📩 FAQ", command=faq_fenster)
    faq_button.grid(row=0, column=3, padx=8)

    logout_button = tk.Button(admin_fenster, text="Logout", command=logout, fg="red")
    logout_button.pack(pady=6)

    # KI-Timer starten (erster Aufruf nach 60s)
    timer_id["id"] = admin_fenster.after(60000, ki_fragen_und_user_erstellen)

    admin_fenster.mainloop()

class SlotMachine:
    def __init__(self, master, money, user):
        self.master = master
        self.money = money
        self.user = user
        master.title(f"Slot Machine - Spieler: {user}")
        master.geometry("700x500")

        self.spielgeld = self.money.get(user, START_GELD)

        self.label_geld = tk.Label(master, text=f"Spielgeld: {self.spielgeld} 💰", font=("Arial", 16))
        self.label_geld.pack(pady=10)

        self.label_einsatz = tk.Label(master, text="Setze deinen Einsatz (max 100):", font=("Arial", 14))
        self.label_einsatz.pack()

        self.einsatz_entry = tk.Entry(master, font=("Arial", 14))
        self.einsatz_entry.pack()

        self.walzen_frame = tk.Frame(master)
        self.walzen_frame.pack(pady=20)

        self.walzen_labels = []
        for _ in range(3):
            lbl = tk.Label(self.walzen_frame, text="❓", font=("Arial", 50), width=2)
            lbl.pack(side=tk.LEFT, padx=20)
            self.walzen_labels.append(lbl)

        self.ziehen_button = tk.Button(master, text="Hebel ziehen!", font=("Arial", 16), command=self.ziehen)
        self.ziehen_button.pack(pady=10)

        self.label_ergebnis = tk.Label(master, text="", font=("Arial", 16))
        self.label_ergebnis.pack(pady=20)

        self.logout_button = tk.Button(master, text="Logout", fg="red", command=self.logout)
        self.logout_button.pack(pady=5)

    def ziehen(self):
        try:
            einsatz = int(self.einsatz_entry.get())
        except ValueError:
            messagebox.showerror("Fehler", "Bitte gib eine gültige Zahl als Einsatz ein!")
            return
        if einsatz <= 0:
            messagebox.showerror("Fehler", "Einsatz muss größer als 0 sein!")
            return
        if einsatz > 100:
            messagebox.showerror("Fehler", "Maximaler Einsatz ist 100!")
            return
        if einsatz > self.spielgeld:
            messagebox.showerror("Fehler", "Du hast nicht genug Spielgeld!")
            return

        gezogene = [random.choice(SYMBOLE) for _ in range(3)]

        for i in range(3):
            self.walzen_labels[i].config(text=gezogene[i])

        if gezogene[0] == gezogene[1] == gezogene[2]:
            gewinn = einsatz * 5
            text = "Jackpot! 3 Gleiche! 🎉"
        elif gezogene[0] == gezogene[1] or gezogene[1] == gezogene[2] or gezogene[0] == gezogene[2]:
            gewinn = einsatz * 2
            text = "2 Gleiche, nicht schlecht!"
        else:
            gewinn = 0
            text = "Leider kein Gewinn."

        self.spielgeld += gewinn - einsatz
        self.money[self.user] = self.spielgeld
        speichere_money(self.money)

        self.label_geld.config(text=f"Spielgeld: {self.spielgeld} 💰")
        self.label_ergebnis.config(text=f"{text}\nGewinn: {gewinn}")

    def logout(self):
        self.master.destroy()
        root = tk.Tk()
        LoginApp(root)
        root.mainloop()

def spiel_screen(money, user):
    spiel_fenster = tk.Tk()
    SlotMachine(spiel_fenster, money, user)
    spiel_fenster.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    LoginApp(root)
    root.mainloop()
