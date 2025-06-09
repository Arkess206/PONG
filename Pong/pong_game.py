import pygame
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import os

# --- Глобальные переменные для сложности ---
ball_speed = [5, 5]  # Начальное значение по умолчанию
opponent_speed = 5

# --- Глобальные настройки ---
WIDTH, HEIGHT = 640, 480
BACKGROUND_FOLDER = "backgrounds"
SELECTED_BACKGROUND_FILE = "selected_background.txt"
PADDLE_FOLDER = "paddles"
SELECTED_PADDLE_FILE = "selected_paddle.txt"
MUSIC_FOLDER = "music"  # Папка для звуков
SETTINGS_FILE = "settings.txt"  # Файл для настроек

# --- Универсальная функция загрузки ресурсов ---
def load_resource(folder, filename, scale_to=None):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            resource_name = f.read().strip()
            if resource_name:
                path = os.path.join(folder, resource_name)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, scale_to) if scale_to else img
    return None

# --- Функция загрузки звука ---
def load_sound(folder, filename):
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        sound = pygame.mixer.Sound(path)
        return sound
    print(f"Звук {filename} не найден.")
    return None

# --- Сохранение счёта ---
def save_score(score):
    with open("scores.txt", "a", encoding="utf-8") as f:
        f.write(f"{score}\n")

# --- Сохранение настроек ---
def save_settings(music_volume, ball_volume, background, paddle):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write(f"music_volume={music_volume}\n")
        f.write(f"ball_volume={ball_volume}\n")
        f.write(f"background={background}\n")
        f.write(f"paddle={paddle}\n")

# --- Загрузка настроек ---
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = {}
            for line in f:
                key, value = line.strip().split("=")
                settings[key] = value
            return (
                float(settings.get("music_volume", 0.3)),
                float(settings.get("ball_volume", 0.2)),
                settings.get("background", ""),
                settings.get("paddle", "")
            )
    return 0.3, 0.2, "", ""  # Значения по умолчанию

# --- Игра Pong ---
def start_pong_game():
    pygame.init()
    pygame.mixer.init()
    music_volume, ball_volume, selected_background, selected_paddle = load_settings()
    bounce_sound = load_sound(MUSIC_FOLDER, "sound.wav")
    if bounce_sound:
        bounce_sound.set_volume(ball_volume)
    try:
        pygame.mixer.music.load(os.path.join(MUSIC_FOLDER, "sound_lofi.mp3"))
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
    except:
        print("Фоновая музыка не найдена.")
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong Zero")
    font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()
    ball = pygame.Rect(WIDTH // 2 - 10, HEIGHT // 2 - 10, 20, 20)
    player = pygame.Rect(WIDTH - 20, HEIGHT // 2 - 60, 10, 120)
    opponent = pygame.Rect(10, HEIGHT // 2 - 60, 10, 120)
    global ball_speed, opponent_speed
    player_score = 0
    opponent_score = 0
    # Загружаем фон и ракетку из settings.txt, если они есть
    bg_image = None
    paddle_image = None
    if selected_background:
        bg_path = os.path.join(BACKGROUND_FOLDER, selected_background)
        if os.path.exists(bg_path):
            bg_image = pygame.image.load(bg_path).convert_alpha()
            bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
            if not bg_image:
                bg_image = load_resource(BACKGROUND_FOLDER, SELECTED_BACKGROUND_FILE, (WIDTH, HEIGHT))
    if selected_paddle:
        paddle_path = os.path.join(PADDLE_FOLDER, selected_paddle)
        if os.path.exists(paddle_path):
            paddle_image = pygame.image.load(paddle_path).convert_alpha()
            paddle_image = pygame.transform.scale(paddle_image, (10, 120))
    if not paddle_image:
        paddle_image = load_resource(PADDLE_FOLDER, SELECTED_PADDLE_FILE, (10, 120))

    def draw():
        screen.blit(bg_image, (0, 0)) if bg_image else screen.fill(WHITE)
        if paddle_image:
            screen.blit(paddle_image, player.topleft)
            screen.blit(paddle_image, opponent.topleft)
        else:
            pygame.draw.rect(screen, BLACK, player)
            pygame.draw.rect(screen, BLACK, opponent)
        pygame.draw.ellipse(screen, BLACK, ball)
        pygame.draw.aaline(screen, BLACK, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        score_text = font.render(f"{opponent_score} : {player_score}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        mouse_y = pygame.mouse.get_pos()[1]
        player.centery = max(60, min(HEIGHT - 60, mouse_y))
        if opponent.centery < ball.centery:
            opponent.centery += opponent_speed
        elif opponent.centery > ball.centery:
            opponent.centery -= opponent_speed
        opponent.centery = max(60, min(HEIGHT - 60, opponent.centery))
        ball.x += ball_speed[0]
        ball.y += ball_speed[1]
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed[1] = -ball_speed[1]
            bounce_sound.play()
        if ball.left <= 0:
            player_score += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_speed[0] = -ball_speed[0]
        elif ball.right >= WIDTH:
            opponent_score += 1
            ball.center = (WIDTH // 2, HEIGHT // 2)
            ball_speed[0] = -ball_speed[0]
        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed[0] = -ball_speed[0]
            bounce_sound.play()
        draw()
        clock.tick(60)
    pygame.mixer.music.stop()
    pygame.quit()
    save_score(player_score)

# --- Таблица рекордов ---
def show_high_scores():
    if not os.path.exists("scores.txt"):
        messagebox.showinfo("Рекорды", "Ещё нет результатов.")
        return
    with open("scores.txt", "r", encoding="utf-8") as f:
        scores = [int(line.strip()) for line in f if line.strip().isdigit()]
    if not scores:
        messagebox.showinfo("Рекорды", "Ещё нет результатов.")
        return
    scores.sort(reverse=True)
    top_scores = scores[:10]
    text = "\n".join([f"{i+1}. {score} очков" for i, score in enumerate(top_scores)])
    messagebox.showinfo("Топ 10 результатов", text)

# --- Настройки звука ---
def open_settings():
    music_volume, ball_volume, _, _ = load_settings()
    settings_window = tk.Toplevel()
    settings_window.title("Настройки звука")
    settings_window.geometry("300x200")
    tk.Label(settings_window, text="Громкость музыки").pack(pady=5)
    music_slider = ttk.Scale(settings_window, from_=0, to=1, value=music_volume, orient="horizontal")
    music_slider.pack()
    def update_music_volume(val):
        pygame.mixer.music.set_volume(float(val))
        save_settings(float(val), ball_slider.get(), *load_settings()[2:])
    music_slider.config(command=update_music_volume)
    tk.Label(settings_window, text="Громкость мяча").pack(pady=5)
    ball_slider = ttk.Scale(settings_window, from_=0, to=1, value=ball_volume, orient="horizontal")
    ball_slider.pack()
    def update_ball_volume(val):
        try:
            bounce_sound = pygame.mixer.Sound(os.path.join(MUSIC_FOLDER, "sound.wav"))
            bounce_sound.set_volume(float(val))
        except:
            print("Звук мяча не найден.")
        save_settings(music_slider.get(), float(val), *load_settings()[2:])
    ball_slider.config(command=update_ball_volume)

# --- Магазин тем ---
def open_theme_shop():
    music_volume, ball_volume, _, _ = load_settings()
    shop = tk.Toplevel()
    shop.title("Магазин тем")
    notebook = ttk.Notebook(shop)
    frame_backgrounds = tk.Frame(notebook)
    frame_paddles = tk.Frame(notebook)
    notebook.add(frame_backgrounds, text="Фоны")
    notebook.add(frame_paddles, text="Ракетки")
    notebook.pack(fill="both", expand=True)

    # --- Фоны ---
    canvas_bg = tk.Canvas(frame_backgrounds, width=300, height=400)
    scrollbar_bg = tk.Scrollbar(frame_backgrounds, orient="vertical", command=canvas_bg.yview)
    inner_frame_bg = tk.Frame(canvas_bg)
    def apply_theme(name):
        with open(SELECTED_BACKGROUND_FILE, "w", encoding="utf-8") as f:
            f.write(name)
        save_settings(music_volume, ball_volume, name, load_settings()[3])  # Сохраняем фон
        messagebox.showinfo("Тема", f"Применена: {name}")
        shop.destroy()
    for filename in os.listdir(BACKGROUND_FOLDER):
        if filename.lower().endswith(".jpg"):
            path = os.path.join(BACKGROUND_FOLDER, filename)
            try:
                img = Image.open(path)
                img.thumbnail((280, 150))
                tk_img = ImageTk.PhotoImage(img)
                frame_inner = tk.Frame(inner_frame_bg, bd=2, relief="ridge")
                label = tk.Label(frame_inner, image=tk_img)
                label.image = tk_img
                label.pack()
                btn = tk.Button(frame_inner, text=f"Применить: {filename}", command=lambda name=filename: apply_theme(name))
                btn.pack(pady=5)
                frame_inner.pack(padx=5, pady=5, fill="x")
            except:
                continue
    canvas_bg.create_window((0, 0), window=inner_frame_bg, anchor="nw")
    canvas_bg.update_idletasks()
    canvas_bg.configure(scrollregion=canvas_bg.bbox("all"), yscrollcommand=scrollbar_bg.set)
    canvas_bg.pack(side="left", fill="both", expand=True)
    scrollbar_bg.pack(side="right", fill="y")

    # --- Ракетки ---
    canvas_pad = tk.Canvas(frame_paddles, width=300, height=400)
    scrollbar_pad = tk.Scrollbar(frame_paddles, orient="vertical", command=canvas_pad.yview)
    inner_frame_pad = tk.Frame(canvas_pad)
    def apply_paddle(name):
        with open(SELECTED_PADDLE_FILE, "w", encoding="utf-8") as f:
            f.write(name)
        save_settings(music_volume, ball_volume, load_settings()[2], name)  # Сохраняем ракетку
        messagebox.showinfo("Ракетка", f"Применён скин: {name}")
        shop.destroy()
    for filename in os.listdir(PADDLE_FOLDER):
        if filename.lower().endswith(".png"):
            path = os.path.join(PADDLE_FOLDER, filename)
            try:
                img = Image.open(path)
                img.thumbnail((40, 120))
                tk_img = ImageTk.PhotoImage(img)
                frame_inner = tk.Frame(inner_frame_pad, bd=2, relief="ridge")
                label = tk.Label(frame_inner, image=tk_img)
                label.image = tk_img
                label.pack()
                btn = tk.Button(frame_inner, text=f"Применить: {filename}", command=lambda name=filename: apply_paddle(name))
                btn.pack(pady=5)
                frame_inner.pack(padx=5, pady=5, fill="x")
            except:
                continue
    canvas_pad.create_window((0, 0), window=inner_frame_pad, anchor="nw")
    canvas_pad.update_idletasks()
    canvas_pad.configure(scrollregion=canvas_pad.bbox("all"), yscrollcommand=scrollbar_pad.set)
    canvas_pad.pack(side="left", fill="both", expand=True)
    scrollbar_pad.pack(side="right", fill="y")
    # --- Главное меню ---
def run_gui():
    root = tk.Tk()
    root.title("Меню Pong")
    root.geometry("350x350")
    root.resizable(False, False)

    def choose_difficulty():
        diff_window = tk.Toplevel()
        diff_window.title("Выбор сложности")
        diff_window.geometry("200x150")
        diff_window.resizable(False, False)
        tk.Button(diff_window, text="Легко", command=lambda: start_game_with_diff("easy"), width=20).pack(pady=5)
        tk.Button(diff_window, text="Нормально", command=lambda: start_game_with_diff("normal"), width=20).pack(pady=5)
        tk.Button(diff_window, text="Хард", command=lambda: start_game_with_diff("hard"), width=20).pack(pady=5)

    def start_game_with_diff(difficulty):
        global ball_speed, opponent_speed
        if difficulty == "easy":
            ball_speed = [3, 3]
            opponent_speed = 3
        elif difficulty == "normal":
            ball_speed = [5, 5]
            opponent_speed = 5
        elif difficulty == "hard":
            ball_speed = [7, 7]
            opponent_speed = 7
        root.destroy()
        threading.Thread(target=start_pong_game).start()

    def quit_game():
        if messagebox.askokcancel("Выход", "Выйти из игры?"):
            root.destroy()

    def about_game():
        messagebox.showinfo("О игре", "Pong (12.0)\nCreated by Arkess\n\nИстория версий:\n1.0 — Создание\n2.0 — Табло счёта\n3.0 — Звук удара\n4.0 — Фоновая музыка\n5.0 — Таблица рекордов\n6.0 — Магазин тем\n7.0 — Темы для ракеток\n8.0 — Настройки звука\n9.0 — Исправление багов\n10.0 — Уровни сложности\n11.0 — Экран 'О игре'\n12.0 — Сохранение настроек")

    btn_start = tk.Button(root, text="Начало игры", command=choose_difficulty, width=25, height=2)
    btn_scores = tk.Button(root, text="Таблица рекордов", command=show_high_scores, width=25, height=2)
    btn_theme = tk.Button(root, text="Магазин тем", command=open_theme_shop, width=25, height=2)
    btn_settings = tk.Button(root, text="Настройки", command=open_settings, width=25, height=2)
    btn_about = tk.Button(root, text="О игре", command=about_game, width=25, height=2)
    btn_exit = tk.Button(root, text="Выход", command=quit_game, width=25, height=2)

    btn_start.pack(pady=10)
    btn_scores.pack(pady=5)
    btn_theme.pack(pady=5)
    btn_settings.pack(pady=5)
    btn_about.pack(pady=5)
    btn_exit.pack(pady=10)

    root.mainloop()

# --- Запуск ---
if __name__ == "__main__":
    os.makedirs(BACKGROUND_FOLDER, exist_ok=True)
    os.makedirs(PADDLE_FOLDER, exist_ok=True)
    os.makedirs(MUSIC_FOLDER, exist_ok=True)
    run_gui()
