from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import time
import math
import os

player_pos = [0, 0]
butterflies = []
caught = 0
misses = 0
lives = 3
butterfly_speed = 1.0
game_time = 120
start_time = time.time()
last_spawn_time = time.time()
game_over = False
high_score = 0
final_remaining_time = 0  

WIDTH, HEIGHT = 1000, 800
GRID = 600
net_radius = 30
butterfly_radius = 10
butterfly_wing_extent = 20


camera_angle = 0
camera_height = 700

HIGH_SCORE_FILE = "high_score.txt"

def load_high_score():
    global high_score
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                high_score = int(f.read().strip())
            except ValueError:
                high_score = 0
    else:
        high_score = 0

def save_high_score():
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(high_score))

def reset_game():
    global player_pos, butterflies, caught, misses, lives, butterfly_speed, start_time, last_spawn_time, game_over, final_remaining_time
    player_pos = [0, 0]
    butterflies = []
    caught = 0
    misses = 0
    lives = 3
    butterfly_speed = 1.0
    start_time = time.time()  # Reset timer
    last_spawn_time = time.time()
    game_over = False
    final_remaining_time = 0
    init_butterflies(15)

def init_butterflies(count=15):
    global butterflies
    butterflies = []
    for _ in range(count):
        x = random.randint(-GRID + 100, GRID - 100)
        y = random.randint(-GRID + 100, GRID - 100)
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        butterflies.append([x, y, dx, dy])

def draw_ground():
    glColor3f(0.5, 1.0, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-GRID, -GRID, 0)
    glVertex3f(GRID, -GRID, 0)
    glVertex3f(GRID, GRID, 0)
    glVertex3f(-GRID, GRID, 0)
    glEnd()

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 30)
    glColor3f(0.1, 0.5, 0.1)
    glutSolidCube(40)
    glTranslatef(0, 0, 40)
    glColor3f(1, 0.8, 0.6)
    glutSolidSphere(20, 20, 20)
    glTranslatef(30, 0, 0)
    glColor3f(1, 1, 1)
    glutWireSphere(net_radius, 10, 10)
    glPopMatrix()

def draw_butterflies():
    for b in butterflies:
        x, y, dx, dy = b
        glPushMatrix()
        glTranslatef(x, y, 30)
        glColor3f(1, 0.5, 0)
        glutSolidSphere(butterfly_radius, 10, 10)
        wing_angle = 30 * math.sin(time.time() * 5)
        glPushMatrix()
        glRotatef(wing_angle, 0, 0, 1)
        glColor3f(0, 1, 1)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(20, 10, 0)
        glVertex3f(20, 20, 0)
        glVertex3f(0, 10, 0)
        glEnd()
        glPopMatrix()
        glPushMatrix()
        glRotatef(-wing_angle, 0, 0, 1)
        glColor3f(0, 1, 1)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(-20, 10, 0)
        glVertex3f(-20, 20, 0)
        glVertex3f(0, 10, 0)
        glEnd()
        glPopMatrix()
        glPopMatrix()

def draw_text(x, y, text):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 0, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def move_butterflies():
    if game_over:
        return
    for b in butterflies:
        x, y, dx, dy = b
        b[0] += dx * butterfly_speed
        b[1] += dy * butterfly_speed
        if abs(b[0]) > GRID - 50:
            b[2] *= -1
        if abs(b[1]) > GRID - 50:
            b[3] *= -1

def spawn_new_butterflies():
    if game_over:
        return
    global last_spawn_time
    current_time = time.time()
    if current_time - last_spawn_time >= 5:
        for _ in range(2):
            x = random.randint(-GRID + 100, GRID - 100)
            y = random.randint(-GRID + 100, GRID - 100)
            dx = random.choice([-1, 1])
            dy = random.choice([-1, 1])
            butterflies.append([x, y, dx, dy])
        last_spawn_time = current_time

def catch():
    if game_over:
        return
    global caught, misses, lives, butterfly_speed
    px, py = player_pos[0] + 30, player_pos[1]
    hit = False
    for b in butterflies[:]:
        x, y, dx, dy = b
        dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
        if dist <= (net_radius + butterfly_wing_extent):
            butterflies.remove(b)
            caught += 1
            butterfly_speed += 0.1
            hit = True
            break

    if not hit:
        misses += 1
        if misses % 5 == 0:
            lives -= 1

    if len(butterflies) < 15 and not hit:
        init_butterflies(1)

def keyboard(key, x, y):
    global game_over
    if game_over:
        if key == b'r' or key == b'R':
            reset_game()
        return

    if key == b'a':
        player_pos[0] -= 20
    elif key == b'd':
        player_pos[0] += 20
    elif key == b'w':
        player_pos[1] += 20
    elif key == b's':
        player_pos[1] -= 20
    elif key == b' ':
        catch()
    elif key == b'q':
        exit()

def specialKeyListener(key, x, y):
    if game_over:
        return
    global camera_angle, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5
    elif key == GLUT_KEY_UP:
        camera_height += 10
    elif key == GLUT_KEY_DOWN:
        camera_height -= 10

def display():
    global start_time, game_over, high_score, final_remaining_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    eye_x = 900 * math.sin(math.radians(camera_angle))
    eye_y = -900 * math.cos(math.radians(camera_angle))
    gluLookAt(eye_x, eye_y, camera_height, 0, 0, 0, 0, 0, 1)

    if not game_over:
        spawn_new_butterflies()
        move_butterflies()

    draw_ground()
    draw_player()
    draw_butterflies()

    remaining = max(0, int(game_time - (time.time() - start_time)))
    if not game_over:
        final_remaining_time = remaining  # Update final time when game ends
    else:
        remaining = final_remaining_time  # Use frozen time after game over

    draw_text(10, HEIGHT - 30, f"Time Left: {remaining}s")
    draw_text(10, HEIGHT - 60, f"Score: {caught}")
    draw_text(10, HEIGHT - 90, f"Lives: {lives}")
    draw_text(10, HEIGHT - 120, f"Misses: {misses}")

    if remaining == 0 or lives <= 0:
        if not game_over:
            game_over = True
            if caught > high_score:
                high_score = caught
                save_high_score()

        draw_text(WIDTH // 2 - 80, HEIGHT // 2, "GAME OVER")
        draw_text(WIDTH // 2 - 80, HEIGHT // 2 - 30, f"Final Score: {caught}")
        draw_text(WIDTH // 2 - 80, HEIGHT // 2 - 60, f"High Score: {high_score}")
        draw_text(WIDTH // 2 - 100, HEIGHT // 2 - 90, "Press R to Restart")

    glutSwapBuffers()

def timer(value):
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def init():
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, WIDTH / HEIGHT, 1, 2000)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Butterfly Hunter 3D")

    load_high_score()
    init()
    init_butterflies(15)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeyListener)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
