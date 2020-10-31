"""
tower defense

author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
part of http://ThePythonGamebook.com
"""

import pygame
# import pygame.locals
import pygame.freetype  # not automatically loaded when importing pygame!
import pygame.gfxdraw
import random


# import os
# import sys


class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygame sprite class"""

    number = 0  # unique number for each sprite

    # numbers = {} # { number, Sprite }

    def __init__(self,
                 pos=None,
                 move=None,
                 _layer=0,
                 angle=0,
                 radius=0,
                 color=(
                               random.randint(0, 255),
                               random.randint(0, 255),
                               random.randint(0, 255),
                       ),
                 hitpoints=100,
                 hitpointsfull=100,
                 stop_on_edge = False,
                 kill_on_edge = False,
                 bounce_on_edge = False,
                 warp_on_edge = False,
                 age = 0,
                 max_age = None,
                 max_distance = None,
                 picture = None,
                 boss = None,
                 #kill_with_boss = False,
                 move_with_boss = False,
                 area = None, # pygame.Rect
                 **kwargs):
        ### initialize pygame sprite DO NOT DELETE THIS LINE
        pygame.sprite.Sprite.__init__(self, self.groups)
        mylocals = locals().copy() # copy locals() so that it does not updates itself
        for key in mylocals:
            if key != "self" and key != "kwargs":  # iterate over all named arguments, including default values
                setattr(self, key, mylocals[key])
        for key, arg in kwargs.items(): # iterate over all **kwargs arguments
            setattr(self, key, arg)
        if pos is None:
            self.pos = pygame.math.Vector2(200,200)
        if move is None:
            self.move = pygame.math.Vector2(0,0)
        self._overwrite_parameters()

        self.number = VectorSprite.number  # unique number for each sprite
        VectorSprite.number += 1
        # VectorSprite.numbers[self.number] = self
        # self.visible = False
        self.create_image()
        self.distance_traveled = 0  # in pixel
        # self.rect.center = (-300,-300) # avoid blinking image in topleft corner
        if self.angle != 0:
            self.set_angle(self.angle)

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
        default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self.layer = 0
        # else:
        #    self.layer = self.layer
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(200, 200)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0, 0)
        if "angle" not in kwargs:
            self.angle = 0  # facing right?
        if "radius" not in kwargs:
            self.radius = 5
        # if "width" not in kwargs:
        #    self.width = self.radius * 2
        # if "height" not in kwargs:
        #    self.height = self.radius * 2
        if "color" not in kwargs:
            # self.color = None
            self.color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
        if "hitpoints" not in kwargs:
            self.hitpoints = 100
        self.hitpointsfull = self.hitpoints  # makes a copy

        if "stop_on_edge" not in kwargs:
            self.stop_on_edge = False
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "age" not in kwargs:
            self.age = 0  # age in seconds. A negative age means waiting time until sprite appears
        if "max_age" not in kwargs:
            self.max_age = None

        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "boss" not in kwargs:
            self.boss = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "move_with_boss" not in kwargs:
            self.move_with_boss = False


    def kill(self):
        # check if this is a boss and kill all his underlings as well
        tokill = [s for s in Viewer.allgroup if "boss" in s.__dict__ and s.boss == self]
        #for s in Viewer.allgroup:
        #    if "boss" in s.__dict__ and s.boss == self:
        #        tokill.append(s)
        for s in tokill:
            s.kill()
        # if self.number in self.numbers:
        #   del VectorSprite.numbers[self.number] # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(self.color)
        self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (round(self.pos[0], 0), round(self.pos[1], 0))
        # self.width = self.rect.width
        # self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        self.angle = self.angle % 360
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, -self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def get_angle(self):
        if self.angle > 180:
            return self.angle - 360
        return self.angle

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        self.angle = self.angle % 360
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, -self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        self.age += seconds
        if self.age < 0:
            return
        # self.visible = True
        self.distance_traveled += self.move.length() * seconds
        # ----- kill because... ------
        if self.hitpoints <= 0:
            self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.boss and self.move_with_boss:
            self.pos = self.boss.pos
            self.move = self.boss.move
        else:
            # move independent of boss
            self.pos += self.move * seconds
            self.wallcheck()
        # print("rect:", self.pos.x, self.pos.y)
        self.rect.center = (int(round(self.pos.x, 0)), int(round(self.pos.y, 0)))

    def wallcheck(self):
        # ---- bounce / kill on screen edge ----
        if self.area is None:
            self.area = Viewer.screenrect
            #print(self.area)
        # ------- left edge ----
        if self.pos.x < self.area.left:
            if self.stop_on_edge:
                self.pos.x = self.area.left
            if self.kill_on_edge:
                self.kill()
            if self.bounce_on_edge:
                self.pos.x = self.area.left
                self.move.x *= -1
            if self.warp_on_edge:
                self.pos.x = self.area.right
        # -------- upper edge -----
        if self.pos.y < self.area.top:
            if self.stop_on_edge:
                self.pos.y = self.area.top
            if self.kill_on_edge:
                self.kill()
            if self.bounce_on_edge:
                self.pos.y = self.area.top
                self.move.y *= -1
            if self.warp_on_edge:
                self.pos.y = self.area.bottom
        # -------- right edge -----
        if self.pos.x > self.area.right:
            if self.stop_on_edge:
                self.pos.x = self.area.right
            if self.kill_on_edge:
                self.kill()
            if self.bounce_on_edge:
                self.pos.x = self.area.right
                self.move.x *= -1
            if self.warp_on_edge:
                self.pos.x = self.area.left
        # --------- lower edge ------------
        if self.pos.y > self.area.bottom:
            if self.stop_on_edge:
                self.pos.y = self.area.bottom
            if self.kill_on_edge:
                self.kill()
            if self.bounce_on_edge:
                self.pos.y = self.area.bottom
                self.move.y *= -1
            if self.warp_on_edge:
                self.pos.y = self.area.top

class UpgradeCursor(VectorSprite):

    def update(self, seconds):
        self.pos = pygame.math.Vector2(pygame.mouse.get_pos())
        if Viewer.gold >= 10:
            self.image = self.image0
        else:
            self.image = self.image1
        super().update(seconds)

    def create_image(self):
        self.width = 20
        self.height = self.width
        self.image = pygame.Surface((self.width, self.width))
        # pygame.gfxdraw.polygon(self.image, ((0,0), (50, 25), (0,50)), pygame.Color("red"))
        pygame.draw.polygon(self.image, self.color,
                            ((self.width//2, 0),
                             (self.width, self.height //3),
                             (self.width * 0.6, self.height // 3),
                             (self.width * 0.6, self.height),
                             (self.width //2, self.height * 0.9),
                             (self.width * 0.4, self.height),
                             (self.width * 0.4, self.height //3),
                             (0, self.height //3),
                             ), 5)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.image1 = pygame.Surface((self.width, self.width))
        pygame.draw.line(self.image1, (222,0,0), (0,0), (self.width, self.height),5)
        pygame.draw.line(self.image1, (222, 0, 0), (self.width,0), (0, self.height), 5)
        self.image1.set_colorkey((0, 0, 0))
        self.image1.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = (int(round(self.pos.x, 0)), int(round(self.pos.y, 0)))


class Flytext(VectorSprite):
    def __init__(
            self,
            pos=pygame.math.Vector2(50, 50),
            move=pygame.math.Vector2(0, -50),
            text="hallo",
            color=(255, 0, 0),
            bgcolor=None,
            max_age=0.5,
            age=0,
            acceleration_factor=1.0,
            fontsize=48,
            textrotation=0,
            style=pygame.freetype.STYLE_STRONG,
            alpha_start=255,
            alpha_end=255,
            width_start=None,
            width_end=None,
            height_start=None,
            height_end=None,
            rotate_start=0,
            rotate_end=0,
            picture=None,
            _layer = 7
    ):
        """Create a flying VectorSprite with text or picture that disappears after a while

        :param pygame.math.Vector2 pos:     startposition in Pixel. To attach the text to another Sprite, use an existing Vector.
        :param pygame.math.Vector2 move:    movevector in Pixel per second
        :param text:                        the text to render. accept unicode chars. Will be overwritten when picture is given
        :param (int,int,int) color:         foregroundcolor for text
        :param (int,int,int) bgcolor:       backgroundcolor for text. If set to None, black is the transparent color
        :param float max_age:               lifetime of Flytext in seconds. Delete itself when age > max_age
        :param float age:                   start age in seconds. If negative, Flytext stay invisible until age >= 0
        :param float acceleration_factor:   1.0 for no acceleration. > 1 for acceleration of move Vector, < 1 for negative acceleration
        :param int fontsize:                fontsize for text
        :param float textrotation:          static textrotation in degree for rendering text.
        :param int style:                   effect for text rendering, see pygame.freetype constants
        :param int alpha_start:             alpha value for age =0. 255 is no transparency, 0 is full transparent
        :param int alpha_end:               alpha value for age = max_age.
        :param int width_start:             start value for dynamic zooming of width in pixel
        :param int width_end:               end value for dynamic zooming of width in pixel
        :param int height_start:            start value for dynamic zooming of height in pixel
        :param int height_end:              end value for dynamic zooming of height in pixel
        :param float rotate_start:          start angle for dynamic rotation of the whole Flytext Sprite
        :param float rotate_end:            end angle for dynamic rotation
        :param picture:                     a picture object. If not None, it overwrites any given text
        :return: None
        """

        self.recalc_each_frame = False
        self.text = text
        self.alpha_start = alpha_start
        self.alpha_end = alpha_end
        self.alpha_diff_per_second = (alpha_start - alpha_end) / max_age
        if alpha_end != alpha_start:
            self.recalc_each_frame = True
        self.style = style
        self.acceleration_factor = acceleration_factor
        self.fontsize = fontsize
        self.textrotation = textrotation
        self.color = color
        self.bgcolor = bgcolor
        self.width_start = width_start
        self.width_end = width_end
        self.height_start = height_start
        self.height_end = height_end
        self.picture = picture
        # print( "my picture is:", self.picture)
        if width_start is not None:
            self.width_diff_per_second = (width_end - width_start) / max_age
            self.recalc_each_frame = True
        else:
            self.width_diff_per_second = 0
        if height_start is not None:
            self.height_diff_per_second = (height_end - height_start) / max_age
            self.recalc_each_frame = True
        else:
            self.height_diff_per_second = 0
        self.rotate_start = rotate_start
        self.rotate_end = rotate_end
        if (rotate_start != 0 or rotate_end != 0) and rotate_start != rotate_end:
            self.rotate_diff_per_second = (rotate_end - rotate_start) / max_age
            self.recalc_each_frame = True
        else:
            self.rotate_diff_per_second = 0
        # self.visible = False
        VectorSprite.__init__(
            self,
            color=color,
            pos=pos,
            move=move,
            max_age=max_age,
            age=age,
            picture=picture,
        )
        #self._layer = 7  # order of sprite layers (before / behind other sprites)
        # acceleration_factor  # if < 1, Text moves slower. if > 1, text moves faster.

    def create_image(self):
        if self.picture is not None:
            # print("picture", self)
            self.image = self.picture
        else:
            # print("no picture", self)
            myfont = Viewer.font
            # text, textrect = myfont.render(
            # fgcolor=self.color,
            # bgcolor=self.bgcolor,
            # get_rect(text, style=STYLE_DEFAULT, rotation=0, size=0) -> rect
            textrect = myfont.get_rect(
                text=self.text,
                size=self.fontsize,
                rotation=self.textrotation,
                style=self.style,
            )  # font 22
            self.image = pygame.Surface((textrect.width, textrect.height))
            # render_to(surf, dest, text, fgcolor=None, bgcolor=None, style=STYLE_DEFAULT, rotation=0, size=0) -> Rect
            textrect = myfont.render_to(
                surf=self.image,
                dest=(0, 0),
                text=self.text,
                fgcolor=self.color,
                bgcolor=self.bgcolor,
                style=self.style,
                rotation=self.textrotation,
                size=self.fontsize,
            )
            if self.bgcolor is None:
                self.image.set_colorkey((0, 0, 0))

            self.rect = textrect
            # picture ? overwrites text

        # transparent ?
        if self.alpha_start == self.alpha_end == 255:
            pass
        elif self.alpha_start == self.alpha_end:
            self.image.set_alpha(self.alpha_start)
            # print("fix alpha", self.alpha_start)
        else:
            self.image.set_alpha(
                self.alpha_start - self.age * self.alpha_diff_per_second
            )
            # print("alpha:", self.alpha_start - self.age * self.alpha_diff_per_second)
        self.image.convert_alpha()
        # save the rect center for zooming and rotating
        oldcenter = self.image.get_rect().center
        # dynamic zooming ?
        if self.width_start is not None or self.height_start is not None:
            if self.width_start is None:
                self.width_start = textrect.width
            if self.height_start is None:
                self.height_start = textrect.height
            w = self.width_start + self.age * self.width_diff_per_second
            h = self.height_start + self.age * self.height_diff_per_second
            self.image = pygame.transform.scale(self.image, (int(w), int(h)))
        # rotation?
        if self.rotate_start != 0 or self.rotate_end != 0:
            if self.rotate_diff_per_second == 0:
                self.image = pygame.transform.rotate(self.image, self.rotate_start)
            else:
                self.image = pygame.transform.rotate(
                    self.image,
                    self.rotate_start + self.age * self.rotate_diff_per_second,
                )
        # restore the old center after zooming and rotating
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        self.rect.center = (int(round(self.pos.x, 0)), int(round(self.pos.y, 0)))

    def update(self, seconds):
        VectorSprite.update(self, seconds)
        if self.age < 0:
            return
        self.move *= self.acceleration_factor
        if self.recalc_each_frame:
            self.create_image()


class Fire(VectorSprite):
    width = 8
    chance_to_stop = .1  # per second
    damage_per_second = 1

    def _overwrite_parameters(self):
        self.kill_with_boss = True
        self.move_with_boss = True
        self.color = (255, 200, 0)

    def create_image(self):
        self.image = pygame.Surface((self.width, self.width))
        # self.color = randomize_colors(self.color, 1 )
        self.color = (255, random.randint(128, 255), 0)
        pygame.draw.circle(self.image, self.color, (self.width // 2, self.width // 2), self.width // 2)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        # self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = int(round(self.pos.x, 0)), int(round(self.pos.y, 0))

    def update(self, seconds):
        super().update(seconds)
        b = self.bossvector.rotate(-self.bossangle + self.boss.get_angle())
        self.pos = self.boss.pos + b * 0.7
        self.create_image()
        # --- small chance of crew to extinguish fire ---
        if self.age > 1:
            if random.random() * seconds < self.chance_to_stop / 60:
                self.kill()
        # ---- start smoking after some time ----
        if self.age > 0.15:
            if random.random() < 0.68:
                Smoke(pos=pygame.math.Vector2(self.pos.x, self.pos.y))
        # --- create fire damage over time ---
        self.boss.hitpoints -= self.damage_per_second * seconds


class Hitpointbar(VectorSprite):
    height = 5

    def _overwrite_parameters(self):
        self.kill_with_boss = True
        self.move_with_boss = True

    def create_image(self):
        self.image = pygame.Surface((self.boss.width, self.height))
        # self.image.fill((0,255,0))
        percent = self.boss.width * (self.boss.hitpoints / self.boss.hitpointsfull)
        pygame.draw.rect(self.image, (0, 255, 0), (0, 0, int(round(percent, 0)), self.height))
        pygame.draw.rect(self.image, (0, 64, 0), (0, 0, self.boss.width, self.height), 1)
        self.image.set_colorkey((0, 0, 0,))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

        # self.rect.center = self.pos.x, self.pos.y

    def update(self, seconds):
        self.create_image()
        # super().update(seconds)
        self.rect.center = self.boss.rect.centerx, self.boss.rect.centery - self.boss.height


class Ship(VectorSprite):
    snap_distance = 15
    speed = 25
    width = 40
    height = 40
    rot_speed = 15
    bounty = 1

    def _overwrite_parameters(self):
        self.index_of_waypoint = 0
        self.hitpoints = 100
        self.hitpointsfull = 100
        self.color = (0, 0, 200)
        Hitpointbar(boss=self)

    def final_explosion(self):
        for _ in range(50):
                m = pygame.math.Vector2()
                m.from_polar((random.random() * 15 + 5.9, random.randint(0, 360)))
                a = m.as_polar()[1]
                Spark2(pos=pygame.math.Vector2(self.pos.x, self.pos.y),
                       move=m,
                       angle=a,
                       color=self.color,
                       max_age=1.5 + random.random() * 1.0)

    def next_waypoint(self):
        self.index_of_waypoint += 1
        self.index_of_waypoint = self.index_of_waypoint % len(Viewer.points)

    def update(self, seconds):
        # if random.random() < 0.1:
        #    Bubble(pos=pygame.math.Vector2(self.pos[0], self.pos[1]),
        #           color=self.color,
        #           max_age=6,
        #           move=-pygame.math.Vector2(self.move[0], self.move[1]),
        #           )
        waypointvector = Viewer.points[self.index_of_waypoint]
        self.move = waypointvector - self.pos
        self.move.scale_to_length(self.speed)
        self.set_angle(self.move.as_polar()[1])
        if self.pos.distance_to(waypointvector) < self.snap_distance:
            self.next_waypoint()
        if self.hitpoints <= 0:
            Viewer.gold += self.bounty
            self.final_explosion()
        super().update(seconds)

    def create_image(self):
        self.image = pygame.Surface((self.width, self.width))
        # pygame.gfxdraw.polygon(self.image, ((0,0), (50, 25), (0,50)), pygame.Color("red"))
        pygame.draw.polygon(self.image, self.color,
                            ((0, 0),
                             (self.width, self.width // 2),
                             (0, self.width),
                             (self.width // 2, self.width // 2)
                             ), 0)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (int(round(self.pos.x, 0)), int(round(self.pos.y, 0)))


class Ship2(Ship):
    # red ship
    snap_distance2 = 88  # how many pixels before waypoint to begin with turning
    width = 40
    speed = 35
    rot_speed = 45  # Grad / seconds
    height = 40
    color = (200, 0, 0)
    bounty = 2

    def _overwrite_parameters(self):
        self.index_of_waypoint = 0
        self.index_of_turnpoint = 0
        self.hitpoints = 150
        self.hitpointsfull = 150
        Hitpointbar(boss=self)
        self.color = (200, 0, 0)

    def next_turnpoint(self):
        self.index_of_turnpoint += 1
        self.index_of_turnpoint = self.index_of_turnpoint % len(Viewer.points)

    def update(self, seconds):
        m = pygame.math.Vector2(self.speed, 0)
        m.from_polar((-self.speed, self.get_angle()))
        # if random.random() < 0.5:
        #    Bubble(pos=pygame.math.Vector2(self.pos[0], self.pos[1]),
        #       color=self.color,
        #       max_age=6,
        #       move=m,
        #       )
        waypointvector = Viewer.points[self.index_of_waypoint]
        turnpointvector = Viewer.points[self.index_of_turnpoint]
        self.move = waypointvector - self.pos
        self.move.scale_to_length(self.speed)
        m2 = turnpointvector - self.pos
        new_angle = self.move.as_polar()[1]
        angle2 = m2.as_polar()[1]
        diff = (self.get_angle() - angle2 - 0) % 360  # new_angle -0) % 360
        if diff > 180:
            self.rotate(self.rot_speed * seconds)
        elif diff < 180:
            self.rotate(-self.rot_speed * seconds)

        # self.set_angle(self.move.as_polar()[1])
        if self.pos.distance_to(waypointvector) < self.snap_distance:
            self.next_waypoint()
        if self.pos.distance_to(turnpointvector) < self.snap_distance2:
            self.next_turnpoint()
        if self.hitpoints <= 0:
            Viewer.gold += self.bounty
            self.final_explosion()
        VectorSprite.update(self, seconds)


class Ship3(Ship):
    rot_speed = 35
    speed = 50
    speed_max = 50
    speed_min = 10
    height = 40
    color = (0, 200, 0)
    bounty = 5

    def _overwrite_parameters(self):
        self.index_of_waypoint = 0
        self.hitpoints = 500
        self.hitpointsfull = 500
        Hitpointbar(boss=self)
        self.color = (0, 200, 0)

    def update(self, seconds):
        # if random.random() < 0.5:
        #    Bubble(pos=pygame.math.Vector2(self.pos[0], self.pos[1]),
        #           color=self.color,
        #           max_age=6,
        #           move=-pygame.math.Vector2(self.move[0], self.move[1]),
        #           )
        waypointvector = Viewer.points[self.index_of_waypoint]
        m = waypointvector - self.pos
        # self.move = waypointvector - self.pos
        # self.move.scale_to_length(self.speed)
        new_angle = m.as_polar()[1]
        diff = (self.get_angle() - new_angle - 0) % 360
        if diff > 180:
            self.rotate(self.rot_speed * seconds)
        elif diff < 180:
            self.rotate(-self.rot_speed * seconds)
        self.move.from_polar((self.speed, self.get_angle()))
        ## slower at turning
        if abs(diff) > 15:
            self.speed *= 0.99
        elif abs(diff) < 10:
            self.speed *= 1.1
        self.speed = between(self.speed, self.speed_min, self.speed_max)

        # self.set_angle(self.move.as_polar()[1])
        if self.pos.distance_to(waypointvector) < self.snap_distance:
            self.next_waypoint()
        if self.hitpoints <= 0:
            Viewer.gold += self.bounty
            self.final_explosion()
        VectorSprite.update(self, seconds)


class Cannon(VectorSprite):
    width = 50
    shooting_radius_max = 250
    shooting_radius_min = 25
    exclusive_radius = 90  # cannons can not be placed closer to each other

    def upgrade(self):
        self.shooting_radius_max *= 1.2
        self.reload_time *= 0.5
        self.rot_speed *= 1.5

    def _overwrite_parameters(self):
        self.ready_to_fire_time = 0
        self.busy_with_upgrading = False
        self.rot_speed = 30
        self.reload_time = 1.5  # seconds
        self.shooting_radius_max = 150
        self.shooting_radius_min = 25
        #self.exclusive_radius = 90  # cannons can not be placed closer to each other

    def rotate_toward(self, target_pos_vector, seconds):
        m = target_pos_vector - self.pos
        new_angle = m.as_polar()[1]
        diff = (self.get_angle() - new_angle - 0) % 360
        if diff > 180:
            self.rotate(self.rot_speed * seconds)
        elif diff < 180:
            self.rotate(-self.rot_speed * seconds)
        # self.move.from_polar((self.speed, self.get_angle()))
        if abs(diff) < 5:
            self.fire()

    def fire(self):
        if self.busy_with_upgrading:
            return
        if self.ready_to_fire_time > self.age:
            return  # still reloading
        self.ready_to_fire_time = self.age + self.reload_time
        # p = pygame.math.Vector2(self.pos.x, self.pos.y)
        angle = self.get_angle()
        m = pygame.math.Vector2(Beam.speed, 0)
        m.from_polar((Beam.speed, angle))
        barrel = pygame.math.Vector2(1, 0)
        barrel.from_polar((self.width // 2, angle))
        Beam(pos=pygame.math.Vector2(self.pos.x, self.pos.y) + barrel,
             move=m,
             angle=angle,
             max_distance=self.shooting_radius_max - self.width // 2,
             color=(222, 0, 111))

    def create_image(self):
        self.image = pygame.Surface((self.width, self.width))
        pygame.draw.circle(
            self.image, self.color,
            (self.width // 2, self.width // 2),
            self.width // 3,
            5
        )
        pygame.draw.rect(self.image, self.color,
                         (self.width // 3, self.width // 2 - 5,
                          self.width, 10))
        self.image.set_colorkey((0, 0, 0))
        # self.image.set_alpha(self.alpha_start - self.age * self.alpha_diff_per_second)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = int(self.pos[0]), int(self.pos[1])
        self.image0 = self.image.copy()

    #def update(self, seconds):
    #    super().update(seconds)
        #print(self.number,  self.starttime)


class Beam(VectorSprite):
    """a glowing laser beam"""
    width = 25  # must be >= 10
    height = 5
    speed = 99
    damage = 1

    def _overwrite_parameters(self):
        self.kill_on_edge = True
        # self.color = randomize_colors(self.color, 50)

    def create_image(self):
        r, g, b = randomize_colors(self.color, 50)
        self.image = pygame.Surface((self.width, self.height))
        pygame.gfxdraw.filled_polygon(self.image,
                                      ((0, self.height // 2),
                                       (self.width * 0.9, 0),
                                       (self.width, self.height // 2),
                                       (self.width * 0.9, self.height),
                                       ),
                                      (r, g, b))
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = int(self.pos.x), int(self.pos.y)
        self.set_angle(self.angle)

    def update(self, seconds):
        # self.create_image()

        super().update(seconds)


class Spark2(VectorSprite):

    def _overwrite_parameters(self):
        self._layer = 9
        self.kill_on_edge = True
        self.color = randomize_colors(self.color, 50)

    def create_image(self):
        self.image = pygame.Surface((10, 10))
        pygame.draw.line(self.image, self.color,
                         (10, 5), (5, 5), 3)
        pygame.draw.line(self.image, self.color,
                         (5, 5), (2, 5), 1)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.image0 = self.image.copy()


class Spark(VectorSprite):
    width = 10
    height = 1
    acc = 1.01

    def create_image(self):
        self.image = pygame.Surface((10, 3))
        pygame.draw.line(self.image, self.color, (0, 1), (10, 1))
        self.image.set_colorkey((0, 0, 0))
        # self.image.fill(randomize_colors(self.color, 20))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.image0 = self.image.copy()
        self.set_angle(self.angle)

    def update(self, seconds):
        self.move *= self.acc
        super().update(seconds)


class Smoke(VectorSprite):
    """a round fragment or bubble particle, fading out"""

    def _overwrite_parameters(self):
        # self.speed = random.randint(10, 50)
        self.start_radius = 1

        self.radius = 1
        self.end_radius = 10  # random.randint(15,20)
        # if self.max_age is None:
        self.max_age = 7.5  # + random.random() * 2.5
        self.kill_on_edge = True
        self.kill_with_boss = False  # VERY IMPORTANT!!!
        # if self.move == pygame.math.Vector2(0, 0):
        #    self.move = pygame.math.Vector2(1, 0)
        #    self.move *= self.speed
        #    a, b = 0, 360
        #    self.move.rotate_ip(random.randint(a, b))
        self.alpha_start = 64
        self.alpha_end = 0
        self.alpha_diff_per_second = (self.alpha_start - self.alpha_end) / self.max_age
        self.color = (10, 10, 10)
        # self.color = randomize_colors(color=self.color, by=35)

    def create_image(self):
        # self.radius = self.start_radius +
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius))
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        self.image.set_colorkey((0, 0, 0))
        self.image.set_alpha(self.alpha_start - self.age * self.alpha_diff_per_second)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = int(round(self.pos.x, 0)), int(round(self.pos.y, 0))
        # self.rect.center=(int(round(self.pos[0],0)), int(round(self.pos[1],0)))

    def update(self, seconds):
        # self.create_image()
        self.radius = (self.end_radius / self.max_age) * self.age
        self.radius = int(round(self.radius, 0))
        self.create_image()
        self.move = Viewer.windvector * seconds
        super().update(seconds)
        self.image.set_alpha(self.alpha_start - self.age * self.alpha_diff_per_second)
        self.image.convert_alpha()


class Viewer:
    width = 0
    height = 0
    screenrect = None
    font = None
    points = []
    windvector = None
    gold = 50
    lives = 0
    maxwind = 400
    spawn_rect_width = 40 # width of rects around topleft screencorner where new ships can spawn

    # playergroup = None # pygame sprite Group only for players

    def __init__(
            self,
            width=800,
            height=600,
    ):

        Viewer.width = width
        Viewer.height = height
        Viewer.screenrect = pygame.Rect(0, 0, width, height)
        Viewer.points = [(100, 100), (width - 50, height - 50)]
        Viewer.windvector = pygame.math.Vector2()
        Viewer.windvector.from_polar((random.randint(50, 250), random.randint(0, 360)))
        # first spwanrect is nort-east of topleft screencorner
        self.spawnrects = [pygame.Rect(-self.spawn_rect_width, - self.spawn_rect_width, self.spawn_rect_width, self.spawn_rect_width)]
        # create 4 additional spawnrects north of topleft screen corner
        for x in range(0, self.spawn_rect_width * 4 + 1, self.spawn_rect_width ):
            self.spawnrects.append(pygame.Rect(x, -self.spawn_rect_width, self.spawn_rect_width, self.spawn_rect_width))
        # create 4 additional spawnrects west of topleft screen corner
        for y in range(0, self.spawn_rect_width * 4 + 1, self.spawn_rect_width ):
            self.spawnrects.append(pygame.Rect(-self.spawn_rect_width, y, self.spawn_rect_width, self.spawn_rect_width))


        # ---- pygame init
        pygame.init()
        # pygame.mixer.init(11025) # raises exception on fail
        # Viewer.font = pygame.font.Font(os.path.join("data", "FreeMonoBold.otf"),26)
        # fontfile = os.path.join("data", "fonts", "DejaVuSans.ttf")
        # --- font ----
        # if you have your own font:
        # Viewer.font = pygame.freetype.Font(os.path.join("data","fonts","INSERT_YOUR_FONTFILENAME.ttf"))
        # otherwise:
        fontname = pygame.freetype.get_default_font()
        Viewer.font = pygame.freetype.SysFont(fontname, 64)

        # ------ joysticks init ----
        pygame.joystick.init()
        self.joysticks = [
            pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
        ]
        for j in self.joysticks:
            j.init()
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.DOUBLEBUF
        )
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.playtime = 0.0


        # ------ background images ------
        # self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        # self.make_background()
        # self.load_images()

        self.prepare_sprites()
        self.setup()
        self.run()

    def setup(self):
        """call this to restart a game"""
        # ------ game variables -----
        Viewer.gold = 50
        Viewer.lives = 100
        self.background = pygame.Surface((Viewer.width, Viewer.height))
        self.background.fill((255, 255, 255))
        # draw start and finish text in topleft / lowerright corners
        pygame.draw.ellipse(self.background, (200, 200, 200), (0, 0, 200, 100))
        surf, rect = Viewer.font.render(
            text="start area",
            fgcolor=(128, 128, 128),
            size=32,
        )
        self.background.blit(surf, (25, 40))
        pygame.draw.ellipse(self.background, (200, 200, 200), (Viewer.width - 200, Viewer.height - 100, 200, 100))
        surf, rect = Viewer.font.render(
            text="finish area",
            fgcolor=(128, 128, 128),
            size=32,
        )
        self.background.blit(surf, (Viewer.width - 180, Viewer.height - 70))

    def prepare_sprites(self):
        """painting on the surface and create sprites"""
        Viewer.allgroup = pygame.sprite.LayeredUpdates()  # for drawing with layers
        Viewer.shipgroup = pygame.sprite.Group()
        Viewer.beamgroup = pygame.sprite.Group()
        Viewer.cannongroup = pygame.sprite.Group()  # GroupSingle
        # assign classes to groups
        VectorSprite.groups = self.allgroup
        Ship.groups = self.allgroup, self.shipgroup
        Cannon.groups = self.allgroup, self.cannongroup
        Beam.groups = self.allgroup, self.beamgroup

        # Bubble.groups = self.allgroup, self.fxgroup  # special effects
        # Flytext.groups = self.allgroup, self.flytextgroup, self.flygroup
        # self.ship1 = Ship(pos=pygame.math.Vector2(400, 200), color=(0,0,200))
        # self.ship2 = Ship2(pos=pygame.math.Vector2(100, 100), color=(200,0,0))
        # self.ship3 = Ship3(pos=pygame.math.Vector2(100, 400), color=(0,200,0))
        # self.cannon1 = Cannon(pos=pygame.math.Vector2(300,400), color=(50,100,100))
        # self.cannon2 = Cannon(pos=pygame.math.Vector2(600,500), color=(50,100,100))

    def change_wind(self):
        # get length (radius) and angle from windvector
        r, a = Viewer.windvector.as_polar()
        delta_r = random.choice(
            (-3, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 3))
        delta_a = random.choice(
            (-3, -2, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3))
        r = between(r + delta_r, 0, Viewer.maxwind)
        a = (a + delta_a) % 360
        Viewer.windvector.from_polar((r, a))
        # --- draw windrose ---
        write(self.screen, "wind: {:.0f} pixel/sec,  {:.0f}° ".format(r, 360 - a), x=5, y=Viewer.height - 115,
              color=(128, 128, 128), font_size=12)
        pygame.draw.circle(self.screen, (128, 128, 128), (50, Viewer.height - 50), 50, 1)
        # ---- calculate wind triangle -----
        p0 = pygame.math.Vector2(50, Viewer.height - 50)  # center of circle
        p1 = pygame.math.Vector2()
        p1.from_polar((50, a))  # - a so that ° goes counterclockwise
        p1 = p0 + p1  # tip of triangle
        p2 = pygame.math.Vector2()
        p2.from_polar((50, a + 120))
        p3 = pygame.math.Vector2()
        p3.from_polar((50, a - 120))
        p2 = p0 + p2
        p3 = p0 + p3
        c = int(round(r / Viewer.maxwind * 255, 0))
        pygame.draw.polygon(self.screen, (c, c, c),
                            [(int(round(p.x, 0)), int(round(p.y, 0))) for p in (p0, p2, p1, p3)], 5)
        # p4 = p0 - p1
        # pygame.draw.circle(self.screen, (200,0,0), (int(p1.x), int(p1.y)), 5)
        # p5 = pygame.math.Vector2()
        # p5.from_polar((windpercent, a))
        # p5 = p4 + p5
        # pygame.draw.line(self.screen, (64,64,64), (int(round(p4.x,0)), int(round(p4.y,0))), (int(round(p5.x,0)), int(round(p5.y,0))), 10)

    def draw_path(self, background):
        # ---- draw circles and polygon for path ---
        for point in Viewer.points:
            pygame.gfxdraw.circle(background, point[0], point[1], 5, pygame.Color("black"))

        # --- draw polygon ---
        # if len(Viewer.points) > 2:
        #    pygame.gfxdraw.polygon(self.screen, Viewer.points, pygame.Color('blue'))
        for nr, point in enumerate(Viewer.points):
            if nr == 0:
                continue
            pygame.draw.line(background, (0, 0, 255),
                             Viewer.points[nr - 1],
                             point)

    def run(self):
        """The mainloop"""
        running = True

        # pygame.mouse.set_visible(False)
        click_oldleft, click_oldmiddle, click_oldright = False, False, False

        # for b in range(-50,50, 5):
        #    Bubble(pos=pygame.math.Vector2(200, 200), age=b/100, max_age=3)
        Flytext(pos=pygame.math.Vector2(Viewer.width // 2, Viewer.height // 2),
                move=pygame.math.Vector2(0, -5),
                text="Tower Defense",
                max_age=5,
                fontsize=100,
                alpha_start=255,
                alpha_end=15,
                acceleration_factor=1.015)
        Flytext(pos=pygame.math.Vector2(Viewer.width // 2, Viewer.height),
                move=pygame.math.Vector2(0, -15),
                text="left-click / right-click with mouse to edit flightpath",
                color=(5, 5, 5),
                max_age=10,
                fontsize=25,
                )
        Flytext(pos=pygame.math.Vector2(Viewer.width // 2, Viewer.height + 50),
                move=pygame.math.Vector2(0, -15),
                text="press space when done",
                color=(200, 0, 200),
                max_age=15,
                age=-3,
                fontsize=35,
                acceleration_factor=1.015,
                )
        self.modus = "path"

        # points = []
        # --------------------------- main loop --------------------------
        monsters_started = 0
        monsters_in_wave = 100
        time_for_next_monster = 0
        wave = 1
        while running:
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            self.playtime += seconds
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        if self.modus == "cannon":
                            self.modus = "play"
                            self.u = UpgradeCursor()

                            # for c in self.cannongroup:
                            # make cannon_shootingrange permanent visible
                            # pygame.draw.circle(self.background, (200,200,200), (int(c.pos.x),int(c.pos.y)), c.shooting_radius_max, 1  )
                            # pygame.draw.circle(self.background, (200, 200, 200), (int(c.pos.x), int(c.pos.y)), c.shooting_radius_min, 1)

                        if self.modus == "path":
                            self.modus = "cannon"
                            # make ship path permanent visible
                            self.draw_path(self.background)
                            print("points: ", Viewer.points)
                            Flytext(pos=pygame.math.Vector2(Viewer.width // 2, 500),
                                    text="place cannons with mouse, press space when done",
                                    max_age=5,
                                    fontsize=23, )

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()

            # ---------- clear all --------------
            # pygame.display.set_caption(f"player 1: {self.player1.deaths}   vs. player 2: {self.player2.deaths}")     #str(nesw))
            self.screen.blit(self.background, (0, 0))

            if self.modus == "path":
                self.draw_path(background=self.screen)

            # ------ mouse handler ------
            mousevector = pygame.math.Vector2(pygame.mouse.get_pos())
            click_left, click_middle, click_right = pygame.mouse.get_pressed()
            if self.modus == "path":
                # delete prev last point by right-klick
                if click_oldright and not click_right:
                    if len(Viewer.points) > 2:
                        # pygame.mouse.get_pressed()
                        # Viewer.points = Viewer.points[:-1]
                        del Viewer.points[-2]
                        for ship in self.shipgroup:
                            ship.index_of_waypoint = between(ship.index_of_waypoint, 0, len(Viewer.points) - 1)
                # add points by left-click
                if click_oldleft and not click_left:
                    Viewer.points.insert(-1, pygame.mouse.get_pos())
            elif self.modus == "cannon":
                # ----- cannon-range circle around mousepointer when in cannon modus:
                pygame.draw.circle(self.screen, (200, 200, 200), pygame.mouse.get_pos(), Cannon.shooting_radius_max, 1)
                pygame.draw.circle(self.screen, (200, 200, 200), pygame.mouse.get_pos(), Cannon.shooting_radius_min, 1)
                pygame.draw.circle(self.screen, (0, 200, 00), pygame.mouse.get_pos(), Cannon.exclusive_radius)
                # --- too close to other cannon ?
                min_distance, othercannon = Viewer.width * 2, None
                for c in self.cannongroup:
                    distance = mousevector.distance_to(c.pos)
                    if distance < min_distance:
                        min_distance, othercannon = distance, c
                ok = True
                if othercannon is not None:
                    if min_distance < Cannon.exclusive_radius + othercannon.exclusive_radius:
                        # red x at cursor
                        pygame.draw.line(self.screen, (200, 0, 0), (int(mousevector.x) - 20, int(mousevector.y) - 20),
                                         (int(mousevector.x) + 20, int(mousevector.y) + 20), 5)
                        pygame.draw.line(self.screen, (200, 0, 0), (int(mousevector.x) + 20, int(mousevector.y) - 20),
                                         (int(mousevector.x) - 20, int(mousevector.y) + 20), 5)
                        ok = False
                if ok and click_oldleft and not click_left and Viewer.gold > 0:
                    # place new cannon
                    #Cannon(pos=pygame.math.Vector2(x=pygame.mouse.get_pos()[0],y=pygame.mouse.get_pos()[1] ))
                    Cannon(mousevector, starttime=self.playtime)
                    Viewer.gold -= 1

            elif self.modus == "play":
                if click_oldleft and not click_left and self.gold >= 10:
                    for c in self.cannongroup:
                        distancevector = c.pos - mousevector
                        distance = distancevector.length()
                        if distance < 25:
                            Viewer.gold -= 10
                            c.upgrade()
                            break



            click_oldleft, click_oldmiddle, click_oldright = click_left, click_middle, click_right

            # paint cannon exclusivranges
            if self.modus == "cannon":
                for c in self.cannongroup:
                    pygame.draw.circle(self.screen, (200, 200, 200), (int(c.pos.x), int(c.pos.y)),
                                       c.shooting_radius_max, 1)
                    pygame.draw.circle(self.screen, (200, 200, 200), (int(c.pos.x), int(c.pos.y)),
                                       c.shooting_radius_min, 1)
                    pygame.draw.circle(self.screen, (200, 00, 00), (int(c.pos.x), int(c.pos.y)), c.exclusive_radius)

            # ------ spawn ships / monsters -----
            if self.modus == "play":
                if monsters_started < monsters_in_wave and random.random() < 0.01 and time_for_next_monster < self.playtime:
                    time_for_next_monster = self.playtime + 0.15
                    MyShip = random.choice((Ship, Ship2, Ship3))

                    # initialize class instance
                    # check the free spawnrects (north/east of topleft screen corner)
                    free = {}
                    for i, rect in enumerate(self.spawnrects):
                        free[i] = True
                        for ship in self.shipgroup:
                            if rect.collidepoint(ship.pos.x, ship.pos.y):
                                free[i] = False
                                continue
                    # any spawnrect free at all?
                    if True in free.values():
                        # choose one index of a free spwanrect
                        i = random.choice([j for j in free.keys() if free[j]])
                        spawnrect = self.spawnrects[i]

                    MyShip(pos=pygame.math.Vector2(spawnrect.center))
                    # monster.pos = pygame.math.Vector2(random.randint(-100,-100), 0)
                    monsters_started += 1
            # ----- delete ships that reached the finish area / subtract lives
            # killnumbers = []
            for ship in self.shipgroup:
                distance = ship.pos - Viewer.points[-1]
                if distance.length() < ship.width:
                    ship.kill()
                    self.lives -= 1

            # ----------- writing on screen ----------

            # -------- write points ------------

            if self.modus == "path":
                for y, point in enumerate(Viewer.points):
                    rect1 = Viewer.font.render_to(
                        surf=self.screen,
                        dest=(10, y * 15),
                        text=f"point # {y}: {point}",
                        fgcolor=(64, 64, 64),
                        size=12,
                    )
            if self.modus == "cannon":
                write(self.screen, f"gold left: {Viewer.gold}", x=Viewer.width//2, y=5, origin="topcenter")

            # write status
            if self.modus == "play":
                write(self.screen,
                      f"wave {wave}: {monsters_started} of {monsters_in_wave} gold: {self.gold} lives: {self.lives}",
                      x=Viewer.width // 2, y=5, origin="topcenter")
                # ------- draw wind information -----
                self.change_wind()
            # -------- fps -----------
            surf, rect = Viewer.font.render(
                text="fps: {:5.2f}".format(self.clock.get_fps()),
                fgcolor=(15, 15, 15),
                size=12,
            )
            self.screen.blit(surf, (85, Viewer.height - rect.height))
            # ----------- collision detection ------------
            # ----- Beam vs. Ship ------
            for ship in self.shipgroup:
                crashgroup = pygame.sprite.spritecollide(ship, self.beamgroup, True, pygame.sprite.collide_mask)
                # crashgroup_m = pygame.sprite.spritecollide(ship, crashgroup_r, True,  pygame.sprite.collide_mask)
                for beam in crashgroup:
                    #ship.pos += beam.move * seconds * 0.5  # impact
                    ship.hitpoints -= beam.damage
                    # ---- start Fire at impact point -----
                    Fire(boss=ship, bossvector=beam.pos - ship.pos, bossangle=ship.get_angle())
                    # ---sparks---
                    for _ in range(5):
                        m = pygame.math.Vector2(1, 0)
                        m.from_polar((random.random() * 0.2 + 5.9, random.randint(0, 360)))
                        a = m.as_polar()[1]
                        Spark2(pos=pygame.math.Vector2(beam.pos.x, beam.pos.y),
                               move=m,
                               angle=a,
                               color=ship.color,
                               max_age=0.2 + random.random() * 1.1)
                # beam.kill()

            # --- each cannon find closest ship and rotates towards it ----
            for cannon in self.cannongroup:
                distance, victim = 2 * Viewer.width, None
                for ship in self.shipgroup:
                    d = (cannon.pos - ship.pos).length()
                    # d = d.length
                    if d > cannon.shooting_radius_max or d < cannon.shooting_radius_min:
                        continue  #
                    if d < distance:
                        distance, victim = d, ship
                if victim is not None:
                    cannon.rotate_toward(victim.pos, seconds)
                    pygame.gfxdraw.line(self.screen, int(cannon.pos.x), int(cannon.pos.y), int(victim.pos.x),
                                        int(victim.pos.y), (200, 0, 200))

            # write angle of ship, angle to mouse
            # diff = pygame.math.Vector2(pygame.mouse.get_pos()-self.ship1.pos)
            # m = diff.as_polar()[1]
            pygame.display.set_caption(f"{self.modus}")

            # --------- update all sprites ----------------
            self.allgroup.update(seconds)

            # ---------- blit all sprites --------------
            self.allgroup.draw(self.screen)
            pygame.display.flip()
            # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()
        # try:
        #    sys.exit()
        # finally:
        #    pygame.quit()


## -------------------- functions --------------------------------

def between(value, lower_limit=0, upper_limit=255):
    """makes sure a (color) value stays between a lower and a upper limit ( 0 and 255 )
    :param float value: the value that should stay between min and max
    :param float lower_limit:  the minimum value (lower limit)
    :param float upper_limit:  the maximum value (upper limit)
    :return: new_value"""
    return lower_limit if value < lower_limit else upper_limit if value > upper_limit else value


def cmp(a, b):
    """compares a with b, returns 1 if a > b, returns 0 if a==b and returns -1 if a < b"""
    return (a > b) - (a < b)


def randomize_colors(color, by=30):
    """randomize each color of a r,g,b tuple by the amount of +- by
    while staying between 0 and 255
    returns a color tuple"""
    r, g, b = color
    r += random.randint(-by, by)
    g += random.randint(-by, by)
    b += random.randint(-by, by)
    r = between(r)  # 0<-->255
    g = between(g)
    b = between(b)
    return r, g, b


def write(background, text, x=50, y=150, color=(0, 0, 0),
          font_size=None, font_name="mono", bold=True, origin="topleft"):
    """blit text on a given pygame surface (given as 'background')
       the origin is the alignment of the text surface
       origin can be 'center', 'centercenter', 'topleft', 'topcenter', 'topright', 'centerleft', 'centerright',
       'bottomleft', 'bottomcenter', 'bottomright'
    """
    if font_size is None:
        font_size = 24
    font = pygame.font.SysFont(font_name, font_size, bold)
    width, height = font.size(text)
    surface = font.render(text, True, color)

    if origin == "center" or origin == "centercenter":
        background.blit(surface, (x - width // 2, y - height // 2))
    elif origin == "topleft":
        background.blit(surface, (x, y))
    elif origin == "topcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "topright":
        background.blit(surface, (x - width, y))
    elif origin == "centerleft":
        background.blit(surface, (x, y - height // 2))
    elif origin == "centerright":
        background.blit(surface, (x - width, y - height // 2))
    elif origin == "bottomleft":
        background.blit(surface, (x, y - height))
    elif origin == "bottomcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "bottomright":
        background.blit(surface, (x - width, y - height))


if __name__ == "__main__":
    # g = Game()
    Viewer(
        width=1200,
        height=800,
    )
