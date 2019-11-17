import sys
import pygame
import pygame.gfxdraw
import time
import math

class BorderedButton(object):
    def __init__(self, text, pos, font, color, padding, draw_border):        
        self.text = text
        self.pos = pos
        self.font = font
        self.color = color
        self.padding = padding
        self.draw_border = draw_border        
        self.create()

    def create(self):
        self.text_obj = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_obj.get_rect()
        self.text_rect.center = self.pos

    def get_bottom_y(self):
        return self.text_rect.y + self.text_rect.height

    def render(self, context):
        x = self.text_rect.x
        y = self.text_rect.y
        w = self.text_rect.width
        h = self.text_rect.height
        px = 2*self.padding
        py = 2*self.padding

        self.create()
        context.blit(self.text_obj, self.text_rect)        

        if self.draw_border:
            pygame.draw.rect(context, self.color, [x - self.padding, y - self.padding, w + 2*px, h + 2*py], 2)


class PlayerHUD(object):
	def __init__(self, player, pos, size, font, fontSize, acolor, scolor, padding):
		self.player = player
		self.pos = pos
		self.size = size
		self.font = font
		self.fontSize = fontSize
		self.actionColor = acolor
		self.stackColor = scolor
		self.text = []
		self.labels = []
		self.padding = padding

	def set_text(self, text):
		self.text = text
		self.labels = []

		self.labels.append(self.font.render(self.text[0], True, self.stackColor))
		self.labels.append(self.font.render(self.text[1], True, self.actionColor))

	def render(self, context):
		pygame.draw.rect(context, self.stackColor, (self.pos[0] , self.pos[1], self.size[0], self.size[1]), 2)
		y = self.pos[1]

		for i in range(len(self.labels)):
			lb = self.labels[i]
			context.blit(lb, (self.padding[0] + self.pos[0], self.padding[1] + y + i * self.fontSize, self.size[0], self.size[1]))


class SceneManager(object):
	def __init__(self, controller):
		self.scene = None
		self.controller = controller

	def go_to(self, scene):
		self.scene = scene
		self.scene.manager = self


class Scene(object):
	def __init__(self, size):
		self.size = size
		self.width = size[0]
		self.height = size[1]

	def render(self, display):
		raise NotImplementedError

	def update(self):
		raise NotImplementedError

	def handle_event(self, event):
		raise NotImplementedError


class PokerTable(Scene):
	def __init__(self, size, players):
		super().__init__(size)
		self.font = pygame.font.SysFont(pygame.font.get_default_font(), 24)
		self.players = players
		self.x0 = self.width * 0.2
		self.y0 = self.height * 0.2

		self.table_w = self.width -2*self.x0
		self.table_h = self.height -2*self.y0
		self.tableRect = (self.x0, self.y0, self.table_w, self.table_h)
		self.x_offset = 30
		self.y_offset = 30
		self.hud_w = 100
		self.hud_h = 50

		x0 = self.x0
		y0 = self.y0
		w = self.table_w
		h = self.table_h
		x_offset = self.x_offset
		y_offset = self.y_offset

		self.positions = [(x0 + w/2 - self.hud_w/2, y0 + h + self.y_offset/2),
					(x0 - x_offset, y0 + h - self.hud_h + y_offset, self.hud_w, self.hud_h),
					(x0 - self.hud_w - x_offset/2, y0 + h/2 - self.hud_h/2, self.hud_w, self.hud_h),
					(x0 - x_offset , y0 - y_offset, self.hud_w, self.hud_h),
					(x0 + w/2 - self.hud_w/2, y0 - self.hud_h/1 - y_offset/2, self.hud_w, self.hud_h),
					(x0 + w - self.hud_w + x_offset , y0 - y_offset , self.hud_w, self.hud_h),
					(x0 + w + x_offset/2, y0 + h/2 - self.hud_h/2, self.hud_w, self.hud_w),
					(x0 + w - self.hud_h + x_offset, y0 + h - self.hud_h + y_offset, self.hud_h, self.hud_h)
		]

		self.huds = []
		for i in range(8):			
			hud = PlayerHUD(None, self.positions[i], (self.hud_w, self.hud_h), self.font, 24, (255, 255, 0), (255, 255, 255), (5, 5))		
			hud.set_text(['P{}: $1000'.format(i), 'folded'])			
			self.huds.append(hud)



	def render(self, display):
		PI = math.pi
		display.fill((0, 150, 0))

		#pygame.draw.rect(display, (255, 255, 255), r, 1)
		# pygame.draw.arc(display, (255, 255, 255), self.tableRect, 0, PI/2, 1)
		# pygame.draw.arc(display, (255, 255, 255), self.tableRect, PI/2, PI, 1)
		# pygame.draw.arc(display, (255, 255, 255), self.tableRect, PI, 3*PI/2, 1)
		# pygame.draw.arc(display, (255, 255, 255), self.tableRect, 3*PI/2, 0, 1)

		pygame.gfxdraw.aaellipse(display, int(self.width/2), int(self.height/2), int(self.table_w/2), int(self.table_h/2), (255, 255, 255))
		#pygame.gfxdraw.filled_ellipse(display, int(self.width/2), int(self.height/2), int(self.table_w/2), int(self.table_h/2), (0, 150, 0))
		
		for i in range(8):						
			self.huds[i].render(display)



	def update(self):
		pass

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			self.manager.go_to(self.manager.controller.scenes[0])
			


class MenuScene(Scene):
	def __init__(self, size):
		super().__init__(size)		
		MenuScene.TITLE_COLOR = (255, 255, 255)
		MenuScene.BTN_COLOR = (255, 255, 0)
		MenuScene.BTN_HOVER_COLOR = (255, 255, 255)
		MenuScene.BG_COLOR = (0, 150, 0)

		top = 60
		self.fontTitle = pygame.font.SysFont(pygame.font.get_default_font(), 81)
		self.fontButton = pygame.font.SysFont(pygame.font.get_default_font(), 64)
		self.title = BorderedButton('Pokerized', (self.width/2, top), self.fontTitle, MenuScene.TITLE_COLOR, 2, False)

		bottom_y_title = self.title.get_bottom_y()
		self.button3 = BorderedButton('3 Players', (self.width/2, 50 + bottom_y_title), self.fontButton, MenuScene.BTN_COLOR, 3, True)
		bottom_y_btn = self.button3.get_bottom_y()
		self.button4 = BorderedButton('4 Players', (self.width/2, 50 + bottom_y_btn), self.fontButton, MenuScene.BTN_COLOR, 3, True)
		bottom_y_btn = self.button4.get_bottom_y()
		self.button5 = BorderedButton('5 Players', (self.width/2, 50 + bottom_y_btn), self.fontButton, MenuScene.BTN_COLOR, 3, True)


	@staticmethod
	def point_inside_rect(px, py, rect):
		return rect.x < px < rect.x + rect.width and rect.y < py < rect.y + rect.height

	def render(self, display):
		display.fill(MenuScene.BG_COLOR)
		self.title.render(display)
		self.button3.render(display)
		self.button4.render(display)
		self.button5.render(display)

	def update(self):
		pass

	def handle_event(self, event):
		mouse = pygame.mouse.get_pos()
		x = mouse[0]
		y = mouse[1]
		selected = None

		for btn in [self.button3, self.button4, self.button5]:
			if MenuScene.point_inside_rect(x, y, btn.text_rect):
				btn.color = MenuScene.BTN_HOVER_COLOR
				selected = btn
			else:
				btn.color = MenuScene.BTN_COLOR

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and selected is not None:
			print('Inside menu selected {}'.format(selected.text))
			self.manager.go_to(self.manager.controller.scenes[1])


class GameViewController(object):
	def __init__(self, size):
		self.scenes = []
		self.size = size
		self.running = False
		self.manager = SceneManager(self)
		pygame.init()
		self.display = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
		

	def add_scene(self, scene):
		self.scenes.append(scene)

		
	def run(self):		
		self.manager.go_to(self.scenes[0])
		timer = pygame.time.Clock()
		self.running = True
		prev_time = time.time()

		while self.running:
			timer.tick(60)			

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
					return
				self.manager.scene.handle_event(event)

			self.manager.scene.update()
			self.manager.scene.render(self.display)
			pygame.display.flip()

			curr_time = time.time()
			diff = curr_time - prev_time
			delay = max(1.0/60 - diff, 0)
			time.sleep(delay)			
			prev_time = curr_time
			fps = 1.0/(delay + diff)
			pygame.display.set_caption('{}: {:.2f}'.format('FPS', fps))



if __name__ == '__main__':
	size = 720, 480
	c = GameViewController(size)
	menu = MenuScene(size)
	table = PokerTable(size, [])
	c.add_scene(menu)
	c.add_scene(table)
	c.run()
