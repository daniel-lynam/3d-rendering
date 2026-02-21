import math
import random
import pygame

pygame.init()
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
HALF_SCREEN_WIDTH = SCREEN_WIDTH // 2
HALF_SCREEN_HEIGHT = SCREEN_HEIGHT // 2

pi = math.pi
# -------------camera data-----------------
cx = 0
cy = -2000
cz = 0

theta = pi
polar = pi / 2

# ------------screen set up----------------
fov_up = 45
fov_side = 45

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3d projection_reset")
font_size = 50
my_font = pygame.font.SysFont('Papyrus MS', font_size)

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
        self.score_gain = 1
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

    def get_bottom(self, amount):
        self.child.get_bottom(amount)


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

    def get_bottom(self, amount):
        if self.child:
            self.child.get_bottom(amount)
        else:
            self.add_length(amount)

    def add_length(self, amount=1):

        self.child = SEGMENT(self, amount - 1)


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


class SHOP:
    def __init__(self, x, y, width, height, parent, initial_cost, upgrade_type, name="upgrade"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.parent = parent
        self.cost = initial_cost
        self.level = 0
        self.type = upgrade_type
        self.name = name

    def upgrade(self):
        global score
        global cy
        if score >= int(self.cost):
            score -= int(self.cost)
            if self.type == 0:
                self.parent.movement_speed += 1
            elif self.type == 1:
                cy *= 1.1
            elif self.type == 2:
                self.parent.score_gain += 1
            self.cost *= 1.1
            self.level += 1

    def is_clicked(self):
        pos = pygame.mouse.get_pos()
        temporary_x = pos[0] - self.x
        temporary_y = pos[1] - self.y
        if 0 <= temporary_x <= self.width and 0 <= temporary_y <= self.height:
            self.upgrade()

    def draw(self):
        pygame.draw.polygon(screen, (122, 122, 122), [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)])

        drawn_level = score_font.render(f"level: {self.level}", False, (0, 0, 0))
        screen.blit(drawn_level, (self.x, self.y))
        drawn_name = score_font.render(f"{self.name}", False, (0, 0, 0))
        screen.blit(drawn_name, (self.x, self.y + self.height - font_size))
        drawn_cost = score_font.render(f"cost: {int(self.cost)}", False, (0, 0, 0))
        screen.blit(drawn_cost, (self.x, self.y + self.height - font_size // 3))


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
upgrades = []

spiders = [BODY((random.randint(-5000, 5000), (random.randint(-5000, 5000))), 12,
                0, 0, segment_amount=30)]
upgrades.append(SHOP(SCREEN_WIDTH - 100, 0, 100, 100, spiders[0], 1, 0, "speed"))
upgrades.append(SHOP(SCREEN_WIDTH - 100, 100, 100, 100, spiders[0], 1, 1, "vision"))
upgrades.append(SHOP(SCREEN_WIDTH - 100, 200, 100, 100, spiders[0], 5, 2, "score"))
spider_quantity = 5
click_check = True
running = True
Movement_target = [random.randint(-5000, 5000), 0, random.randint(-5000, 5000)]
ttl_targets = 0
score = 0
score_font = pygame.font.SysFont('Papyrus MS', 30)
move = True
wall_vertices = []
wall_faces = []
limit_distance = (5000 ** 2 * 2) ** 0.5
circle_definition = 60
stop_font = pygame.font.SysFont('Papyrus MS', 300)
frame_timer = 0
pause_sign = score_font.render("PAUSED", False, (244, 244, 244))
lose_sign = score_font.render("YOU LOSE", False, (244, 2, 2))
for angle in range(circle_definition):
    wall_vertices.append((
        math.sin(2 * pi / circle_definition * angle) * limit_distance,
        0,
        math.cos(2 * pi / circle_definition * angle) * limit_distance))

    wall_faces.append((angle, (angle + 1) % circle_definition))
un_pause = False
while running:
    vertices = []
    polygons = []
    priority_display = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE and not un_pause:
                move = not move

    keys = pygame.key.get_pressed()
    if move:
        spiders[0].x += math.sin(spiders[0].angle) * spiders[0].movement_speed
        spiders[0].z += math.cos(spiders[0].angle) * spiders[0].movement_speed
    if keys[pygame.K_a] and move:
        spiders[0].angle -= 0.08
    if keys[pygame.K_d] and move:
        spiders[0].angle += 0.08

    theta = math.atan2(spiders[0].x - cx, spiders[0].z - cz)
    polar = math.atan2(get_distance((spiders[0].x - cx, spiders[0].z - cz)), spiders[0].y - cy)
    r_plane = [math.cos(theta),
               0,
               -math.sin(theta)]

    u_plane = [math.sin(theta) * -math.cos(polar),
               math.sin(polar),
               math.cos(theta) * -math.cos(polar)]

    f_plane = [math.sin(theta) * math.sin(polar),
               math.cos(polar),
               math.cos(theta) * math.sin(polar)]

    for spider in spiders:
        spider.update()

    rel_vertices = []

    if get_distance((spiders[0].x - Movement_target[0],
                     spiders[0].y - Movement_target[1],
                     spiders[0].z - Movement_target[2])) < 200:
        spiders[0].get_bottom(1)
        Movement_target = [random.randint(-5000, 5000), 0, random.randint(-5000, 5000)]
        score += spiders[0].score_gain
        ttl_targets += 1

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
    angle_to_target = math.atan2(Movement_target[0] - spiders[0].x, Movement_target[2] - spiders[0].z)
    new_vert = get_new_rel((
        spiders[0].x + math.sin(angle_to_target) * 100,
        0,
        spiders[0].z + math.cos(angle_to_target) * 100
    ))
    priority_display.append(
        ("A",
         [HALF_SCREEN_WIDTH + math.degrees(
             math.atan2(new_vert[0], new_vert[2])) * p_scale * 1.5,
          HALF_SCREEN_HEIGHT + math.degrees(
              math.atan2(new_vert[1], new_vert[2])) * y_scale * 1.5]

         ))

    screen.fill((0, 0, 0))
    new_walls = []
    for wall in wall_vertices:
        relative_wall = get_new_rel(wall)
        new_walls.append((HALF_SCREEN_WIDTH + math.degrees(math.atan2(relative_wall[0],
                                                                      relative_wall[2])) * p_scale * 1.5,
                          HALF_SCREEN_HEIGHT + math.degrees(math.atan2(relative_wall[1],
                                                                       relative_wall[2])) * y_scale * 1.5))

    wall_colour = (255, 111, 111)

    pygame.draw.lines(screen, wall_colour, True, new_walls)

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
        if priority[0] == "A":
            position = priority[1]
            pygame.draw.circle(screen, (233, 111, 111), (position[0], position[1]), 5)
    for upgrade in upgrades:
        upgrade.draw()
    text = score_font.render(str(score), False, (244, 244, 255))
    screen.blit(text, (0, 0))

    if not move:
        if get_distance((spiders[0].x, spiders[0].z)) < limit_distance:
            screen.blit(pause_sign, (HALF_SCREEN_WIDTH - 100, HALF_SCREEN_HEIGHT))
        else:
            screen.blit(lose_sign, (HALF_SCREEN_WIDTH - 100, HALF_SCREEN_HEIGHT))
            screen.blit(score_font.render(f"targets eaten: {ttl_targets}",
                                          False,
                                          (244, 244, 244)),
                        (HALF_SCREEN_WIDTH - 100, HALF_SCREEN_HEIGHT - 50))
            un_pause = True
            frame_timer -= 1
            if frame_timer <= 0:
                running = False
    elif get_distance((spiders[0].x, spiders[0].z)) > limit_distance:
        move = False
        frame_timer = 250
    for level in range(0, SCREEN_HEIGHT, 3):
        pygame.draw.line(screen, (20, 20, 20), (0, level), (SCREEN_WIDTH, level))

    pygame.display.flip()

    if pygame.mouse.get_pressed()[0]:
        if click_check:
            for upgrade in upgrades:
                upgrade.is_clicked()
        click_check = False
    else:
        click_check = True
