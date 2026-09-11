from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ButtonSimulation': {'Parameters':['Scene','Other','Slider'], 'Status': {}},
            'ModeStatus': { 'Status': {}},
            'PageButtonStatus': { 'Status': {}},
            'SceneSelect': {'Parameters':['Page','Button'], 'Status': {}},
            'SceneStatus': {'Parameters':['Button'], 'Status': {}},
            'SliderStatus': { 'Status': {}},
            }

                        
        self.AddMatchString(re.compile(b'\x53\x74\x69\x63\x6b\x5f\x55\x31\x69\x00\x00\x00([\x00-\x02])\x00'), self.__MatchModeStatus, None)
        self.AddMatchString(re.compile(b'\x53\x74\x69\x63\x6b\x5f\x55\x31\x68\x00\x00\x00([\x00-\xFF])\x00'), self.__MatchPageButtonStatus, None)
        self.AddMatchString(re.compile(b'\x53\x74\x69\x63\x6b\x5f\x55\x31\x67\x00\x00\x00([\x00-\xFF])\x00'), self.__MatchSceneStatus, None)
        self.AddMatchString(re.compile(b'\x53\x74\x69\x63\x6b\x5f\x55\x31\x6A\x00[\x01-\x02]\x00([\x00-\xFF])([\x00-\xFF])'), self.__MatchSliderStatus, None)

    def SetButtonSimulation(self, value, qualifier):

        SceneStates = {
            '1'     : 1, 
            '2'     : 2, 
            '3'     : 4, 
            '4'     : 8, 
            '5'     : 16, 
            '6'     : 32, 
            '7'     : 64, 
            '8'     : 128, 
            'Empty' : 0
        }

        OtherStates = {
            'Page Down' : 1, 
            'Page Up'   : 2, 
            'Select'    : 4, 
            'Blackout'  : 8, 
            'Empty'     : 0
        }

        sceneBtn = qualifier['Scene']
        otherBtn = qualifier['Other']
        sliderBtn = qualifier['Slider']
        if sceneBtn in SceneStates and otherBtn in OtherStates and (sliderBtn == 'Empty' or 0 <= int(sliderBtn) <= 100):
            if sliderBtn == 'Empty':
                ButtonSimulationCmdString = pack('13B', 0x53, 0x74, 0x69, 0x63, 0x6b, 0x5f, 0x55, 0x31, 0x65, 0x00,
                                                SceneStates[sceneBtn], OtherStates[otherBtn], 0xFF)
            else:
                ButtonSimulationCmdString = pack('13B', 0x53, 0x74, 0x69, 0x63, 0x6b, 0x5f, 0x55, 0x31, 0x65, 0x00,
                                                SceneStates[sceneBtn], OtherStates[otherBtn], int(sliderBtn))
            self.__SetHelper('ButtonSimulation', ButtonSimulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonSimulation')

    def __MatchModeStatus(self, match, tag):

        ModeStatusStates = {
            '\x00' : 'Dimmer', 
            '\x01' : 'Speed', 
            '\x02' : 'Color'
        }
        value = ModeStatusStates[match.group(1).decode()]
        self.WriteStatus('ModeStatus', value, None)
        
    def __MatchPageButtonStatus(self, match, tag):

        value = ord(match.group(1))
        self.WriteStatus('PageButtonStatus', value, None)
        
    def SetSceneSelect(self, value, qualifier):

        PageStates = {
            'A' : 1, 
            'B' : 2, 
            'C' : 3, 
            'D' : 4, 
            'E' : 5, 
            'F' : 6, 
            'G' : 7, 
            'H' : 8, 
            'I' : 9, 
            'J' : 10, 
            'K' : 11, 
            'L' : 12, 
            'M' : 13, 
            'N' : 14, 
            'O' : 15, 
            'P' : 16, 
            'Q' : 17, 
            'R' : 18, 
            'S' : 19, 
            'T' : 20, 
            'U' : 21, 
            'V' : 22, 
            'W' : 23, 
            'X' : 24, 
            'Y' : 25
        }

        page_val = qualifier['Page']
        button_val = int(qualifier['Button'])
        if page_val in PageStates and 1 <= button_val <= 8:
            val = 8 * (PageStates[page_val] - 1) + button_val
            SceneSelectCmdString = pack('12B', 0x53, 0x74, 0x69, 0x63, 0x6b, 0x5f, 0x55, 0x31, 0x06, 0x00,
                                        val, 0x00)
            self.__SetHelper('SceneSelect', SceneSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSelect')

    def __MatchSceneStatus(self, match, tag):

        SceneStates = {
            '1' : 'On', 
            '0' : 'Off'
        }
        
        temp = bin(ord(match.group(1)))[2:].zfill(8)
        
        self.WriteStatus('SceneStatus', SceneStates[temp[7]], {'Button' : '1'})
        self.WriteStatus('SceneStatus', SceneStates[temp[6]], {'Button' : '2'})
        self.WriteStatus('SceneStatus', SceneStates[temp[5]], {'Button' : '3'})
        self.WriteStatus('SceneStatus', SceneStates[temp[4]], {'Button' : '4'})
        self.WriteStatus('SceneStatus', SceneStates[temp[3]], {'Button' : '5'})
        self.WriteStatus('SceneStatus', SceneStates[temp[2]], {'Button' : '6'})
        self.WriteStatus('SceneStatus', SceneStates[temp[1]], {'Button' : '7'})
        self.WriteStatus('SceneStatus', SceneStates[temp[0]], {'Button' : '8'})
        
    def __MatchSliderStatus(self, match, tag):

        value = int((ord(match.group(1)) + (256 * ord(match.group(2))))/10)
        self.WriteStatus('SliderStatus', value, None)
        
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

     ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}
class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])