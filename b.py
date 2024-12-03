import os
import random
import sys
import time
import pygame as pg

WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5  # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """オブジェクトが画面内か判定"""
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate

class Bird:
    """こうかとんを管理するクラス"""
    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+5, 0): img,
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0): img0,
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0)  # 初期向き

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):  # 移動が発生したら向きを更新
            self.dire = tuple(sum_mv)
            self.img = __class__.imgs[self.dire]
        screen.blit(self.img, self.rct)


class Beam:
    """ビームを管理するクラス"""
    def __init__(self, bird: "Bird"):
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centerx = bird.rct.centerx + bird.dire[0] * bird.rct.width // 2
        self.rct.centery = bird.rct.centery + bird.dire[1] * bird.rct.height // 2
        self.vx, self.vy = bird.dire  # ビームの速度をこうかとんの向きに合わせる

    def update(self, screen: pg.Surface):
        self.rct.move_ip(self.vx, self.vy)
        if check_bound(self.rct) == (True, True):
            screen.blit(self.img, self.rct)
        else:
            self.rct = None

class Bomb:
    """爆弾を管理するクラス"""
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2 * rad, 2 * rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    """スコアを管理するクラス"""
    def __init__(self):
        """スコアの初期設定"""
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)  # フォント設定
        self.score = 0  # 初期スコア
        self.color = (0, 0, 255)  # 文字色

    def increase(self):
        """スコアを1点加算する"""
        self.score += 1

    def draw(self, screen: pg.Surface):
        """スコアを画面に描画する"""
        text = self.font.render(f"スコア: {self.score}", True, self.color)
        screen.blit(text, (100, HEIGHT - 50))  # 画面左下に表示


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    score = Score()
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])

        for bomb in bombs[:]:
            if bird.rct.colliderect(bomb.rct):
                font = pg.font.Font(None, 80)
                text = font.render("Game Over", True, (255, 0, 0))
                screen.blit(text, [WIDTH // 2 - 150, HEIGHT // 2])
                pg.display.update()
                time.sleep(2)
                return
            bomb.update(screen)

        for beam in beams[:]:
            beam.update(screen)
            if beam.rct is None:
                beams.remove(beam)
                continue
            for bomb in bombs[:]:
                if beam.rct.colliderect(bomb.rct):
                    bombs.remove(bomb)
                    beams.remove(beam)
                    score.increase()
                    bird.change_img(6, screen)
                    break

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        score.draw(screen)
        pg.display.update()
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
