import curses

# ── Konstanta karakter ──────────────────────────────────────────────────────
CHAR_WALL = '+'
CHAR_HEAD = '@'
CHAR_BODY = 'o'
CHAR_FOOD = '*'

# ── Konstanta papan ─────────────────────────────────────────────────────────
BOARD_WIDTH  = 40
BOARD_HEIGHT = 20

# ── Arah gerak ──────────────────────────────────────────────────────────────
UP    = ( 0, -1)
DOWN  = ( 0,  1)
LEFT  = (-1,  0)
RIGHT = ( 1,  0)

# ── Key mapping ─────────────────────────────────────────────────────────────
KEY_UP    = ('KEY_UP',    'w', 'W')
KEY_DOWN  = ('KEY_DOWN',  's', 'S')
KEY_LEFT  = ('KEY_LEFT',  'a', 'A')
KEY_RIGHT = ('KEY_RIGHT', 'd', 'D')
KEY_QUIT  = ('q', 'Q')


# ── Helper (dipanggil oleh render) ──────────────────────────────────────────

def get_length(snake_body: list) -> int:
    """Kembalikan panjang ular."""
    return len(snake_body)


def is_game_over(state: dict) -> bool:
    """Cek apakah game sudah berakhir."""
    return state.get('game_over', False)


# ── Fungsi display utama ────────────────────────────────────────────────────

def init_display(stdscr) -> None:
    """
    Inisialisasi terminal ke mode curses.

    IS  stdscr — objek screen curses dari curses.wrapper()
    FS  None; side effect: terminal siap masuk mode curses
    """
    curses.curs_set(0)       # sembunyikan cursor
    stdscr.nodelay(True)     # input non-blocking
    stdscr.keypad(True)      # aktifkan arrow key

    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN,  curses.COLOR_BLACK)  # ular
        curses.init_pair(2, curses.COLOR_RED,    curses.COLOR_BLACK)  # food
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # UI

    stdscr.clear()


def draw_border(stdscr) -> None:
    """
    Gambar border '+' di sekeliling board.

    IS  stdscr — objek screen curses
    FS  None; side effect: border tergambar di layar
    """
    # Tembok atas
    for col in range(BOARD_WIDTH + 2):
        try:
            stdscr.addch(1, col, CHAR_WALL)
        except curses.error:
            pass

    # Tembok bawah
    for col in range(BOARD_WIDTH + 2):
        try:
            stdscr.addch(BOARD_HEIGHT + 2, col, CHAR_WALL)
        except curses.error:
            pass

    # Tembok kiri
    for row in range(1, BOARD_HEIGHT + 3):
        try:
            stdscr.addch(row, 0, CHAR_WALL)
        except curses.error:
            pass

    # Tembok kanan
    for row in range(1, BOARD_HEIGHT + 3):
        try:
            stdscr.addch(row, BOARD_WIDTH + 1, CHAR_WALL)
        except curses.error:
            pass


def draw_snake(stdscr, snake_body: list) -> None:
    """
    Gambar seluruh tubuh ular ke layar.

    IS  stdscr     — objek screen curses
        snake_body — list posisi ular saat ini
    FS  None; side effect: tubuh ular tergambar di layar
    """
    for i, (x, y) in enumerate(snake_body):
        screen_col = x + 1
        screen_row = y + 2
        try:
            if i == 0:
                stdscr.addch(screen_row, screen_col, CHAR_HEAD,
                             curses.color_pair(1))
            else:
                stdscr.addch(screen_row, screen_col, CHAR_BODY)
        except curses.error:
            pass


def draw_food(stdscr, food_pos: tuple) -> None:
    """
    Gambar food ke layar.

    IS  stdscr    — objek screen curses
        food_pos  — tuple (x, y) posisi food
    FS  None; side effect: karakter food tergambar di layar
    """
    x, y = food_pos
    screen_col = x + 1
    screen_row = y + 2
    try:
        stdscr.addch(screen_row, screen_col, CHAR_FOOD,
                     curses.color_pair(2))
    except curses.error:
        pass


def draw_score(stdscr, score: int, length: int) -> None:
    """
    Tampilkan skor dan panjang ular di baris paling atas.

    IS  stdscr  — objek screen curses
        score   — skor saat ini
        length  — panjang ular
    FS  None; side effect: teks skor tampil di baris 0
    """
    text = f"Score: {score}  Length: {length}"
    try:
        stdscr.addstr(0, 1, text, curses.color_pair(3))
    except curses.error:
        pass


def draw_game_over(stdscr, score: int) -> None:
    """
    Tampilkan overlay 'GAME OVER' di tengah board.

    IS  stdscr — objek screen curses
        score  — skor akhir
    FS  None; side effect: overlay game over tampil di layar
    """
    mid_row = BOARD_HEIGHT // 2 + 2
    mid_col = BOARD_WIDTH  // 2 - 5

    try:
        stdscr.addstr(mid_row,     mid_col, "GAME OVER!")
    except curses.error:
        pass
    try:
        stdscr.addstr(mid_row + 1, mid_col, f"Score: {score}")
    except curses.error:
        pass
    try:
        stdscr.addstr(mid_row + 2, mid_col, "Press Q to quit")
    except curses.error:
        pass


def render(stdscr, snake_body: list, state: dict) -> None:
    """
    Render satu frame penuh ke terminal.

    IS  stdscr     — objek screen curses
        snake_body — posisi ular saat ini
        state      — game state (food, score, game_over)
    FS  None; side effect: satu frame dirender ke terminal
    """
    stdscr.erase()
    draw_border(stdscr)
    draw_snake(stdscr, snake_body)
    draw_food(stdscr, state['food'])
    draw_score(stdscr, state['score'], get_length(snake_body))

    if is_game_over(state):
        draw_game_over(stdscr, state['score'])

    stdscr.refresh()


def get_input(stdscr, current_direction: tuple) -> tuple | None:
    """
    Baca input keyboard dan kembalikan arah baru.

    IS  stdscr            — objek screen curses (nodelay=True)
        current_direction — arah gerak saat ini
    FS  tuple arah baru, atau current_direction jika tidak ada input valid,
        atau None sebagai sinyal quit
    """
    try:
        key = stdscr.getkey()
    except curses.error:
        # Tidak ada input tersedia (non-blocking)
        return current_direction

    if key in KEY_UP    and current_direction != DOWN:
        return UP
    if key in KEY_DOWN  and current_direction != UP:
        return DOWN
    if key in KEY_LEFT  and current_direction != RIGHT:
        return LEFT
    if key in KEY_RIGHT and current_direction != LEFT:
        return RIGHT
    if key in KEY_QUIT:
        return None   # sinyal keluar game

    return current_direction
