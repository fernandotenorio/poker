import sys
import pygame
import time

class GameCanvas(object):
    def __init__(self, width=640, height=400):
        self._running = True
        self._display_surf = None
        self.width = width
        self.height = height
        self.size = self.width, self.height
        self.target_fps = 60


    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True


    def on_event(self, event):        
        if event.type == pygame.QUIT:            
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.fill((0, 150, 0, 0))
        # begin render world

        # end render world
        pygame.display.flip()


    def on_cleanup(self):
        pygame.quit()
        sys.exit()


    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        prev_time = time.time()
        while(self._running):

            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

            curr_time = time.time()
            diff = curr_time - prev_time
            delay = max(1.0/self.target_fps - diff, 0)
            time.sleep(delay)
            fps = 1.0/(delay + diff)
            prev_time = curr_time
            pygame.display.set_caption("{0}: {1:.2f}".format('Test', fps))

        self.on_cleanup()
        


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


class Menu(GameCanvas):
    def __init__(self, width=640, height=400, event_handler=None):
        super().__init__(width, height)
        Menu.TITLE_COLOR = (255, 255, 255)
        Menu.BTN_COLOR = (255, 255, 0)
        Menu.BTN_HOVER_COLOR = (255, 255, 255)
        self.event_handler = event_handler        

    @staticmethod
    def point_inside_rect(px, py, rect):
        if rect.x < px < rect.x + rect.width and rect.y < py < rect.y + rect.height:
            return True
        else:
            return False

        
    def on_event(self, event):        
        if event.type == pygame.QUIT:            
            self._running = False
        
        mouse = pygame.mouse.get_pos()
        x = mouse[0]
        y = mouse[1]
        selected = None

        # hover
        for btn in [self.button3, self.button4, self.button5]:
            if Menu.point_inside_rect(x, y, btn.text_rect):
                btn.color = Menu.BTN_HOVER_COLOR
                selected = btn
            else:
                btn.color = Menu.BTN_COLOR

        # click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and selected is not None:
            print('Inside menu selected {}'.format(selected.text))

            if self.event_handler is not None:
                self.event_handler.btn_clicked(selected.text)



    def on_init(self):
        super().on_init()
        left = self.width * 0.8/2
        top = 60
        self.fontTitle = pygame.font.SysFont(pygame.font.get_default_font(), 81)
        self.fontButton = pygame.font.SysFont(pygame.font.get_default_font(), 64)
        self.title = BorderedButton('Pokerized', (self.width/2, top), self.fontTitle, Menu.TITLE_COLOR, 2, False)

        bottom_y_title = self.title.get_bottom_y()
        self.button3 = BorderedButton('3 Players', (self.width/2, 50 + bottom_y_title), self.fontButton, Menu.BTN_COLOR, 3, True)
        bottom_y_btn = self.button3.get_bottom_y()
        self.button4 = BorderedButton('4 Players', (self.width/2, 50 + bottom_y_btn), self.fontButton, Menu.BTN_COLOR, 3, True)
        bottom_y_btn = self.button4.get_bottom_y()
        self.button5 = BorderedButton('5 Players', (self.width/2, 50 + bottom_y_btn), self.fontButton, Menu.BTN_COLOR, 3, True)
        

    def on_render(self):        
        self._display_surf.fill((0, 150, 0, 0))        
        self.title.render(self._display_surf)
        self.button3.render(self._display_surf)
        self.button4.render(self._display_surf)
        self.button5.render(self._display_surf)
        pygame.display.flip()        


    def on_cleanup(self):
        print('Exiting menu')


class FakeGame(GameCanvas):
    def __init__(self, event_handler):
        super().__init__()
        self.event_handler = event_handler

    def on_event(self, event):        
        if event.type == pygame.QUIT:            
            self._running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button:            
            if self.event_handler is not None:
                self.event_handler.game_clicked()


class Controller(object):
    def __init__(self):
        self.menu = Menu(event_handler=self)
        self.game = FakeGame(event_handler=self)

    def btn_clicked(self, txt):        
        self.menu._running = False
        self.game.on_execute()

    def game_clicked(self):
        self.game._running = False
        self.menu.on_execute()


if __name__ == "__main__":    
    c = Controller()
    c.menu.on_execute()