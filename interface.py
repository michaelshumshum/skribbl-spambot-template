import datetime
import npyscreen
import shutil
import random
from time import sleep

class grid(npyscreen.SimpleGrid):
    def custom_print_cell(self, actual_cell, cell_display_value):
        text1 = ['is drawing now','left.','joined.','is voting to kick','was kicked!']
        text2 = ['EXCEPTION','Spam detected!']
        text3 = ['START','JOINED GAME','LEFT GAME']

        if any(text in cell_display_value for text in text1):
            actual_cell.color = 'IMPORTANT'
        elif any(text in cell_display_value for text in text2):
            actual_cell.color = 'DANGER'
        elif any(text in cell_display_value for text in text3):
            actual_cell.color = 'WARNING'
        else:
            actual_cell.color = 'DEFAULT'

class box(npyscreen.BoxTitle):
    _contained_widget = grid
    entry_widget = grid

class DefaultTheme(npyscreen.ThemeManager):
    default_colors = {
    'DEFAULT'     : 'WHITE_BLACK',
    'FORMDEFAULT' : 'WHITE_BLACK',
    'NO_EDIT'     : 'BLUE_BLACK',
    'STANDOUT'    : 'CYAN_BLACK',
    'CURSOR'      : 'WHITE_BLACK',
    'CURSOR_INVERSE': 'BLACK_WHITE',
    'LABEL'       : 'WHITE_BLACK',
    'LABELBOLD'   : 'WHITE_BLACK',
    'CONTROL'     : 'YELLOW_BLACK',
    'IMPORTANT'   : 'GREEN_BLACK',
    'SAFE'        : 'GREEN_BLACK',
    'WARNING'     : 'YELLOW_BLACK',
    'DANGER'      : 'RED_BLACK',
    'CRITICAL'    : 'BLACK_RED',
    'GOOD'        : 'GREEN_BLACK',
    'GOODHL'      : 'GREEN_BLACK',
    'VERYGOOD'    : 'BLACK_GREEN',
    'CAUTION'     : 'YELLOW_BLACK',
    'CAUTIONHL'   : 'BLACK_YELLOW',
    }

class Form(npyscreen.Form):
    def create(self):
        self.name = 'skribbl'
        self.start_time = datetime.datetime.now()
        self.count = 6
        self.columns, self.rows = shutil.get_terminal_size()
        self.widget_dimensions = []
        self.widgets = []
        self.active_times = []
        self.player_counts = []
        if (self.count / 2 >= 2) and (self.count % 2 == 0):
            self.widget_width = int(self.columns/(self.count/2))-4
            self.widget_height = int(self.rows/2)-2
            for i in range(self.count):
                if i+1 <= self.count/2:
                    rely = 2
                else:
                    rely = self.widget_height+2
                if (self.count/2 == i) or (i == 0):
                    relx = 3
                else:
                    if i+1 <= self.count/2:
                        factor = i
                    else:
                        factor = int(i - (self.count/2))
                    relx = (self.widget_width) * factor + 3
                data = ((self.widget_width,self.widget_height),(relx,rely))
                self.widget_dimensions.append(data)
        else:
            self.widget_width = int(self.columns/(self.count/2))-25
            self.widget_height = self.rows-10
            for i in range(self.count):
                relx = self.widget_height * i
                data = ((self.widget_width,self.widget_height),(relx+2,0))
                self.widget_dimensions.append(data)
        for dimensions in self.widget_dimensions:
            self.active_times.append(None)
            self.player_counts.append(0)
            i = self.widget_dimensions.index(dimensions) + 1
            hw = dimensions[0]
            rel = dimensions[1]
            widget = self.add(box,editable=False,max_width=hw[0],max_height=hw[1],relx=rel[0],rely=rel[1],color='DEFAULT',values=['===================='],contained_widget_arguments={'column_width' : self.widget_width-5})
            self.widgets.append(widget)
    def update_values(self,queues):
        self.queues = queues
        while True:
            self.name = datetime.datetime.now() - self.start_time
            for widget in self.widgets:
                index = self.widgets.index(widget)
                queue = self.queues[index]
                start_time = self.active_times[index]
                if start_time != None:
                    since_time = datetime.datetime.now() - start_time
                    widget.name = f'bot{index} - {since_time.__str__()[:7]} - {self.player_counts[index]} players'
                else:
                    widget.name = f'bot{index}'
                if not queue.empty():
                    messages = queue.get()
                    if messages == 'START':
                        widget.color = 'DEFAULT'
                        widget.values.append([f"{str(datetime.datetime.now())[11:-7]} > {messages}"])
                    elif messages == 'JOINED GAME':
                        self.active_times[index] = datetime.datetime.now()
                        widget.color = 'STANDOUT'
                        widget.values.append([f"{str(datetime.datetime.now())[11:-7]} > {messages}"])
                        continue
                    elif messages == 'LEFT GAME':
                        self.active_times[index] = None
                        widget.color = 'DEFAULT'
                        widget.values.append([f"{str(datetime.datetime.now())[11:-7]} > {messages}"])
                        continue
                    elif 'EXCEPTION' in messages:
                        widget.color = 'DANGER'
                        widget.values.append([f"{str(datetime.datetime.now())[11:-7]} > {messages}"])
                    elif 'PLAYERS_COUNT' in messages:
                        self.player_counts[index] = messages[1]
                    else:
                        for message in messages:
                            if message == '':
                                continue
                            line = (f"{str(datetime.datetime.now())[11:-7]} > {message}"[:self.widget_width]).encode("ascii", errors="ignore").decode()
                            widget.values.append([line])
                start = len(widget.values)-self.widget_height-27
                widget.values = widget.values[start:]
            self.display()
