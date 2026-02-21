import math
import random
import pygame

# import time

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2

pi = math.pi
# -------------camera data-----------------
cx = 0
cy = -0
cz = 0

theta = pi
polar = pi / 2

# ------------screen set up----------------
fov_up = 45
fov_side = 45

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3d projection_reset")
my_font = pygame.font.SysFont('Papyrus MS', 50)

y_scale = min(SCREEN_WIDTH, SCREEN_HEIGHT) / fov_side
p_scale = SCREEN_HEIGHT / fov_up


# --------------functions-----------------

def dot_product(point, plane):
    res = [a * b for a, b in zip(point, plane)]

    return sum(res)


def new_pos(p1):
    return [a - b for a, b in zip(p1, [cx, cy, cz])]


def get_distance(p1):
    total = 0
    for i in p1:
        total += i * i
    return math.sqrt(total)


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

    for i in polygon:
        tx += i[0] / length
        ty += i[1] / length
        tz += i[2] / length

    return get_distance((tx, ty, tz))


def draw_face(polygon):
    coordinates = []
    for i in polygon[0][1]:
        if abs(i[0]) < fov_side and abs(i[1]) < fov_up:
            coordinates.append((HALF_SCREEN_WIDTH + i[0] * p_scale, HALF_SCREEN_HEIGHT + i[1] * y_scale))
        else:
            return
    pygame.draw.polygon(screen, polygon[1], coordinates)


class BODY:
    def __init__(self, starting_pos, movement_speed, forward_line, turn_line, height=3, segment_amount=12):
        self.x, self.z = starting_pos
        self.angle = 1
        self.movement_speed = movement_speed
        self.forward_line = forward_line
        self.turn_line = turn_line
        self.y = height
        self.child = SEGMENT(self, segment_amount)
        self.stalking = 250
        self.left_leg = TEST_LEG(self, -1)
        self.right_leg = TEST_LEG(self, 1)

    def move(self, target):
        spider_forward_x = self.x + math.sin(self.angle) * self.forward_line
        spider_forward_z = self.z + math.cos(self.angle) * self.forward_line

        forward_angle = math.atan2(
            target[0] - spider_forward_x,
            target[2] - spider_forward_z
        )

        forward_to_target_x = spider_forward_x + math.sin(forward_angle) * self.turn_line
        forward_to_target_z = spider_forward_z + math.cos(forward_angle) * self.turn_line

        current_distance_to_target = (self.x - target[0]) ** 2 + (self.z - target[2]) ** 2

        forward_distance = (
                (target[0] - self.x + math.sin(self.angle) * self.movement_speed) ** 2 +
                (target[2] - self.z + math.cos(self.angle) * self.movement_speed) ** 2
        )

        backward_distance = (
                (target[0] - self.x - math.sin(self.angle) * self.movement_speed) ** 2 +
                (target[2] - self.z - math.cos(self.angle) * self.movement_speed) ** 2
        )

        if current_distance_to_target > 1:
            if forward_distance >= current_distance_to_target + self.stalking:

                self.x += math.sin(self.angle) * self.movement_speed
                self.z += math.cos(self.angle) * self.movement_speed

            elif backward_distance >= current_distance_to_target + self.stalking:
                self.x -= math.sin(self.angle) * self.movement_speed
                self.z -= math.cos(self.angle) * self.movement_speed

        self.angle = math.atan2(forward_to_target_x - self.x, forward_to_target_z - self.z)

    def update(self):
        draw_pyramid((self.x,
                      self.y,
                      self.z),
                     (self.x + math.sin(self.angle) * 40,
                      self.y,
                      self.z + math.cos(self.angle) * 40), 7)
        self.child.update()
        self.left_leg.update()
        self.right_leg.update()


class SEGMENT:
    def __init__(self, father, child, length=40):
        self.father = father
        self.length = length
        self.x = father.x - math.sin(father.angle) * self.length
        self.y = father.y
        self.z = father.z - math.cos(father.angle) * self.length
        self.angle = father.angle
        if child > 0:
            self.child = SEGMENT(self, child - 1)
        else:
            self.child = None
        self.left_leg = TEST_LEG(self, -1)
        self.right_leg = TEST_LEG(self, 1)
        self.update()

    def update(self):
        self.angle = math.atan2(self.father.x - self.x, self.father.z - self.z)
        self.x = self.father.x - math.sin(self.angle) * self.length
        self.z = self.father.z - math.cos(self.angle) * self.length
        if self.child:
            self.child.update()
        self.left_leg.update()
        self.right_leg.update()
        draw_pyramid((self.x, self.y, self.z), (self.father.x, self.father.y, self.father.z), 4)


class TEST_LEG:
    def __init__(self, father, side, length=32, stretch=44):
        self.side = side
        self.father = father
        self.length = length

        self.x = self.father.x + math.sin(self.father.angle - pi / 2) * self.length * self.side
        self.y = self.father.y + 7
        self.z = self.father.z + math.cos(self.father.angle - pi / 2) * self.length * self.side

        self.stretch = stretch

    def update(self):
        possible_x = self.father.x + math.sin(self.father.angle - pi / 2) * self.length * self.side
        possible_z = self.father.z + math.cos(self.father.angle - pi / 2) * self.length * self.side
        if math.sqrt((possible_x - self.x) ** 2 + (possible_z - self.z) ** 2) >= self.stretch:
            self.x = possible_x
            self.z = possible_z

        draw_pyramid((
            self.father.x,
            self.father.y,
            self.father.z
        ), (self.x, self.y, self.z), 3
        )


class LEG:
    def __init__(self, father, starting_position,
                 relative_target, leg_segments,
                 tolerance=0.1, stretch=0.5):
        self.father = father

        self.ang, self.distance = starting_position

        self.relative_angle, self.relative_length = relative_target

        # -------- initialize positions ---------
        self.fx = self.father.x + math.sin(
            self.father.angle + self.ang) * self.distance

        self.fz = self.father.z + math.cos(
            self.father.angle + self.ang) * self.distance
        # ---------------------------------------

        self.leg_lengths = leg_segments
        self.tolerance = tolerance
        self.stretch = stretch

    def get_target2d(self):
        return (self.father.x + math.sin(
            self.father.angle + self.ang) * self.distance,
                self.father.z + math.cos(
                    self.father.angle + self.ang) * self.distance)

    def check(self):
        x, z = self.get_target2d()
        if get_distance([self.fx - x, self.fz - z]) > self.stretch:
            self.fx, self.fz = x, z


vertices = []
polygons = []


def draw_pyramid(position1, position2, width):
    global vertices
    global polygons
    starting_index = len(vertices)
    x1, y1, z1 = position1
    x2, y2, z2 = position2
    relative_polar = math.atan2(get_distance([x2 - x1, y2 - y1, z2 - z1]), y2 - y1)

    relative_azimuth = math.atan2(x2 - x1, z2 - z1)
    a = [x1 + math.sin(relative_azimuth - pi / 2) * width,
         y1,
         z1 + math.cos(relative_azimuth - pi / 2) * width]
    b = [x1 + math.sin(relative_azimuth) * -math.cos(relative_polar) * width,
         y1 + math.sin(relative_polar) * width,
         z1 + math.cos(relative_azimuth) * -math.cos(relative_polar) * width]

    c = [x1 + math.sin(relative_azimuth + pi / 2) * width,
         y1,
         z1 + math.cos(relative_azimuth + pi / 2) * width]

    d = [x1 + math.sin(relative_azimuth) * math.cos(relative_polar) * width,
         y1 + math.sin(relative_polar) * -width,
         z1 + math.cos(relative_azimuth) * math.cos(relative_polar) * width]

    e = [x2, y2, z2]

    faces = [[starting_index,
              starting_index + 1,
              starting_index + 2,
              starting_index + 3],

             [starting_index,
              starting_index + 4,
              starting_index + 1],

             [starting_index + 1,
              starting_index + 4,
              starting_index + 2],

             [starting_index + 2,
              starting_index + 4,
              starting_index + 3],

             [starting_index + 3,
              starting_index + 4,
              starting_index],
             ]

    vertices = vertices + [a, b, c, d, e]
    polygons = polygons + faces


# --------------game-loop-------------------
spiders = [BODY((random.randint(-5000, 5000), (random.randint(-5000, 5000))), 12,
                0, 0, segment_amount=random.randint(20, 35))]
spider_quantity = 5
for spider in range(spider_quantity):
    spiders.append(BODY((random.randint(-5000, 5000), (random.randint(-5000, 5000))), random.uniform(8, 10),
                        random.uniform(80, 100), random.uniform(1.5, 3), segment_amount=random.randint(20, 35)))
click_check = 0
running = True
Movement_target = None
while running:
    vertices = []
    polygons = []
    priority_display = []
    speed = 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    keys = pygame.key.get_pressed()
    if keys[pygame.K_LCTRL]:
        speed = 1000
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
        spiders[0].x += math.sin(spiders[0].angle) * spiders[0].movement_speed
        spiders[0].z += math.cos(spiders[0].angle) * spiders[0].movement_speed
    if keys[pygame.K_DOWN]:
        spiders[0].x -= math.sin(spiders[0].angle) * spiders[0].movement_speed
        spiders[0].z -= math.cos(spiders[0].angle) * spiders[0].movement_speed
    if keys[pygame.K_LEFT]:
        spiders[0].angle -= 0.18
    if keys[pygame.K_RIGHT]:
        spiders[0].angle += 0.18
    if keys[pygame.K_r]:
        theta = math.atan2(spiders[0].x-cx, spiders[0].z-cz)
        polar = math.atan2(get_distance((spiders[0].x-cx, spiders[0].z-cz)),spiders[0].y-cy)
    r_plane = [math.cos(theta),
               0,
               -math.sin(theta)]

    u_plane = [math.sin(theta) * -math.cos(polar),
               math.sin(polar),
               math.cos(theta) * -math.cos(polar)]

    f_plane = [math.sin(theta) * math.sin(polar),
               math.cos(polar),
               math.cos(theta) * math.sin(polar)]

    if Movement_target and keys[pygame.K_f]:
        for spider in range(1, len(spiders)):
            spiders[spider].move(Movement_target)
    for spider in spiders:
        spider.update()

    rel_vertices = []
    for spider_index in range(1, len(spiders)):
        spider = spiders[spider_index]
        rel_target = get_new_rel((spider.x, spider.y, spider.z))
        priority_display.append(("N", ((HALF_SCREEN_WIDTH + math.degrees(math.atan2(rel_target[0],
                                                                                    rel_target[2])) * p_scale * 1.5,
                                        HALF_SCREEN_HEIGHT + math.degrees(math.atan2(rel_target[1],
                                                                                     rel_target[
                                                                                         2])) * y_scale * 1.5))))

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

    if pygame.mouse.get_pressed()[0]:
        if click_check == 0:
            # screen.fill((255, 255, 255))
            # pygame.display.flip()
            # time.sleep(0.1)
            Movement_target = [random.randint(-5000, 5000), 0, random.randint(-5000, 5000)]
            click_check = 60
    else:
        if click_check > 0:
            click_check -= 1
    for vertex in vertices:
        new_vert = get_new_rel(vertex)
        rel_vertices.append(
            [new_vert,
             [HALF_SCREEN_WIDTH + math.degrees(
                 math.atan2(new_vert[0], new_vert[2])) * p_scale * 1.5,

              HALF_SCREEN_HEIGHT + math.degrees(
                  math.atan2(new_vert[1], new_vert[2])) * y_scale * 1.5]
             ]
        )

    screen.fill((0, 0, 0))

    new_polys = []

    for face in polygons:
        all_vertices_in_face = []
        vertex_base = []
        skip = False
        for j in face:
            vertex_base.append(rel_vertices[j][0])
            all_vertices_in_face.append([rel_vertices[j][1][0], rel_vertices[j][1][1]])
            if not (0 < rel_vertices[j][1][0] < SCREEN_WIDTH or 0 < rel_vertices[j][1][1] < SCREEN_HEIGHT):
                skip = True
        if skip:
            continue
        new_polys.append([all_vertices_in_face, get_polygon_data(vertex_base)])
    distances_and_faces = sorted(new_polys, key=lambda x: x[1], reverse=True)
    n = len(distances_and_faces)

    for face in range(n):
        colour = int(min(2558 / (distances_and_faces[face][1] / 150), 255))
        pygame.draw.polygon(screen, (colour, colour, colour), distances_and_faces[face][0])

    if Movement_target:
        rel_target = get_new_rel(Movement_target)
        priority_display.append([
            "S",
            get_distance(rel_target),
            (HALF_SCREEN_WIDTH + math.degrees(math.atan2(rel_target[0],
                                                         rel_target[2])) * p_scale * 1.5,
             HALF_SCREEN_HEIGHT + math.degrees(math.atan2(rel_target[1],
                                                          rel_target[2])) * y_scale * 1.5)]
        )
    for priority in priority_display:
        if priority[0] == "S":
            distance = priority[1]
            position = priority[2]
            pygame.draw.circle(screen, (233, 111, 233), (position[0], position[1]), 5)
            pygame.draw.line(screen, (233, 111, 233), (position[0], position[1] - 12),
                             (position[0], position[1] - 25), 6)

        if priority[0] == "N":
            position = priority[1]
            pygame.draw.circle(screen, (233, 111, 111), (position[0], position[1]), 5)
            pygame.draw.line(screen, (233, 111, 111), (position[0], position[1] - 12),
                             (position[0], position[1] - 25), 6)

    pygame.display.flip()
