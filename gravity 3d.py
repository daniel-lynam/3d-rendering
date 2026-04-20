import math
import pygame

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3d projection_reset")
my_font = pygame.font.SysFont('Papyrus MS', 50)
pi = math.pi
FPS = 60

# -------------camera data-----------------

cx = 0
cy = 0
cz = 0

theta = pi
polar = pi / 2
# ------------screen set up----------------
FOV = 35

SCALE = min(SCREEN_WIDTH, SCREEN_HEIGHT) / FOV
ANG_IN_WIDTH = SCREEN_WIDTH / SCREEN_HEIGHT * FOV


# --------------functions-----------------

def dot_product(point, plane):
    res = [a * b for a, b in zip(point, plane)]

    return sum(res)


def new_pos(p1):
    return [a - b for a, b in zip(p1, [cx, cy, cz])]


def get_distance(p1):
    ttl = 0
    for vc in p1:
        ttl += vc * vc
    return math.sqrt(ttl)


def get_new_rel(point):
    dp = new_pos(point)
    return [dot_product(dp, r_plane),
            dot_product(dp, u_plane),
            dot_product(dp, f_plane)]


def get_polygon_data(polygon):
    tx = 0
    ty = 0
    tz = 0
    length = len(polygon)

    for point in polygon:
        tx += point[0] / length
        ty += point[1] / length
        tz += point[2] / length

    return get_distance((tx, ty, tz))


# --------------models---------------------

def draw_polygon(polygon):
    coordinates = []
    for edge in polygon[0][1]:
        if abs(edge[0]) < FOV and abs(edge[1]) < FOV:
            coordinates.append((HALF_SCREEN_WIDTH + edge[0] * SCALE, HALF_SCREEN_HEIGHT + edge[1] * SCALE))
        else:
            return
    pygame.draw.polygon(screen, polygon[1], coordinates, 2)


def sum_lists(l1, l2, add=True):
    temporary_list = []
    if add:
        for index in range(len(l1)):
            temporary_list.append(l1[index] + l2[index])
    else:
        for index in range(len(l1)):
            temporary_list.append(l1[index] - l2[index])
    return temporary_list


lines_seg = 40

vertex_list, polygon_list = [], [(0, 1, lines_seg + 1, lines_seg)]
for i in range(lines_seg):
    for j in range(lines_seg):
        vertex_list.append((-i, 0, -j))
        if i < lines_seg - 1 and j < lines_seg - 1:
            polygon_list.append((i + j * lines_seg, i + j * lines_seg + 1, i + j * lines_seg + lines_seg + 1,
                                 i + j * lines_seg + lines_seg))

planets = [[10, 0, 10], [3, 0, 3]]
colours = [(244, 0, 0), (0, 244, 0)]
mass = [10, 2]
planets_radius = [3, 2]
GRAV = 9.8
running = True
projectiles = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if pygame.mouse.get_pressed()[2]:
        turning = True
        pygame.mouse.set_visible(False)
        mouse_movement = pygame.mouse.get_rel()
        if mouse_movement != (0, 0):
            pygame.mouse.set_pos([HALF_SCREEN_WIDTH, HALF_SCREEN_HEIGHT])
        theta = theta + (mouse_movement[0]) * 0.0002
        polar = min(max(polar - (mouse_movement[1]) * 0.0002, 0), pi)
    else:
        turning = False
        pygame.mouse.set_visible(True)

    speed = 1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LCTRL]:
        speed = 10
    if keys[pygame.K_s]:
        cz -= 0.02 * math.cos(theta) * speed
        cx -= 0.02 * math.sin(theta) * speed
    if keys[pygame.K_w]:
        cz += 0.02 * math.cos(theta) * speed
        cx += 0.02 * math.sin(theta) * speed
    if keys[pygame.K_a]:
        cx -= 0.02 * math.cos(theta) * speed
        cz += 0.02 * math.sin(theta) * speed
    if keys[pygame.K_d]:
        cx += 0.02 * math.cos(theta) * speed
        cz -= 0.02 * math.sin(theta) * speed

    if keys[pygame.K_SPACE]:
        cy -= 0.01 * speed
    if keys[pygame.K_LSHIFT]:
        cy += 0.01 * speed
    if keys[pygame.K_UP]:
        planets[1][2] += 0.04
    if keys[pygame.K_DOWN]:
        planets[1][2] -= 0.04
    if keys[pygame.K_LEFT]:
        planets[1][0] -= 0.04
    if keys[pygame.K_RIGHT]:
        planets[1][0] += 0.04
    r_plane = [math.cos(theta), 0, -math.sin(theta)]
    u_plane = [math.sin(theta) * -math.cos(polar), math.sin(polar), math.cos(theta) * -math.cos(polar)]
    f_plane = [math.sin(theta) * math.sin(polar), math.cos(polar), math.cos(theta) * math.sin(polar)]
    for i in range(len(vertex_list)):
        x, z = vertex_list[i][0], vertex_list[i][2]
        y = 0
        for j in range(len(planets)):
            dis = get_distance(sum_lists(planets[j], (x, 0, z)))
            dis = max(dis, planets_radius[j]) ** 2
            y += GRAV / dis * mass[j]

        vertex_list[i] = (x, y, z)
    relative_angles = []
    relative_vertices = []
    for vert in vertex_list:
        new_vert = get_new_rel(vert)
        horizontal_angle = math.degrees(math.atan2(new_vert[0], new_vert[2]))
        vertical_angle = math.degrees(math.atan2(new_vert[1], new_vert[2]))
        relative_angles.append((horizontal_angle, vertical_angle))
        relative_vertices.append(
            [new_vert, [HALF_SCREEN_WIDTH + horizontal_angle * SCALE,
                        HALF_SCREEN_HEIGHT + vertical_angle * SCALE]
             ]
        )
    screen.fill((0, 0, 0))
    new_polys = []
    for i in polygon_list:
        all_vertices_in_poly = []
        vertex_base = []
        skip = False
        for j in i:
            vertex_base.append(relative_vertices[j][0])
            all_vertices_in_poly.append([relative_vertices[j][1][0], relative_vertices[j][1][1]])
            if not (0 < relative_vertices[j][1][0] < SCREEN_WIDTH or 0 < relative_vertices[j][1][1] < SCREEN_HEIGHT):
                skip = True
        if skip:
            continue
        new_polys.append([all_vertices_in_poly, get_polygon_data(vertex_base)])

    for i in range(len(planets)):
        temp_planet = planets[i][0] * -1, 0, planets[i][2] * -1
        distance_from_planet = get_distance(sum_lists(temp_planet, (cx, cy, cz), False))
        radius = planets_radius[i] / distance_from_planet * 50
        new_vert = get_new_rel(temp_planet)
        horizontal_angle = math.degrees(math.atan2(new_vert[0], new_vert[2]))
        vertical_angle = math.degrees(math.atan2(new_vert[1], new_vert[2]))
        new_polys.append(
            [[HALF_SCREEN_WIDTH + horizontal_angle * SCALE,
              HALF_SCREEN_HEIGHT + vertical_angle * SCALE], distance_from_planet, radius, colours[i % len(colours)]
             ]
        )

    distances_and_faces = sorted(new_polys, key=lambda d: d[1], reverse=True)
    n = len(distances_and_faces)

    for face in range(n):
        proper_face = distances_and_faces[face]
        if len(proper_face) == 2:
            colour = int(min(400 / (proper_face[1] / 4), 255))
            pygame.draw.polygon(screen, (colour, colour, colour), proper_face[0])
        else:
            colour = tuple(proper_face[3])
            pygame.draw.circle(screen, colour, tuple(proper_face[0]), proper_face[2] * 4)

    pygame.display.flip()
