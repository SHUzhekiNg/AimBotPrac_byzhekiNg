class ModeChooser():
    def __init__(self,color,debug):
        self.colors=['blue','red']
        self.modes=['armor_stable','armor_rotate','armor_lob','energy']
        assert color in self.colors
        self.current_color = color     #default
        self.current_mode='armor_stable'
        self.debug = debug
    def mode_set(self,mode):
        assert mode in self.modes
        self.current_mode = mode
