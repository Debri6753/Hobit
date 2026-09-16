import datetime
import json
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView

DATA_FILE = "habits_data.json"


class HabitHeroApp(App):

    def build(self):
        self.data = self.load_data()
        self.check_daily_reset()

        self.root_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Шапка профиля
        self.lbl_level = Label(
            text="", font_size="18sp", bold=True, size_hint_y=None, height=40
        )
        self.lbl_streak = Label(
            text="", font_size="14sp", color=(1, 0.7, 0.5, 1), size_hint_y=None, height=30
        )
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=20)

        self.root_layout.add_widget(self.lbl_level)
        self.root_layout.add_widget(self.lbl_streak)
        self.root_layout.add_widget(self.progress)

        # Ввод новой привычки
        add_box = BoxLayout(size_hint_y=None, height=40, spacing=5)
        self.input_habit = TextInput(hint_text="Новая привычка...", multiline=False)
        btn_add = Button(text="+", size_hint_x=None, width=50)
        btn_add.bind(on_press=self.add_habit)
        add_box.add_widget(self.input_habit)
        add_box.add_widget(btn_add)
        self.root_layout.add_widget(add_box)

        # Прокручиваемый список
        self.scroll = ScrollView()
        self.list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.scroll.add_widget(self.list_layout)
        self.root_layout.add_widget(self.scroll)

        self.refresh_ui()
        return self.root_layout

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "level": 1,
            "xp": 0,
            "streak": 1,
            "last_login": str(datetime.date.today()),
            "habits": [
                {"title": "Зарядка / 10к шагов", "xp": 25, "completed": False},
                {"title": "Чтение книги 15 мин", "xp": 20, "completed": False},
            ],
        }

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def check_daily_reset(self):
        today = datetime.date.today()
        last_login = datetime.date.fromisoformat(self.data["last_login"])
        delta = (today - last_login).days
        if delta >= 1:
            self.data["streak"] = self.data["streak"] + 1 if delta == 1 else 1
            for h in self.data["habits"]:
                h["completed"] = False
            self.data["last_login"] = str(today)
            self.save_data()

    def refresh_ui(self):
        max_xp = self.data["level"] * 100
        self.lbl_level.text = f"Уровень {self.data['level']} ({self.data['xp']}/{max_xp} XP)"
        self.lbl_streak.text = f"🔥 Серия дней: {self.data['streak']}"
        self.progress.max = max_xp
        self.progress.value = self.data["xp"]

        self.list_layout.clear_widgets()
        for idx, habit in enumerate(self.data["habits"]):
            row = BoxLayout(size_hint_y=None, height=40, spacing=5)

            chk = CheckBox(active=habit["completed"], size_hint_x=None, width=40)
            chk.bind(
                active=lambda instance, val, i=idx: self.toggle_habit(i, val)
            )

            lbl = Label(
                text=f"{habit['title']} (+{habit['xp']} XP)",
                text_size=(None, None),
                halign="left",
            )
            btn_del = Button(text="X", size_hint_x=None, width=40)
            btn_del.bind(on_press=lambda instance, i=idx: self.delete_habit(i))

            row.add_widget(chk)
            row.add_widget(lbl)
            row.add_widget(btn_del)
            self.list_layout.add_widget(row)

    def toggle_habit(self, index, is_checked):
        habit = self.data["habits"][index]
        if habit["completed"] == is_checked:
            return

        habit["completed"] = is_checked
        if is_checked:
            self.data["xp"] += habit["xp"]
        else:
            self.data["xp"] = max(0, self.data["xp"] - habit["xp"])

        max_xp = self.data["level"] * 100
        if self.data["xp"] >= max_xp:
            self.data["level"] += 1
            self.data["xp"] -= max_xp

        self.save_data()
        self.refresh_ui()

    def add_habit(self, instance):
        text = self.input_habit.text.strip()
        if text:
            self.data["habits"].append({"title": text, "xp": 20, "completed": False})
            self.input_habit.text = ""
            self.save_data()
            self.refresh_ui()

    def delete_habit(self, index):
        del self.data["habits"][index]
        self.save_data()
        self.refresh_ui()


if __name__ == "__main__":
    HabitHeroApp().run()