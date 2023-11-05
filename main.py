# main.py

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import src.models.constants
from src.renderer.renderer import Renderer
from src.controllers.game_controller import GameController

frame1 = frame2 = avg_fps = delta_time = 0


def fps_callback(calculated_fps, dt):
    global frame1, frame2, avg_fps, delta_time
    frame2 = frame1
    frame1 = calculated_fps
    delta_time = dt
    avg_fps = (frame1 + frame2) // 2


def window_resize(w, h):
    glutReshapeWindow(1024, 512)


def idle_func():
    game_controller.update(delta_time)
    glutPostRedisplay()


game_controller = GameController()
renderer = Renderer(game_controller, fps_callback)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
glutInitWindowSize(src.models.constants.WINDOW_WIDTH, src.models.constants.WINDOW_HEIGHT)
glutInitWindowPosition(500, 400)
glutCreateWindow(src.models.constants.WINDOW_TITLE.encode('ascii'))

# initialization code
glClearColor(0.3, 0.3, 0.3, 0)
gluOrtho2D(0, src.models.constants.WINDOW_WIDTH, src.models.constants.WINDOW_HEIGHT, 0)

glutKeyboardFunc(game_controller.handle_keyboard_input_down)
glutKeyboardUpFunc(game_controller.handle_keyboard_input_up)
glutDisplayFunc(renderer.display)
glutReshapeFunc(window_resize)
glutIdleFunc(idle_func)
# glutKeyboardFunc(game_controller.handle_keyboard_input)
glutMainLoop()
