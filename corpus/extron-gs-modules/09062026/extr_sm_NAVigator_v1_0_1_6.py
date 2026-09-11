from extronlib.interface import SPInterface
from re import compile, search
from extronlib.system import Wait
from json import loads
import time

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 10000
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'NAVigator': self.extr_18_4118_NAVigator,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMuteDecoder': {'Parameters': ['ID', 'Type'], 'Status': {}},
            'AudioMuteEncoder': {'Parameters': ['ID'], 'Status': {}},
            'BitRateControl': {'Parameters': ['ID'], 'Status': {}},
            'CustomBorderVisibilityDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomBorderDurationDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomBorderColorDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDEncoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDDurationEncoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDDurationDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDLocationEncoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDLocationDecoder': {'Parameters': ['ID'], 'Status': {}},
            'CustomOSDTextEncoder': {'Parameters': ['ID', 'Row'], 'Status': {}},
            'CustomOSDTextDecoder': {'Parameters': ['ID', 'Row'], 'Status': {}},
            'CustomClearOSDTextEncoder': {'Parameters': ['ID', 'Row'], 'Status': {}},
            'CustomClearOSDTextDecoder': {'Parameters': ['ID', 'Row'], 'Status': {}},
            'DeviceConnectionStatusDecoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceConnectionStatusEncoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceLocationDecoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceLocationEncoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceNameDecoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceNameEncoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceTagsDecoder': {'Parameters': ['ID'], 'Status': {}},
            'DeviceTagsEncoder': {'Parameters': ['ID'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['ID'], 'Status': {}},
            'HDCPInputStatusDecoder': {'Parameters': ['ID'], 'Status': {}},
            'HDCPInputStatusEncoder': {'Parameters': ['ID'], 'Status': {}},
            'HDCPOutputStatusDecoder': {'Parameters': ['ID'], 'Status': {}},
            'HDCPOutputStatusEncoder': {'Parameters': ['ID'], 'Status': {}},
            'HotkeySequenceDetectionDecoder': {'Parameters': ['ID', 'Modifier'], 'Status': {}},
            'InputPresetRecallDecoder': {'Parameters': ['ID'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['ID'], 'Status': {}},
            'InputSwitchtoWindow': {'Parameters': ['Canvas', 'Window'], 'Status': {}},
            'LLDPStatusOOBLAN': {'Parameters': ['Data Type'], 'Status': {}},
            'LLDPStatusNAVLAN': {'Parameters': ['Data Type'], 'Status': {}},
            'LLDPStatusDecoder': {'Parameters':  ['ID', 'Data Type'], 'Status': {}},
            'LLDPStatusEthExtDecoder': {'Parameters':  ['ID', 'Data Type'], 'Status': {}},
            'LLDPStatusEncoder': {'Parameters':  ['ID', 'Data Type'], 'Status': {}},
            'LLDPStatusEthExtEncoder': {'Parameters':  ['ID', 'Data Type'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters':['Type'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters':['Type','Number'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters':['Output','Tie Type'], 'Status': {}},
            'PartNumber': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'USBDeviceTieStatus': {'Parameters': ['Device I/O Number', 'Device Type', 'Host Type'], 'Status': {}},
            'USBMatrixTieCommand': {'Parameters': ['Device I/O Number', 'Device Type', 'Host I/O Number', 'Host Type'], 'Status': {}},
            'VideoMuteDecoder': {'Parameters': ['ID'], 'Status': {}},
            'VideoMuteEncoder': {'Parameters': ['ID'], 'Status': {}},
            'VideoWallPresetRecall': {'Parameters': ['Canvas'], 'Status': {}},
            'Volume': {'Parameters': ['ID'], 'Status': {}},
            'WindowMute': {'Parameters': ['Canvas', 'Window'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.InputList = []
        self.OutputList = []

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Amt([0-2])\*([0-1])\r\n'), self.__MatchAudioMuteDecoder, 'Set')
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Amt([0-1])\r\n'), self.__MatchAudioMuteDecoder, 'SetAll')
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Amt([0-1]) ([0-1])'), self.__MatchAudioMuteDecoder, 'Update')
            self.AddMatchString(compile(b'\{(\d{1,4})i\}Amt1\*([0-1])'), self.__MatchAudioMuteEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}Amt([0-1])'), self.__MatchAudioMuteEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}BitrV([0-9]{1,5})\r\n'), self.__MatchBitRateControl, None)
            self.AddMatchString(compile(b'\{(\d{1,4})([io])\}Dtag (\{"tags":\[[A-Za-z0-9-\, "]+\]\})\r\n'), self.__MatchDeviceTags, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}HdcpE(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'Output\t InVid\t InAud\r\n   ([0-9- ]{4}\t  [0-9- ]{4}\t  [0-9- ]{4}\r\n {0,3})+\r\n'), self.__MatchAllMatrixTie, None)
            self.AddMatchString(compile(b'Out(\d{4}) In([0-9]{1,4}) (All|Vid|Aud)\r\n'), self.__MatchAllMatrixTie, 'Individual')
            self.AddMatchString(compile(b'Device\tHost\r\n([0-9- io]{2,5}\t[0-9- io]{2,5}\r\n)+\r\n'), self.__MatchUSBMatrixTie, None)
            self.AddMatchString(compile(b'Out(\d{4})([io]) In([0-9]{1,4})([io]) Usb\r\n'), self.__MatchUSBMatrixTie, 'Individual')
            self.AddMatchString(compile(b'\{(\d{1,4})([io])\}In([0-9]{1,4})([io]) Usb\r\n'), self.__MatchUSBMatrixTie, 'Individual')
            self.AddMatchString(compile(b'\{(\d{1,4})o\}HdcpI([0-2])\r\n'), self.__MatchHDCPInputStatusDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}HdcpI([0-2])\r\n'), self.__MatchHDCPInputStatusEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatusEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatusDecoder, None)
            self.AddMatchString(compile(b'Rprt\*Inventory\*I\*([0-9]{4096})\r\n'), self.__MatchInputInventory, 'Individual')
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Hkdm(P|K)(\d{1,2}|[A-Z])\r\n'), self.__MatchHotkeySequenceDetectionDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}In00 ([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Grp(\d+) Win(\d+) In(\d+)\r\n'), self.__MatchInputSwitchtoWindow, None)
            self.AddMatchString(compile(b'(\{(\d{1,4})(i|o)\}){0,1}(6[01])Stat ({.*})\r\n'), self.__MatchLLDPStatus, None)
            self.AddMatchString(compile(b'Rprt\*Inventory\*O\*([0-9]{4096})\r\n'), self.__MatchOutputInventory, 'Individual')
            self.AddMatchString(compile(b'\{(\d{4})o\}In([0-9]{1,4}) (All|Vid|Aud)\r\n'), self.__MatchAllMatrixTie, 'Individual')
            self.AddMatchString(compile(b'\{(\d{4})o\}In([0-9]{1,4}) Aud\nIn([0-9]{1,4}) Vid\r\n'), self.__MatchAllMatrixTie, 'WebInterface')
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Vmt([0-2])\r\n'), self.__MatchVideoMuteDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}Vmt([0-2])\r\n'), self.__MatchVideoMuteEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Vol\+{0,1}([0-9]{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}VidI([0-1])\*HdcpI([0-2])\*HdcpO([0-2])\*ResI[0-9]{1,4}x[0-9]{1,4}@[0-9.]{1,5}\*AudI([0-1])\*StrmI[0-2]\*Lnk[0-2]\*Dec\r\n'), self.__MatchDecoderInfo, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}SigI([0-1])\*HdcpI([0-2])\*HdcpO([0-2])\*ResI([0-9]{1,4}x[0-9]{1,4}@[0-9.]{1,5}|NOT DETECTED)\*AudI([0-1])\*StrmI[0-2]\*Lnk[0-2]\*Enc\r\n'), self.__MatchEncoder2Info, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}Inf35\*([0-2])\r\n'), self.__MatchEncoderInfo, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}Inf35\*([0-2])\r\n'), self.__MatchDecoder2Info, None)
            self.AddMatchString(compile(b'DevpC\*(\d{1,4})(i|o)\*([0-1])'), self.__MatchConnection, None)
            #self.AddMatchString(compile(b'DevpA\*(\d{1,4})(i|o)\*([0-1])'), self.__MatchConnection, None)
            self.AddMatchString(compile(b'Pno60-1534-01\r\n'), self.__MatchPartNumber, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwV1\*([0-1])\r\n'), self.__MatchCustomBorderVisibilityDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwD1\*(\d{1,3})\r\n'), self.__MatchCustomBorderDurationDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwB1\*([1-7])\r\n'), self.__MatchCustomBorderColorDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}WndwV4\*([0-1])\r\n'), self.__MatchCustomOSDEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}WndwD4\*(\d{1,3})\r\n'), self.__MatchCustomOSDDurationEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}WndwL4\*([0-4])\r\n'), self.__MatchCustomOSDLocationEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})i\}TextT4\*([1-2])\*([\w|\W]{0,})\r\n'), self.__MatchCustomOSDTextEncoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwV4\*([0-1])\r\n'), self.__MatchCustomOSDDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwD4\*(\d{1,3})\r\n'), self.__MatchCustomOSDDurationDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}WndwL4\*([0-4])\r\n'), self.__MatchCustomOSDLocationDecoder, None)
            self.AddMatchString(compile(b'\{(\d{1,4})o\}TextT4\*([1-2])\*([\w|\W]{0,})\r\n'), self.__MatchCustomOSDTextDecoder, None)
            self.AddMatchString(compile(b'Vmt(0[0-8])\*([0-6][0-4])\*([0-1])\r\n'), self.__MatchWindowMute, None)
            self.AddMatchString(compile(b'\[\{(.|\r\n)*\]\}\]\r\n'), self.__MatchJInventory, None)
            self.AddMatchString(compile(b'\{(\d{1,4})(i|o)\}Ipn ([a-zA-z0-9-]+)\r\n'), self.__MatchDeviceName, None)
            self.AddMatchString(compile(b'E(10|12|13|14|17|22|24|25|28)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'PrstR1\*(\d+)\*(\d+)\r\n'), self.__MatchVideoWallPresetRecall, None)
            self.AddMatchString(compile(b'PrstL1\*(\d+)\*(\d+)\r\n'), self.__MatchVideoWallPresetRecall, None)
            self.AddMatchString(compile(b'Nm([io])(\d+),([ \S]{0,48})\r\n'), self.__MatchMatrixIONameStatus, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchPartNumber(self, match, qualifer):
        self.WriteStatus('PartNumber', '60-1534-01')

    def UpdateAllMatrixTie(self, value, qualifier):
        self.__UpdateHelper('RefreshMatrix', 'wInventory*I*RPRT\r\n', None, None)
        self.__UpdateHelper('RefreshMatrix', 'wInventory*O*RPRT\r\n', None, None)
        self.__UpdateHelper('RefreshMatrix', 'wInventory*J*RPRT\r\n', None, None)
        self.__UpdateHelper('RefreshMatrix', 'wTies*A*RPRT\r\n', None, None)
        self.__UpdateHelper('RefreshMatrix', 'wTies*U*RPRT\r\n', None, None)

    def __NormalizeDeviceType(self, model):
        # Remove last character
        model = model[:-1]
        # Remove Key words and letters that arent needed
        for item in ['NAV', 'DT', 'DTP', 'S']:
            model = model.replace(item, '')
        # Remove Digits and space
        model = ''.join([x for x in model if x.isalpha()])

        return {'E':'Encoder', 'D':'Decoder'}[model]

    def __MatchDeviceName(self, match, tag):
        if match.group(2).decode() == 'o':
            self.WriteStatus('DeviceNameDecoder', 
                              match.group(3).decode(), 
                              {'ID': int(match.group(1).decode())})
        elif match.group(2).decode() == 'i':
            self.WriteStatus('DeviceNameEncoder', 
                              match.group(3).decode(), 
                              {'ID': int(match.group(1).decode())})
    def __MatchJInventory(self, match, tag):
        deviceInfo = str(match.group(0).decode()).replace('\r\n', '')
        deviceInfo = loads(deviceInfo)

        for device in deviceInfo:
            device_type = self.__NormalizeDeviceType(device['model'])
            # Write DeviceName
            self.WriteStatus({'Encoder': 'DeviceNameEncoder',
                              'Decoder': 'DeviceNameDecoder'}[device_type], 
                              device['name'], 
                              {'ID': device['channel']})
            # Write DeviceTags
            tags = ', '.join(x for x in device['tags'])
            self.WriteStatus({'Encoder': 'DeviceTagsEncoder',
                              'Decoder': 'DeviceTagsDecoder'}[device_type], 
                              tags, 
                              {'ID': device['channel']})
            # Write device Location
            self.WriteStatus({'Encoder': 'DeviceLocationEncoder',
                              'Decoder': 'DeviceLocationDecoder'}[device_type], 
                              device['location'], 
                              {'ID': device['channel']})

    def __MatchInputInventory(self, match, tag):
        """
            Input Inventory Status handler
        """
        lst = list(match.group(1).decode())
        for key, input in enumerate(lst):
            if input == '1': #and (int(key+1)) not in self.InputList:
                self.WriteStatus('DeviceConnectionStatusEncoder', 'Connected', {'ID': int(key+1)})
                if (int(key+1)) not in self.InputList:
                    self.InputList.append(int(key+1))
            elif input == '2':
                self.WriteStatus('DeviceConnectionStatusEncoder', 'Disconnected', {'ID': int(key+1)})

    def __MatchOutputInventory(self, match, tag):
        """
            Output Inventory Status handler
        """
        lst = list(match.group(1).decode())
        for key, input in enumerate(lst):
            if input == '1': #and (int(key+1)) not in self.OutputList:
                self.WriteStatus('DeviceConnectionStatusDecoder', 'Connected', {'ID': int(key+1)})
                if (int(key+1)) not in self.OutputList:
                    self.OutputList.append(int(key+1))
            elif input == '2':
                self.WriteStatus('DeviceConnectionStatusDecoder', 'Disconnected', {'ID': int(key+1)})
                
    def __MatchConnection(self, match, tag):
        id = match.group(1).decode()
        type = match.group(2).decode()
        state = match.group(3).decode()
        if type == 'i':
            if state == '1':
                if int(id) not in self.InputList:
                    self.InputList.append(int(id))
                    self.WriteStatus('DeviceConnectionStatusEncoder', 'Connected', {'ID': int(id)})
            elif state == '0':
                if int(id) in self.InputList:
                    self.InputList.remove(int(id))
                    self.WriteStatus('DeviceConnectionStatusEncoder', 'Disconnected', {'ID': int(id)})
        elif type == 'o':
            if state == '1':
                if int(id) not in self.OutputList:
                    self.OutputList.append(int(id))
                    self.WriteStatus('DeviceConnectionStatusDecoder', 'Connected', {'ID': int(id)})
            elif state == '0':
                if int(id) in self.OutputList:
                    self.OutputList.remove(int(id))
                    self.WriteStatus('DeviceConnectionStatusDecoder', 'Disconnected', {'ID': int(id)})

    def __MatchAllMatrixTie(self, match, tag):
        """
            Initial Matrix Tie Status handler
        """
        
        Audio = False
        Video = False
        AV = False
        if tag == 'Individual' or tag == 'WebInterface':
            Output = int(match.group(1))
            OldAud = self.ReadStatus('OutputTieStatus', {'Output': Output, 'Tie Type': 'Audio'})
            OldVid = self.ReadStatus('OutputTieStatus', {'Output': Output, 'Tie Type': 'Video'})
            OldAV = self.ReadStatus('OutputTieStatus', {'Output': Output, 'Tie Type': 'Audio/Video'})
            current = None
            if OldAV != 0:
                current = 'Audio/Video'
            elif OldAud != 0:
                current = 'Audio'
            elif OldVid != 0:
                current = 'Video'
            if tag == 'Individual':
                Input = int(match.group(2))
                inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': Input})
                Type = match.group(3).decode()
                if Input == 0:
                    if Type == 'Aud':
                        if current == 'Audio':
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                        else:
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                    elif Type == 'Vid':
                        if current == 'Video':
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                        else:
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                    elif Type == 'All':
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                elif Input != 0:
                    if Type == 'Vid':
                        if current == 'Audio':
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        else:
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Video'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Video'})
                    elif Type == 'Aud':
                        if current == 'Video':
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        else:
                            self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio'})
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio'})
                    else:
                        self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatus', Input, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio/Video'})
                            
            elif tag == 'WebInterface':
                AudInput = int(match.group(2))
                VidInput = int(match.group(3))
                inputNameAud = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': AudInput})
                inputNameVid = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': VidInput})
                if AudInput == 0:
                    self.WriteStatus('OutputTieStatus', VidInput, {'Output': Output, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Audio'})
                    self.WriteStatus('OutputTieStatusName', inputNameVid, {'Output': Output, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                elif VidInput == 0:
                    self.WriteStatus('OutputTieStatus', 0, {'Output': Output, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatus', AudInput, {'Output': Output, 'Tie Type': 'Audio'})
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                    self.WriteStatus('OutputTieStatusName', inputNameAud, {'Output': Output, 'Tie Type': 'Audio'})

        else:
            tielist = match.group(0)
            stripstring = tielist[24:-2].decode()
            removespaces = stripstring.replace(' ', '')
            splitoutputs = removespaces.strip('\r\n').split('\r\n')

            for items in splitoutputs:
                Audio = False
                Video = False
                items = items.split('\t')
                Output = int(items[0])
                try:
                    inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': int(items[1])})
                except ValueError:
                    inputName = None
                try:
                    inputName2 = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': int(items[2])})
                except ValueError:
                    inputName2 = None

                if items[1] == items[2]:
                    if items[1] == '----':
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                    else:
                        self.WriteStatus('OutputTieStatus',int(items[1]), {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',int(items[1]), {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatus',int(items[1]), {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Audio/Video'})
                else:
                    if items[1] == '----':
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                    else:
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',int(items[1]), {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': Output, 'Tie Type': 'Video'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                        Video = True
                    if items[2] == '----':
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                    else:
                        self.WriteStatus('OutputTieStatus',0, {'Output': Output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatus',int(items[2]), {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', inputName2, {'Output': Output, 'Tie Type': 'Audio'})
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': Output, 'Tie Type': 'Audio/Video'})
                        Audio = True
                        
    def __MatchUSBMatrixTie(self, match, tag):
        """
            Initial Matrix Tie Status handler
        """
        if tag == 'Individual':
            numlookup = {
                'i': 'Input',
                'o': 'Output'
            }
            devicenum = int(match.group(1).decode())
            devicetype = match.group(2).decode()
            hostnum = int(match.group(3).decode())
            hosttype = match.group(4).decode()
            self.WriteStatus('USBDeviceTieStatus', hostnum, {'Device I/O Number': devicenum, 'Device Type': numlookup[devicetype], 'Host Type': numlookup[hosttype]})
            self.WriteStatus('USBDeviceTieStatus', 0, {'Device I/O Number': devicenum, 'Device Type': devicetype, 'Host Type': 'Output' if hosttype == 'Input' else 'Input'})
        else:
            tielist = match.group(0)
            stripstring = tielist[13:].decode()
            splitoutputs = stripstring.strip('\r\n').split('\r\n')
            for items in splitoutputs:
                Audio = False
                Video = False
                items = items.split('\t')
                device = items[0]
                host = items[1]
                devicetype = ''
                hosttype = ''
                if 'i' in device:
                    devicetype = 'Input'
                elif 'o' in device:
                    devicetype = 'Output'
                if '-----' not in host:
                    hostnum = int(host[:-1])
                    if 'i' in host:
                        hosttype = 'Input'
                    elif 'o' in host:
                        hosttype = 'Output'
                devicenum = int(device[:-1])
                
                
                if items[1] == '-----':
                    self.WriteStatus('USBDeviceTieStatus', 0, {'Device I/O Number': devicenum, 'Device Type': devicetype, 'Host Type': 'Input'})
                    self.WriteStatus('USBDeviceTieStatus', 0, {'Device I/O Number': devicenum, 'Device Type': devicetype, 'Host Type': 'Output'})
                else:
                    self.WriteStatus('USBDeviceTieStatus', hostnum, {'Device I/O Number': devicenum, 'Device Type': devicetype, 'Host Type': hosttype})
                    self.WriteStatus('USBDeviceTieStatus', 0, {'Device I/O Number': devicenum, 'Device Type': devicetype, 'Host Type': 'Output' if hosttype == 'Input' else 'Input'})
    
    def __MatchDecoderInfo(self, match, tag):

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusDecoder', HDCPStatusState[match.group(3).decode()], {'ID': int(match.group(1).decode())})
        self.WriteStatus('HDCPOutputStatusDecoder', HDCPStatusState[match.group(4).decode()], {'ID': int(match.group(1).decode())})

    def __MatchDecoder2Info(self, match, tag):
        """
        Processes the capture verbose mode setting response.
        """
        #the first time device response should be this function

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusDecoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def __MatchEncoderInfo(self, match, qualifier):
        """
        Processes the capture verbose mode setting response.
        """
        #the first time device response should be this function
        DeviceTypeState = {
            'i': 'Encoder',
            'o': 'Decoder'
            }

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusEncoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def __MatchEncoder2Info(self, match, qualifier):
        """
        Processes the capture verbose mode setting response.
        """
        #the first time device response should be this function

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusEncoder', HDCPStatusState[match.group(3).decode()], {'ID': int(match.group(1).decode())})
        self.WriteStatus('HDCPOutputStatusEncoder', HDCPStatusState[match.group(4).decode()], {'ID': int(match.group(1).decode())})
    
    def SetAudioMuteDecoder(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        TypeState = {
            'HDMI': '1',
            'Analog': '2',
            'All': '3'
        }
        
        channel = int(qualifier['ID'])
        type = qualifier['Type']
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            if type == 'All':
                self.__SetHelper('AudioMuteDecoder', '{{{0}o:{1}Z\r}}\r'.format(channel, AudioMuteState[value]), value, qualifier)
            else:
                self.__SetHelper('AudioMuteDecoder', '{{{0}o:{1}*{2}Z\r}}\r'.format(channel, TypeState[type], AudioMuteState[value]), value, qualifier)

    def UpdateAudioMuteDecoder(self, value, qualifier):
        TypeState = {
            'HDMI': '1',
            'Analog': '2',
        }

        channel = int(qualifier['ID'])
        type = qualifier['Type']
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            self.__UpdateHelper('AudioMuteDecoder', '{{{0}o:Z\r}}\r'.format(channel), value, qualifier)

    def __MatchAudioMuteDecoder(self, match, tag):
        
        AudioMuteName = {
            '1': 'On',
            '0': 'Off',
        }
        
        output = int(match.group(1).decode())
        if tag == 'SetAll':
            mutestate = AudioMuteName[match.group(2).decode()]
            self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': 'HDMI'})
            self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': 'Analog'})
            self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': 'All'})
        elif tag == 'Update':
            hdmi = AudioMuteName[match.group(2).decode()]
            analog = AudioMuteName[match.group(3).decode()]
            self.WriteStatus('AudioMuteDecoder', hdmi, {'ID': output, 'Type': 'HDMI'})
            self.WriteStatus('AudioMuteDecoder', analog, {'ID': output, 'Type': 'Analog'})
        else:
            TypeState = {
            '1': 'HDMI',
            '2': 'Analog',
            '3': 'All'
            }
            type = TypeState[match.group(2).decode()]
            mutestate = AudioMuteName[match.group(3).decode()]
            self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': type})
            otherstate = None
            if type == 'HDMI':
                otherstate = self.ReadStatus('AudioMuteDecoder', {'ID': output, 'Type': 'Analog'})
                if otherstate == mutestate:
                    self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': 'All'})
                else:
                    self.WriteStatus('AudioMuteDecoder', 'Off', {'ID': output, 'Type': 'All'})
            elif type == 'Analog':
                otherstate = self.ReadStatus('AudioMuteDecoder', {'ID': output, 'Type': 'HDMI'})
                if otherstate == mutestate:
                    self.WriteStatus('AudioMuteDecoder', mutestate, {'ID': output, 'Type': 'All'})
                else:
                    self.WriteStatus('AudioMuteDecoder', 'Off', {'ID': output, 'Type': 'All'})

    def SetAudioMuteEncoder(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        
        channel = int(qualifier['ID'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMuteEncoder')
        else:
            self.__SetHelper('AudioMuteEncoder', '{{{0}i:1*{1}Z\r}}\r'.format(channel, AudioMuteState[value]), value, qualifier)

    def UpdateAudioMuteEncoder(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateAudioMuteEncoder')
        else:
            self.__UpdateHelper('AudioMuteEncoder', '{{{0}i:Z\r}}\r'.format(channel), value, qualifier)

    def __MatchAudioMuteEncoder(self, match, tag):
        
        AudioMuteName = {
            '1': 'On',
            '0': 'Off',
        }
        
        input = int(match.group(1).decode())
        self.WriteStatus('AudioMuteEncoder', AudioMuteName[match.group(2).decode()], {'ID': input})

    # Begin BitRateControl, pg. 72
    def SetBitRateControl(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetBitRateControl')
        elif value < 150 or value > 900:
            self.Discard('Invalid Command for SetBitRateControl')
        else:
            self.__SetHelper('BitRateControl', '{{{0}i:wV{1}BITR\r}}\r'.format(channel, value), value, qualifier)

    def UpdateBitRateControl(self, value, qualifier):
        """Update Bit Rate Control
        value: None
        qualifier: {'ID': integer, 'Device Type': enum},

        """

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('BitRateControl', '{{{0}i:wVBITR\r}}\r'.format(channel), value, qualifier)

    def __MatchBitRateControl(self, match, qualifier):
        """Bit Rate Control MatchString Handler

        """

        output = int(match.group(1).decode())
        bitratestate = int(match.group(2).decode())
        self.WriteStatus('BitRateControl', bitratestate, {'ID': output})
    
    def __MatchDeviceTags(self, match, qualifier):
        """Device Tags MatchString Handler

        """

        output = int(match.group(1).decode())
        _type = match.group(2).decode()
        string = match.group(3).decode()
        string = loads(string)
        text = ''
        for strings in string['tags']:
            if text:
                text = text + ', ' + strings
            else:
                text = text + strings            
        if _type == 'o':
            self.WriteStatus('DeviceTagsDecoder', text, {'ID': output})
        elif _type == 'i':
            self.WriteStatus('DeviceTagsEncoder', text, {'ID': output})
        
    def SetCustomBorderVisibilityDecoder(self, value, qualifier):
        BorderState = {
            'Visible': 1,
            'Hidden': 0
        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomBorderVisibilityDecoder')
        else:
            self.__SetHelper('CustomBorderVisibilityDecoder', '{{{0}o:wV1*{1}WNDW\r}}\r'.format(channel, BorderState[value]), value, qualifier)

    def UpdateCustomBorderVisibilityDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomBorderVisibilityDecoder', '{{{0}o:wV1WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomBorderVisibilityDecoder(self, match, qualifier):
        BorderState = {
            1:'Visible',
            0:'Hidden'
        }
        output = int(match.group(1).decode())

        self.WriteStatus('CustomBorderVisibilityDecoder', BorderState[int(match.group(2).decode())], {'ID': output})

    def SetCustomBorderDurationDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomBorderDurationDecoder')
        else:
            if 0 < int(value) <= 501:
                self.__SetHelper('CustomBorderDurationDecoder', '{{{0}o:wD1*{1}WNDW\r}}\r'.format(channel, value), value, qualifier)
            else:
                self.Discard('Invalid Value for SetCustomBorderDurationDecoder')

    def UpdateCustomBorderDurationDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomBorderDurationDecoder', '{{{0}o:wD1WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomBorderDurationDecoder(self, match, qualifier):

        output = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('CustomBorderDurationDecoder', value, {'ID': output})

    def SetCustomBorderColorDecoder(self, value, qualifier):

        CustomBorderColorDecoder = {'Yellow': 1,
                       'Orange': 2,
                       'Red': 3,
                       'Blue': 4,
                       'Green': 5,
                       'Magenta': 6,
                       'Teal': 7,
                       'White': 8,
                       'Black': 9
                        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomBorderColorDecoder')
        else:
            if value in CustomBorderColorDecoder:
                self.__SetHelper('CustomBorderColorDecoder', '{{{0}o:wB1*{1}WNDW\r}}\r'.format(channel, CustomBorderColorDecoder[value]), value, qualifier)
            else:
                self.Discard('Invalid Value for SetCustomBorderColorDecoder')

    def UpdateCustomBorderColorDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomBorderColorDecoder', '{{{0}o:wB1WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomBorderColorDecoder(self, match, qualifier):
        output = int(match.group(1).decode())
        value = int(match.group(2).decode())
        CustomBorderColorDecoder = {1: 'Yellow',
                       2: 'Orange',
                       3: 'Red',
                       4: 'Blue',
                       5: 'Green',
                       6: 'Magenta',
                       7: 'Teal',
                       8: 'White',
                       9: 'Black'
                    }
        
        self.WriteStatus('CustomBorderColorDecoder', CustomBorderColorDecoder[value], {'ID': output})

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }
        
        channel = int(qualifier['ID'])
        
        if channel < 0 or channel > self.InputSize:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')
        else:
            self.__SetHelper('HDCPInputAuthorization', '{{{0}i:\x1bE{1}HDCP\r}}\r'.format(channel, ValueStateValues[value]), value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        channel = int(qualifier['ID'])

        if channel < 0 or channel > self.InputSize:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')
        else:
            self.__UpdateHelper('HDCPInputAuthorization', '{{{0}i:\x1bEHDCP\r}}\r'.format(channel), value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, qualifier):
        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }
        
        input = int(match.group(1).decode())
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'ID': input})
        
    def UpdateHDCPInputStatusDecoder(self, value, qualifier):

        input = int(qualifier['ID'])

        if input < 0 or input > self.InputSize:
            self.Discard('Invalid Command for UpdateHDCPInputStatusDecoder')
        else:
            self.__UpdateHelper('HDCPInputStatusDecoder', '{{{0}o:35i\r}}\r'.format(input), value, qualifier)

    def __MatchHDCPInputStatusDecoder(self, match, tag):
        """Input HDCP Input Status Decoder Handler

        """

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusDecoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def UpdateHDCPInputStatusEncoder(self, value, qualifier):

        input = int(qualifier['ID'])

        if input < 0 or input > self.InputSize:
            self.Discard('Invalid Command for UpdateHDCPInputStatusEncoder')
        else:
            self.__UpdateHelper('HDCPInputStatusEncoder', '{{{0}i:35i\r}}\r'.format(input), value, qualifier)

    def __MatchHDCPInputStatusEncoder(self, match, tag):
        """Input HDCP Input Status Encoder Handler

        """

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPInputStatusEncoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})
            
    def UpdateHDCPOutputStatusDecoder(self, value, qualifier):

        output = int(qualifier['ID'])

        if output < 0 or output > self.OutputSize:
            self.Discard('Invalid Command for UpdateHDCPOutputStatusDecoder')
        else:
            self.__UpdateHelper('HDCPOutputStatusDecoder', '{{{0}o:i\r}}\r'.format(output), value, qualifier)

    def __MatchHDCPOutputStatusDecoder(self, match, tag):
        """Input HDCP Input Status Decoder Handler

        """

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPOutputStatusDecoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def UpdateHDCPOutputStatusEncoder(self, value, qualifier):

        output = int(qualifier['ID'])

        if output < 0 or output > self.OutputSize:
            self.Discard('Invalid Command for UpdateHDCPOutputStatusncoder')
        else:
            self.__UpdateHelper('HDCPOutputStatusEncoder', '{{{0}i:i\r}}\r'.format(output), value, qualifier)

    def __MatchHDCPOutputStatusEncoder(self, match, tag):
        """Input HDCP Input Status Encoder Handler

        """

        HDCPStatusState = {
            '0': 'No Device',
            '1': 'Non HDCP Device',
            '2': 'HDCP Device',
            }

        self.WriteStatus('HDCPOutputStatusEncoder', HDCPStatusState[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def __MatchHotkeySequenceDetectionDecoder(self, match, tag):
        
        TypeState = {
            'P': 'Ctrl, Ctrl',
            'K': 'Ctrl, Shift',
        }

        output = int(match.group(1).decode())
        self.WriteStatus('HotkeySequenceDetectionDecoder', match.group(3).decode(), {'ID': output, 'Modifier': TypeState[match.group(2).decode()]})
        @Wait(1)
        def senstat():
            self.WriteStatus('HotkeySequenceDetectionDecoder', 'Waiting for sequence', {'ID': output, 'Modifier': TypeState[match.group(2).decode()]})

    def SetInputPresetRecallDecoder(self, value, qualifier):
        
        channel = int(qualifier['ID'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            self.__SetHelper('InputPresetRecallDecoder', '{{{0}o:\x1bR2*{1}PRST\r}}\r'.format(channel, value.zfill(2)), value, qualifier)


    def UpdateInputSignalStatus(self, value, qualifier):

        channel = int(qualifier['ID'])

        if channel < 0 or channel > self.InputSize:
            self.Discard('Invalid Command for UpdateInputSignalStatus')
        else:
            self.__UpdateHelper('InputSignalStatus', '{{{0}i:\x1b0LS\r}}\r'.format(channel), value, qualifier)
            
    def __MatchInputSignalStatus(self, match, qualifier):
        InputList = match.group(2).decode()
        inputVal = int(match.group(1).decode())
        value = 'Not Active' if InputList == '0' else 'Active'
        self.WriteStatus('InputSignalStatus', value, {'ID': inputVal})

    def SetInputSwitchtoWindow(self, value, qualifier):

        Canvas = int(qualifier['Canvas'])
        Window = int(qualifier['Window'])
        value = int(value)

        if Canvas < 0 or Canvas > 8:
            self.Discard('Invalid Command for InputSwitchtoWindow')
        elif Window < 0 or Window > 64:
            self.Discard('Invalid Command for InputSwitchtoWindow')
        elif value < 1 or value > 4096:
            self.Discard('Invalid Command for InputSwitchtoWindow')
        else:
            InputSwitchtoWindowCmdString = '\x1B{0}*{1}*{2}!X\r'.format(Canvas, Window, value)
            self.__SetHelper('InputSwitchtoWindow', InputSwitchtoWindowCmdString, value, qualifier)

    def UpdateInputSwitchtoWindow(self, value, qualifier):
        Canvas = int(qualifier['Canvas'])
        Window = int(qualifier['Window'])
        if Canvas < 0 or Canvas > 8:
            self.Discard('Invalid Command for InputSwitchtoWindow')
        elif Window < 0 or Window > 64:
            self.Discard('Invalid Command for InputSwitchtoWindow')
        else:
            self.__UpdateHelper('InputSwitchtoWindow', '\x1B{0}*{1}!X\r'.format(Canvas, Window), value, qualifier)

    def __MatchInputSwitchtoWindow(self, match, qualifier):
        Window = str(int(match.group(2).decode()))
        Canvas = str(int(match.group(1).decode()))
        value = int(match.group(3).decode())
        self.WriteStatus('InputSwitchtoWindow', value, {'Canvas': Canvas, 'Window': Window})

    def UpdateLLDPStatusNAVLAN(self, value, qualifier):
        self.__UpdateHelper('LLDPStatusNAVLAN', '\x1b60STAT\r', value, qualifier)
     
    def UpdateLLDPStatusOOBLAN(self, value, qualifier):
        self.__UpdateHelper('LLDPStatusOOBLAN', '\x1b61STAT\r', value, qualifier)
        
    def UpdateLLDPStatusDecoder(self, value, qualifier):
    
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('LLDPStatusDecoder', '{{{0}o:\x1b60STAT\r}}\r'.format(channel), value, qualifier)
                
    def UpdateLLDPStatusEthExtDecoder(self, value, qualifier):
    
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('LLDPStatusEthExtDecoder', '{{{0}o:\x1b61STAT\r}}\r'.format(channel), value, qualifier)
        
    def UpdateLLDPStatusEncoder(self, value, qualifier):
    
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('LLDPStatusEncoder', '{{{0}i:\x1b60STAT\r}}\r'.format(channel), value, qualifier)
        
    def __MatchLLDPStatus(self, match, qualifier):
        LANtype = match.group(4).decode()
        value = match.group(5).decode()
        test = loads(value)
        try:
            name = test['neighbors'][0]['System Name']
        except (KeyError, IndexError):
            name = 'N/A'
        try:
            managementaddress = test['neighbors'][0]['Management Address']
        except (KeyError, IndexError):
            managementaddress = 'N/A'
        try:
            PortID = test['neighbors'][0]['Port ID']
        except (KeyError, IndexError):
            PortID = 'N/A'
        try:
            SystemDescription = test['neighbors'][0]['System Description']
        except (KeyError, IndexError):
            SystemDescription = 'N/A'
        try:
            PortVLANID = test['neighbors'][0]['Port VLAN ID']
        except (KeyError, IndexError):
            PortVLANID = 'N/A'
        try:
            ChassisID = test['neighbors'][0]['Chassis ID']
        except (KeyError, IndexError):
            ChassisID = 'N/A'
        try:
            PortDescription = test['neighbors'][0]['Port Description']
        except (KeyError, IndexError):
            PortDescription = 'N/A'
        try:
            SystemCapabilities = test['neighbors'][0]['System Capabilities']
        except (KeyError, IndexError):
            SystemCapabilities = 'N/A'
        try:
            TimetoLive = test['neighbors'][0]['Time to live']
        except (KeyError, IndexError):
            TimetoLive = 'N/A'
        if match.group(1):
            _input = int(match.group(2).decode())
            _type = match.group(3).decode()
            
            if _type == 'i':
                namedict = {
                    '60': 'LLDPStatusEncoder',
                    '61': 'LLDPStatusEthExtEncoder'
                
                }
                cmdname = namedict[LANtype]

            elif _type == 'o':
                namedict = {
                    '60': 'LLDPStatusDecoder',
                    '61': 'LLDPStatusEthExtDecoder'   
                }
                cmdname = namedict[LANtype]
            try:
                self.WriteStatus(cmdname, name, {'ID': _input, 'Data Type': 'System Name'})
                self.WriteStatus(cmdname, managementaddress, {'ID': _input, 'Data Type': 'Management Address'})
                self.WriteStatus(cmdname, PortID, {'ID': _input, 'Data Type': 'Port ID'})
                self.WriteStatus(cmdname, SystemDescription, {'ID': _input, 'Data Type': 'System Description'})
                self.WriteStatus(cmdname, PortVLANID, {'ID': _input, 'Data Type': 'Port VLAN ID'})
                self.WriteStatus(cmdname, ChassisID, {'ID': _input, 'Data Type': 'Chassis ID'})
                self.WriteStatus(cmdname, PortDescription, {'ID': _input, 'Data Type': 'Port Description'})
                self.WriteStatus(cmdname, SystemCapabilities, {'ID': _input, 'Data Type': 'System Capabilities'})
                self.WriteStatus(cmdname, TimetoLive, {'ID': _input, 'Data Type': 'Time to Live'})
            except Exception as e:
                print('{}'.format(e))
        else:
            namedict = {
                '60': 'LLDPStatusNAVLAN',
                '61': 'LLDPStatusOOBLAN'
            
            }
            self.WriteStatus(namedict[LANtype], name, {'Data Type': 'System Name'})
            self.WriteStatus(namedict[LANtype], managementaddress, {'Data Type': 'Management Address'})
            self.WriteStatus(namedict[LANtype], PortID, {'Data Type': 'Port ID'})
            self.WriteStatus(namedict[LANtype], SystemDescription, {'Data Type': 'System Description'})
            self.WriteStatus(namedict[LANtype], PortVLANID, {'Data Type': 'Port VLAN ID'})
            self.WriteStatus(namedict[LANtype], ChassisID, {'Data Type': 'Chassis ID'})
            self.WriteStatus(namedict[LANtype], PortDescription, {'Data Type': 'Port Description'})
            self.WriteStatus(namedict[LANtype], SystemCapabilities, {'Data Type': 'System Capabilities'})
            self.WriteStatus(namedict[LANtype], TimetoLive, {'Data Type': 'Time to Live'})
            
    def UpdateLLDPStatusEthExtEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('LLDPStatusEthExtEncoder', '{{{0}i:\x1b61STAT\r}}\r'.format(channel), value, qualifier)

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'I',
            'Output': 'O'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 0 <= len(name) <= 16 and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0},{1}N{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
            if qualifier['Type'] == 'Input': #only write the name if it's for input
                for x in self.OutputList:
                    audioVal = self.ReadStatus('OutputTieStatus', {'Output': x, 'Tie Type': 'Audio'}) # get audio input
                    videoVal = self.ReadStatus('OutputTieStatus', {'Output': x, 'Tie Type': 'Video'}) # get video input
                    if audioVal == int(number):
                        self.WriteStatus('OutputTieStatusName', name, {'Output': x, 'Tie Type': 'Audio'})
                    if videoVal == int(number):
                        self.WriteStatus('OutputTieStatusName', name, {'Output': x, 'Tie Type': 'Video'})
                    if audioVal == videoVal == int(number): # if video input is the same as audio input
                        self.WriteStatus('OutputTieStatusName', name, {'Output': x, 'Tie Type': 'Audio/Video'}) # write AV name
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': int(number)})
        if type_ == 'Input': # only write the name if type is input
            for x in self.OutputList:
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': x, 'Tie Type': 'Audio'}) # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': x, 'Tie Type': 'Video'}) # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': x, 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': x, 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': x, 'Tie Type': 'Audio/Video'})

    def SetRefreshMatrixIONames(self, value, qualifier):

        self.UpdateMatrixIONames( None, None)

    def UpdateMatrixIONames(self, value, qualifier):
        
        prevTime = 0
        for i in self.InputList:
            ctime = time.monotonic()
            while True:
                if ctime - prevTime > 0.2:
                    break
                else:
                    ctime = time.monotonic()
            self.Send('w{0}NI\r'.format(i))
            prevTime = ctime
        prevTime = 0
        for o in self.OutputList:
            ctime = time.monotonic()
            while True:
                if ctime - prevTime > 0.2:
                    break
                else:
                    ctime = time.monotonic()
            self.Send('w{0}NO\r'.format(o))
            prevTime = ctime
        
    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$',
        }

        Input = int(qualifier['Input'])
        tieType = qualifier['Tie Type']
        Output = int(qualifier['Output'])

        if Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Output Command for SetMatrixTieCommand')
        elif Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Input Command for SetMatrixTieCommand')
        else:
            if Output == 0:
                MatrixTieCmdString = '\x1B{0}*{1}\r'.format(Input, TieTypeValues[tieType])
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)
            else:
                MatrixTieCmdString = '\x1B{0}*{1}{2}\r'.format(Input, Output, TieTypeValues[tieType])
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)

    def SetRefreshMatrix(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)
        

    def SetCustomOSDEncoder(self, value, qualifier):
        VisibilityState = {
            'On': 1,
            'Off': 0
        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDEncoder')
        else:
            self.__SetHelper('CustomOSDEncoder', '{{{0}i:wV4*{1}WNDW\r}}\r'.format(channel, 
                                                                                  VisibilityState[value]), value, qualifier)

    def UpdateCustomOSDEncoder(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDEncoder', '{{{0}i:wV4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDEncoder(self, match, qualifier):
        VisibilityState = {
            1: 'On',
            0: 'Off'
        }
        _input = int(match.group(1).decode())
        value = int(match.group(2).decode())

        self.WriteStatus('CustomOSDEncoder', VisibilityState[value], {'ID': _input})

    def SetCustomOSDDurationEncoder(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDDurationEncoder')
        else:
            if 0 < int(value) < 501:
                self.__SetHelper('CustomOSDDurationEncoder', '{{{0}i:wD4*{1}WNDW\r}}\r'.format(channel, value), value, qualifier)
            else:
                self.Discard('Invalid Value for SetCustomOSDDurationEncoder')

    def UpdateCustomOSDDurationEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDDurationEncoder', '{{{0}i:wD4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDDurationEncoder(self, match, qualifier):
        _input = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('CustomOSDDurationEncoder', value, {'ID': _input})

    def SetCustomOSDLocationEncoder(self, value, qualifier):
        LocationState = {
            'Top-Left': 1,
            'Top-Right': 2,
            'Bottom-Left': 3,
            'Bottom-Right': 4
        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDLocationEncoder')
        else:
            self.__SetHelper('OSDLocation', '{{{0}i:wL4*{1}WNDW\r}}\r'.format(channel, 
                                                                                  LocationState[value]), value, qualifier)

    def UpdateCustomOSDLocationEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDLocationEncoder', '{{{0}i:wL4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDLocationEncoder(self, match, qualifier):
        LocationState = {
            1: 'Top-Left',
            2: 'Top-Right',
            3: 'Bottom-Left',
            4: 'Bottom-Right'
        }
        _input = int(match.group(1).decode())
        value = int(match.group(2).decode())

        self.WriteStatus('CustomOSDLocationEncoder', LocationState[value], {'ID': _input})

    def SetCustomOSDTextEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDTextEncoder')
        else:
            self.__SetHelper('CustomOSDTextEncoder', '{{{0}i:wT4*{1}*{2}TEXT\r}}\r'.format(channel, line, value), value, qualifier)

    def UpdateCustomOSDTextEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDTextEncoder', '{{{0}i:wT4*{1}TEXT\r}}\r'.format(channel, line), value, qualifier)

    def __MatchCustomOSDTextEncoder(self, match, qualifier):
        _input = int(match.group(1).decode())
        line = int(match.group(2).decode())
        text = match.group(3).decode()

        self.WriteStatus('CustomOSDTextEncoder', text, {'ID': _input, 'Row': line})

    def SetCustomClearOSDTextEncoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomClearOSDTextEncoder')
        else:
            self.__SetHelper('CustomClearOSDTextEncoder', '{{{0}i:wT4*{1}* TEXT\r}}\r'.format(channel, line), value, qualifier)

    def SetCustomOSDDecoder(self, value, qualifier):
        VisibilityState = {
            'On': 1,
            'Off': 0
        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDDecoder')
        else:
            self.__SetHelper('CustomOSDDecoder', '{{{0}o:wV4*{1}WNDW\r}}\r'.format(channel, 
                                                                                  VisibilityState[value]), value, qualifier)

    def UpdateCustomOSDDecoder(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDDecoder', '{{{0}o:wV4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDDecoder(self, match, qualifier):
        VisibilityState = {
            1: 'On',
            0: 'Off'
        }
        output = int(match.group(1).decode())
        value = int(match.group(2).decode())

        self.WriteStatus('CustomOSDDecoder', VisibilityState[value], {'ID': output})

    def SetCustomOSDDurationDecoder(self, value, qualifier):

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetOSDDuration')
        else:
            if 0 < int(value) <= 501:
                self.__SetHelper('CustomOSDDurationDecoder', '{{{0}o:wD4*{1}WNDW\r}}\r'.format(channel, value), value, qualifier)
            else:
                self.Discard('Invalid Value for SetCustomOSDDurationDecoder')

    def UpdateCustomOSDDurationDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDDurationDecoder', '{{{0}o:wD4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDDurationDecoder(self, match, qualifier):
        output = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('CustomOSDDurationDecoder', value, {'ID': output})

    def SetCustomOSDLocationDecoder(self, value, qualifier):
        LocationState = {
            'Top-Left': 1,
            'Top-Right': 2,
            'Bottom-Left': 3,
            'Bottom-Right': 4
        }

        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDLocationDecoder')
        else:
            self.__SetHelper('CustomOSDLocationDecoder', '{{{0}o:wL4*{1}WNDW\r}}\r'.format(channel, 
                                                                                  LocationState[value]), value, qualifier)

    def UpdateCustomOSDLocationDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDLocationDecoder', '{{{0}o:wL4WNDW\r}}\r'.format(channel), value, qualifier)

    def __MatchCustomOSDLocationDecoder(self, match, qualifier):
        LocationState = {
            1: 'Top-Left',
            2: 'Top-Right',
            3: 'Bottom-Left',
            4: 'Bottom-Right'
        }
        output = int(match.group(1).decode())
        value = int(match.group(2).decode())

        self.WriteStatus('CustomOSDLocationDecoder', LocationState[value], {'ID': output})

    def SetCustomOSDTextDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomOSDTextDecoder')
        else:
            self.__SetHelper('CustomOSDTextDecoder', '{{{0}o:wT4*{1}*{2}TEXT\r}}\r'.format(channel, line, value), value, qualifier)

    def UpdateCustomOSDTextDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command')
        else:
            self.__UpdateHelper('CustomOSDTextDecoder', '{{{0}o:wT4*{1}TEXT\r}}\r'.format(channel, line), value, qualifier)

    def __MatchCustomOSDTextDecoder(self, match, qualifier):
        output = int(match.group(1).decode())
        line = int(match.group(2).decode())
        text = match.group(3).decode()

        self.WriteStatus('CustomOSDTextDecoder', text, {'ID': output, 'Row': line})

    def SetCustomClearOSDTextDecoder(self, value, qualifier):
        channel = int(qualifier['ID'])
        line = qualifier['Row']
        if channel < 0 or channel > 4096:
            self.Discard('Invalid Command for SetCustomClearOSDText')
        else:
            self.__SetHelper('CustomClearOSDTextDecoder', '{{{0}o:wT4*{1}* TEXT\r}}\r'.format(channel, line), value, qualifier)

    def UpdatePartNumber(self, value, qualifier):
        self.__UpdateHelper('PartNumber', 'n' , value, qualifier)


    def SetUSBMatrixTieCommand(self, value, qualifier):
        """Set USB Matrix Tie Command
        
        """

        HostTypeValues = {
            'Input': 'i',
            'Output': 'o'
        }

        Device = int(qualifier['Device I/O Number'])
        DeviceType = qualifier['Device Type']
        Host = int(qualifier['Host I/O Number'])
        HostType = qualifier['Host Type']

        MatrixTieCmdString = '\x1B{0}{1}*{2}{3}^\r'.format(Host, HostTypeValues[HostType], Device, HostTypeValues[DeviceType])
        self.__SetHelper('USBMatrixTieCommand', MatrixTieCmdString, value, qualifier)


    def SetVideoMuteDecoder(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
            'Video and Sync': '2'
        }

        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for SetVideoMute')
        else:
            self.__SetHelper('VideoMuteDecoder', '{{{0}o:{1}B\r}}\r'.format(channel, VideoMuteState[value]), value, qualifier)

    def UpdateVideoMuteDecoder(self, value, qualifier):

        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoMuteCmdString = '{{{0}o:B\r}}\r'.format(channel)
            self.__UpdateHelper('VideoMuteDecoder', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMuteDecoder(self, match, qualifier):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
            '2': 'Video and Sync'
        }

        self.WriteStatus('VideoMuteDecoder', VideoMuteName[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def SetVideoMuteEncoder(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
            'Video and Sync': '2'
        }

        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for SetVideoMute')
        else:
            self.__SetHelper('VideoMuteEncoder', '{{{0}i:{1}B\r}}\r'.format(channel, VideoMuteState[value]), value, qualifier)

    def UpdateVideoMuteEncoder(self, value, qualifier):

        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoMuteCmdString = '{{{0}i:B\r}}\r'.format(channel)
            self.__UpdateHelper('VideoMuteEncoder', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMuteEncoder(self, match, qualifier):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
            '2': 'Video and Sync'
        }

        self.WriteStatus('VideoMuteEncoder', VideoMuteName[match.group(2).decode()], {'ID': int(match.group(1).decode())})

    def SetVideoWallPresetRecall(self, value, qualifier):

        Canvas = int(qualifier['Canvas'])
        value = int(value)

        if Canvas < 0 or Canvas > 8:
            self.Discard('Invalid Command for VideoWallPresetRecall')
        elif value < 0 or value > 8:
            self.Discard('Invalid Command for VideoWallPresetRecall')
        else:
            VideoWallPresetRecallCmdString = '\x1BR1*{0}*{1}PRST\r'.format(Canvas, value)
            self.__SetHelper('VideoWallPresetRecall', VideoWallPresetRecallCmdString, value, qualifier)

    def UpdateVideoWallPresetRecall(self, value, qualifier):

        canvas = qualifier['Canvas']
        if int(canvas) < 0 or int(canvas) > 8:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoWallPresetRecallCmdString = 'wL1*{}PRST\r'.format(canvas)
            self.__UpdateHelper('VideoWallPresetRecall', VideoWallPresetRecallCmdString, value, qualifier)

    def __MatchVideoWallPresetRecall(self, match, qualifier):

        self.WriteStatus('VideoWallPresetRecall', str(int(match.group(2).decode())), {'Canvas': str(int(match.group(1).decode()))})

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
            
        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for SetVolume')
        else:
            self.__SetHelper('Volume', '{{{0}o:{1}V\r}}\r'.format(channel,value), value, qualifier)

    def UpdateVolume(self, value, qualifier):
        channel = qualifier['ID']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for UpdateVolume')
        else:
            self.__UpdateHelper('Volume', '{{{0}o:V\r}}\r'.format(channel), value, qualifier)

    def __MatchVolume(self, match, qualifier):

        output = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'ID': int(match.group(1).decode())})
        
    def SetWindowMute(self, value, qualifier):

        Canvas = int(qualifier['Canvas'])
        Window = int(qualifier['Window'])
        WindowMuteState = {
            'On': '1',
            'Off': '0'
            }

        if Canvas < 0 or Canvas > 8:
            self.Discard('Invalid Command for WindowMute')
        elif Window < 0 or Window > 64:
            self.Discard('Invalid Command for WindowMute')
        else:
            WindowMuteCmdString = '{0}*{1}*{2}B'.format(Canvas, Window, WindowMuteState[value])
            self.__SetHelper('WindowMute', WindowMuteCmdString, value, qualifier)

    def UpdateWindowMute(self, value, qualifier):
        Canvas = int(qualifier['Canvas'])
        Window = int(qualifier['Window'])
        if Canvas < 0 or Canvas > 8:
            self.Discard('Invalid Command for WindowMute')
        elif Window < 0 or Window > 64:
            self.Discard('Invalid Command for WindowMute')
        else:
            self.__UpdateHelper('WindowMute', '{0}*{1}B'.format(Canvas, Window), value, qualifier)

    def __MatchWindowMute(self, match, qualifier):
        
        ValueStateValues = {
            '1'  : 'On', 
            '0' : 'Off'
        }
        Window = str(int(match.group(2).decode()))
        Canvas = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('WindowMute', value, {'Canvas': Canvas, 'Window': Window})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False
        
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number or port number',
            '13': 'Invalid parameter (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out (caused by direct write of global presets)',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }
        self.counter = 0  # incase the device keeps returning Error this is still connected
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        self.InputList = []
        self.OutputList = []

    def extr_18_4118_NAVigator(self):

        self.InputSize = 4096
        self.OutputSize = 4096

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
            return None

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

class SPIClass(SPInterface, DeviceClass):

    def __init__(self, spd, Model=None):
        SPInterface.__init__(self, spd)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        self.OnDisconnected()