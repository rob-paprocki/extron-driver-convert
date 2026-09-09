from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main_switch import main_switch

from mod_ross_matrix_RossTalk_v1_1_0_0 import DeviceClass as switch_mod
from mod_ross_matrix_tsl_3_1_v1_1_0_0 import DeviceClass as switch_mod2

from extronlib.system import Timer,Wait

'''

Generic plugin should implement class access and standardize the commands to and from the device, providing a
translation layer between the main program and hardware module.  Logic defined in this class should be only device specific from program generic.

'''


class plugin():
    def __init__(self,parent:'main_switch'):
        self.p = parent
        self.v = parent.v
        self.d = parent.d
        self.dev = parent.switch #type:switch_mod
        self.dev2 = parent.switch2 #type:switch_mod2
        self.dev3 = parent.switch3 #type:switch_mod


    def event_ConnectionStatus(self):
        def e(command,value,qualifier):
            self.p.event_switch_ConnectionStatus(command,value,qualifier)
        return e
    def event_ConnectionStatus2(self):
        def e(command,value,qualifier):
            pass#self.p.event_switch_ConnectionStatus(command,value,qualifier)
        return e
    def event_ConnectionStatus3(self):
        def e(command,value,qualifier):
            pass#self.p.event_switch_ConnectionStatus(command,value,qualifier)
        return e
    def event_OutputTieStatus(self):
        def e(command,value,qualifier):
            self.p.event_switch_OutputTieStatus(command,value,qualifier)
        return e
    #command functions
    def setMatrixTieCommand(self,input,output,sw_type):
        levels = ''
        if 'Video' == sw_type:
            levels = '1'
        if 'Audio' == sw_type:
            levels = '2-17'
        if 'Audio/Vdeo' == sw_type:
            levels = '1-17'
        output = int(output)+53
        self.dev.Set('MatrixTieCommand',None,{'Input':input,'Output':str(output),'Levels':levels,'Tie Type':sw_type})
    def recall_salvo(self,preset_num):
        self.dev.Set('SalvoRecall',preset_num)
    def recall_loadset(self,preset_name):
        self.dev3.Set('LoadSet',preset_name)
    def custom_control(self,control_number,bank_number):
        self.dev3.Set('CustomControl',control_number,{'Bank':bank_number})

    def subscribe(self):
        self.dev.SubscribeStatus('ConnectionStatus',None,self.event_ConnectionStatus())
        self.dev.OnDisconnected()
        self.dev2.SubscribeStatus('ConnectionStatus',None,self.event_ConnectionStatus2())
        self.dev2.SubscribeStatus('OutputTieStatus',None,self.event_OutputTieStatus())
        self.dev2.OnDisconnected()
        self.dev3.SubscribeStatus('ConnectionStatus',None,self.event_ConnectionStatus3())
        self.dev2.OnDisconnected()
        @Wait(0.1)
        def w():
            self.dev.Connect()
        @Wait(0.1)
        def w2():
            self.dev2.Connect()
        @Wait(0.1)
        def w3():
            self.dev3.Connect()