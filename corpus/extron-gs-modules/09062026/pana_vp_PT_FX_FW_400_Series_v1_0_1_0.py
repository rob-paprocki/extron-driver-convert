from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify


class DeviceClass:

    def __init__(self):

        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.Debug = False
        self.DeviceID = '1'
        self.Models = {
            'PT-FW430U': self.pana_1_1563_430,
            'PT-FW430EA': self.pana_1_1563_430,
            'PT-FW430E': self.pana_1_1563_430,
            'PT-FX400U': self.pana_1_1563_400,
            'PT-FX400EA': self.pana_1_1563_400,
            'PT-FX400E': self.pana_1_1563_400,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.md5hash = ''
        self.Security = False

        DeviceIDValues = {
            'ID All': 'ADZZ',
            'ID 1': 'AD01',
            'ID 2': 'AD02',
            'ID 3': 'AD03',
            'ID 4': 'AD04',
            'ID 5': 'AD05',
            'ID 6': 'AD06'
        }       

        self.deviceUsername = 'admin1'
        self.devicePassword = 'panasonic'
        
        self.AddMatchString(re.compile(b'NTCONTROL 1 ([a-zA-z0-9]{8})\r'), self.__MatchAuthentication, None)
        self.AddMatchString(re.compile(b'ERR([1-5A])\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = 'ID {}'.format(value)
        
    def __MatchAuthentication(self, match, tag):
        rand_num = match.group(1).decode()
        full_str = self.deviceUsername + ':' + self.devicePassword + ':' + rand_num
        code_hash = hashlib.md5(full_str.encode())
        self.md5hash = hexlify(code_hash.digest())
        self.Security = True

    def SetAspectRatio(self, value, qualifier):
        AspectRatioCmdString = '00{0};VS1:{1}\r'.format(self.DeviceID, self.SetAspectRatios[value])
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        AudioMuteCmdString = '00{0};AMT:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = '00{0};OAS\r'.format(self.DeviceID)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        AVMuteCmdString = '00{0};OSH:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'CC1': '1',
            'CC2': '2',
            'CC3': '3',
            'CC4': '4'
        }

        ClosedCaptionCmdString = '00{0};OCC:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        FreezeCmdString = '00{0};OFZ:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer': 'RG1',
            'DVI-I': 'RG2',
            'Video': 'VID',
            'S-Video': 'SVD',
            'DVI': 'DVI',
            'Network': 'NWP',
            'HDMI': 'HDI'
        }

        InputCmdString = '00{0};IIS:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco': '0',
            'Normal': '1'
        }

        LampModeCmdString = '00{0};OLP:{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'OMN',
            'Back': 'OBK',
            'Enter': 'OEN',
            'Up': 'OCU',
            'Down': 'OCD',
            'Left': 'OCL',
            'Right': 'OCR'
        }

        MenuNavigationCmdString = '00{0};{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': 'POF',
            'On': 'PON'
        }

        PowerCmdString = '00{0};{1}\r'.format(self.DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '00{0};AVL:{1}'.format(self.DeviceID, str(value).zfill(3))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Security:
            self.Send(self.md5hash + commandstring.encode())
        else:
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorValue = {
            '1': 'Undefined control command',
            '2': 'Out of parameter range',
            '3': 'Busy state or no-acceptable period',
            '4': 'Timeout or no-acceptable period',
            '5': 'Wrong data length',
            'A': 'Password mismatch',
        }

        value = match.group(1).decode()
        print(ErrorValue[value])

    def pana_1_1563_400(self):

        self.SetAspectRatios = {
            'Auto': '00',
            'Normal': '01',
            'Wide': '02',
            '4:3': '03',
            'Native': '05',
            'Full': '06',
            'H-Fit': '09',
            'V-Fit': '10'
        }

    def pana_1_1563_430(self):

        self.SetAspectRatios = {
            'Auto': '00',
            '4:3': '01',
            'Normal': '02',
            'Native': '05',
            'Full': '06',
            'H-Fit': '09',
            'V-Fit': '10'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        #if hasattr(self, method) and callable(getattr(self, method)):
        getattr(self, method)(value, qualifier)
        #else:
            #print(command, 'does not support Set.')

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
