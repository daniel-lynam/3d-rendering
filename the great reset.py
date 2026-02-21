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

colours = [(100, 244, 100), (244, 244, 100),
           (244, 244, 244), (100, 244, 244),
           (244, 100, 244), (100, 244, 100),
           (100, 100, 100), (200, 200, 200),
           (200, 0, 200), (200, 200, 0),
           (200, 0, 200), (100, 100, 100), (244, 100, 100), (244, 0, 0), (10, 10, 10), (20, 20, 20)]

# -------------camera data-----------------
cx = 0
cy = -0.5
cz = 3

theta = pi
polar = pi / 2
# ------------screen set up----------------
fov_up = 45
fov_side = 45

y_scale = min(SCREEN_WIDTH, SCREEN_HEIGHT) / fov_side
p_scale = SCREEN_HEIGHT / fov_up


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


# -------------projectile------------------
class GRAV_ORB:
    def __init__(self, x, y, z, proj_speed, p_theta, p_polar, grav=1):
        self.x = x
        self.y = y
        self.z = z
        self.theta = p_theta
        self.polar = p_polar
        self.gravity = grav
        self.proj_speed = proj_speed

    def move(self):

        # stsp cp  ctsp
        self.x += math.sin(self.theta) * math.sin(self.polar) * self.proj_speed
        self.y += math.cos(self.polar) * self.proj_speed
        self.z += math.cos(self.theta) * math.sin(self.polar) * self.proj_speed
        pass

    def use_grav(self):
        global verts
        for point in range(len(verts)):
            np = verts[point]
            rp = (self.x - np[0],
                  self.y - np[1],
                  self.z - np[2])
            dis = get_distance(rp)
            if dis > 0.1:  # and self.gravity < 0:
                continue
            else:
                pass
            if dis != 0:
                force = min(0.03 / dis, dis) * self.gravity
                mrp = (rp[0] / dis * force, rp[1] / dis * force, rp[2] / dis * force)
                verts[point] = (np[0] + mrp[0], np[1] + mrp[1], np[2] + mrp[2])

        pass


# --------------models---------------------
def parse_obj(file_path):
    vertices = []
    faces = []

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split()

                prefix = parts[0]

                if prefix == 'v':  # Vertex line
                    try:
                        x, y, z = map(float, parts[1:4])
                        vertices.append((x, -y, z))
                    except ValueError:
                        print(f"Warning: Skipping malformed vertex line: {line}")

                elif prefix == 'f':  # Face line
                    face_indices = []
                    for v in parts[1:]:
                        try:
                            idx = int(v.split('/')[0]) - 1
                            face_indices.append(idx)
                        except ValueError:
                            print(f"Warning: Skipping malformed face index in: {line}")
                    if len(face_indices) >= 3:
                        faces.append(face_indices)
    except:
        print("load failed")
    finally:
        return vertices, faces


def make_superquadric(a=1.0, b=1.0, c=1.0, eps1=0.5, eps2=0.5, n_eta=48, n_omega=48):
    vertices = []
    quads = []
    for i in range(n_eta + 1):
        eta = -math.pi / 2 + math.pi * i / n_eta
        cos_eta = math.cos(eta)
        sin_eta = math.sin(eta)

        def spow(h, e):
            return math.copysign(abs(h) ** e, h)

        for j in range(n_omega + 1):
            omega = -math.pi + 2 * math.pi * j / n_omega
            cos_omega = math.cos(omega)
            sin_omega = math.sin(omega)

            x = a * spow(cos_eta, eps1) * spow(cos_omega, eps2)
            y = b * spow(cos_eta, eps1) * spow(sin_omega, eps2)
            z = c * spow(sin_eta, eps1)

            vertices.append((x, y, z))
    for i in range(n_eta):
        for j in range(n_omega):
            v0 = i * (n_omega + 1) + j
            v1 = v0 + 1
            v2 = v0 + (n_omega + 1) + 1
            v3 = v0 + (n_omega + 1)
            quads.append((v0, v1, v2, v3))

    return vertices, quads


def draw_face(face):
    coords = []
    for i in face[0][1]:
        if abs(i[0]) < fov_side and abs(i[1]) < fov_up:
            coords.append((HALF_SCREEN_WIDTH + i[0] * p_scale, HALF_SCREEN_HEIGHT + i[1] * y_scale))
        else:
            return
    pygame.draw.polygon(screen, face[1], coords)


verts, polygons = parse_obj("C:\\Users\\35387\\PycharmProjects\\3d projection\\Models\\crab.obj")
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
    if pygame.mouse.get_pressed()[0] and keys[pygame.K_LCTRL]:
        projectiles.append(GRAV_ORB(cx, cy, cz, 0.1, theta, polar, grav=-1))
    elif pygame.mouse.get_pressed()[0]:
        projectiles.append(GRAV_ORB(cx, cy, cz, 0.1, theta, polar, grav=1))
    cross_hair_colour = (100, 0, 130)
    if keys[pygame.K_LCTRL]:
        cross_hair_colour = (200, 30, 30)
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

    r_plane = [math.cos(theta), 0, -math.sin(theta)]
    u_plane = [math.sin(theta) * -math.cos(polar), math.sin(polar), math.cos(theta) * -math.cos(polar)]
    f_plane = [math.sin(theta) * math.sin(polar), math.cos(polar), math.cos(theta) * math.sin(polar)]
    for i in range(len(projectiles)):
        p = projectiles[i]
        p.move()
        p.use_grav()
        if get_distance((p.x - cx, p.y - cy, p.z - cz)) > 5:
            projectiles[i] = ""
    while "" in projectiles:
        projectiles.remove("")

    rel_vertices = []
    for vert in verts:
        new_vert = get_new_rel(vert)
        rel_vertices.append(
            [new_vert, [HALF_SCREEN_WIDTH + math.degrees(math.atan2(new_vert[0], new_vert[2])) * p_scale * 1.5,
                        HALF_SCREEN_HEIGHT + math.degrees(math.atan2(new_vert[1], new_vert[2])) * y_scale * 1.5]
             ]
        )

    screen.fill((200, 231, 213))
    new_polys = []
    for i in polygons:
        all_verts_in_poly = []
        vertbase = []
        skip = False
        for j in i:
            vertbase.append(rel_vertices[j][0])
            all_verts_in_poly.append([rel_vertices[j][1][0], rel_vertices[j][1][1]])
            if not (0 < rel_vertices[j][1][0] < SCREEN_WIDTH or 0 < rel_vertices[j][1][1] < SCREEN_HEIGHT):
                skip = True
        if skip:
            continue
        new_polys.append([all_verts_in_poly, get_polygon_data(vertbase)])
    distances_and_faces = sorted(new_polys, key=lambda x: x[1], reverse=True)
    n = len(distances_and_faces)

    for face in range(n):
        colour = int(min(255 / (distances_and_faces[face][1] / 2), 255))
        pygame.draw.polygon(screen, (colour, colour, colour), distances_and_faces[face][0])

    for orb in projectiles:
        base = (orb.x, orb.y, orb.z)
        nv = get_new_rel(base)
        tcolour = int(min(200 / get_distance(base), 200))
        if orb.gravity < 0:
            pygame.draw.circle(screen, (tcolour, 0, 0),
                               (HALF_SCREEN_WIDTH + math.degrees(math.atan2(nv[0], nv[2])) * p_scale * 1.5,
                                HALF_SCREEN_HEIGHT + math.degrees(math.atan2(nv[1], nv[2])) * y_scale * 1.5),
                               50 / get_distance(nv) - 3)
        else:
            pygame.draw.circle(screen, (tcolour, 0, tcolour),
                               (HALF_SCREEN_WIDTH + math.degrees(math.atan2(nv[0], nv[2])) * p_scale * 1.5,
                                HALF_SCREEN_HEIGHT + math.degrees(math.atan2(nv[1], nv[2])) * y_scale * 1.5),
                               50 / get_distance(nv) - 3)

    pygame.draw.circle(screen, cross_hair_colour, (HALF_SCREEN_WIDTH, HALF_SCREEN_HEIGHT), 5)
    pygame.display.flip()
