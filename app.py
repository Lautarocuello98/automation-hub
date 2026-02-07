import json
import sys
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from tools import (
    QuickSearchTool,
    SocialShortcutsTool,
    WeatherTool,
    WebDownloaderTool,
    LinkCheckerTool,
)


# ---------------- Paths (work for source + exe) ----------------

def get_app_dir() -> Path:
    # If packaged (PyInstaller), use the folder where the exe is located.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()
CONFIG_PATH = APP_DIR / "config.json"
HISTORY_PATH = APP_DIR / "history.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"socials": {}, "search_engines": {}, "download_folder": "downloads"}


# ---------------- History Store ----------------

class HistoryStore:
    def __init__(self, path: Path, max_items: int = 300):
        self.path = path
        self.max_items = max_items

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def append(self, event: dict) -> None:
        items = self.load()
        items.append(event)
        if len(items) > self.max_items:
            items = items[-self.max_items:]
        self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_params(tool_name: str, params: dict) -> dict:
    # Keep history useful but not huge.
    p = dict(params)
    # Avoid storing giant blobs
    if tool_name in ("Web Downloader", "Link Checker"):
        # keep only key fields
        allowed = {"url", "mode", "out_dir", "timeout", "show_errors"}
        p = {k: v for k, v in p.items() if k in allowed}
    if tool_name == "Quick Search":
        allowed = {"engine", "query"}
        p = {k: v for k, v in p.items() if k in allowed}
    if tool_name == "Weather":
        p = {"city": p.get("city")}
    if tool_name == "Social Shortcuts":
        p = {"platform": p.get("platform")}
    return p


# ---------------- App ----------------

class AutomationHubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automation Hub")
        self.geometry("980x600")
        self.minsize(920, 560)

        self.config_data = load_config()
        self.history = HistoryStore(HISTORY_PATH)

        # ---- Style (nice look) ----
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("App.TFrame", background="#0f172a")
        self.style.configure("Main.TFrame", background="#0b1220")
        self.style.configure("Card.TFrame", background="#0e1a31", relief="flat")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground="white", background="#0b1220")
        self.style.configure("Desc.TLabel", font=("Segoe UI", 10), foreground="#cbd5e1", background="#0b1220")
        self.style.configure("H.TLabel", font=("Segoe UI", 10, "bold"), foreground="#e2e8f0", background="#0e1a31")
        self.style.configure("Body.TLabel", font=("Segoe UI", 9), foreground="#cbd5e1", background="#0e1a31")
        self.style.configure("Sidebar.TLabel", font=("Segoe UI", 11, "bold"), foreground="white", background="#0f172a")
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))

        # ---- Tools registry ----
        self.tools = {
            "Quick Search": QuickSearchTool(self.config_data.get("search_engines", {})),
            "Social Shortcuts": SocialShortcutsTool(self.config_data.get("socials", {})),
            "Weather": WeatherTool(),
            "Web Downloader": WebDownloaderTool(),
            "Link Checker": LinkCheckerTool(),
            "History": None,  # UI-only panel
        }

        self._build_layout()
        self._select_tool("Quick Search")

    # ---------------- UI Layout ----------------

    def _build_layout(self):
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(root, style="App.TFrame", padding=14)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(self.sidebar, text="Automation Hub", style="Sidebar.TLabel").pack(anchor="w")
        ttk.Label(self.sidebar, text="Tools", style="Sidebar.TLabel").pack(anchor="w", pady=(12, 6))

        self.tool_list = tk.Listbox(
            self.sidebar,
            height=20,
            activestyle="none",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#e2e8f0",
            highlightthickness=0,
            selectbackground="#1d4ed8",
            selectforeground="white",
            relief="flat",
        )
        for name in self.tools.keys():
            self.tool_list.insert(tk.END, name)
        self.tool_list.pack(fill=tk.Y, expand=True)
        self.tool_list.bind("<<ListboxSelect>>", self._on_tool_select)

        # Main
        self.main = ttk.Frame(root, style="Main.TFrame", padding=18)
        self.main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.title_lbl = ttk.Label(self.main, text="", style="Title.TLabel")
        self.title_lbl.pack(anchor="w")

        self.desc_lbl = ttk.Label(self.main, text="", style="Desc.TLabel", wraplength=680, justify="left")
        self.desc_lbl.pack(anchor="w", pady=(4, 12))

        self.card = ttk.Frame(self.main, style="Card.TFrame", padding=14)
        self.card.pack(fill=tk.BOTH, expand=True)

        self.tool_panel = ttk.Frame(self.card, style="Card.TFrame")
        self.tool_panel.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main, text="Output", style="Desc.TLabel").pack(anchor="w", pady=(14, 6))

        self.output = tk.Text(
            self.main,
            height=9,
            wrap="word",
            font=("Consolas", 10),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="white",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.output.pack(fill=tk.X)
        self.output.configure(state="disabled")

    def _log(self, text: str):
        self.output.configure(state="normal")
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)
        self.output.configure(state="disabled")

    def _on_tool_select(self, _event):
        idxs = self.tool_list.curselection()
        if not idxs:
            return
        name = self.tool_list.get(idxs[0])
        self._select_tool(name)

    def _select_tool(self, tool_name: str):
        # highlight
        try:
            idx = list(self.tools.keys()).index(tool_name)
            self.tool_list.selection_clear(0, tk.END)
            self.tool_list.selection_set(idx)
        except ValueError:
            pass

        for w in self.tool_panel.winfo_children():
            w.destroy()

        if tool_name == "History":
            self.title_lbl.config(text="History")
            self.desc_lbl.config(text="View the latest saved actions (searches, downloads, scans).")
            self._ui_history()
            return

        tool = self.tools[tool_name]
        self.title_lbl.config(text=tool_name)
        self.desc_lbl.config(text=getattr(tool, "description", ""))

        if tool_name == "Quick Search":
            self._ui_quick_search()
        elif tool_name == "Social Shortcuts":
            self._ui_social()
        elif tool_name == "Weather":
            self._ui_weather()
        elif tool_name == "Web Downloader":
            self._ui_downloader()
        elif tool_name == "Link Checker":
            self._ui_link_checker()

    # ---------------- History recording ----------------

    def _run_tool(self, tool_name: str, params: dict):
        tool = self.tools[tool_name]
        res = tool.run(params)

        # log on screen
        self._log(("✅ " if res.ok else "❌ ") + res.message)

        # save to history.json
        event = {
            "time": now_iso(),
            "tool": tool_name,
            "params": safe_params(tool_name, params),
            "ok": res.ok,
            "message": res.message,
            "data": res.data or {},
        }
        try:
            self.history.append(event)
        except Exception:
            # if history fails, don't crash the app
            pass

        return res

    # ---------------- Panels ----------------

    def _ui_quick_search(self):
        engines = list(self.config_data.get("search_engines", {}).keys()) or ["Google"]

        ttk.Label(self.tool_panel, text="Search engine", style="H.TLabel").pack(anchor="w")
        engine_var = tk.StringVar(value=engines[0])
        ttk.Combobox(self.tool_panel, textvariable=engine_var, values=engines, state="readonly").pack(
            anchor="w", fill=tk.X, pady=(6, 12)
        )

        ttk.Label(self.tool_panel, text="Query", style="H.TLabel").pack(anchor="w")
        query_var = tk.StringVar()
        entry = ttk.Entry(self.tool_panel, textvariable=query_var)
        entry.pack(anchor="w", fill=tk.X, pady=(6, 12))
        entry.focus_set()

        def run():
            self._run_tool("Quick Search", {"engine": engine_var.get(), "query": query_var.get()})

        ttk.Button(self.tool_panel, text="Search", style="Accent.TButton", command=run).pack(anchor="w")

    def _ui_social(self):
        socials = list(self.config_data.get("socials", {}).keys())
        if not socials:
            ttk.Label(self.tool_panel, text="No socials configured in config.json", style="Body.TLabel").pack(anchor="w")
            return

        ttk.Label(self.tool_panel, text="Platform", style="H.TLabel").pack(anchor="w")
        platform_var = tk.StringVar(value=socials[0])
        ttk.Combobox(self.tool_panel, textvariable=platform_var, values=socials, state="readonly").pack(
            anchor="w", fill=tk.X, pady=(6, 12)
        )

        def run():
            self._run_tool("Social Shortcuts", {"platform": platform_var.get()})

        ttk.Button(self.tool_panel, text="Open", style="Accent.TButton", command=run).pack(anchor="w")

    def _ui_weather(self):
        ttk.Label(self.tool_panel, text="City", style="H.TLabel").pack(anchor="w")
        city_var = tk.StringVar()
        entry = ttk.Entry(self.tool_panel, textvariable=city_var)
        entry.pack(anchor="w", fill=tk.X, pady=(6, 12))
        entry.focus_set()

        def run():
            self._run_tool("Weather", {"city": city_var.get()})

        ttk.Button(self.tool_panel, text="Get Weather", style="Accent.TButton", command=run).pack(anchor="w")

    def _ui_downloader(self):
        ttk.Label(self.tool_panel, text="URL", style="H.TLabel").pack(anchor="w")
        url_var = tk.StringVar()
        entry = ttk.Entry(self.tool_panel, textvariable=url_var)
        entry.pack(anchor="w", fill=tk.X, pady=(6, 12))
        entry.focus_set()

        ttk.Label(self.tool_panel, text="Mode", style="H.TLabel").pack(anchor="w")
        mode_var = tk.StringVar(value="all")
        ttk.Combobox(self.tool_panel, textvariable=mode_var, values=["all", "html", "links", "images"], state="readonly").pack(
            anchor="w", fill=tk.X, pady=(6, 12)
        )

        ttk.Label(self.tool_panel, text="Output folder", style="H.TLabel").pack(anchor="w")
        default_out = self.config_data.get("download_folder", "downloads")
        out_var = tk.StringVar(value=default_out)
        ttk.Entry(self.tool_panel, textvariable=out_var).pack(anchor="w", fill=tk.X, pady=(6, 12))

        def run():
            self._run_tool(
                "Web Downloader",
                {"url": url_var.get(), "mode": mode_var.get(), "out_dir": out_var.get(), "timeout": 12},
            )

        ttk.Button(self.tool_panel, text="Download", style="Accent.TButton", command=run).pack(anchor="w")

    def _ui_link_checker(self):
        ttk.Label(self.tool_panel, text="URL", style="H.TLabel").pack(anchor="w")
        url_var = tk.StringVar()
        entry = ttk.Entry(self.tool_panel, textvariable=url_var)
        entry.pack(anchor="w", fill=tk.X, pady=(6, 12))
        entry.focus_set()

        row = ttk.Frame(self.tool_panel, style="Card.TFrame")
        row.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(row, text="Timeout (sec)", style="Body.TLabel").pack(side=tk.LEFT)
        timeout_var = tk.StringVar(value="10")
        ttk.Entry(row, textvariable=timeout_var, width=8).pack(side=tk.LEFT, padx=(8, 18))

        show_errors_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text="Show non-404 errors", variable=show_errors_var).pack(side=tk.LEFT)

        def run():
            try:
                timeout = int(timeout_var.get())
            except ValueError:
                timeout = 10

            self._run_tool(
                "Link Checker",
                {"url": url_var.get(), "timeout": timeout, "show_errors": show_errors_var.get()},
            )

        ttk.Button(self.tool_panel, text="Scan Links", style="Accent.TButton", command=run).pack(anchor="w")

    def _ui_history(self):
        container = ttk.Frame(self.tool_panel, style="Card.TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        top = ttk.Frame(container, style="Card.TFrame")
        top.pack(fill=tk.X)

        ttk.Label(top, text="Latest events", style="H.TLabel").pack(side=tk.LEFT)

        def refresh():
            self._history_list.delete(0, tk.END)
            items = self.history.load()
            items = items[-200:]  # show last 200
            items.reverse()
            self._history_items = items
            for ev in items:
                line = f"{ev.get('time','')} | {ev.get('tool','')} | {'OK' if ev.get('ok') else 'FAIL'}"
                self._history_list.insert(tk.END, line)

        def open_file():
            messagebox.showinfo("History file", f"History is saved at:\n{HISTORY_PATH}")

        ttk.Button(top, text="Refresh", command=refresh).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(top, text="Show path", command=open_file).pack(side=tk.RIGHT)

        self._history_list = tk.Listbox(
            container,
            activestyle="none",
            font=("Consolas", 10),
            bg="#020617",
            fg="#e2e8f0",
            highlightthickness=0,
            selectbackground="#1d4ed8",
            selectforeground="white",
            relief="flat",
        )
        self._history_list.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        details = tk.Text(
            container,
            height=8,
            wrap="word",
            font=("Consolas", 10),
            bg="#020617",
            fg="#e2e8f0",
            relief="flat",
            padx=10,
            pady=10,
        )
        details.pack(fill=tk.X, expand=False)

        def on_select(_event):
            sel = self._history_list.curselection()
            if not sel:
                return
            idx = sel[0]
            ev = self._history_items[idx]
            details.delete("1.0", tk.END)
            details.insert(tk.END, json.dumps(ev, indent=2, ensure_ascii=False))

        self._history_list.bind("<<ListboxSelect>>", on_select)

        self._history_items = []
        refresh()


if __name__ == "__main__":
    app = AutomationHubApp()
    app.mainloop()
