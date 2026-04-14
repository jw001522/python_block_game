import pygame, sys, random

pygame.init()
WIDTH, HEIGHT = 500, 600
WHITE, BLACK, RED, GREEN, BLUE = (255,255,255), (0,0,0), (255,0,0), (0,255,0), (0,0,255)
COLOR = ((255,165,0), (242,242,0), (0,128,0), (128,0,128), (0,0,250), (0,128,128))

BLOCK_COLS, BLOCK_ROWS = 7, len(COLOR)
TOTAL_BLOCKS = BLOCK_COLS * BLOCK_ROWS
MIN_PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
PADDLE_STEP_CM_PX = round(96 / 2.54)
MAX_PADDLE_SHRINK_STEPS = TOTAL_BLOCKS // 4
START_PADDLE_WIDTH = min(WIDTH - 20, MIN_PADDLE_WIDTH + MAX_PADDLE_SHRINK_STEPS * PADDLE_STEP_CM_PX)

BALL_SPEED_LO, BALL_SPEED_HI = 5, 8
BALL_SPEED_RAMP_PER_SEC = 1.025
BALL_MAX_ABS_SPEED = 15

win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
PADDLE_SPEED = 8
pygame.time.set_timer(pygame.USEREVENT, 1000)    # 타이머 설정

# 공 클래스
class Ball(pygame.sprite.Sprite):
     def __init__(self, color, size, pos=(0,0), speed=(0,0)):
          super().__init__()            # 부모 클래스(Sprite) 초기화
          self.image = pygame.Surface(size, pygame.SRCALPHA)
          pygame.draw.ellipse(self.image, color, (0,0)+size, 0)  # 공 이미지
          self.rect = self.image.get_rect()                      # Rect 객체
          self.rect.center = pos
          self.speed = list(speed)      # 방향과 속력 (dx, dy) – 이동 거리

     def update(self):
          global num_live_ball
          self.rect.x += self.speed[0]
          self.rect.y += self.speed[1]   
          if self.rect.left <= 0 or self.rect.right >= WIDTH:
               self.speed[0] *= -1          # 수평 방향 반대로 전환
          if self.rect.top <= 0:
               self.speed[1] *= -1          # 수직 방향 반대로 전환
          if self.rect.top > HEIGHT:
               num_live_ball -= 1              # 생명 감소
               self.rect.center = (250,300)  # 공의 초기 위치
               self.speed = random_ball_speed()

# 패들 클래스
class Paddle(pygame.sprite.Sprite):
     def __init__(self, color, size, ypos=10):
          super().__init__()
          self.paddle_color = color
          self.paddle_h = size[1]
          self.ypos = ypos
          self.image = pygame.Surface(size)
          pygame.draw.rect(self.image, color, (0, 0) + size, 0)
          self.rect = self.image.get_rect()
          self.rect.bottom = HEIGHT - ypos
          self.rect.centerx = WIDTH // 2

     def set_width(self, width):
          width = max(MIN_PADDLE_WIDTH, min(int(width), WIDTH))
          if width == self.rect.width:
               return
          cx, bottom = self.rect.centerx, self.rect.bottom
          self.image = pygame.Surface((width, self.paddle_h))
          pygame.draw.rect(self.image, self.paddle_color, (0, 0, width, self.paddle_h), 0)
          self.rect = self.image.get_rect()
          self.rect.centerx = cx
          self.rect.bottom = bottom

# 벽돌 클래스 (색에 따른 내구도: 주황1·노랑2·초록3·보라4·파랑5·청록6회 충돌 시 제거)
class Block(pygame.sprite.Sprite):
     def __init__(self, color, size, pos, max_hits):
          super().__init__()
          self.base_color = color
          self.size = size
          self.max_hits = max_hits
          self.hits_left = max_hits
          self.image = pygame.Surface(size, pygame.SRCALPHA)
          self.rect = self.image.get_rect()
          self.rect.topleft = pos
          self._redraw()

     def _redraw(self):
          cx, cy = self.rect.center
          self.image = pygame.Surface(self.size, pygame.SRCALPHA)
          ratio = self.hits_left / self.max_hits
          dim = tuple(max(0, min(255, int(c * ratio))) for c in self.base_color)
          pygame.draw.rect(self.image, dim, (0, 0) + self.size, 0)
          self.rect = self.image.get_rect()
          self.rect.center = (cx, cy)

     def hit(self):
          self.hits_left -= 1
          if self.hits_left <= 0:
               self.kill()
          else:
               self._redraw()

def random_ball_speed():
     return [
          random.randint(BALL_SPEED_LO, BALL_SPEED_HI) * random.choice([-1, 1]),
          -random.randint(BALL_SPEED_LO, BALL_SPEED_HI),
     ]

def accelerate_ball():
     for i in range(2):
          v = ball.speed[i]
          if v == 0:
               continue
          sign = 1 if v > 0 else -1
          nv = min(abs(v) * BALL_SPEED_RAMP_PER_SEC, BALL_MAX_ABS_SPEED)
          ball.speed[i] = sign * nv

# 게임 초기화
def init_game():
     global game_over, game_speed, num_live_ball
     block_group.empty()
     all_sprite_group.empty()

     ball.speed = random_ball_speed()
     
     for ypos in range(BLOCK_ROWS):      # 벽돌 배치 (칸마다 색 랜덤, 내구도는 COLOR 순서와 동일)
          for xpos in range(BLOCK_COLS):
               color = random.choice(COLOR)
               max_hits = COLOR.index(color) + 1
               block_group.add(Block(color, (55, 25), (xpos*60+40, ypos*30+20), max_hits))
          
     game_over = False        # 게임 진행 변수
     game_speed = 60          # 게임 속도
     num_live_ball = 3        # 남은 생명의 수
     paddle.set_width(START_PADDLE_WIDTH)
     paddle.rect.centerx = WIDTH // 2
     paddle.rect.bottom = HEIGHT - paddle.ypos
     all_sprite_group.add(ball, paddle, block_group)

# 게임 종료 메시지
def game_over_message():
     font1 = pygame.font.Font(None, 70)
     font2 = pygame.font.Font(None, 50)
     font3 = pygame.font.Font(None, 30)
     text1 = "Game over"
     if len(block_group) > 0:
          text2 = "You lose!"
     else:
          text2 = " You win!"
     text3 = "Press the space key to play again"
     text1_img = font1.render(text1, True, RED)
     text2_img = font2.render(text2, True, BLACK)
     text3_img = font3.render(text3, True, BLACK)
     pos1 = (win.get_width()-text1_img.get_width())/2
     pos2 = (win.get_width()-text2_img.get_width())/2
     pos3 = (win.get_width()-text3_img.get_width())/2
     win.blit(text1_img, (pos1, 150))
     win.blit(text2_img, (pos2, 250))
     win.blit(text3_img, (pos3, 350))

# 살아있는 공을 그리는 함수
def draw_live_ball():
     xpos = WIDTH - 15
     for i in range(1, num_live_ball):
          pygame.draw.ellipse(win, RED, (xpos, 580, 10, 10))
          xpos -= 15
     
# Main Program
ball = Ball(RED, (10,10), (250,300))         # 볼 객체 생성
paddle = Paddle(GREEN, (START_PADDLE_WIDTH, PADDLE_HEIGHT))
block_group = pygame.sprite.Group()          # 벽돌 스프라이트 그룹
all_sprite_group = pygame.sprite.Group()     # 모든 스프라이트 그룹 생성
init_game()         # 게임 초기화

# Main Loop
while True:
     for event in pygame.event.get():
          if event.type == pygame.QUIT:
               pygame.quit()
               sys.exit()
          elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_SPACE and game_over:
                    init_game()      # 초기화 작업
          elif event.type == pygame.USEREVENT:
               game_speed += 1
               if not game_over:
                    accelerate_ball()

     if not game_over:             # 게임 진행
          keys = pygame.key.get_pressed()
          if keys[pygame.K_LEFT]:
               paddle.rect.x -= PADDLE_SPEED
          if keys[pygame.K_RIGHT]:
               paddle.rect.x += PADDLE_SPEED
          paddle.rect.left = max(0, min(paddle.rect.left, WIDTH - paddle.rect.width))

          win.fill(WHITE)          # 배경 그리기
          ball.update()

          hit_blocks = pygame.sprite.spritecollide(ball, block_group, False)
          if hit_blocks:
               ball.speed[1] *= -1
               for blk in hit_blocks:
                    blk.hit()
          destroyed = TOTAL_BLOCKS - len(block_group)
          shrink_steps = destroyed // 4
          paddle.set_width(START_PADDLE_WIDTH - shrink_steps * PADDLE_STEP_CM_PX)
          paddle.rect.left = max(0, min(paddle.rect.left, WIDTH - paddle.rect.width))

          if paddle in pygame.sprite.spritecollide(ball, all_sprite_group, False):
               ball.speed[1] *= -1
          if len(block_group) == 0 or num_live_ball == 0: # 남은 벽돌이 없으면 게임 종료
               game_over = True          

          block_group.draw(win)
          all_sprite_group.draw(win)
          draw_live_ball()
     else:                         # 게임 종료 상황
          game_over_message()      # 게임 종료 메시지 출력

     pygame.display.flip()         # 그리기 갱신
     clock.tick(game_speed)        # 게임 진행 속도 설정
    