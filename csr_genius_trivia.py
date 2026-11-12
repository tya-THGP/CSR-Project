"""
CSR GENIUS CHALLENGE
A beginner-friendly Tkinter trivia game based on the supplied PowerPoint mockup.

Run:
    python csr_genius_trivia.py

The first launch creates:
    trivia_questions.json  - editable question bank
    trivia_scores.db      - persistent local leaderboard

The mockup contains category/level placeholders, not actual questions. The
included questions are demonstrations and should be replaced with your own.
"""

import json
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
import re
import unicodedata

# ----------------------------- GAME SETTINGS -----------------------------

BASE_DIR = Path(__file__).resolve().parent
QUESTION_FILE = BASE_DIR / "trivia_questions.json"
DATABASE_FILE = BASE_DIR / "trivia_scores.db"

BG = "#FFF500"          # Bright yellow from the mockup
BLACK = "#080808"
WHITE = "#FFFFFF"
DARK_YELLOW = "#E6D900"
MUTED = "#555555"
GREEN = "#16803C"
RED = "#B42318"
BLUE = "#244B70"

# These labels follow the supplied PowerPoint. "Clams" and "Evident Scenario"
# may be typos in the mockup; edit them here and in trivia_questions.json
# if you intended "Claims" and "Evidence Scenario".
CATEGORIES = [
    "Ethics",
    "Legal",
    "PHL Outreach",
    "Philanthropic",
    "Economic",
    "Clams",
    "Evident Scenario",
]

# The PowerPoint shows these three values (it does not show $900).
LEVEL_VALUES = {1: 300, 2: 600, 3: 1200}

# ----------------------------- DEMO QUESTIONS ----------------------------

# These are starter/demo questions written to make the game playable.
# Replace or edit them in trivia_questions.json after the first launch.
DEMO_QUESTIONS = {
    "Ethics": {
        "1": {
            "question": "Which action is an example of ethical business behavior?",
            "choices": [
                "Being honest with customers",
                "Hiding product safety information",
                "Misleading workers about wages",
                "Ignoring community concerns"
            ],
            "answer": "Being honest with customers",
            "type": "multiple_choice"
        },
        "2": {
            "question": "A company discovers that an advertisement makes a misleading claim. What is the most ethical next step?",
            "choices": [
                "Leave the advertisement unchanged",
                "Correct the claim and explain the change",
                "Blame the customer",
                "Delete all customer feedback"
            ],
            "answer": "Correct the claim and explain the change",
            "type": "multiple_choice"
        },
        "3": {
            "question": "In your own words, explain one way a company can demonstrate transparency when a product or decision negatively affects a community.",
            "accepted_answers": [
                "share information honestly",
                "communicate openly",
                "disclose the impact and explain how it will be addressed"
            ],
            "answer": "A strong response explains that the company communicates honestly, shares relevant evidence, acknowledges harm, and describes corrective action.",
            "type": "typed"
        }
    },
    "Legal": {
        "1": {
            "question": "What does it generally mean when a company follows labor laws?",
            "choices": [
                "It follows rules protecting workers",
                "It can ignore workplace safety",
                "It never has to pay taxes",
                "It can change laws on its own"
            ],
            "answer": "It follows rules protecting workers",
            "type": "multiple_choice"
        },
        "2": {
            "question": "A company learns that its facility is violating an environmental regulation. What should it do?",
            "choices": [
                "Hide the violation",
                "Continue operating without changes",
                "Address the violation and follow reporting requirements",
                "Delete the inspection records"
            ],
            "answer": "Address the violation and follow reporting requirements",
            "type": "multiple_choice"
        },
        "3": {
            "question": "Name one type of public regulation that can affect how a company operates, and explain why it matters.",
            "accepted_answers": [
                "environmental regulations protect air water and land",
                "labor laws protect workers",
                "consumer protection laws protect customers",
                "safety regulations reduce harm"
            ],
            "answer": "Examples include environmental regulations, labor laws, consumer protection laws, and workplace safety rules. The explanation should connect the rule to the people or environment it protects.",
            "type": "typed"
        }
    },
    "PHL Outreach": {
        "1": {
            "question": "What is one example of a company supporting its local Philadelphia community?",
            "choices": [
                "Partnering with a neighborhood school",
                "Avoiding all local partnerships",
                "Removing public resources",
                "Refusing to listen to residents"
            ],
            "answer": "Partnering with a neighborhood school",
            "type": "multiple_choice"
        },
        "2": {
            "question": "Which piece of evidence would best help evaluate a company's local community outreach?",
            "choices": [
                "A list of local programs and participation outcomes",
                "A product color chart",
                "An unrelated celebrity endorsement",
                "A company's office furniture inventory"
            ],
            "answer": "A list of local programs and participation outcomes",
            "type": "multiple_choice"
        },
        "3": {
            "question": "Describe one question you would ask Philadelphia residents to determine whether a company's outreach is meeting community needs.",
            "accepted_answers": [
                "what needs are not being met",
                "how has the program helped the community",
                "what would you change about the company's community program"
            ],
            "answer": "A strong response asks residents about their priorities, whether the program is accessible, what outcomes they have experienced, or what should change.",
            "type": "typed"
        }
    },
    "Philanthropic": {
        "1": {
            "question": "Which activity is an example of corporate philanthropy?",
            "choices": [
                "Donating funds to a community nonprofit",
                "Increasing hidden fees",
                "Reducing product safety testing",
                "Withholding employee pay"
            ],
            "answer": "Donating funds to a community nonprofit",
            "type": "multiple_choice"
        },
        "2": {
            "question": "Which information would make a company's charitable giving report more useful?",
            "choices": [
                "The amount donated, recipients, and outcomes",
                "Only the company's slogan",
                "A list of unrelated products",
                "The names of executives' favorite movies"
            ],
            "answer": "The amount donated, recipients, and outcomes",
            "type": "multiple_choice"
        },
        "3": {
            "question": "Explain the difference between a one-time donation and a long-term philanthropic partnership.",
            "accepted_answers": [
                "a long term partnership provides ongoing support",
                "a one time donation happens once while a partnership continues",
                "a partnership includes sustained collaboration and support"
            ],
            "answer": "A one-time donation is a single contribution. A long-term partnership involves continued support, collaboration, and often shared goals or measurable outcomes.",
            "type": "typed"
        }
    },
    "Economic": {
        "1": {
            "question": "Which is an example of a company's economic impact?",
            "choices": [
                "Creating jobs and paying employees",
                "Changing the weather",
                "Writing a movie script",
                "Choosing a team mascot"
            ],
            "answer": "Creating jobs and paying employees",
            "type": "multiple_choice"
        },
        "2": {
            "question": "A company hires local workers and purchases supplies from nearby businesses. What is one possible community benefit?",
            "choices": [
                "More money may circulate in the local economy",
                "Local businesses must close",
                "The community loses all employment",
                "The company no longer has customers"
            ],
            "answer": "More money may circulate in the local economy",
            "type": "multiple_choice"
        },
        "3": {
            "question": "Identify two ways a company can affect the economic well-being of a neighborhood.",
            "accepted_answers": [
                "jobs and local purchasing",
                "employment and wages",
                "hiring local workers and supporting local businesses",
                "wages taxes and local investment"
            ],
            "answer": "Possible answers include job creation, wages and benefits, local purchasing, taxes, investment, and effects on nearby businesses.",
            "type": "typed"
        }
    },
    "Clams": {
        "1": {
            "question": "When evaluating a claim made by a company, what should you look for first?",
            "choices": [
                "Evidence that supports the claim",
                "The largest font on the website",
                "The number of colors in the logo",
                "An unrelated social media trend"
            ],
            "answer": "Evidence that supports the claim",
            "type": "multiple_choice"
        },
        "2": {
            "question": "A company says its product is environmentally friendly. Which source would best help you evaluate that claim?",
            "choices": [
                "A credible report with methods and supporting data",
                "An anonymous comment with no details",
                "A celebrity photo",
                "A product slogan"
            ],
            "answer": "A credible report with methods and supporting data",
            "type": "multiple_choice"
        },
        "3": {
            "question": "Choose one claim made by a company you researched. Explain what evidence would support or challenge that claim.",
            "accepted_answers": [
                "compare the claim with credible data",
                "use independent research and company reports",
                "check sources methods and measurable outcomes"
            ],
            "answer": "A strong response identifies a specific claim and explains how credible, relevant evidence—such as independent research, public records, data, or a company report—could verify or challenge it.",
            "type": "typed"
        }
    },
    "Evident Scenario": {
        "1": {
            "question": "A company report includes a chart showing that donations increased. What is the chart?",
            "choices": [
                "A piece of evidence",
                "A legal contract",
                "A customer complaint",
                "A company logo"
            ],
            "answer": "A piece of evidence",
            "type": "multiple_choice"
        },
        "2": {
            "question": "A company says its new program improved student outcomes. Which additional information would help test this statement?",
            "choices": [
                "Before-and-after results and how they were measured",
                "The program's color scheme",
                "The CEO's favorite subject",
                "A list of office locations only"
            ],
            "answer": "Before-and-after results and how they were measured",
            "type": "multiple_choice"
        },
        "3": {
            "question": "A company claims that its community program is successful, but residents report that they have not seen any benefits. What evidence would you gather before reaching a conclusion?",
            "accepted_answers": [
                "interview residents and review program outcomes",
                "compare company data with community feedback",
                "collect independent data and community testimony"
            ],
            "answer": "A strong response compares multiple sources, such as resident interviews, participation records, measurable outcomes, independent reporting, and the company's own data.",
            "type": "typed"
        }
    }
}


def create_question_file():
    """Create an editable JSON question bank the first time the game runs."""
    if not QUESTION_FILE.exists():
        with QUESTION_FILE.open("w", encoding="utf-8") as file:
            json.dump(DEMO_QUESTIONS, file, indent=4, ensure_ascii=False)


def load_questions():
    create_question_file()
    try:
        with QUESTION_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        messagebox.showerror(
            "Question bank error",
            f"Could not read trivia_questions.json.\n\n{error}\n\n"
            "The game will close. Restore the original JSON file or correct it."
        )
        raise

    # Check that all expected categories and levels are present.
    for category in CATEGORIES:
        if category not in data:
            data[category] = {}
        for level in ("1", "2", "3"):
            if level not in data[category]:
                data[category][level] = None
    return data


def normalize_answer(value):
    """Normalize text for a forgiving exact/phrase comparison."""
    value = unicodedata.normalize("NFKD", str(value)).casefold()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    return " ".join(value.split())


# ------------------------------- DATABASE --------------------------------

def initialize_database():
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                player_name TEXT PRIMARY KEY COLLATE NOCASE,
                highest_score INTEGER NOT NULL DEFAULT 0,
                games_played INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                incorrect_count INTEGER NOT NULL,
                played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_game_result(player, score, correct, incorrect):
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute("""
            INSERT INTO leaderboard
                (player_name, highest_score, games_played, updated_at)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(player_name) DO UPDATE SET
                highest_score = MAX(leaderboard.highest_score, excluded.highest_score),
                games_played = leaderboard.games_played + 1,
                updated_at = CURRENT_TIMESTAMP
        """, (player, score))
        connection.execute("""
            INSERT INTO game_history
                (player_name, score, correct_count, incorrect_count)
            VALUES (?, ?, ?, ?)
        """, (player, score, correct, incorrect))


def get_leaderboard(limit=20):
    with sqlite3.connect(DATABASE_FILE) as connection:
        return connection.execute("""
            SELECT player_name, highest_score, games_played
            FROM leaderboard
            ORDER BY highest_score DESC, player_name COLLATE NOCASE ASC
            LIMIT ?
        """, (limit,)).fetchall()


# ------------------------------- GAME APP --------------------------------

class TriviaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CSR Genius Challenge")
        self.root.geometry("1280x820")
        self.root.minsize(980, 680)
        self.root.configure(bg=BG)

        initialize_database()
        self.questions = load_questions()

        self.player = self.ask_player_name()
        self.score = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.used_questions = set()
        self.current_question = None
        self.current_key = None
        self.answer_locked = False
        self.game_saved = False

        self.build_shell()
        self.show_board()

    def ask_player_name(self):
        name = simpledialog.askstring(
            "Welcome to CSR Genius",
            "Enter your gamer name:",
            parent=self.root
        )
        return (name or "Guest").strip()[:30] or "Guest"

    def build_shell(self):
        self.header = tk.Frame(self.root, bg=BG, padx=12, pady=8)
        self.header.pack(fill="x")

        nav_items = [
            ("Company Overview", self.show_overview),
            ("Highest Score Board", self.show_leaderboard),
            ("Game Instructions", self.show_instructions),
            ("Contact Genius", self.show_contact),
        ]
        for label, command in nav_items:
            button = tk.Button(
                self.header, text=label, command=command,
                font=("Arial", 13, "bold"), bg=BG, fg=BLACK,
                activebackground=DARK_YELLOW, relief="solid",
                bd=1, padx=12, pady=10, cursor="hand2"
            )
            button.pack(side="left", expand=True, fill="x", padx=2)

        self.status = tk.Frame(self.root, bg=BG, padx=18, pady=6)
        self.status.pack(fill="x")

        self.player_label = tk.Label(
            self.status, text="", bg=BG, fg=BLACK,
            font=("Arial", 12, "bold")
        )
        self.player_label.pack(side="left")

        tk.Button(
            self.status, text="Change Player",
            command=self.change_player, bg=BG, fg=BLACK,
            relief="groove", cursor="hand2"
        ).pack(side="right", padx=4)

        tk.Button(
            self.status, text="New Game",
            command=self.new_game, bg=BG, fg=BLACK,
            relief="groove", cursor="hand2"
        ).pack(side="right", padx=4)

        self.body = tk.Frame(self.root, bg=BG, padx=18, pady=10)
        self.body.pack(fill="both", expand=True)

        self.refresh_status()

    def refresh_status(self):
        self.player_label.config(
            text=f"PLAYER: {self.player}     |     SCORE: ${self.score:,}     "
                 f"|     CORRECT: {self.correct_count}     "
                 f"|     INCORRECT: {self.incorrect_count}"
        )

    def clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def add_page_title(self, title, subtitle=None):
        tk.Label(
            self.body, text=title, bg=BG, fg=BLACK,
            font=("Arial", 25, "bold")
        ).pack(anchor="w", pady=(0, 4))
        if subtitle:
            tk.Label(
                self.body, text=subtitle, bg=BG, fg=BLACK,
                font=("Arial", 11), wraplength=1100, justify="left"
            ).pack(anchor="w", pady=(0, 12))

    # ------------------------------ BOARD --------------------------------

    def show_board(self):
        self.clear_body()
        self.add_page_title(
            "CSR GENIUS CHALLENGE",
            "Choose a category and question value. Each question can only be played once per game."
        )

        board_area = tk.Frame(self.body, bg=BG)
        board_area.pack(fill="both", expand=True)

        # Seven category columns; three question-value rows.
        for col, category in enumerate(CATEGORIES):
            board_area.grid_columnconfigure(col, weight=1, uniform="category")
            heading = tk.Label(
                board_area, text=category, bg=BLACK, fg=WHITE,
                font=("Arial", 10, "bold"), wraplength=130,
                height=3, relief="solid", bd=1
            )
            heading.grid(row=0, column=col, sticky="nsew", padx=2, pady=2)

            for row, level in enumerate((1, 2, 3), start=1):
                key = (category, level)
                used = key in self.used_questions
                question = self.questions.get(category, {}).get(str(level))
                available = isinstance(question, dict) and bool(question.get("question"))
                value = LEVEL_VALUES[level]

                if used:
                    label, color, state = "PLAYED", "#555555", "disabled"
                elif not available:
                    label, color, state = "ADD QUESTION", "#777777", "disabled"
                else:
                    label, color, state = f"${value:,}", BLACK, "normal"

                button = tk.Button(
                    board_area, text=label,
                    command=lambda c=category, l=level: self.open_question(c, l),
                    bg=color, fg=WHITE, activebackground=BLUE,
                    activeforeground=WHITE, disabledforeground="#DDDDDD",
                    font=("Arial", 17, "bold"), relief="solid", bd=1,
                    cursor="hand2" if state == "normal" else "arrow",
                    state=state
                )
                button.grid(
                    row=row, column=col, sticky="nsew",
                    padx=2, pady=2, ipadx=3, ipady=28
                )

        for row in range(4):
            board_area.grid_rowconfigure(row, weight=1)

        footer = tk.Frame(self.body, bg=BG)
        footer.pack(fill="x", pady=(10, 0))
        tk.Label(
            footer,
            text="Scoring: correct answers earn the displayed points. Incorrect answers earn 0 points.",
            bg=BG, fg=BLACK, font=("Arial", 10, "italic")
        ).pack(side="left")
        tk.Button(
            footer, text="Finish Game & Save Score",
            command=self.finish_game, bg=BLACK, fg=WHITE,
            font=("Arial", 11, "bold"), padx=12, pady=8,
            cursor="hand2"
        ).pack(side="right")

    # ---------------------------- QUESTIONS ------------------------------

    def open_question(self, category, level):
        key = (category, level)
        if key in self.used_questions:
            return

        question = self.questions.get(category, {}).get(str(level))
        if not isinstance(question, dict) or not question.get("question"):
            messagebox.showinfo(
                "Question not added",
                f"No question has been added for {category}, Level {level}.\n\n"
                f"Edit this entry in:\n{QUESTION_FILE}"
            )
            return

        self.current_question = question
        self.current_key = key
        self.answer_locked = False
        self.show_question()

    def show_question(self):
        self.clear_body()
        category, level = self.current_key
        value = LEVEL_VALUES[level]

        top = tk.Frame(self.body, bg=BG)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(
            top, text=f"{category.upper()}  |  LEVEL {level}",
            bg=BG, fg=BLACK, font=("Arial", 14, "bold")
        ).pack(side="left")
        tk.Label(
            top, text=f"${value:,} POINTS",
            bg=BG, fg=BLACK, font=("Arial", 14, "bold")
        ).pack(side="right")

        card = tk.Frame(
            self.body, bg=BLACK, padx=35, pady=30,
            highlightbackground=BLACK, highlightthickness=2
        )
        card.pack(fill="both", expand=True, padx=35, pady=8)

        tk.Label(
            card, text="QUESTION SELECTED",
            bg=BLACK, fg=BG, font=("Arial", 25, "bold")
        ).pack(anchor="w", pady=(0, 18))

        tk.Label(
            card, text=self.current_question["question"],
            bg=BLACK, fg=WHITE, font=("Arial", 20),
            wraplength=950, justify="left"
        ).pack(anchor="w", pady=(0, 24))

        self.answer_area = tk.Frame(card, bg=BLACK)
        self.answer_area.pack(fill="both", expand=True)

        question_type = self.current_question.get("type", "multiple_choice")
        if level in (1, 2) and question_type == "multiple_choice":
            self.show_multiple_choice()
        else:
            self.show_typed_response()

        self.feedback = tk.Label(
            card, text="", bg=BLACK, fg=BG,
            font=("Arial", 13, "bold"), wraplength=950,
            justify="left"
        )
        self.feedback.pack(anchor="w", pady=12)

        bottom = tk.Frame(self.body, bg=BG)
        bottom.pack(fill="x", pady=10)
        tk.Button(
            bottom, text="← Return to Game Board",
            command=self.show_board, bg=BG, fg=BLACK,
            font=("Arial", 11, "bold"), cursor="hand2"
        ).pack(side="left")

    def show_multiple_choice(self):
        choices = self.current_question.get("choices", [])
        if not choices:
            tk.Label(
                self.answer_area,
                text="No answer choices have been added to this question.",
                bg=BLACK, fg=WHITE, font=("Arial", 13)
            ).pack(anchor="w")
            return

        for index, choice in enumerate(choices):
            tk.Button(
                self.answer_area,
                text=f"{chr(65 + index)}.  {choice}",
                command=lambda selected=choice: self.grade_multiple_choice(selected),
                bg=WHITE, fg=BLACK, activebackground=BG,
                font=("Arial", 14), anchor="w", justify="left",
                wraplength=900, padx=14, pady=10,
                relief="flat", cursor="hand2"
            ).pack(fill="x", pady=5)

    def show_typed_response(self):
        tk.Label(
            self.answer_area,
            text="TYPE YOUR RESPONSE BELOW:",
            bg=BLACK, fg=WHITE, font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.response_box = tk.Text(
            self.answer_area, height=5, wrap="word",
            font=("Arial", 14), padx=10, pady=10
        )
        self.response_box.pack(fill="x", pady=(0, 10))

        tk.Label(
            self.answer_area,
            text="After submitting, the game host can review the response and award the points.",
            bg=BLACK, fg="#DDDDDD", font=("Arial", 10, "italic")
        ).pack(anchor="w")

        self.submit_button = tk.Button(
            self.answer_area, text="Submit Response",
            command=self.submit_typed_response,
            bg=BG, fg=BLACK, font=("Arial", 12, "bold"),
            padx=15, pady=8, cursor="hand2"
        )
        self.submit_button.pack(anchor="w", pady=10)

    def grade_multiple_choice(self, selected):
        if self.answer_locked:
            return
        self.answer_locked = True
        correct_answer = self.current_question.get("answer", "")
        is_correct = normalize_answer(selected) == normalize_answer(correct_answer)
        self.record_result(is_correct)
        if is_correct:
            self.feedback.config(
                text=f"CORRECT! You earned ${LEVEL_VALUES[self.current_key[1]]:,}.",
                fg="#7CFF9B"
            )
        else:
            self.feedback.config(
                text=f"Not quite. Correct answer: {correct_answer}",
                fg="#FFB4A9"
            )
        self.show_continue_button()

    def submit_typed_response(self):
        if self.answer_locked:
            return
        response = self.response_box.get("1.0", "end").strip()
        if not response:
            messagebox.showwarning("Response needed", "Please type a response before submitting.")
            return

        self.answer_locked = True
        self.submit_button.config(state="disabled")
        self.response_box.config(state="disabled")

        tk.Label(
            self.answer_area,
            text="HOST REVIEW: Read the response, then choose whether it meets the answer criteria.",
            bg=BLACK, fg=BG, font=("Arial", 11, "bold"),
            wraplength=900, justify="left"
        ).pack(anchor="w", pady=(8, 4))

        review = tk.Frame(self.answer_area, bg=BLACK)
        review.pack(anchor="w", pady=8)

        tk.Button(
            review, text="Mark Correct",
            command=lambda: self.grade_typed(True),
            bg=GREEN, fg=WHITE, font=("Arial", 11, "bold"),
            padx=14, pady=8, cursor="hand2"
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            review, text="Mark Incorrect",
            command=lambda: self.grade_typed(False),
            bg=RED, fg=WHITE, font=("Arial", 11, "bold"),
            padx=14, pady=8, cursor="hand2"
        ).pack(side="left")

        tk.Button(
            review, text="View Suggested Answer",
            command=self.show_suggested_answer,
            bg=WHITE, fg=BLACK, font=("Arial", 10),
            padx=10, pady=8, cursor="hand2"
        ).pack(side="left", padx=8)

    def show_suggested_answer(self):
        messagebox.showinfo(
            "Suggested answer / grading guidance",
            self.current_question.get("answer", "No suggested answer supplied.")
        )

    def grade_typed(self, is_correct):
        self.record_result(is_correct)
        if is_correct:
            self.feedback.config(
                text=f"MARKED CORRECT! You earned ${LEVEL_VALUES[self.current_key[1]]:,}.",
                fg="#7CFF9B"
            )
        else:
            self.feedback.config(
                text="MARKED INCORRECT. No points awarded.",
                fg="#FFB4A9"
            )
        self.show_continue_button()

    def record_result(self, is_correct):
        self.used_questions.add(self.current_key)
        if is_correct:
            self.score += LEVEL_VALUES[self.current_key[1]]
            self.correct_count += 1
        else:
            self.incorrect_count += 1
        self.refresh_status()

    def show_continue_button(self):
        tk.Button(
            self.answer_area, text="Continue to Game Board",
            command=self.show_board,
            bg=BG, fg=BLACK, font=("Arial", 12, "bold"),
            padx=14, pady=8, cursor="hand2"
        ).pack(anchor="w", pady=10)

    # ------------------------------ PAGES --------------------------------

    def show_leaderboard(self):
        self.clear_body()
        self.add_page_title(
            "HIGHEST SCORE BOARD",
            "The leaderboard saves each player's highest score on this computer."
        )

        rows = get_leaderboard(25)
        table = tk.Frame(self.body, bg=BLACK, padx=2, pady=2)
        table.pack(fill="x", pady=10)

        headers = ["RANK", "GAMER", "HIGHEST SCORE", "GAMES PLAYED"]
        widths = [12, 40, 25, 20]
        for col, (heading, width) in enumerate(zip(headers, widths)):
            tk.Label(
                table, text=heading, width=width, bg=BLACK, fg=BG,
                font=("Arial", 11, "bold"), padx=8, pady=10
            ).grid(row=0, column=col, sticky="nsew")

        if not rows:
            tk.Label(
                self.body, text="No scores saved yet. Finish a game to appear here.",
                bg=BG, fg=BLACK, font=("Arial", 13)
            ).pack(anchor="w", pady=15)
        else:
            for rank, (name, highest, games) in enumerate(rows, start=1):
                values = [str(rank), name, f"${highest:,}", str(games)]
                for col, (value, width) in enumerate(zip(values, widths)):
                    tk.Label(
                        table, text=value, width=width,
                        bg=WHITE if rank % 2 else "#F0F0F0",
                        fg=BLACK, font=("Arial", 12),
                        padx=8, pady=9
                    ).grid(row=rank, column=col, sticky="nsew")

        tk.Button(
            self.body, text="Return to Game Board",
            command=self.show_board, bg=BLACK, fg=WHITE,
            font=("Arial", 11, "bold"), padx=12, pady=8
        ).pack(anchor="w", pady=15)

    def show_instructions(self):
        self.clear_body()
        self.add_page_title("GAME INSTRUCTIONS")
        instructions = [
            "1. Enter a gamer name. Your highest score is saved under that name.",
            "2. Choose any available category and dollar value on the game board.",
            "3. Levels 1 and 2 use multiple-choice answers.",
            "4. Level 3 uses a typed response. The host reviews it and marks it correct or incorrect.",
            "5. Correct answers earn the displayed point value. Incorrect answers earn 0 points.",
            "6. Each question can only be selected once during a game.",
            "7. Select Finish Game & Save Score to record the game on the Highest Score Board.",
            "8. The leaderboard keeps each player's highest score and total games played."
        ]
        for line in instructions:
            tk.Label(
                self.body, text=line, bg=BG, fg=BLACK,
                font=("Arial", 14), wraplength=1050,
                justify="left", anchor="w"
            ).pack(fill="x", anchor="w", pady=7)

        tk.Button(
            self.body, text="Return to Game Board",
            command=self.show_board, bg=BLACK, fg=WHITE,
            font=("Arial", 11, "bold"), padx=12, pady=8
        ).pack(anchor="w", pady=15)

    def show_overview(self):
        self.clear_body()
        self.add_page_title(
            "COMPANY OVERVIEW",
            "Use this section to introduce the company or companies being investigated."
        )
        tk.Label(
            self.body,
            text=(
                "PROJECT TITLE\n\n"
                "Why did you choose your topic of focus? Acknowledge your investigation "
                "tools and experience discovering and evaluating companies that impact "
                "your daily living.\n\n"
                "ABOUT THE COMPANY\n\n"
                "Describe the company, its community impact, and the claims you are "
                "investigating. Share your final conclusion through a report card, "
                "feedback, or comparison report card.\n\n"
                "CSR REPORT\n\n"
                "Evaluate the Ethical, Economic, Legal, and Philanthropic pillars. "
                "Summarize your evidence and include citations."
            ),
            bg=BG, fg=BLACK, font=("Arial", 15),
            wraplength=1050, justify="left", anchor="w"
        ).pack(fill="x", pady=15)

        tk.Button(
            self.body, text="Return to Game Board",
            command=self.show_board, bg=BLACK, fg=WHITE,
            font=("Arial", 11, "bold"), padx=12, pady=8
        ).pack(anchor="w", pady=15)

    def show_contact(self):
        self.clear_body()
        self.add_page_title("CONTACT GENIUS")
        tk.Label(
            self.body,
            text=(
                "Add your program or facilitator contact information here.\n\n"
                "To customize this page, edit the show_contact() function in the Python script."
            ),
            bg=BG, fg=BLACK, font=("Arial", 15),
            justify="left", anchor="w"
        ).pack(anchor="w", pady=15)
        tk.Button(
            self.body, text="Return to Game Board",
            command=self.show_board, bg=BLACK, fg=WHITE,
            font=("Arial", 11, "bold"), padx=12, pady=8
        ).pack(anchor="w", pady=15)

    # -------------------------- GAME MANAGEMENT --------------------------

    def finish_game(self):
        if self.game_saved:
            messagebox.showinfo("Already saved", "This game has already been saved.")
            return

        save_game_result(
            self.player, self.score, self.correct_count, self.incorrect_count
        )
        self.game_saved = True
        messagebox.showinfo(
            "Game saved",
            f"Great work, {self.player}!\n\n"
            f"Final score: ${self.score:,}\n"
            f"Correct: {self.correct_count}\n"
            f"Incorrect: {self.incorrect_count}\n\n"
            "Your highest score board has been updated."
        )
        self.show_leaderboard()

    def new_game(self):
        if (self.score or self.correct_count or self.incorrect_count) and not self.game_saved:
            answer = messagebox.askyesno(
                "Start a new game?",
                "This game has not been saved. Start a new game without saving this score?"
            )
            if not answer:
                return

        self.score = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.used_questions = set()
        self.current_question = None
        self.current_key = None
        self.answer_locked = False
        self.game_saved = False
        self.refresh_status()
        self.show_board()

    def change_player(self):
        name = simpledialog.askstring(
            "Change Player", "Enter the next gamer name:", parent=self.root
        )
        if name and name.strip():
            if (self.score or self.correct_count or self.incorrect_count) and not self.game_saved:
                save_first = messagebox.askyesno(
                    "Save current game?",
                    "Would you like to save the current player's score before switching?"
                )
                if save_first:
                    save_game_result(
                        self.player, self.score,
                        self.correct_count, self.incorrect_count
                    )
            self.player = name.strip()[:30]
            self.score = 0
            self.correct_count = 0
            self.incorrect_count = 0
            self.used_questions = set()
            self.current_question = None
            self.current_key = None
            self.answer_locked = False
            self.game_saved = False
            self.refresh_status()
            self.show_board()


def main():
    root = tk.Tk()
    app = TriviaGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
