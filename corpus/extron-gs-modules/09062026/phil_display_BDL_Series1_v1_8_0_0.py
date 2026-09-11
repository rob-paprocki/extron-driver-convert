from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re
class DeviceClass:


    
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'BDL-4620QL': self.phil_10_265_QL,
            'BDL-5520QL': self.phil_10_265_QL,
            'BDL-4220QL': self.phil_10_265_QL,
            'BDL-3220QL': self.phil_10_265_QL,
            'BDL-6420EL': self.phil_10_265_QL,
            'BDL-4650TT': self.phil_10_265_QLTT,
            'BDL-6520QL': self.phil_10_265_QLTT,
            'BDL-4330QL': self.phil_10_265_QL,
            'BDL-4771V': self.phil_10_265_V,
            'BDL-8470QU': self.phil_10_265_QU,
            'BDL-4830QL': self.phil_10_265_QL,
            'BDL-8470EU': self.phil_10_265_QU,
            }


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'AutoAdjust': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'Input': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'PictureInPicture': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'PictureInPictureSource': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID','Group ID'], 'Status': {}},
            'Volume': {'Parameters':['Device ID','Group ID', 'Type'], 'Status': {}},
            'VolumeSpeaker': {'Parameters':['Device ID','Group ID'], 'Status': {}},
        }
                
        self.UpdateRegex = re.compile(b'(\x06|\x07|\x09)([\x01-\xFF])([\x00-\xFF])([\x00-\xFF]{3,6})')
        

    def SetAspectRatio(self, value, qualifier):


        AspectRatioStateValues = {
            'Normal'  : 0, 
            'Custom'  : 1, 
            'Real'    : 2, 
            'Full'    : 3, 
            '21:9'    : 4, 
            'Dynamic' : 5,
            '16:9'    : 6
        }

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x06 ^ DeviceID ^ GroupID ^ 0x3A ^ AspectRatioStateValues[value]
            CmdString = pack('>BBBBBB',6,DeviceID,GroupID,0x3A,AspectRatioStateValues[value],checksum)
            self.__SetHelper('AspectRatio', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')
    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00' : 'Normal', 
            b'\x01' : 'Custom', 
            b'\x02' : 'Real', 
            b'\x03' : 'Full', 
            b'\x04' : '21:9', 
            b'\x05' : 'Dynamic',
            b'\x06' : '16:9'
        }
        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x3B
            AspectRatioCmdString = pack('>BBBBB',5,DeviceID,GroupID,0x3B,checksum)
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[4:5]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio') 

    def SetAutoAdjust(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x07 ^ DeviceID ^ GroupID ^ 0x70 ^ 0x40
            AutoAdjustCmdString = pack('>BBBBBBB',7,DeviceID,GroupID,0x70,0x40,0x00,checksum)
            self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAdjust')



    def SetInput(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254): 
            checksum = 0x09 ^ DeviceID ^ GroupID ^ 0xAC ^ self.InputStateValues[value] ^ self.InputStateValues[value] ^ 1 ^ 0
            InputCmdString = pack('>BBBBBBBBB',9,DeviceID,GroupID,0xAC,self.InputStateValues[value], self.InputStateValues[value],1,0,checksum)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')
    def UpdateInput(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0xAD
            InputCmdString = pack('>BBBBB',5,DeviceID,GroupID,0xAD,checksum)
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = self.InputStateNames[res[5:6]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetPictureInPicture(self, value, qualifier):

        PictureInPictureStatus = {
            'Bottom Left'  : 0, 
            'Top Left'     : 1, 
            'Top Right'    : 2, 
            'Bottom Right' : 3
        }

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            if value == 'Off':
                checksum = 0x09 ^ DeviceID ^ GroupID ^ 0x3C ^ 0 ^ 0 ^ 0 ^ 0 
                PictureInPictureCmdString = pack('>BBBBBBBBB', 9, DeviceID, GroupID, 0x3C, 0, 0, 0, 0, checksum)
            else:
                checksum = 0x09 ^ DeviceID ^ GroupID ^ 0x3C ^ 1 ^ PictureInPictureStatus[value] ^ 0 ^ 0
                PictureInPictureCmdString = pack('>BBBBBBBBB', 9, DeviceID, GroupID, 0x3C, 1, PictureInPictureStatus[value], 0, 0, checksum)
            if PictureInPictureCmdString:
                self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPictureInPicture')
        else:
            self.Discard('Invalid Command for SetPictureInPicture')
    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPicturePositions = {
            b'\x00': 'Bottom Left',
            b'\x01': 'Top Left',
            b'\x02': 'Top Right',
            b'\x03': 'Bottom Right',
            b'\x04': 'Other'
        }

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x3D
            PictureInPictureCmdString = pack('>BBBBB', 5, DeviceID, GroupID, 0x3D, checksum)
            res = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
            if res:
                try:
                    value = PictureInPicturePositions[res[5:6]]
                    self.WriteStatus('PictureInPicture', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureInPicture')

    def SetPictureInPictureSource(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x07 ^ DeviceID ^ GroupID ^ 0x84 ^ 0xFD ^ self.PictureInPictureSourceValues[value]
            PictureInPictureSourceCmdString = pack('>BBBBBBB',7, DeviceID, GroupID, 0x84, 0xFD, self.PictureInPictureSourceValues[value], checksum)
            self.__SetHelper('PictureInPictureSource', PictureInPictureSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPictureSource')
    def UpdatePictureInPictureSource(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x85
            PictureInPictureSourceCmdString = pack('>BBBBB', 5, DeviceID, GroupID, 0x85, checksum)
            res = self.__UpdateHelper('PictureInPictureSource', PictureInPictureSourceCmdString, value, qualifier)
            if res:
                try:
                    value = self.PictureInPictureSourceNames[res[5:6]]
                    self.WriteStatus('PictureInPictureSource', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture in Picture Source: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureInPictureSource')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'Off': 1,
            'On' : 2
        }

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x06 ^ DeviceID ^ GroupID ^ 0x18 ^ PowerStateValues[value]
            PowerCmdString = pack('>BBBBBB',6,DeviceID,GroupID,0x18,PowerStateValues[value],checksum)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x02' : 'On', 
            b'\x01' : 'Off'
        }
        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x19
            PowerCmdString = pack('>BBBBB', 5, DeviceID, GroupID, 0x19, checksum)
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[4:5]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetVolume(self, value, qualifier):

        if qualifier['Type'] in ['Speaker Out', 'Audio Line Out']:
            DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
            GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
            if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254) and (0 <= value <= 100):
                if qualifier['Type'] == 'Speaker Out':
                    dataOne = value
                    dataTwo = 0xFF
                else:
                    dataTwo = value
                    dataOne = 0xFF

                checksum = 0x07 ^ DeviceID ^ GroupID ^ 0x44 ^ dataOne ^ dataTwo
                VolumeCmdString = pack('>BBBBBBB', 7, DeviceID, GroupID, 0x44, dataOne, dataTwo, checksum)
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetVolume')
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x45
            VolumeCmdString = pack('>BBBBB', 5, DeviceID, GroupID, 0x45, checksum)
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    if qualifier['Type'] == 'Speaker Out':
                        value = int(res[4])
                    else:
                        value = int(res[5])
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def SetVolumeSpeaker(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254) and (0 <= value <= 100):
            checksum = 0x06 ^ DeviceID ^ GroupID ^ 0x44 ^ value
            VolumeSpeakerCmdString = pack('>BBBBBB', 6, DeviceID, GroupID, 0x44, value, checksum)
            self.__SetHelper('VolumeSpeaker', VolumeSpeakerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeSpeaker')
    def UpdateVolumeSpeaker(self, value, qualifier):

        DeviceID = 0 if qualifier['Device ID'] == 'Broadcast' else int(qualifier['Device ID'])
        GroupID = 0 if qualifier['Group ID'] == 'Broadcast' else int(qualifier['Group ID'])
        if (0 <= DeviceID <= 255) and (0 <= GroupID <= 254):
            checksum = 0x05 ^ DeviceID ^ GroupID ^ 0x45
            VolumeSpeakerCmdString = pack('>BBBBB', 5, DeviceID, GroupID, 0x45, checksum)
            res = self.__UpdateHelper('VolumeSpeaker', VolumeSpeakerCmdString, value, qualifier)
            if res:
                try:

                    value = int(res[4])
                    self.WriteStatus('VolumeSpeaker', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolumeSpeaker')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Not Acknowledge',
            b'\x18': 'Not Available',
        }
        if response[4:5] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[4:5]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=6)
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or (qualifier['Device ID'] == 'Broadcast' and qualifier['Group ID'] == 'Broadcast'):
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
            return self.__CheckResponseForErrors(command , res)
           
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        

    def phil_10_265_QL(self):


        self.InputStateValues = {
            'HDMI'      : 13, 
            'DVI'       : 14, 
            'Component' : 3, 
            'Composite' : 1, 
            'VGA'       : 5,
            'USB'       : 12
        }
        
        self.PictureInPictureSourceValues = {
            'HDMI'      : 13,
            'DVI'       : 14,
            'Component' : 3,
            'Composite' : 1,
            'VGA'       : 5,
            'USB'       : 12,
        }
        
        self.InputStateNames = {
            b'\x0D' : 'HDMI', 
            b'\x0E' : 'DVI', 
            b'\x03' : 'Component', 
            b'\x01' : 'Composite', 
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        }
        self.PictureInPictureSourceNames = {
            b'\x0D' : 'HDMI', 
            b'\x0E' : 'DVI', 
            b'\x03' : 'Component', 
            b'\x01' : 'Composite', 
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        }

            
    def phil_10_265_QLTT(self):


        self.InputStateValues = {
            'HDMI 1'       : 13, 
            'HDMI 2'       : 6, 
            'DVI'          : 14, 
            'Display Port' : 10, 
            'Component'    : 3, 
            'Composite'    : 1, 
            'VGA'          : 5, 
            'USB'          : 12
            }
            
        self.PictureInPictureSourceValues = {
            'HDMI 1'       : 13,
            'HDMI 2'       : 6,
            'DVI'          : 14,
            'Component'    : 3,
            'Composite'    : 1,
            'Display Port' : 10,
            'VGA'          : 5,
            'USB'          : 12,
        }
        self.InputStateNames = {
            b'\x0D' : 'HDMI 1', 
            b'\x06' : 'HDMI 2', 
            b'\x0E' : 'DVI', 
            b'\x0A' : 'Display Port',
            b'\x03' : 'Component', 
            b'\x01' : 'Composite', 
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        }
        self.PictureInPictureSourceNames = {
            b'\x0D' : 'HDMI 1', 
            b'\x06' : 'HDMI 2', 
            b'\x0E' : 'DVI', 
            b'\x0A' : 'Display Port',
            b'\x03' : 'Component', 
            b'\x01' : 'Composite', 
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        }


    def phil_10_265_V(self):


        self.InputStateValues = {
            'HDMI'      	: 3,
            'DVI'       	: 14,
            'Display Port'  : 10,
            'Component' 	: 3,
            'VGA'       	: 5,
            'USB'       	: 12
            }
        self.PictureInPictureSourceValues = {
            'HDMI'         : 13,
            'DVI'          : 14,
            'Display Port' : 19,
            'Component'    : 3,
            'VGA'          : 5,
            'USB'          : 12,
        }
        self.InputStateNames = {
            b'\x0D' : 'HDMI', 
            b'\x0E' : 'DVI',
            b'\x0A' : 'Display Port', 
            b'\x03' : 'Component',  
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        }
        self.PictureInPictureSourceNames = {
            b'\x0D' : 'HDMI', 
            b'\x0E' : 'DVI',
            b'\x0A' : 'Display Port', 
            b'\x03' : 'Component',  
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB'
        } 
        

    def phil_10_265_QU(self):


        self.InputStateValues = {
            'DVI'       	: 14,
            'Display Port'  : 10,  
            'Component' 	: 3, 
            'VGA'       	: 5, 
            'USB'       	: 12,
            'HDMI 1'      	: 13, 
            'HDMI 2'      	: 6, 
            'HDMI 3'      	: 15,
            'Video'         : 1
        }
        
        self.InputStateNames = {
            b'\x0E' : 'DVI',
            b'\x0A' : 'Display Port', 
            b'\x03' : 'Component',  
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB',
            b'\x0D' : 'HDMI 1', 
            b'\x06' : 'HDMI 2', 
            b'\x0F' : 'HDMI 3', 
            b'\x01' : 'Video'
        }

        self.PictureInPictureSourceValues = {
            'HDMI 1'       : 13,
            'HDMI 2'       : 6,
            'HDMI 3'       : 15,
            'DVI'          : 14,
            'Display Port' : 10,
            'Component'    : 3,
            'VGA'          : 5,
            'USB'          : 12,
            'Video'         : 1
        }

        self.PictureInPictureSourceNames = {
            b'\x0D' : 'HDMI 1',
            b'\x06' : 'HDMI 2',
            b'\x0F' : 'HDMI 3', 
            b'\x0E' : 'DVI',
            b'\x0A' : 'Display Port', 
            b'\x03' : 'Component',  
            b'\x05' : 'VGA', 
            b'\x0C' : 'USB',
            b'\x01' : 'Video'
        } 

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
	# Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

