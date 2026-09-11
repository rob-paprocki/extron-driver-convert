import sys; sys.path.insert(0,'tools'); import wire_table
A = "\n".join([
 "class DeviceClass:",
 "    def __init__(self):",
 "        self.Commands = {'CustomControl': {'Parameters':['Bank'], 'Status': {}}}",
 "    def SetCustomControl(self,value,qualifier):",
 "        CmdString = 'CC {}{:02}' + chr(13)",
 "        CmdString = 'CC {}{:02}'.format(int(qualifier['Bank']),int(value))",
 "        self._DeviceClass__SetHelper('CustomControl', CmdString, value, qualifier)",
])
B = A.replace("{}{:02}", "{}{}")
ta=wire_table.extract_table(A,'a.py'); tb=wire_table.extract_table(B,'b.py')
print('A(:02) canonical:',repr(ta.commands['CustomControl'].set_templates[0].canonical))
print('B(bare) canonical:',repr(tb.commands['CustomControl'].set_templates[0].canonical))
print('diff:',wire_table.diff_tables(ta,tb))
