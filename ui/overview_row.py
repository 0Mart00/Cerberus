from panda3d.core import LVector4 as LColor, TextNode # <--- TextNode importálása
from direct.gui.DirectGui import DirectFrame, DirectLabel, DGG

# UI Style Constants (EVE-like)
ROW_HEIGHT = 0.05
COLUMN_WIDTHS = [0.03, 0.25, 0.15, 0.1, 0.1, 0.05] 
OVERVIEW_BG = LColor(0.05, 0.05, 0.1, 0.9)
OVERVIEW_LINE = LColor(0.1, 0.3, 0.5, 0.9)
OVERVIEW_TEXT_COLOR = LColor(0.7, 0.8, 1.0, 1.0) 
HIGHLIGHT_COLOR = LColor(0.2, 0.3, 0.4, 1.0) 
RANGE_COLOR_GLOW = LColor(0.8, 0.4, 0.9, 1.0) 

STANDING_COLORS = {
    "Enemy": LColor(0.8, 0.2, 0.2, 0.8),    
    "Neutral": LColor(0.8, 0.8, 0.2, 0.8),  
    "Friendly": LColor(0.2, 0.8, 0.2, 0.8), 
    "Corp/Fleet": LColor(0.2, 0.5, 0.8, 0.8) 
}

def format_distance(distance):
    if distance >= 149597870700: 
        return f"{distance / 149597870700:.2f} AU"
    elif distance >= 1000:
        return f"{distance / 1000:.2f} km"
    else:
        return f"{distance:.2f} m"

class OverviewRow(DirectFrame):
    def __init__(self, parent, item_data, command_callback, **kwargs):
        self.item_data = item_data
        self.command_callback = command_callback
        self.is_selected = False
        
        total_width = sum(COLUMN_WIDTHS)
        
        DirectFrame.__init__(self, parent=parent,
            frameColor=OVERVIEW_BG * 0.9,
            frameSize=(-total_width/2, total_width/2, -ROW_HEIGHT/2, ROW_HEIGHT/2),
            borderWidth=(0.001, 0.001),
            relief=DGG.FLAT,
            **kwargs
        )
        self.initialiseoptions(OverviewRow)
        
        self.setup_cells(total_width)
        self.update_content(item_data)

        self.bind('mouse3', self.show_context_menu)      
          
    def setup_cells(self, total_width):
        self.standing_line = DirectFrame(parent=self,
            frameColor=(0, 0, 0, 0),
            frameSize=(-total_width/2, -total_width/2 + COLUMN_WIDTHS[0]/5, -ROW_HEIGHT/2, ROW_HEIGHT/2),
            relief=DGG.FLAT
        )
        
        x_offset = -total_width/2
        self.cells = []
        col_names = ['icon', 'name', 'distance', 'velocity', 'angular', 'threat']
        
        for i, (width, col_name) in enumerate(zip(COLUMN_WIDTHS, col_names)):
            label = DirectLabel(parent=self,
                relief=DGG.FLAT,
                text="",
                text_fg=OVERVIEW_TEXT_COLOR,
                text_scale=0.018,
                # JAVÍTVA: TextNode.ALeft használata
                text_align=TextNode.ALeft,
                frameColor=(0, 0, 0, 0),
                pos=(x_offset + width/2, 0, 0),
                frameSize=(-width/2, width/2, -ROW_HEIGHT/2, ROW_HEIGHT/2)
            )
            
            text_x_pos = -width/2 + 0.005 if col_name not in ('icon', 'threat') else 0
            label['text_pos'] = (text_x_pos, -ROW_HEIGHT/4)
            
            if col_name in ('icon', 'threat'):
                # JAVÍTVA: TextNode.ACenter használata
                label['text_align'] = TextNode.ACenter
                if col_name == 'threat':
                    label['text_scale'] = 0.025
                 
            self.cells.append(label)
            x_offset += width

    def update_content(self, item_data):
        self.item_data = item_data
        
        color = STANDING_COLORS.get(item_data['standing'], OVERVIEW_BG)
        self.standing_line['frameColor'] = color
        
        threat_icon = ""
        if "Attacking" in item_data['flags']:
            threat_icon += "!" 
        if "Targeted" in item_data['flags']:
            threat_icon += "X"
            
        range_color = RANGE_COLOR_GLOW if "WithinRange" in item_data['flags'] else OVERVIEW_TEXT_COLOR

        content = [
            item_data['icon'],
            item_data['name'],
            format_distance(item_data['distance']),
            f"{item_data['velocity']:.2f} m/s",
            f"{item_data['angular']:.2f}",
            threat_icon
        ]
        
        for i, cell in enumerate(self.cells):
            cell['text'] = str(content[i])
            if i in (2, 3): 
                cell['text_fg'] = range_color
            else:
                cell['text_fg'] = OVERVIEW_TEXT_COLOR

    def set_selected(self, is_selected):
        self.is_selected = is_selected
        if is_selected:
            self['frameColor'] = HIGHLIGHT_COLOR
        else:
            self['frameColor'] = OVERVIEW_BG * 0.9

    def show_context_menu(self, event):
        self.command_callback('context_menu', self.item_data['id'], event)
        
    def destroy(self):
        for cell in self.cells:
            cell.destroy()
        self.standing_line.destroy()
        DirectFrame.destroy(self)