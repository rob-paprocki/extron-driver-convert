import sys; sys.path.insert(0,'tools'); import wire_table
CR = chr(92)+'r'
base = ("class DeviceClass:\n"
        "    def __init__(self):\n"
        "        self.Commands = {'A':{'Parameters':['Out'],'Status':{}}}\n"
        "{BODY}\n"
        "    def __SetHelper(self,c,s,v,q): pass\n")
v1 = ("    def SetA(self, value, qualifier):\n"
      "        CmdString = 'XPT D:{}"+CR+"'.format(qualifier['Out'])\n"
      "        self.__SetHelper('A', CmdString, value, qualifier)\n")
v2 = ("    def SetA(self, value, qualifier):\n"
      "        if value != 'ALL':\n"
      "            CmdString = 'XPT D:{} L"+CR+"'.format(qualifier['Out'])\n"
      "        else:\n"
      "            CmdString = 'XPT D:{}"+CR+"'.format(qualifier['Out'])\n"
      "        self.__SetHelper('A', CmdString, value, qualifier)\n")
v3 = ("    def SetA(self, value, qualifier):\n"
      "        if value != 'ALL':\n"
      "            ACmdString = 'XPT D:{} L"+CR+"'.format(qualifier['Out'])\n"
      "            self.__SetHelper('A', ACmdString, value, qualifier)\n"
      "        else:\n"
      "            ACmdString = 'XPT D:{}"+CR+"'.format(qualifier['Out'])\n"
      "            self.__SetHelper('A', ACmdString, value, qualifier)\n")
for name, body in [('single assign, no branch',v1),('if/else join then one call (human)',v2),('call inside each branch (Extron)',v3)]:
    t = wire_table.extract_table(base.replace('{BODY}', body), 't')
    print(name, '->', [(s.canonical, s.slots) for s in t.commands['A'].set_templates])
