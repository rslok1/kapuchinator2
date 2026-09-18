import asyncio
import os
import pygame

# ================= ФИКС ПУТЕЙ ДЛЯ ANDROID =================
# На Android __file__ указывает не туда, где лежат ресурсы.
# os.path.abspath('.') возвращает папку, куда распакованы картинки и звуки.
BASE_DIR = os.path.abspath('.')


def get_path(filename):
    """Возвращает полный путь к файлу внутри APK."""
    return os.path.join(BASE_DIR, filename)


# Инициализация Pygame
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Не удалось запустить микшер звука: {e}")

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("Капучинатор - Фиксики")

clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)
GREEN = (50, 205, 50)
RED = (220, 50, 50)
ORANGE = (255, 140, 0)
BLUE = (30, 144, 255)
PURPLE = (138, 43, 225)
GOLD = (255, 215, 0)

# Шрифты
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 22)


# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ЗАГРУЗКИ =================
def load_image(filename, size, fallback_color, text=""):
    """Загружает картинку по правильному пути Android."""
    full_path = get_path(filename)
    try:
        img = pygame.image.load(full_path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"Ошибка загрузки картинки {filename} по пути {full_path}: {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(fallback_color)
        if text:
            txt_surf = font_small.render(text, True, WHITE)
            surf.blit(txt_surf, (5, size[1] // 2 - 10))
        return surf


def load_sound(filename):
    """Загружает звук (FX) по правильному пути Android."""
    full_path = get_path(filename)
    try:
        return pygame.mixer.Sound(full_path)
    except Exception as e:
        print(f"Ошибка загрузки звука {filename}: {e}")
        return None


def play_music(filename):
    """Загружает и запускает фоновую песню по правильному пути."""
    full_path = get_path(filename)
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Ошибка воспроизведения музыки {filename}: {e}")


# ================= ЗАГРУЗКА ЗВУКОВ И КАРТИНОК =================
sound_menu_top = load_sound("67.mp3")
intro_song_path = "1.mp3"

song_files = [
    "song1.mp3",
    "song2.mp3",
    "song3.mp3",
    "song4.mp3",
    "song5.mp3",
    "song6.mp3",
    "song7.mp3",
    "song8.mp3",
    "song9.mp3",
    "song10.mp3",
]

# Картинки фонов
img_bg_menu = load_image("1fon.jpg", (WIDTH, HEIGHT), (230, 240, 250), "")
img_bg_game = load_image("fon2.png", (WIDTH, HEIGHT), (255, 240, 245), "")
img_bg_shop = load_image("shop.jpg", (WIDTH, HEIGHT), (200, 220, 255), "")

# Главное меню
img_menu_top = load_image("kapych.png", (500, 150), ORANGE, "Капучинатор")

# Перфоратор и стандартные герои
img_perforator = load_image("perf.png", (550, 300), DARK_GRAY, "Перфоратор")
img_simka = load_image("simka.png", (100, 130), ORANGE, "Симка")
img_nolik_closed = load_image("nolik.png", (100, 120), BLUE, "Нолик")
img_nolik_open = load_image("nolik.png", (100, 120), BLUE, "Нолик (Рот)")

# Микрофоны
img_microphone = load_image("micro.png", (15, 35), GRAY, "Микрофон")
img_microphone_large = load_image("micro.png", (18, 42), GRAY, "Микрофон")

# Новые герои
img_new_hero1 = load_image("simka2.png", (125, 160), RED, "Новый Герой 1")
img_new_hero2_closed = load_image(
    "nolik2.png", (125, 150), PURPLE, "Новый Герой 2"
)
img_new_hero2_open = load_image(
    "nolik2.png", (125, 150), PURPLE, "Герой 2 (Рот)"
)

# Иконки
img_pause_icon = load_image("stop.png", (40, 40), RED, "||")
img_play_icon = load_image("stop.png", (40, 40), GREEN, ">")


# ================= ГЛАВНЫЙ ЦИКЛ =================
async def main():
    state = "MENU"

    # Движение перфоратора
    hero_x = -500
    target_x = 260
    hero_y = 250
    hero_stopped = False

    is_music_playing = False
    is_paused = False

    unlocked_songs_shop = {4: False, 5: False, 6: False, 7: False}
    unlocked_heroes = {"hero1": False, "hero2": False}
    active_heroes = "DEFAULT"

    secret_unlocked = {8: False, 9: False}

    simka_flip_timer = 0
    simka_mirrored = False

    # --- КНОПКИ ИГРОВОГО ЭКРАНА ---
    top_buttons = []
    btn_width, btn_height = 140, 50
    start_x = 180
    for i in range(4):
        rect = pygame.Rect(start_x + i * 160, 20, btn_width, btn_height)
        top_buttons.append({"rect": rect, "id": i, "title": f"Песня {i+1}"})

    shop_open_btn = pygame.Rect(830, 15, 150, 55)

    btn_bottom_left = {
        "rect": pygame.Rect(10, 530, 230, 60),
        "id": 8,
        "title": "Секретная песня 1",
    }
    btn_bottom_right = {
        "rect": pygame.Rect(760, 530, 230, 60),
        "id": 9,
        "title": "Секретная песня 2",
    }

    pause_button_rect = pygame.Rect(WIDTH // 2 - 30, 540, 60, 50)

    capuchinator_btn = pygame.Rect(WIDTH // 2 - 150, 420, 300, 80)
    menu_top_img_rect = pygame.Rect(WIDTH // 2 - 250, 80, 500, 150)

    # --- КНОПКИ ЭКРАНА МАГАЗИНА ---
    shop_exit_btn = pygame.Rect(30, 20, 140, 50)
    shop_pause_btn_rect = pygame.Rect(WIDTH - 90, 20, 60, 50)

    shop_song_btns = []
    for idx, s_id in enumerate([4, 5, 6, 7]):
        r = pygame.Rect(100 + (idx % 2) * 420, 120 + (idx // 2) * 90, 360, 65)
        shop_song_btns.append(
            {"rect": r, "id": s_id, "title": f"Песня {s_id+1}"}
        )

    shop_hero1_btn = pygame.Rect(100, 320, 360, 70)
    shop_hero2_btn = pygame.Rect(520, 320, 360, 70)
    shop_use_new_heroes_btn = pygame.Rect(WIDTH // 2 - 200, 430, 400, 65)

    running = True

    while running:
        dt = clock.tick(60)
        current_time = pygame.time.get_ticks()

        # ---------------- 1. ОБРАБОТКА СОБЫТИЙ ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if state == "MENU":
                    if menu_top_img_rect.collidepoint(mx, my):
                        if sound_menu_top:
                            sound_menu_top.play(-1)

                    elif capuchinator_btn.collidepoint(mx, my):
                        if sound_menu_top:
                            sound_menu_top.stop()
                        state = "SLIDING"
                        play_music(intro_song_path)
                        is_music_playing = True
                        is_paused = False

                elif state == "GAME" and hero_stopped:
                    if shop_open_btn.collidepoint(mx, my):
                        state = "SHOP"

                    elif pause_button_rect.collidepoint(mx, my):
                        if is_music_playing:
                            if not is_paused:
                                pygame.mixer.music.pause()
                                is_paused = True
                            else:
                                pygame.mixer.music.unpause()
                                is_paused = False

                    for btn in top_buttons:
                        if btn["rect"].collidepoint(mx, my):
                            play_music(song_files[btn["id"]])
                            is_music_playing = True
                            is_paused = False

                    for btn in [btn_bottom_left, btn_bottom_right]:
                        if btn["rect"].collidepoint(mx, my):
                            song_id = btn["id"]
                            if secret_unlocked[song_id]:
                                play_music(song_files[song_id])
                                is_music_playing = True
                                is_paused = False
                            else:
                                secret_unlocked[song_id] = True
                                play_music(song_files[song_id])
                                is_music_playing = True
                                is_paused = False

                elif state == "SHOP":
                    if shop_exit_btn.collidepoint(mx, my):
                        state = "GAME"

                    elif shop_pause_btn_rect.collidepoint(mx, my):
                        if is_music_playing:
                            if not is_paused:
                                pygame.mixer.music.pause()
                                is_paused = True
                            else:
                                pygame.mixer.music.unpause()
                                is_paused = False

                    for s_btn in shop_song_btns:
                        if s_btn["rect"].collidepoint(mx, my):
                            s_id = s_btn["id"]
                            if not unlocked_songs_shop[s_id]:
                                unlocked_songs_shop[s_id] = True
                            play_music(song_files[s_id])
                            is_music_playing = True
                            is_paused = False

                    if shop_hero1_btn.collidepoint(mx, my):
                        if not unlocked_heroes["hero1"]:
                            unlocked_heroes["hero1"] = True

                    if shop_hero2_btn.collidepoint(mx, my):
                        if not unlocked_heroes["hero2"]:
                            unlocked_heroes["hero2"] = True

                    if shop_use_new_heroes_btn.collidepoint(mx, my):
                        if (
                            unlocked_heroes["hero1"]
                            and unlocked_heroes["hero2"]
                        ):
                            active_heroes = (
                                "NEW"
                                if active_heroes == "DEFAULT"
                                else "DEFAULT"
                            )

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if state == "MENU":
                    if sound_menu_top:
                        sound_menu_top.stop()

        # ---------------- 2. ЛОГИКА И АНИМАЦИИ ----------------
        if (
            state in ["SLIDING", "GAME", "SHOP"]
            and is_music_playing
            and not is_paused
        ):
            if not pygame.mixer.music.get_busy():
                is_music_playing = False

        if state == "SLIDING":
            if hero_x < target_x:
                hero_x += 3
            else:
                hero_x = target_x
                hero_stopped = True
                state = "GAME"

        if is_music_playing and not is_paused:
            if current_time - simka_flip_timer >= 670:
                simka_mirrored = not simka_mirrored
                simka_flip_timer = current_time
        else:
            simka_mirrored = False

        # ---------------- 3. ОТРИСОВКА ЭКРАНА ----------------
        if state == "MENU":
            screen.blit(img_bg_menu, (0, 0))
            screen.blit(img_menu_top, menu_top_img_rect.topleft)

            title_txt = font_large.render("ГЛАВНОЕ МЕНЮ", True, BLACK)
            screen.blit(
                title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 260)
            )

            pygame.draw.rect(screen, BLACK, capuchinator_btn, border_radius=15)
            pygame.draw.rect(
                screen, WHITE, capuchinator_btn, 3, border_radius=15
            )
            cap_text = font_medium.render("КАПУЧИНАТОР", True, WHITE)
            screen.blit(
                cap_text,
                (
                    capuchinator_btn.centerx - cap_text.get_width() // 2,
                    capuchinator_btn.centery - cap_text.get_height() // 2,
                ),
            )

        elif state in ["SLIDING", "GAME"]:
            screen.blit(img_bg_game, (0, 0))

            screen.blit(img_perforator, (hero_x, hero_y + 80))

            if active_heroes == "NEW":
                left_hero_img = img_new_hero1
                left_pos = (hero_x + 40, hero_y - 70)
            else:
                left_hero_img = img_simka
                left_pos = (hero_x + 50, hero_y - 15)

            current_left_img = (
                pygame.transform.flip(left_hero_img, True, False)
                if simka_mirrored
                else left_hero_img
            )
            screen.blit(current_left_img, left_pos)

            if active_heroes == "NEW":
                right_pos = (hero_x + 350, hero_y - 65)
                right_hero_img = (
                    img_new_hero2_open
                    if (is_music_playing and not is_paused)
                    else img_new_hero2_closed
                )
            else:
                right_pos = (hero_x + 360, hero_y - 10)
                right_hero_img = (
                    img_nolik_open
                    if (is_music_playing and not is_paused)
                    else img_nolik_closed
                )

            screen.blit(right_hero_img, right_pos)

            if is_music_playing and not is_paused:
                if active_heroes == "NEW":
                    screen.blit(
                        img_microphone_large,
                        (right_pos[0] + 100, right_pos[1] + 35),
                    )
                else:
                    screen.blit(
                        img_microphone, (right_pos[0] + 5, right_pos[1] + 55)
                    )

            if hero_stopped:
                for btn in top_buttons:
                    pygame.draw.rect(
                        screen, GREEN, btn["rect"], border_radius=10
                    )
                    pygame.draw.rect(
                        screen, BLACK, btn["rect"], 2, border_radius=10
                    )
                    txt = font_small.render(btn["title"], True, BLACK)
                    screen.blit(
                        txt,
                        (
                            btn["rect"].centerx - txt.get_width() // 2,
                            btn["rect"].centery - txt.get_height() // 2,
                        ),
                    )

                pygame.draw.rect(screen, GOLD, shop_open_btn, border_radius=12)
                pygame.draw.rect(
                    screen, BLACK, shop_open_btn, 2, border_radius=12
                )
                shop_txt = font_medium.render("МАГАЗИН", True, BLACK)
                screen.blit(
                    shop_txt,
                    (
                        shop_open_btn.centerx - shop_txt.get_width() // 2,
                        shop_open_btn.centery - shop_txt.get_height() // 2,
                    ),
                )

                for btn in [btn_bottom_left, btn_bottom_right]:
                    b_id = btn["id"]
                    b_color = (
                        PURPLE if secret_unlocked[b_id] else (120, 120, 120)
                    )
                    pygame.draw.rect(
                        screen, b_color, btn["rect"], border_radius=12
                    )
                    pygame.draw.rect(
                        screen, BLACK, btn["rect"], 2, border_radius=12
                    )

                    label = (
                        btn["title"]
                        if secret_unlocked[b_id]
                        else "Реклама за песню"
                    )
                    txt = font_small.render(label, True, WHITE)
                    screen.blit(
                        txt,
                        (
                            btn["rect"].centerx - txt.get_width() // 2,
                            btn["rect"].centery - txt.get_height() // 2,
                        ),
                    )

                pygame.draw.rect(
                    screen, DARK_GRAY, pause_button_rect, border_radius=10
                )
                pygame.draw.rect(
                    screen, WHITE, pause_button_rect, 2, border_radius=10
                )
                current_pause_icon = (
                    img_play_icon if is_paused else img_pause_icon
                )
                screen.blit(
                    current_pause_icon,
                    (
                        pause_button_rect.centerx - 20,
                        pause_button_rect.centery - 20,
                    ),
                )

        elif state == "SHOP":
            screen.blit(img_bg_shop, (0, 0))

            shop_title = font_large.render(
                "МАГАЗИН ТРЕКОВ И ГЕРОЕВ", True, BLACK
            )
            screen.blit(
                shop_title, (WIDTH // 2 - shop_title.get_width() // 2, 25)
            )

            pygame.draw.rect(screen, RED, shop_exit_btn, border_radius=10)
            pygame.draw.rect(screen, WHITE, shop_exit_btn, 2, border_radius=10)
            exit_txt = font_medium.render("Назад", True, WHITE)
            screen.blit(
                exit_txt,
                (
                    shop_exit_btn.centerx - exit_txt.get_width() // 2,
                    shop_exit_btn.centery - exit_txt.get_height() // 2,
                ),
            )

            pygame.draw.rect(
                screen, DARK_GRAY, shop_pause_btn_rect, border_radius=10
            )
            pygame.draw.rect(
                screen, WHITE, shop_pause_btn_rect, 2, border_radius=10
            )
            current_shop_pause_icon = (
                img_play_icon if is_paused else img_pause_icon
            )
            screen.blit(
                current_shop_pause_icon,
                (
                    shop_pause_btn_rect.centerx - 20,
                    shop_pause_btn_rect.centery - 20,
                ),
            )

            for s_btn in shop_song_btns:
                s_id = s_btn["id"]
                is_unlocked = unlocked_songs_shop[s_id]

                color = GREEN if is_unlocked else ORANGE
                pygame.draw.rect(screen, color, s_btn["rect"], border_radius=12)
                pygame.draw.rect(
                    screen, BLACK, s_btn["rect"], 2, border_radius=12
                )

                lbl = (
                    f"Играть {s_btn['title']}"
                    if is_unlocked
                    else f"{s_btn['title']} (За рекламу)"
                )
                txt = font_small.render(lbl, True, BLACK)
                screen.blit(
                    txt,
                    (
                        s_btn["rect"].centerx - txt.get_width() // 2,
                        s_btn["rect"].centery - txt.get_height() // 2,
                    ),
                )

            h1_unlocked = unlocked_heroes["hero1"]
            h1_color = GREEN if h1_unlocked else PURPLE
            pygame.draw.rect(
                screen, h1_color, shop_hero1_btn, border_radius=12
            )
            pygame.draw.rect(
                screen, BLACK, shop_hero1_btn, 2, border_radius=12
            )
            h1_lbl = (
                "Новый Герой 1 открыт"
                if h1_unlocked
                else "Открыть Героя 1 (За рекламу)"
            )
            h1_txt = font_small.render(h1_lbl, True, WHITE)
            screen.blit(
                h1_txt,
                (
                    shop_hero1_btn.centerx - h1_txt.get_width() // 2,
                    shop_hero1_btn.centery - h1_txt.get_height() // 2,
                ),
            )

            h2_unlocked = unlocked_heroes["hero2"]
            h2_color = GREEN if h2_unlocked else PURPLE
            pygame.draw.rect(
                screen, h2_color, shop_hero2_btn, border_radius=12
            )
            pygame.draw.rect(
                screen, BLACK, shop_hero2_btn, 2, border_radius=12
            )
            h2_lbl = (
                "Новый Герой 2 открыт"
                if h2_unlocked
                else "Открыть Героя 2 (За рекламу)"
            )
            h2_txt = font_small.render(h2_lbl, True, WHITE)
            screen.blit(
                h2_txt,
                (
                    shop_hero2_btn.centerx - h2_txt.get_width() // 2,
                    shop_hero2_btn.centery - h2_txt.get_height() // 2,
                ),
            )

            both_unlocked = h1_unlocked and h2_unlocked
            use_btn_color = GOLD if both_unlocked else GRAY
            pygame.draw.rect(
                screen, use_btn_color, shop_use_new_heroes_btn, border_radius=15
            )
            pygame.draw.rect(
                screen, BLACK, shop_use_new_heroes_btn, 2, border_radius=15
            )

            if both_unlocked:
                active_str = (
                    "Используются: НОВЫЕ ГЕРОИ"
                    if active_heroes == "NEW"
                    else "Используются: СИМКА И НОЛИК"
                )
            else:
                active_str = "Откройте обоих героев за рекламу!"

            active_txt = font_medium.render(active_str, True, BLACK)
            screen.blit(
                active_txt,
                (
                    shop_use_new_heroes_btn.centerx
                    - active_txt.get_width() // 2,
                    shop_use_new_heroes_btn.centery
                    - active_txt.get_height() // 2,
                ),
            )

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()
    return


if __name__ == "__main__":
    asyncio.run(main())
