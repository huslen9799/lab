import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "Employee.db"


# =========================
# DATABASE CREATE
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Branch(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bname TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS Worker(
        wid INTEGER PRIMARY KEY AUTOINCREMENT,
        wname TEXT,
        bid INTEGER,
        FOREIGN KEY(bid) REFERENCES Branch(id)
    )
    """)

    conn.commit()
    conn.close()


# =========================
# Branch CLASS
# =========================
class Branch:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()

    def add(self, bname):
        self.cur.execute("INSERT INTO Branch(bname) VALUES(?)", (bname,))
        self.conn.commit()

    def getRecords(self):
        self.cur.execute("SELECT * FROM Branch")
        return self.cur.fetchall()

    def edit(self, bid, new_name):
        self.cur.execute("UPDATE Branch SET bname=? WHERE id=?", (new_name, bid))
        self.conn.commit()

    def delete(self, bid):
        self.cur.execute("DELETE FROM Branch WHERE id=?", (bid,))
        self.conn.commit()


# =========================
# Worker CLASS
# =========================
class Worker:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()

    def add(self, wname, bid):
        self.cur.execute("INSERT INTO Worker(wname, bid) VALUES(?,?)", (wname, bid))
        self.conn.commit()

    def getRecords(self):
        self.cur.execute("""
            SELECT Worker.wid, Worker.wname, Branch.bname
            FROM Worker LEFT JOIN Branch ON Worker.bid = Branch.id
        """)
        return self.cur.fetchall()

    def edit(self, wid, new_name, new_bid):
        self.cur.execute("UPDATE Worker SET wname=?, bid=? WHERE wid=?",
                         (new_name, new_bid, wid))
        self.conn.commit()

    def delete(self, wid):
        self.cur.execute("DELETE FROM Worker WHERE wid=?", (wid,))
        self.conn.commit()


# =========================
# Tkinter GUI
# =========================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Employee Management")

        self.branch = Branch()
        self.worker = Worker()

        tabControl = ttk.Notebook(root)

        self.tab1 = ttk.Frame(tabControl)
        self.tab2 = ttk.Frame(tabControl)

        tabControl.add(self.tab1, text='Branch')
        tabControl.add(self.tab2, text='Worker')
        tabControl.pack(expand=1, fill="both")

        self.branchUI()
        self.workerUI()

    # ========================= Branch UI =========================
    def branchUI(self):
        frame = self.tab1

        tk.Label(frame, text="Branch Name:").pack()
        self.bname_entry = tk.Entry(frame)
        self.bname_entry.pack()

        tk.Button(frame, text="Add Branch", command=self.addBranch).pack()

        self.branch_list = tk.Listbox(frame, width=40)
        self.branch_list.pack()
        self.branch_list.bind("<<ListboxSelect>>", self.selectBranch)

        tk.Button(frame, text="Edit", command=self.editBranch).pack()
        tk.Button(frame, text="Delete", command=self.deleteBranch).pack()

        self.loadBranches()

    def loadBranches(self):
        self.branch_list.delete(0, tk.END)
        for b in self.branch.getRecords():
            self.branch_list.insert(tk.END, f"{b[0]} — {b[1]}")

    def addBranch(self):
        name = self.bname_entry.get()
        if name:
            self.branch.add(name)
            self.loadBranches()
            self.bname_entry.delete(0, tk.END)

    def selectBranch(self, event):
        pass

    def editBranch(self):
        try:
            item = self.branch_list.get(self.branch_list.curselection())
            bid = int(item.split(" — ")[0])
        except:
            return

        new_name = self.bname_entry.get()
        if new_name:
            self.branch.edit(bid, new_name)
            self.loadBranches()

    def deleteBranch(self):
        try:
            item = self.branch_list.get(self.branch_list.curselection())
            bid = int(item.split(" — ")[0])
        except:
            return

        self.branch.delete(bid)
        self.loadBranches()

    # ========================= Worker UI =========================
    def workerUI(self):
        frame = self.tab2

        tk.Label(frame, text="Worker Name:").pack()
        self.wname_entry = tk.Entry(frame)
        self.wname_entry.pack()

        tk.Label(frame, text="Branch:").pack()
        self.branch_combo = ttk.Combobox(frame)
        self.branch_combo.pack()
        self.loadBranchDropdown()

        tk.Button(frame, text="Add Worker", command=self.addWorker).pack()

        self.worker_list = tk.Listbox(frame, width=50)
        self.worker_list.pack()
        self.worker_list.bind("<<ListboxSelect>>", self.selectWorker)

        tk.Button(frame, text="Edit", command=self.editWorker).pack()
        tk.Button(frame, text="Delete", command=self.deleteWorker).pack()

        self.loadWorkers()

    def loadBranchDropdown(self):
        branches = self.branch.getRecords()
        self.branch_combo['values'] = [f"{b[0]} — {b[1]}" for b in branches]

    def loadWorkers(self):
        self.worker_list.delete(0, tk.END)
        for w in self.worker.getRecords():
            self.worker_list.insert(tk.END, f"{w[0]} — {w[1]} — {w[2]}")

    def addWorker(self):
        name = self.wname_entry.get()

        try:
            bid = int(self.branch_combo.get().split(" — ")[0])
        except:
            messagebox.showerror("Error", "Branch сонгоно уу!")
            return

        self.worker.add(name, bid)
        self.loadWorkers()

        self.wname_entry.delete(0, tk.END)
        self.loadBranchDropdown()

    def selectWorker(self, event):
        pass

    def editWorker(self):
        try:
            item = self.worker_list.get(self.worker_list.curselection())
            wid = int(item.split(" — ")[0])
        except:
            return

        new_name = self.wname_entry.get()

        try:
            new_bid = int(self.branch_combo.get().split(" — ")[0])
        except:
            messagebox.showerror("Error", "Branch сонгоно уу!")
            return

        self.worker.edit(wid, new_name, new_bid)
        self.loadWorkers()

    def deleteWorker(self):
        try:
            item = self.worker_list.get(self.worker_list.curselection())
            wid = int(item.split(" — ")[0])
        except:
            return

        self.worker.delete(wid)
        self.loadWorkers()


# =============== RUN PROGRAM ===============
init_db()

root = tk.Tk()
app = App(root)
root.mainloop()
