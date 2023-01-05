import os, sys
import pygame
import numpy as np
import time
import os, sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import sys
sys.path.append("../")

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config


"""
TODO: 
    wrap_text has a bug: if the user types a super long word it will hang.
    render different bg colors -- wait with design
    AI text popping up one by one. openai does this word-wise
    AI cursor blinking like a square for the AI
    pictures in front of text
"""

#%% Show the chat history
def wrap_text(font, text, max_width):
    r'''This function takes in a font, a string of text, and a maximum width.
    It returns a list of strings, each of which is no wider than the
    maximum width.
    Args:
        font: a pygame font object
        text: a string of text
        max_width: an integer for the maximum width of a line of text in pixels
    Returns:
        A list of strings. Each string is no wider than max_width.
    '''
    lines = []
    # If the width of the text is smaller than the maximum width, return it as a single line
    if font.size(text)[0] <= max_width:
        lines.append(text)
    else:
        # Split the text into words
        words = text.split(' ')
        i = 0
        # While there are words left to process
        while i < len(words):
            # Find the maximum number of words that can fit on a single line
            line = ''
            while i < len(words) and font.size(line + words[i])[0] <= max_width:
                line = line + words[i] + ' '
                i += 1
            # Remove the extra space at the end of the line
            if line:
                line = line[:-1]
            # Add the line to the list of lines
            lines.append(line)
    return lines


def get_key(pg_keycode):
    r'''This function takes a pygame keycode and returns the corresponding character.
    
    Args:
    pg_keycode : int
        The pygame keycode of the key that was pressed.
        
    Returns:
        The character that corresponds to the key that was pressed.'''
    # print(f"get_key: symbol is {pg_keycode}")
    
    # Check space
    if pg_keycode == pygame.K_SPACE:
        return " "
    
    # Check enter
    if pg_keycode == pygame.K_RETURN:
        return "+"
    
    # Check backspace
    if pg_keycode == pygame.K_BACKSPACE:
        return "&"
    
    # Check period
    if pg_keycode == pygame.K_PERIOD:
        return "."
    
    # Check comma
    if pg_keycode == pygame.K_COMMA:
        return ","
    
    # Check if shift was pressed before and a capital character should be returned
    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
        # Check capital alphabetic characters
        if pg_keycode >= pygame.K_a and pg_keycode <= pygame.K_z:
            return chr(pg_keycode).upper()
        
        # Check question mark
        if pg_keycode == 47:
           return "?"
       
        # Check exclamation mark
        if pg_keycode == 49:
            return "!"
        
    # Check small alphabetic letters
    if pg_keycode >= pygame.K_a and pg_keycode <= pygame.K_z:
        return chr(pg_keycode)
    
    # Check numbers
    if pg_keycode >= pygame.K_0 and pg_keycode <= pygame.K_9:
        return str(pg_keycode - pygame.K_0)

    if pg_keycode == pygame.K_QUOTE:
        return "'"
    
    # Everything else    
    return '~'

class TimeMan():
    r'''Class for measuring time intervals.
    Args:
    use_counter : bool, optional
        If True, the time is incremented by a constant amount.
        If False, the time is taken from the system clock.
        The default is False.
    count_time_increment : float, optional
        The amount of time to increment the counter by.
        The default is 0.02.'''
    def __init__(self, use_counter=False, count_time_increment=0.02):
        self.t_start = time.perf_counter()
        self.t_last = self.t_start 
        self.use_counter = use_counter
        self.count_time_increment = count_time_increment
        self.t_last_interval = 0
        self.dt_interval=-1
        
    def set_interval(self, dt_inverval=1):
        self.dt_interval = dt_inverval
        self.t_interval_last = time.perf_counter()
        
    def reset_start(self):
        self.t_start = time.perf_counter()
        self.t_last = self.t_start       
        
    def check_interval(self):
        self.update()
        if self.t_last > self.t_interval_last + self.dt_interval:
            self.t_interval_last = np.copy(self.t_last)
            # print("self.t_last: {} self.t_inverval_last {}".format(self.t_last, self.t_interval_last))
            return True
        else:
            return False
    
    def tic(self):
        self.reset_start()
        
    def toc(self):
        self.update()
        dt = self.t_last - self.t_start
        print("dt = {}ms".format(int(1000*dt)))
    
    def get_time(self):
        return self.t_last
        
    def get_dt(self):
        if not self.use_counter:
            self.t_last = time.perf_counter()
        dt = self.t_last - self.t_start
        return dt

    def update(self):
        if self.use_counter:
            self.t_last += self.count_time_increment 
        else:
            self.t_last = time.perf_counter()


class ChatGUI():
    r''' Pygame based user interface for an AI chatbot. 
    All parameters are defined in init_parameters for the moment'''
    def __init__(
            self,
            fp_config: str = "../metamersion_latent/configs/chat/mad_bot.py",
            use_ai_chat: bool = True,
            ):
        
        pygame.init()
        self.use_ai_chat = use_ai_chat
        self.init_parameters()
        self.init_vars()
        if use_ai_chat:
            self.init_ai_chat(fp_config=fp_config)
        else:
            self.history_sham()
        self.tm = TimeMan()
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption("Metamersion Chat")
        self.clock = pygame.time.Clock()

        
    def init_parameters(self):
        self.fp_font = '/usr/share/fonts/kongtext.ttf'
        self.font_size = 20
        self.display_height = 900
        self.display_width = 1500
        
        self.x_begin_text = 50
        self.x_end_text = self.display_width - self.x_begin_text
        self.y_begin_text_history = 10
        self.y_end_text_history = self.display_height - 200
        self.y_end_text_typing = self.display_height - 50
        
        self.line_distance = 10
        self.person_separation = 15
        
        self.text_color_human = (200, 200, 200)
        self.text_color_ai = (0, 200, 0)
        self.background_color = (0, 0, 0)
        
        # Fonts
        if not os.path.isfile(self.fp_font):
            print(f"font not found: {self.fp_font}. Taking default.")
            fp_font = None
        else:
            fp_font = self.fp_font
        self.font_typing = pygame.font.Font(fp_font, self.font_size)
        self.font_history_human = pygame.font.Font(fp_font, self.font_size)
        self.font_history_ai = pygame.font.Font(fp_font, self.font_size)
        self.line_height_typing = self.font_typing.size('HohoInit')[1]
        self.line_height_human = self.font_history_human.size('HohoInit')[1]
        self.line_height_ai = self.font_history_ai.size('HohoInit')[1]
        
        # Cursors
        self.cursor_period = 1.0 # Period time in seconds
        self.cursor_fract_on = 0.35 # How much of the period time cursor is on

        self.col_cursor_human = self.text_color_human 
        self.width_cursor_human = 3 # px
        self.fract_cursor_height_human = 1.2 # Relative to text field height
        self.cursor_xdist_human = 10
        self.cursor_height_human = int(self.fract_cursor_height_human*self.line_height_typing)
        self.cursor_human_y = 0
        self.cursor_human_x = 0
        
    def init_vars(self):
        self.history_ai = []
        self.history_human = []
        self.text_typing = ""
        self.send_message = False
        # self.history_sham()
        
    def init_ai_chat(self, fp_config, verbose=False):
        config = Config.fromfile(fp_config)
        self.chat = Chat(config, False)
        self.history_ai.append(self.chat.first_message)
        self.send_message_timer = 3
        
    def hit_enter(self):
        if not self.last_input_ai():
            print("hit_enter: last input was not AI!")
            return
        if len(self.text_typing) > 0:
            self.history_human.append(self.text_typing)
            self.text_typing = ""
            self.send_message = True
    
    def send_message_check(self):
        if not self.use_ai_chat and self.send_message:
            self.history_ai.append("FAKE MESSAGE ...")
            self.send_message = False
            
        if self.send_message:
            self.send_message_timer -= 1
            if self.send_message_timer == 0:
                print("SENDING MESSAGE!")
                self.send_message_timer = 3
                self.send_message = False
                output = self.chat(self.history_human[-1])
                output = output.strip()
                print(f"GOT: {output}")
                self.history_ai.append(output)
                self.send_message = False
    
    def last_input_ai(self):
        nmb_items = max(len(self.history_ai), len(self.history_human))
        if len(self.history_human) == nmb_items:
            last_input_ai = False
        else:
            last_input_ai = True
        return last_input_ai
    
    def history_sham(self):
        self.history_ai.append("AI i am AI")
        self.history_human.append("Human i am human")
        self.history_ai.append("AI i am AI")
        self.history_human.append("Human i am human")
        self.history_ai.append("AI i am AI")
        # self.history_human.append("Human i am human")
    
    def render_text_history(self):
        # Go from bottom to top and render text if there is space
        y_current = self.y_end_text_history
        nmb_items = max(len(self.history_ai), len(self.history_human))
        
        # loop over all items
        for idx_item in range(nmb_items-1, -1, -1):
            for person_type in range(2):
                if person_type == 0:
                    if len(self.history_human) > idx_item:
                        text = self.history_human[idx_item]
                    else:
                        # last word was the AI. don't show human history.
                        continue
                else:
                    text = self.history_ai[idx_item]
                
                if person_type == 0: 
                    font = self.font_history_human
                    color = self.text_color_human
                else:
                    font = self.font_history_ai
                    color = self.text_color_ai
                    
                text_lines = wrap_text(font, text, self.x_end_text)
                
                for line in text_lines[::-1]:
                    # Render text
                    text_render = font.render(line, True, color)
                    
                    # Get text size
                    text_size = text_render.get_size()
                
                    # Get text rect
                    text_rect = text_render.get_rect()
                
                    # Set text rect center
                    text_rect.bottomleft = (self.x_begin_text, y_current)
                
                    # Blit text
                    self.screen.blit(text_render, text_rect)
                    y_current -= (text_size[1] + self.line_distance)
                    
                    # Don't draw if above FOV
                    if y_current < self.y_begin_text_history:
                        continue
                
                # print(f"{idx_item} {y_current}")
                y_current -= self.person_separation
            
    def render_text_typing(self):
        if not self.last_input_ai():
            return
        # Get events
        for event in pygame.event.get():
            # Check if event is quit
            # if event.type == pygame.QUIT:
            #     # Set running to false
            #     running = False
            # Check if event is keydown
            if event.type == pygame.KEYDOWN:
                # Get key
                key = get_key(event.key)
                
                # Check if enter was pressed
                if key == "+":
                    self.hit_enter()
                    return
                
                # Check if key is not !
                if key != '~' and key != "&":
                    # Add key to text
                    self.text_typing += key
                # Check if key is & for removal
                if key == '&':
                    # Remove last character from text
                    self.text_typing = self.text_typing[:-1]

        
        
        # Multiline splitting
        text_lines = wrap_text(self.font_typing, self.text_typing, self.x_end_text)
        
        # Measure out total ydim
        y_total = len(text_lines)*(self.line_height_typing+self.line_distance)
        y_begin = self.y_end_text_typing - y_total
        for j, line in enumerate(text_lines):
            # Render text
            text_render = self.font_typing.render(line, True, self.text_color_human)
    
            # Get text rect
            text_rect = text_render.get_rect()
            
            # Get text size
            text_size = text_render.get_size()
    
            # Set text rect pos
            text_pos = (self.x_begin_text, y_begin)
            text_rect.bottomleft = text_pos
            
            # Set the cursor
            self.cursor_human_y = y_begin - self.cursor_height_human
            self.cursor_human_x = text_size[0] + self.x_begin_text#+ self.cursor_xdist_human 
    
            # Blit text
            self.screen.blit(text_render, text_rect)
            
            y_begin += self.line_height_typing+self.line_distance
    
    def render_cursor_human(self):
        if not self.last_input_ai():
            return
        if np.mod(self.tm.get_dt(), self.cursor_period) / self.cursor_period < self.cursor_fract_on:
            pygame.draw.rect(self.screen, self.col_cursor_human, (self.cursor_human_x, self.cursor_human_y, self.width_cursor_human, self.cursor_height_human))


if __name__ == "__main__":

    self = ChatGUI(use_ai_chat=True)
    
    while True:
        
        # Set clock speed
        self.clock.tick(60)
    
        # Fill screen with background color
        self.screen.fill(self.background_color)
        
        self.render_text_history()
        self.render_text_typing()
        self.render_cursor_human()
        
        self.send_message_check()
        
        # Update display
        pygame.display.update()
    
   
