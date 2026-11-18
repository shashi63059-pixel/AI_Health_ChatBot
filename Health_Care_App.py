# ==============================================================================
# HealthCare AI ChatBot - Premium Medical Consultation Interface
# ==============================================================================
import os
import re
import datetime
import webbrowser
from tkinter import *
import tkinter.messagebox
from tkinter import ttk

from bot import getresponse, get_pridected_value, get_diesese_practions

# ------------------------------------------------------------------------------
# Modern Dark Medical Theme System
# ------------------------------------------------------------------------------
THEME = {
    "bg_main": "#0B1120",        # Deep Midnight Navy
    "bg_card": "#1E293B",        # Card / Panel Background
    "bg_surface": "#0F172A",     # Surface Background
    "bg_sidebar": "#111827",     # Sidebar Dark Slate
    "bg_input": "#1E293B",       # Textbox / Input Background
    "border": "#334155",         # Subtle Border
    "border_light": "#475569",   # Elevated Border
    "border_accent": "#0EA5E9",  # Cyan Active Border
    
    "primary": "#0EA5E9",        # Sky Blue Primary
    "primary_hover": "#0284C7",  # Sky Blue Hover
    "primary_dark": "#0369A1",   # Deep Sky Blue
    
    "secondary": "#334155",      # Neutral Slate
    "secondary_hover": "#475569",# Slate Hover
    
    "teal": "#14B8A6",           # Medical Teal
    "teal_hover": "#0D9488",
    
    "emerald": "#10B981",        # Success / Online Green
    "emerald_hover": "#059669",
    
    "amber": "#F59E0B",          # Warning / Duration Alert
    "rose": "#EF4444",           # Critical Alert / Exit
    "rose_hover": "#DC2626",
    
    "text_main": "#F8FAFC",      # High-emphasis Text
    "text_body": "#E2E8F0",      # Body Text
    "text_muted": "#94A3B8",     # Subtitles & Placeholders
    "text_dim": "#64748B",       # Metadata & Minor Details
    
    "user_accent": "#38BDF8",    # User name accent
    "bot_accent": "#2DD4BF",     # Bot name accent
}

FONTS = {
    "brand": ("Segoe UI", 16, "bold"),
    "title_large": ("Segoe UI", 18, "bold"),
    "title_med": ("Segoe UI", 13, "bold"),
    "heading": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small": ("Segoe UI", 9),
    "small_bold": ("Segoe UI", 9, "bold"),
    "mono": ("Consolas", 10),
}

# ------------------------------------------------------------------------------
# UI Helper Functions
# ------------------------------------------------------------------------------
def center_window(win, width, height):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = max(0, (sw - width) // 2)
    y = max(0, (sh - height) // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def make_btn(parent, text, command=None, bg=THEME["primary"], fg=THEME["text_main"],
             hover_bg=THEME["primary_hover"], font=FONTS["body_bold"], padx=14, pady=7, **kwargs):
    btn = Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        font=font,
        bd=0,
        relief=FLAT,
        cursor="hand2",
        padx=padx,
        pady=pady,
        **kwargs
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg) if btn.cget("state") != DISABLED else None)
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg) if btn.cget("state") != DISABLED else None)
    return btn


# ==============================================================================
# Main Chat Application Class
# ==============================================================================
class ChatApplication:
    
    def __init__(self):
        self.window = Tk()
        self.outputs = []
        self.days = 0
        self.patient_name = "Patient"
        self._get_name()
        
    def run(self):
        self.window.mainloop()

    # --------------------------------------------------------------------------
    # Custom Aesthetic Modal Dialogs
    # --------------------------------------------------------------------------
    def giveanswer(self, dises, ans):
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        sender = self.patient_name.split(" ")[0]
        
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, f"👤 {sender} ", "user_name")
        self.text_widget.insert(END, f"• {time_str}\n", "timestamp")
        self.text_widget.insert(END, f"  ↳ {dises}: ", "question_tag")
        self.text_widget.insert(END, f"{ans}\n\n", "answer_tag")
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    def _suffering_days(self):
        """Aesthetic modal for asking duration of symptoms."""
        dlg = Toplevel(self.window)
        dlg.title("Symptom Duration")
        dlg.configure(bg=THEME["bg_card"], padx=24, pady=20)
        dlg.resizable(False, False)
        center_window(dlg, 420, 310)
        dlg.transient(self.window)
        dlg.grab_set()

        # Icon & Title
        header_frame = Frame(dlg, bg=THEME["bg_card"])
        header_frame.pack(fill=X, pady=(0, 14))
        
        Label(
            header_frame,
            text="⏱ Consultation Detail",
            font=FONTS["title_med"],
            bg=THEME["bg_card"],
            fg=THEME["primary"]
        ).pack(anchor=W)
        
        Label(
            header_frame,
            text="Since how many days have you been experiencing these symptoms?",
            font=FONTS["body"],
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            wraplength=370,
            justify=LEFT
        ).pack(anchor=W, pady=(4, 0))

        # Entry Card
        input_frame = Frame(dlg, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border"], padx=12, pady=10)
        input_frame.pack(fill=X, pady=8)

        Label(
            input_frame,
            text="Number of Days:",
            font=FONTS["body_bold"],
            bg=THEME["bg_surface"],
            fg=THEME["text_body"]
        ).pack(anchor=W, pady=(0, 4))

        days_var = StringVar(value="3")
        entry = Entry(
            input_frame,
            textvariable=days_var,
            font=FONTS["title_med"],
            bg=THEME["bg_input"],
            fg=THEME["text_main"],
            insertbackground=THEME["primary"],
            bd=0,
            relief=FLAT
        )
        entry.pack(fill=X, ipady=4)
        entry.focus()

        # Quick presets
        preset_frame = Frame(dlg, bg=THEME["bg_card"])
        preset_frame.pack(fill=X, pady=(6, 14))
        Label(preset_frame, text="Quick select:", font=FONTS["small"], bg=THEME["bg_card"], fg=THEME["text_dim"]).pack(side=LEFT, padx=(0, 6))

        for p_days in ["1", "3", "7", "14"]:
            def set_preset(d=p_days):
                days_var.set(d)
                entry.focus()
            p_btn = Button(
                preset_frame,
                text=f"{p_days}d",
                font=FONTS["small_bold"],
                bg=THEME["bg_surface"],
                fg=THEME["text_muted"],
                activebackground=THEME["primary"],
                activeforeground=THEME["text_main"],
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=set_preset
            )
            p_btn.pack(side=LEFT, padx=3)

        result_holder = {"days": 0}

        def confirm(event=None):
            val = days_var.get().strip()
            if val.isdigit() and int(val) > 0:
                result_holder["days"] = int(val)
                dlg.destroy()
            else:
                self.msg_warning("Invalid Duration", "Please enter a valid positive number of days.")
                entry.focus()

        entry.bind("<Return>", confirm)

        btn_frame = Frame(dlg, bg=THEME["bg_card"])
        btn_frame.pack(fill=X, pady=(4, 0))

        make_btn(
            btn_frame,
            text="Continue Consultation  →",
            command=confirm,
            bg=THEME["primary"],
            hover_bg=THEME["primary_hover"],
            font=FONTS["body_bold"],
            pady=8
        ).pack(fill=X)

        self.window.wait_window(dlg)
        
        confirmed_days = result_holder["days"] if result_holder["days"] > 0 else 1
        self.days += confirmed_days
        self.giveanswer("Symptom Duration", f"{confirmed_days} day(s)")

    def ask_box(self, desid):
        """Aesthetic Yes/No question modal with direct one-click buttons."""
        dlg = Toplevel(self.window)
        dlg.title("Symptom Verification")
        dlg.configure(bg=THEME["bg_card"], padx=24, pady=20)
        dlg.resizable(False, False)
        center_window(dlg, 440, 260)
        dlg.transient(self.window)
        dlg.grab_set()

        # Header
        Label(
            dlg,
            text="🩺 Clinical Check",
            font=FONTS["title_med"],
            bg=THEME["bg_card"],
            fg=THEME["teal"]
        ).pack(anchor=W)

        Label(
            dlg,
            text="Are you currently experiencing this symptom?",
            font=FONTS["body"],
            bg=THEME["bg_card"],
            fg=THEME["text_muted"]
        ).pack(anchor=W, pady=(2, 12))

        # Symptom Badge Card
        badge_frame = Frame(dlg, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border"], padx=16, pady=12)
        badge_frame.pack(fill=X, pady=(0, 16))

        display_name = desid.replace("_", " ").title()
        Label(
            badge_frame,
            text=f"•  {display_name}",
            font=FONTS["heading"],
            bg=THEME["bg_surface"],
            fg=THEME["primary"]
        ).pack(anchor=W)
        
        Label(
            badge_frame,
            text=f"System identifier: {desid}",
            font=FONTS["small"],
            bg=THEME["bg_surface"],
            fg=THEME["text_dim"]
        ).pack(anchor=W, pady=(2, 0))

        choice = {"ans": "no"}

        def on_yes():
            choice["ans"] = "yes"
            dlg.destroy()

        def on_no():
            choice["ans"] = "no"
            dlg.destroy()

        dlg.bind("<y>", lambda e: on_yes())
        dlg.bind("<Y>", lambda e: on_yes())
        dlg.bind("<n>", lambda e: on_no())
        dlg.bind("<N>", lambda e: on_no())
        dlg.bind("<Return>", lambda e: on_yes())

        # Buttons
        btn_frame = Frame(dlg, bg=THEME["bg_card"])
        btn_frame.pack(fill=X)

        btn_yes = make_btn(
            btn_frame,
            text="✓  Yes, I have this",
            command=on_yes,
            bg=THEME["emerald"],
            hover_bg=THEME["emerald_hover"],
            font=FONTS["body_bold"],
            pady=8
        )
        btn_yes.pack(side=LEFT, fill=X, expand=True, padx=(0, 6))

        btn_no = make_btn(
            btn_frame,
            text="✕  No",
            command=on_no,
            bg=THEME["secondary"],
            hover_bg=THEME["secondary_hover"],
            fg=THEME["text_body"],
            font=FONTS["body_bold"],
            pady=8
        )
        btn_no.pack(side=RIGHT, fill=X, expand=True, padx=(6, 0))

        self.window.wait_window(dlg)

        ans = choice["ans"]
        self.giveanswer(desid, ans)
        if ans.lower() == "yes":
            self.outputs.append(desid)

    # ==========================================================================
    # Screen 1: Welcome & Patient Name Setup
    # ==========================================================================
    def _get_name(self):
        self.window.title("HealthCare AI Assistant - Welcome")
        self.window.configure(bg=THEME["bg_main"])
        center_window(self.window, 540, 580)
        self.window.resizable(False, False)

        # Clear existing widgets if any
        for widget in self.window.winfo_children():
            widget.destroy()

        # Outer Container Frame
        outer = Frame(self.window, bg=THEME["bg_main"], padx=36, pady=36)
        outer.pack(fill=BOTH, expand=True)

        # Brand Header
        header_card = Frame(outer, bg=THEME["bg_main"])
        header_card.pack(fill=X, pady=(0, 20))

        Label(
            header_card,
            text="🩺 MediCare AI",
            font=FONTS["title_large"],
            bg=THEME["bg_main"],
            fg=THEME["primary"]
        ).pack(anchor=CENTER)

        Label(
            header_card,
            text="Intelligent Clinical Assessment & Diagnostic Assistant",
            font=FONTS["body"],
            bg=THEME["bg_main"],
            fg=THEME["text_muted"]
        ).pack(anchor=CENTER, pady=(4, 12))

        # Feature badges
        badge_box = Frame(header_card, bg=THEME["bg_main"])
        badge_box.pack(anchor=CENTER)
        
        badges = ["⚡ 130+ Symptoms", "🧠 Neural Analysis", "📋 Clinical Guidance"]
        for b_text in badges:
            Label(
                badge_box,
                text=b_text,
                font=FONTS["small_bold"],
                bg=THEME["bg_card"],
                fg=THEME["teal"],
                padx=8,
                pady=4
            ).pack(side=LEFT, padx=4)

        # Center Form Card
        card = Frame(outer, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"], padx=24, pady=24)
        card.pack(fill=X, pady=(10, 18))

        Label(
            card,
            text="Patient Registration",
            font=FONTS["title_med"],
            bg=THEME["bg_card"],
            fg=THEME["text_main"]
        ).pack(anchor=W)

        Label(
            card,
            text="Please enter your name to personalize your diagnostic consultation session.",
            font=FONTS["body"],
            bg=THEME["bg_card"],
            fg=THEME["text_muted"],
            wraplength=420,
            justify=LEFT
        ).pack(anchor=W, pady=(4, 16))

        # Input Frame
        entry_container = Frame(card, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border_light"], padx=10, pady=8)
        entry_container.pack(fill=X, pady=(0, 16))

        Label(
            entry_container,
            text="Full Name",
            font=FONTS["small_bold"],
            bg=THEME["bg_surface"],
            fg=THEME["primary"]
        ).pack(anchor=W)

        self.name_entry = Entry(
            entry_container,
            font=FONTS["heading"],
            bg=THEME["bg_surface"],
            fg=THEME["text_main"],
            insertbackground=THEME["primary"],
            bd=0,
            relief=FLAT
        )
        self.name_entry.pack(fill=X, pady=(4, 0))
        self.name_entry.focus()
        self.name_entry.bind("<Return>", self.get_name_after_click)

        # Submit Button
        make_btn(
            card,
            text="Start Consultation  →",
            command=lambda: self.get_name_after_click(None),
            bg=THEME["primary"],
            hover_bg=THEME["primary_hover"],
            font=FONTS["body_bold"],
            pady=10
        ).pack(fill=X)

        # Footer notes
        footer = Frame(outer, bg=THEME["bg_main"])
        footer.pack(fill=X, side=BOTTOM)

        Label(
            footer,
            text="🔒 Private & Confidential • Powered by Scikit-Learn & PyTorch",
            font=FONTS["small"],
            bg=THEME["bg_main"],
            fg=THEME["text_dim"]
        ).pack(anchor=CENTER)

    def get_name_after_click(self, event=None):
        raw_name = self.name_entry.get().strip()
        if len(raw_name) >= 2:
            self.patient_name = raw_name
            self._setup_main_window()
            self.coming_msg()
        else:
            self.msg_warning("Name Required", "Please enter your name (at least 2 characters) to continue.")

    # ==========================================================================
    # Screen 2: Main Diagnostic Consultation Dashboard
    # ==========================================================================
    def _setup_main_window(self):
        self.window.title(f"MediCare AI - Consultation for {self.patient_name}")
        self.window.configure(bg=THEME["bg_main"])
        center_window(self.window, 1260, 780)
        self.window.minsize(1050, 650)
        self.window.resizable(True, True)

        # Clear existing login widgets
        for widget in self.window.winfo_children():
            widget.destroy()

        # ----------------------------------------------------------------------
        # Top Navigation Bar
        # ----------------------------------------------------------------------
        top_bar = Frame(self.window, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border"], padx=20, pady=10)
        top_bar.pack(fill=X, side=TOP)

        # Brand on left
        brand_frame = Frame(top_bar, bg=THEME["bg_surface"])
        brand_frame.pack(side=LEFT)

        Label(
            brand_frame,
            text="🩺 MediCare AI",
            font=FONTS["brand"],
            bg=THEME["bg_surface"],
            fg=THEME["primary"]
        ).pack(side=LEFT, padx=(0, 12))

        # Status Pill
        status_pill = Frame(brand_frame, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"], padx=8, pady=3)
        status_pill.pack(side=LEFT)
        Label(
            status_pill,
            text="● Online & Ready",
            font=FONTS["small_bold"],
            bg=THEME["bg_card"],
            fg=THEME["emerald"]
        ).pack(side=LEFT)

        # Right side actions
        actions_frame = Frame(top_bar, bg=THEME["bg_surface"])
        actions_frame.pack(side=RIGHT)

        # Patient Badge
        patient_badge = Frame(actions_frame, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"], padx=10, pady=4)
        patient_badge.pack(side=LEFT, padx=(0, 10))
        Label(
            patient_badge,
            text=f"👤 Patient: {self.patient_name.title()}",
            font=FONTS["body_bold"],
            bg=THEME["bg_card"],
            fg=THEME["text_body"]
        ).pack()

        # Clear Chat Button
        make_btn(
            actions_frame,
            text="🧹 Clear Chat",
            command=self.clear_chat,
            bg=THEME["secondary"],
            hover_bg=THEME["secondary_hover"],
            font=FONTS["small_bold"],
            padx=10,
            pady=4
        ).pack(side=LEFT, padx=(0, 8))

        # Exit Button
        make_btn(
            actions_frame,
            text="✕ Exit",
            command=lambda: self.msg_msg_askcancle("Exit Consultation", "Are you sure you want to exit the application?"),
            bg=THEME["rose"],
            hover_bg=THEME["rose_hover"],
            font=FONTS["small_bold"],
            padx=10,
            pady=4
        ).pack(side=LEFT)

        # ----------------------------------------------------------------------
        # Main Two-Column Body
        # ----------------------------------------------------------------------
        body_frame = Frame(self.window, bg=THEME["bg_main"], padx=16, pady=14)
        body_frame.pack(fill=BOTH, expand=True)

        # Left Column: Symptom Explorer (Width ~340)
        left_col = Frame(body_frame, bg=THEME["bg_sidebar"], highlightthickness=1, highlightbackground=THEME["border"], width=340)
        left_col.pack(side=LEFT, fill=Y, padx=(0, 12))
        left_col.pack_propagate(False)

        # Left Sidebar Header
        left_header = Frame(left_col, bg=THEME["bg_sidebar"], padx=14, pady=12)
        left_header.pack(fill=X)

        Label(
            left_header,
            text="🔍 Symptom Explorer",
            font=FONTS["title_med"],
            bg=THEME["bg_sidebar"],
            fg=THEME["text_main"]
        ).pack(anchor=W)

        Label(
            left_header,
            text="Search among 130+ supported clinical symptoms.",
            font=FONTS["small"],
            bg=THEME["bg_sidebar"],
            fg=THEME["text_muted"],
            wraplength=310,
            justify=LEFT
        ).pack(anchor=W, pady=(2, 0))

        # Search Bar
        search_bar = Frame(left_col, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"], padx=8, pady=6)
        search_bar.pack(fill=X, padx=14, pady=(0, 10))

        self.help_entry = Entry(
            search_bar,
            font=FONTS["body"],
            bg=THEME["bg_card"],
            fg=THEME["text_main"],
            insertbackground=THEME["primary"],
            bd=0,
            relief=FLAT
        )
        self.help_entry.pack(side=LEFT, fill=X, expand=True, padx=(4, 6))
        self.help_entry.bind("<Return>", self._on_enter_help_search)

        make_btn(
            search_bar,
            text="Search",
            command=lambda: self._on_enter_help_search(None),
            bg=THEME["primary"],
            hover_bg=THEME["primary_hover"],
            font=FONTS["small_bold"],
            padx=10,
            pady=3
        ).pack(side=RIGHT)

        # Quick Suggestion Chips
        chips_frame = Frame(left_col, bg=THEME["bg_sidebar"], padx=14)
        chips_frame.pack(fill=X, pady=(0, 8))

        Label(
            chips_frame,
            text="QUICK SUGGESTIONS",
            font=FONTS["small_bold"],
            bg=THEME["bg_sidebar"],
            fg=THEME["text_dim"]
        ).pack(anchor=W, pady=(0, 4))

        quick_chips = [
            ("Fever", "fever"),
            ("Headache", "headache"),
            ("Cough", "cough"),
            ("Joint Pain", "joint_pain"),
            ("Stomach Pain", "stomach_pain"),
            ("Fatigue", "fatigue")
        ]

        chips_row = Frame(chips_frame, bg=THEME["bg_sidebar"])
        chips_row.pack(fill=X)

        for label_text, kw in quick_chips:
            def on_chip_click(k=kw):
                self.help_entry.delete(0, END)
                self.help_entry.insert(0, k)
                self._on_enter_help_search(None)
            c_btn = Button(
                chips_row,
                text=label_text,
                command=on_chip_click,
                font=FONTS["small"],
                bg=THEME["bg_card"],
                fg=THEME["teal"],
                activebackground=THEME["primary"],
                activeforeground=THEME["text_main"],
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2"
            )
            c_btn.pack(side=LEFT, padx=2, pady=2)

        # Search Results Text Area
        results_container = Frame(left_col, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        results_container.pack(fill=BOTH, expand=True, padx=14, pady=6)

        self.search_box = Text(
            results_container,
            font=FONTS["mono"],
            bg=THEME["bg_card"],
            fg=THEME["text_body"],
            bd=0,
            padx=10,
            pady=10,
            wrap=WORD,
            cursor="arrow"
        )
        self.search_box.pack(side=LEFT, fill=BOTH, expand=True)

        # Allow clicking search results to auto-fill into chat input
        def on_search_result_click(event):
            try:
                index = self.search_box.index(f"@{event.x},{event.y}")
                line_text = self.search_box.get(f"{index} linestart", f"{index} lineend").strip()
                match = re.search(r"\d+\)\s+([a-zA-Z0-9_]+)", line_text)
                if match:
                    symptom = match.group(1)
                    self.msg_entry.delete(0, END)
                    self.msg_entry.insert(0, symptom)
                    self.msg_entry.focus()
            except Exception:
                pass

        self.search_box.bind("<ButtonRelease-1>", on_search_result_click)

        scrollsearch = Scrollbar(results_container, command=self.search_box.yview)
        scrollsearch.pack(side=RIGHT, fill=Y)
        self.search_box.configure(yscrollcommand=scrollsearch.set, state=DISABLED)

        # Quick tip at bottom of sidebar
        tip_card = Frame(left_col, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border"], padx=10, pady=8)
        tip_card.pack(fill=X, padx=14, pady=(6, 12))

        Label(
            tip_card,
            text="💡 Format Tip:",
            font=FONTS["small_bold"],
            bg=THEME["bg_surface"],
            fg=THEME["amber"]
        ).pack(anchor=W)

        Label(
            tip_card,
            text="Use underscores for multi-word symptoms (e.g., high_fever, joint_pain, chest_pain).",
            font=FONTS["small"],
            bg=THEME["bg_surface"],
            fg=THEME["text_muted"],
            wraplength=290,
            justify=LEFT
        ).pack(anchor=W, pady=(2, 0))

        # ----------------------------------------------------------------------
        # Right Column: Chat Consultation Area
        # ----------------------------------------------------------------------
        right_col = Frame(body_frame, bg=THEME["bg_card"], highlightthickness=1, highlightbackground=THEME["border"])
        right_col.pack(side=RIGHT, fill=BOTH, expand=True)

        # Consultation Header
        chat_header = Frame(right_col, bg=THEME["bg_card"], padx=16, pady=12)
        chat_header.pack(fill=X, side=TOP)

        Label(
            chat_header,
            text="💬 Clinical Consultation",
            font=FONTS["title_med"],
            bg=THEME["bg_card"],
            fg=THEME["text_main"]
        ).pack(side=LEFT)

        Label(
            chat_header,
            text="Active AI Diagnostic Session",
            font=FONTS["small"],
            bg=THEME["bg_card"],
            fg=THEME["text_muted"]
        ).pack(side=LEFT, padx=(8, 0), pady=(3, 0))

        # Chat Text Widget Container
        chat_container = Frame(right_col, bg=THEME["bg_surface"])
        chat_container.pack(fill=BOTH, expand=True, padx=14, pady=(0, 10))

        self.text_widget = Text(
            chat_container,
            font=FONTS["body"],
            bg=THEME["bg_surface"],
            fg=THEME["text_body"],
            bd=0,
            padx=16,
            pady=14,
            wrap=WORD,
            cursor="arrow",
            spacing1=3,
            spacing3=4
        )
        self.text_widget.pack(side=LEFT, fill=BOTH, expand=True)

        chat_scroll = Scrollbar(chat_container, command=self.text_widget.yview)
        chat_scroll.pack(side=RIGHT, fill=Y)
        self.text_widget.configure(yscrollcommand=chat_scroll.set, state=DISABLED)

        # Configure Aesthetic Chat Tags
        self.text_widget.tag_config("user_name", foreground=THEME["user_accent"], font=FONTS["body_bold"])
        self.text_widget.tag_config("bot_name", foreground=THEME["bot_accent"], font=FONTS["body_bold"])
        self.text_widget.tag_config("timestamp", foreground=THEME["text_dim"], font=FONTS["small"])
        self.text_widget.tag_config("user_msg", foreground=THEME["text_main"], font=FONTS["body"])
        self.text_widget.tag_config("bot_msg", foreground=THEME["text_body"], font=FONTS["body"])
        self.text_widget.tag_config("question_tag", foreground=THEME["amber"], font=FONTS["body_bold"])
        self.text_widget.tag_config("answer_tag", foreground=THEME["emerald"], font=FONTS["body_bold"])
        self.text_widget.tag_config("alert_tag", foreground=THEME["rose"], font=FONTS["body_bold"])
        self.text_widget.tag_config("highlight_tag", foreground=THEME["primary"], font=FONTS["body_bold"])
        self.text_widget.tag_config("divider", foreground=THEME["border"], font=FONTS["small"])

        # Bottom Input Area
        bottom_bar = Frame(right_col, bg=THEME["bg_card"], padx=14, pady=10)
        bottom_bar.pack(fill=X, side=BOTTOM, pady=(0, 6))

        input_wrapper = Frame(bottom_bar, bg=THEME["bg_surface"], highlightthickness=1, highlightbackground=THEME["border_light"], padx=12, pady=6)
        input_wrapper.pack(fill=X)

        self.msg_entry = Entry(
            input_wrapper,
            font=FONTS["heading"],
            bg=THEME["bg_surface"],
            fg=THEME["text_main"],
            insertbackground=THEME["primary"],
            bd=0,
            relief=FLAT
        )
        self.msg_entry.pack(side=LEFT, fill=X, expand=True, padx=(4, 10), ipady=3)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        send_btn = make_btn(
            input_wrapper,
            text="Send  ➤",
            command=lambda: self._on_enter_pressed(None),
            bg=THEME["primary"],
            hover_bg=THEME["primary_hover"],
            font=FONTS["body_bold"],
            padx=16,
            pady=6
        )
        send_btn.pack(side=RIGHT)

        # Helper hint below input
        hint_label = Label(
            bottom_bar,
            text="💡 Tip: Type a symptom (e.g. fever, headache, cold) or greeting. Type 'quit' or 'bye' to exit.",
            font=FONTS["small"],
            bg=THEME["bg_card"],
            fg=THEME["text_dim"]
        )
        hint_label.pack(anchor=W, pady=(4, 0))

    # ==========================================================================
    # Symptom Search Handler
    # ==========================================================================
    def _on_enter_help_search(self, event=None):
        dis_list = [
            'itching', 'skin rash', 'nodal skin eruptions', 'continuous sneezing', 'shivering', 'chills',
            'joint pain', 'stomach pain', 'acidity', 'ulcers on tongue', 'muscle wasting', 'vomiting',
            'burning micturition', 'spotting urination', 'fatigue', 'weight gain', 'anxiety',
            'cold hands and feets', 'mood swings', 'weight loss', 'restlessness', 'lethargy',
            'patches in throat', 'irregular sugar level', 'cough', 'high fever', 'sunken eyes',
            'breathlessness', 'sweating', 'dehydration', 'indigestion', 'headache', 'yellowish skin',
            'dark urine', 'nausea', 'loss of appetite', 'pain behind the eyes', 'back pain',
            'constipation', 'abdominal pain', 'diarrhoea', 'mild fever', 'yellow urine',
            'yellowing of eyes', 'acute liver failure', 'fluid overload', 'swelling of stomach',
            'swelled lymph nodes', 'malaise', 'blurred and distorted vision', 'phlegm',
            'throat irritation', 'redness of eyes', 'sinus pressure', 'runny nose', 'congestion',
            'chest pain', 'weakness in limbs', 'fast heart rate', 'pain during bowel movements',
            'pain in anal region', 'bloody stool', 'irritation in anus', 'neck pain', 'dizziness',
            'cramps', 'bruising', 'obesity', 'swollen legs', 'swollen blood vessels',
            'puffy face and eyes', 'enlarged thyroid', 'brittle nails', 'swollen extremeties',
            'excessive hunger', 'extra marital contacts', 'drying_and_tingling_lips', 'slurred_speech',
            'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
            'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
            'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort', 'foul_smell_of urine',
            'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching', 'toxic_look_(typhos)',
            'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body',
            'belly_pain', 'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes',
            'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum',
            'lack_of_concentration', 'visual_disturbances', 'receiving_blood_transfusion',
            'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen',
            'history_of_alcohol_consumption', 'fluid_overload.1', 'blood_in_sputum',
            'prominent_veins_on_calf', 'palpitations', 'painful_walking', 'pus_filled_pimples',
            'blackheads', 'scurring', 'skin_peeling', 'silver_like_dusting', 'small_dents_in_nails',
            'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'
        ]

        raw_query = self.help_entry.get().strip()
        pred_list = []
        if len(raw_query) > 0:
            query = raw_query.replace("_", " ").lower()
            try:
                pattern = re.compile(re.escape(query), re.IGNORECASE)
                for item in dis_list:
                    if pattern.search(item):
                        pred_list.append(item)
            except Exception:
                pred_list = [item for item in dis_list if query in item.lower()]

        self.search_box.configure(state=NORMAL)
        self.search_box.delete("1.0", END)

        if len(pred_list) > 0:
            self.search_box.insert(END, f"Found {len(pred_list)} matching symptom(s):\n\n")
            for idx, item in enumerate(pred_list, 1):
                clean_name = item.replace(" ", "_")
                self.search_box.insert(END, f" {idx:2d})  {clean_name}\n")
            self.search_box.insert(END, "\nClick or type the exact name with underscores into the chat box.")
        else:
            if raw_query:
                self.search_box.insert(END, f"No matching symptoms discovered for '{raw_query}'.\n\nTry searching for generic terms like:\n• fever\n• cough\n• pain\n• rash\n• headache")
            else:
                self.search_box.insert(END, "Enter a symptom keyword above and click Search.")

        self.search_box.configure(state=DISABLED)

    # ==========================================================================
    # Chat Communication Handlers
    # ==========================================================================
    def coming_msg(self):
        good_name = self.patient_name.split(" ")[0].capitalize()
        welcome_text = (
            f"Hello {good_name}, I am your MediCare AI Diagnostic Assistant.\n\n"
            "If you are not feeling well, please describe your primary symptom. Here are common examples:\n"
            "  • fever (or high_fever / mild_fever)\n"
            "  • headache\n"
            "  • cough\n"
            "  • stomach_pain\n"
            "  • chills / shivering\n"
            "  • fatigue / lethargy\n"
            "  • joint_pain\n"
            "  • vomiting / acidity\n\n"
            "Note: For multi-word symptoms, please use an underscore ( _ ) instead of spaces."
        )
        self._bot_insert(welcome_text)

    def _on_enter_pressed(self, event=None):
        msg = self.msg_entry.get().strip()
        self._insert_message(msg)

    def _insert_message(self, msg):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        sender = self.patient_name.split(" ")[0].capitalize()

        # Display user's message
        self._user_instet_msg(f"👤 {sender}", msg)

        # Exit commands check
        quit_msg = ["quit", "exit", "bye", "bye bye"]
        if msg.lower() in quit_msg:
            self.msg_msg_askcancle("Exit Consultation", "Are you sure you want to exit the consultation?")
            return

        # Query response from bot engine
        chat_hear = getresponse(msg)

        if len(chat_hear) == 1:
            self._bot_insert(chat_hear[0])
        elif len(chat_hear) > 1:
            intro_msg = chat_hear[0]
            candidate_symptoms = chat_hear[1]
            primary_sym = chat_hear[2] if len(chat_hear) > 2 else None

            # Fallback extraction if primary_sym was not explicitly passed
            if not primary_sym:
                match = re.search(r"suffering from\s+([a-zA-Z0-9_]+)", intro_msg)
                if match:
                    primary_sym = match.group(1).strip()

            self._bot_insert(f"{intro_msg}Let's evaluate your clinical condition through a few quick questions.")
            
            # Reset duration & prompt duration modal
            self.days = 0
            self._suffering_days()
            
            # CRITICAL FIX: Ensure the confirmed primary symptom is ALWAYS retained!
            self.outputs.clear()
            if primary_sym:
                self.outputs.append(primary_sym)
            
            # Ask symptom confirmation questions for relevant candidates
            for s_item in candidate_symptoms:
                if s_item != primary_sym:
                    self.ask_box(s_item)

            # Summarize confirmed symptoms
            summary_msg = "Summary of Confirmed Symptoms:\n"
            if len(self.outputs) > 0:
                for idx, out_symptom in enumerate(self.outputs, 1):
                    summary_msg += f"  {idx}) {out_symptom.replace('_', ' ').title()}\n"
            else:
                summary_msg += f"  • Primary symptom: {primary_sym if primary_sym else 'General discomfort'}\n"
            self._bot_insert(summary_msg)

            # Duration Warning
            if self.days > 10:
                self._bot_insert("⚠️ URGENT ADVISORY: Your symptoms have persisted for over 10 days. Please discontinue self-medication and consult a hospital or medical specialist immediately.")

            # Model Prediction based on user's actual symptoms
            final_dieses = get_pridected_value(self.outputs)
            try:
                diesese_is = get_diesese_practions(final_dieses)
            except Exception:
                diesese_is = f"Preliminary assessment: {final_dieses}. Please seek medical guidance."

            self._bot_insert(diesese_is)

            # Prompt to open Google Maps for hospitals if duration > 10 days
            if self.days > 10:
                ask_to_web = tkinter.messagebox.askokcancel(
                    "Nearby Hospital Locator",
                    "Your symptoms have lasted more than 10 days.\n\nWould you like to open Google Maps in your web browser to locate nearby hospitals and clinics?"
                )
                if ask_to_web is True:
                    webbrowser.open_new_tab('https://www.google.com/maps/search/hospital+near+me/')
                    self._bot_insert("🌐 Opened Google Maps in your browser to help locate nearby healthcare facilities.")

    def clear_chat(self):
        self.text_widget.config(state=NORMAL)
        self.text_widget.delete("1.0", END)
        self.text_widget.config(state=DISABLED)
        self.coming_msg()

    def _user_instet_msg(self, usr, msg):
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, f"{usr} ", "user_name")
        self.text_widget.insert(END, f"• {time_str}\n", "timestamp")
        self.text_widget.insert(END, f"{msg}\n\n", "user_msg")
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    def _bot_insert(self, msg):
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, "🤖 MediBot ", "bot_name")
        self.text_widget.insert(END, f"• {time_str}\n", "timestamp")

        # Check for urgent or highlighted content
        if "⚠️" in msg or "URGENT" in msg:
            self.text_widget.insert(END, f"{msg}\n\n", "alert_tag")
        else:
            self.text_widget.insert(END, f"{msg}\n\n", "bot_msg")

        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    # --------------------------------------------------------------------------
    # Message Box Helpers
    # --------------------------------------------------------------------------
    def msg_showinfo(self, title, msg):
        tkinter.messagebox.showinfo(title, msg)

    def msg_warning(self, title, msg):
        tkinter.messagebox.showwarning(title, msg)

    def msg_msg_askcancle(self, title, msg):
        msg_data = tkinter.messagebox.askokcancel(title, msg)
        if msg_data is True:
            self.window.destroy()


# ==============================================================================
# Application Entry Point
# ==============================================================================
if __name__ == "__main__":
    app = ChatApplication()
    app.run()
