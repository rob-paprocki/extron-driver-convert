from extronlib.interface import EthernetClientInterface
import re
import struct

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True

        self.Models = {
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AuxinFaderLevel': {'Parameters':['Auxin'], 'Status': {}},
            'AuxinFaderMute': {'Parameters':['Auxin'], 'Status': {}},
            'BusFaderLevel': {'Parameters':['Bus'], 'Status': {}},
            'BusFaderMute': {'Parameters':['Bus'], 'Status': {}},
            'ChannelFaderLevel': {'Parameters':['Channel'], 'Status': {}},
            'ChannelFaderMute': {'Parameters':['Channel'], 'Status': {}},
            'DCAFaderLevel': {'Parameters':['DCA'], 'Status': {}},
            'DCAFaderMute': {'Parameters':['DCA'], 'Status': {}},
            'FXReturnFaderLevel': {'Parameters':['FX Return'], 'Status': {}},
            'FXReturnFaderMute': {'Parameters':['FX Return'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'MainFaderLevel': {'Parameters':['Type'], 'Status': {}},
            'MainFaderMute': {'Parameters':['Type'], 'Status': {}},
            'MatrixFaderLevel': {'Parameters':['Matrix'], 'Status': {}},
            'MatrixFaderMute': {'Parameters':['Matrix'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'auxin\/0([1-8])\/mix\/fader\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchAuxinFaderLevel, None)
            self.AddMatchString(re.compile(b'auxin\/0([1-8])\/mix\/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchAuxinFaderMute, None)
            self.AddMatchString(re.compile(b'bus\/([0-9]{2})\/mix\/fader\x00\x00\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchBusFaderLevel, None)
            self.AddMatchString(re.compile(b'bus\/([0-9]{2})\/mix\/on\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchBusFaderMute, None)
            self.AddMatchString(re.compile(b'ch\/([0-9]{2})\/mix\/fader\x00\x00\x00\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchChannelFaderLevel, None)
            self.AddMatchString(re.compile(b'ch\/([0-9]{2})\/mix\/on\x00\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchChannelFaderMute, None)
            self.AddMatchString(re.compile(b'dca\/([1-8])\/fader\x00\x00\x00\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchDCAFaderLevel, None)
            self.AddMatchString(re.compile(b'dca\/([1-8])\/on\x00\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchDCAFaderMute, None)
            self.AddMatchString(re.compile(b'fxrtn\/0([1-8])\/mix\/fader\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchFXReturnFaderLevel, None)
            self.AddMatchString(re.compile(b'fxrtn\/0([1-8])\/mix\/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchFXReturnFaderMute, None)
            self.AddMatchString(re.compile(b'config\/mute\/([1-6])\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchGroupMute, None)
            self.AddMatchString(re.compile(b'main\/(m|st)\/mix\/fader\x00\x00(\x00)?,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchMainFaderLevel, None)
            self.AddMatchString(re.compile(b'main\/(m|st)\/mix\/on\x00(\x00)?,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchMainFaderMute, None)
            self.AddMatchString(re.compile(b'mtx\/0([1-6])\/mix\/fader\x00\x00\x00,f\x00\x00([\x00-\xff]{4})\/'), self.__MatchMatrixFaderLevel, None)
            self.AddMatchString(re.compile(b'mtx\/0([1-6])\/mix\/on\x00\x00,i\x00\x00\x00\x00\x00(\x00|\x01)'), self.__MatchMatrixFaderMute, None)

    def floatTobinary32(self, value):
        val = struct.unpack('Q', struct.pack('d', value))[0]
        getBin = lambda x: x>0 and str(bin(x))[2:] or "-" + str(bin(x))[3:]
        return getBin(val)

    def SetAuxinFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        aux = int(qualifier['Auxin'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= aux <=8):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                AuxinFaderLevelCmdString = b'/auxin/0' + bytes(qualifier['Auxin'], 'utf-8') + b'/mix/fader\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                AuxinFaderLevelCmdString = b'/auxin/0' + bytes(qualifier['Auxin'], 'utf-8') + b'/mix/fader\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('AuxinFaderLevel', AuxinFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAuxinFaderLevel')

    def UpdateAuxinFaderLevel(self, value, qualifier):

        aux = int(qualifier['Auxin'])
        if 1 <= aux <=8:
            AuxinFaderLevelCmdString = '/auxin/0{0}/mix/fader\x00'.format(aux)
            self.__UpdateHelper('AuxinFaderLevel', AuxinFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateAuxinFaderLevel')
            
    def __MatchAuxinFaderLevel(self, match, tag):
        qualifier = {}
        qualifier['Auxin'] = match.group(1).decode()
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('AuxinFaderLevel', value, qualifier)

    def SetAuxinFaderMute(self, value, qualifier):

        aux = int(qualifier['Auxin']) 
        if value in ('On', 'Off') and 1<= aux <=8:
            auxin = '{0:02d}'.format(aux)
            if value == 'On':
                AuxinFaderMuteCmdString = b'/auxin/'+ bytes(auxin, 'utf-8')+ b'/mix/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                AuxinFaderMuteCmdString = b'/auxin/'+ bytes(auxin, 'utf-8')+ b'/mix/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('AuxinFaderMute', AuxinFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAuxinFaderMute')

    def UpdateAuxinFaderMute(self, value, qualifier):

        aux = int(qualifier['Auxin']) 
        if 1<= aux <= 8:
            AuxinFaderMuteCmdString = '/auxin/{0:02}/mix/\x00\x00'.format(aux)
            self.__UpdateHelper('AuxinFaderMute', AuxinFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateAuxinFaderMute')

    def __MatchAuxinFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01'  : 'Off',
        }

        auxin = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(auxin) <= 8:
            self.WriteStatus('AuxinFaderMute', value, {'Auxin' : auxin})

    def SetBusFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        bus = int(qualifier['Bus'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1<= bus <= 16):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:   
                final = '{0:02d}'.format(bus)
                BusFaderLevelCmdString = b'/bus/' + bytes(final, 'utf-8') + b'/mix/fader\x00\x00\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                final = '{0:02d}'.format(bus)
                BusFaderLevelCmdString = b'/bus/' + bytes(final, 'utf-8') + b'/mix/fader\x00\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBusFaderLevel')


    def UpdateBusFaderLevel(self, value, qualifier):

        bus = int(qualifier['Bus'])
        if 1<= bus <= 16:
            BusFaderLevelCmdString = '/bus/{0:02d}/mix/fader\x00\x00\x00'.format(bus)
            self.__UpdateHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateBusFaderLevel')
            
    def __MatchBusFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Bus'] = str(int(match.group(1).decode()))
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('BusFaderLevel', value, qualifier)

    def SetBusFaderMute(self, value, qualifier):

        busqual = int(qualifier['Bus']) 
        if value in ('On', 'Off') and 1<= busqual <=16:
            bus = '{0:02d}'.format(busqual)
            if value == 'On':
                BusFaderMuteCmdString = b'/bus/'+ bytes(bus, 'utf-8')+ b'/mix/on\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                BusFaderMuteCmdString = b'/bus/'+ bytes(bus, 'utf-8')+ b'/mix/on\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBusFaderMute')

    def UpdateBusFaderMute(self, value, qualifier):

        bus = int(qualifier['Bus']) 
        if 1<= bus <= 16:
            BusFaderMuteCmdString = '/bus/{0:02}/mix/\x00\x00\x00\x00'.format(bus)
            self.__UpdateHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateBusFaderMute')

    def __MatchBusFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01'  : 'Off',
        }

        bus = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(bus) <= 16:
            self.WriteStatus('BusFaderMute', value, {'Bus' : bus})

    def SetChannelFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }
        chn = int(qualifier['Channel']) 
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and (1 <= chn <=32):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                channel = '{0:02d}'.format(chn)
                ChannelFaderLevelCmdString = b'/ch/'+ bytes(channel, 'utf-8') + b'/mix/fader\x00\x00\x00\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                channel = '{0:02d}'.format(chn)
                ChannelFaderLevelCmdString = b'/ch/'+ bytes(channel, 'utf-8') + b'/mix/fader\x00\x00\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('ChannelFaderLevel', ChannelFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelFaderLevel')

    def UpdateChannelFaderLevel(self, value, qualifier):

        chn = int(qualifier['Channel']) 
        if 1 <= chn <=32:
            ChannelFaderLevelCmdString = '/ch/{0:02d}/mix/fader\x00\x00\x00\x00'.format(chn)
            self.__UpdateHelper('ChannelFaderLevel', ChannelFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateChannelFaderLevel')
            
    def __MatchChannelFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Channel'] = str(int(match.group(1).decode()))
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('ChannelFaderLevel', value, qualifier)

    def SetChannelFaderMute(self, value, qualifier):

        chn = int(qualifier['Channel']) 
        if value in ('On', 'Off') and 1<= chn <= 32:
            channel = '{0:02d}'.format(chn)
            if value == 'On':
                ChannelFaderMuteCmdString = b'/ch/'+ bytes(channel, 'utf-8')+ b'/mix/on\x00\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                ChannelFaderMuteCmdString = b'/ch/'+ bytes(channel, 'utf-8')+ b'/mix/on\x00\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('ChannelFaderMute', ChannelFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannelFaderMute')

    def UpdateChannelFaderMute(self, value, qualifier):

        chn = int(qualifier['Channel']) 
        if 1<= chn <= 32:
            ChannelFaderMuteCmdString = '/ch/{0:02}/mix/\x00'.format(chn)
            self.__UpdateHelper('ChannelFaderMute', ChannelFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateChannelFaderMute')
        
    def __MatchChannelFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01' : 'Off',
        }

        channel = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(channel) <= 32:
            self.WriteStatus('ChannelFaderMute', value, {'Channel' : channel})

    def SetDCAFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        dca = int(qualifier['DCA'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= dca <=8):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                DCAFaderLevelCmdString = b'/dca/' + bytes(qualifier['DCA'], 'utf-8') + b'/fader\x00\x00\x00\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                DCAFaderLevelCmdString = b'/dca/' + bytes(qualifier['DCA'], 'utf-8') + b'/fader\x00\x00\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDCAFaderLevel')

    def UpdateDCAFaderLevel(self, value, qualifier):

        dca = int(qualifier['DCA'])
        if 1 <= dca <=8:
            DCAFaderLevelCmdString = '/dca/{0}/fader\x00\x00\x00\x00'.format(dca)
            self.__UpdateHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateDCAFaderLevel')
            
    def __MatchDCAFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['DCA'] = match.group(1).decode()
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('DCAFaderLevel', value, qualifier)

    def SetDCAFaderMute(self, value, qualifier):

        dca = int(qualifier['DCA']) 
        if value in ('On', 'Off') and 1<= dca <= 8:
            dcaval = str(dca)
            if value == 'On':
                DCAFaderMuteCmdString = b'/dca/'+ bytes(dcaval, 'utf-8')+ b'/on\x00\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                DCAFaderMuteCmdString = b'/dca/'+ bytes(dcaval, 'utf-8')+ b'/on\x00\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDCAFaderMute')

    def UpdateDCAFaderMute(self, value, qualifier):

        dca = int(qualifier['DCA']) 
        if 1<= dca <= 8:
            DCAFaderMuteCmdString = '/dca/{0}/on/\x00\x00'.format(dca)
            self.__UpdateHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateDCAFaderMute')
        
    def __MatchDCAFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01' : 'Off',
        }

        DCA = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(DCA) <= 8:
            self.WriteStatus('DCAFaderMute', value, {'DCA' : DCA})

    def SetFXReturnFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        fx = int(qualifier['FX Return'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= fx <=8):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                FxrtnFaderLevelCmdString = b'/fxrtn/0' + bytes(qualifier['FX Return'], 'utf-8') + b'/mix/fader\x00,f\x00\x00\x00\x00\x00\x00'

            if temp:
                FxrtnFaderLevelCmdString = b'/fxrtn/0' + bytes(qualifier['FX Return'], 'utf-8') + b'/mix/fader\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('FXReturnFaderLevel', FxrtnFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFXReturnFaderLevel')

    def UpdateFXReturnFaderLevel(self, value, qualifier):

        fx = int(qualifier['FX Return'])
        if 1 <= fx <=8:
            FxrtnFaderLevelCmdString = '/fxrtn/0{0}/mix/fader\x00'.format(fx)
            self.__UpdateHelper('FXReturnFaderLevel', FxrtnFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateFXReturnFaderLevel')
            
    def __MatchFXReturnFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['FX Return'] = match.group(1).decode()
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('FXReturnFaderLevel', value, qualifier)

    def SetFXReturnFaderMute(self, value, qualifier):

        fx = int(qualifier['FX Return']) 
        if value in ('On', 'Off') and 1<= fx <= 8:
            fxval = '{0:02d}'.format(fx)
            if value == 'On':
                FXReturnFaderMuteCmdString = b'/fxrtn/'+ bytes(fxval, 'utf-8')+ b'/mix/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                FXReturnFaderMuteCmdString = b'/fxrtn/'+ bytes(fxval, 'utf-8')+ b'/mix/on\x00\x00\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('FXReturnFaderMute', FXReturnFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFXReturnFaderMute')

    def UpdateFXReturnFaderMute(self, value, qualifier):

        fx = int(qualifier['FX Return']) 
        if 1<= fx <= 8:
            FXReturnFaderMuteCmdString = '/fxrtn/{0:02}/mix/\x00\x00'.format(fx)
            self.__UpdateHelper('FXReturnFaderMute', FXReturnFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateFXReturnFaderMute')
        
    def __MatchFXReturnFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01' : 'Off',
        }

        FXReturn = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(FXReturn) <= 8:
            self.WriteStatus('FXReturnFaderMute', value, {'FX Return' : FXReturn})

    def SetGroupMute(self, value, qualifier):

        grp = int(qualifier['Group']) 
        if (value in ('On', 'Off')) and (1<= grp <= 6):
            if value == 'On':
                GroupMuteCmdString = b'/config/mute/' + bytes(qualifier['Group'], 'utf-8') + b'\x00\x00,s\x00\x00ON\x00\x00'
            elif value == 'Off':
                GroupMuteCmdString = b'/config/mute/' + bytes(qualifier['Group'], 'utf-8') + b'\x00\x00,s\x00\x00OFF\x00'
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        grp = int(qualifier['Group']) 
        if 1<= grp <= 6:
            GroupMuteCmdString = '/config/mute/{0}\x00\x00'.format(grp)
            self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateGroupMute')
            
    def __MatchGroupMute(self, match, tag):

        ValueStateValues = {
            '\x01' : 'On', 
            '\x00' : 'Off'
        }

        qualifier = {}
        qualifier['Group'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GroupMute', value, qualifier)

    def SetMainFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        sndtype = qualifier['Type']
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (sndtype in ['Mono', 'Stereo']):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                if sndtype == 'Mono':
                    MainFaderLevelCmdString = b'/main/m/mix/fader\x00\x00\x00,f\x00\x00\x00\x00\x00\x00'
                else:
                    MainFaderLevelCmdString = b'/main/st/mix/fader\x00\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                if sndtype == 'Mono':
                    MainFaderLevelCmdString = b'/main/m/mix/fader\x00\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
                else:
                    MainFaderLevelCmdString = b'/main/st/mix/fader\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('MainFaderLevel', MainFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMainFaderLevel')

    def UpdateMainFaderLevel(self, value, qualifier):

        sndtype = qualifier['Type']
        if sndtype in ['Mono', 'Stereo']:
            if sndtype == 'Mono':
                MainFaderLevelCmdString = '/main/m/mix/fader\x00\x00\x00'
            else:
                MainFaderLevelCmdString = '/main/st/mix/fader\x00\x00'
            self.__UpdateHelper('MainFaderLevel', MainFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMainFaderLevel')
            
    def __MatchMainFaderLevel(self, match, tag):

        TypeStates = {
            'm'  : 'Mono', 
            'st' : 'Stereo'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = int(struct.unpack('>f', match.group(3))[0]*100)
        self.WriteStatus('MainFaderLevel', value, qualifier)

    def SetMainFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '\x00',
            'Off': '\x01'
        }
        sndtype = qualifier['Type']
        if sndtype in ['Mono', 'Stereo']:
            if sndtype == 'Mono':
                MainFaderMuteCmdString = '/main/m/mix/on\x00\x00,i\x00\x00\x00\x00\x00{0}'.format(ValueStateValues[value])
            else:
                MainFaderMuteCmdString = '/main/st/mix/on\x00,i\x00\x00\x00\x00\x00{0}'.format(ValueStateValues[value])
            self.__SetHelper('MainFaderMute', MainFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMainFaderMute')

    def UpdateMainFaderMute(self, value, qualifier):

        sndtype = qualifier['Type']
        if sndtype in ['Mono', 'Stereo']:
            if sndtype == 'Mono':
                MainFaderMuteCmdString = '/main/m/mix/\x00\x00\x00\x00'
            else:
                MainFaderMuteCmdString = '/main/st/mix/\x00\x00\x00'
            self.__UpdateHelper('MainFaderMute', MainFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMainFaderMute')
        
    def __MatchMainFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01' : 'Off',
        }

        TypeStates = {
            'm'  : 'Mono', 
            'st' : 'Stereo'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('MainFaderMute', value, qualifier)

    def SetMatrixFaderLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        Matrix = int(qualifier['Matrix'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (1 <= Matrix <=6):
            temp = self.floatTobinary32(value/100)[3:33]
            if value == 0:
                MtxFaderLevelCmdString = b'/mtx/0' + bytes(qualifier['Matrix'],'utf-8') + b'/mix/fader\x00\x00\x00,f\x00\x00\x00\x00\x00\x00'
            if temp:
                MtxFaderLevelCmdString = b'/mtx/0' + bytes(qualifier['Matrix'],'utf-8') + b'/mix/fader\x00\x00\x00,f\x00\x00' + struct.pack('>I',int(temp, 2))
            self.__SetHelper('MatrixFaderLevel', MtxFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixFaderLevel')

    def UpdateMatrixFaderLevel(self, value, qualifier):

        Matrix = int(qualifier['Matrix'])
        if 1 <= Matrix <=6:
            MtxFaderLevelCmdString = '/mtx/0{0}/mix/fader\x00\x00\x00'.format(Matrix)
            self.__UpdateHelper('MatrixFaderLevel', MtxFaderLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMatrixFaderLevel')
            
    def __MatchMatrixFaderLevel(self, match, tag):

        qualifier = {}
        qualifier['Matrix'] = match.group(1).decode()
        value = int(struct.unpack('>f', match.group(2))[0]*100)
        self.WriteStatus('MatrixFaderLevel', value, qualifier)

    def SetMatrixFaderMute(self, value, qualifier):

        mtrx = int(qualifier['Matrix']) 
        if value in ('On', 'Off') and 1<= mtrx <= 6:
            matrix = '{0:02d}'.format(mtrx)
            if value == 'On':
                MatrixFaderMuteCmdString = b'/mtx/'+ bytes(matrix, 'utf-8')+ b'/mix/on\x00\x00,i\x00\x00\x00\x00\x00\x00'
            elif value == 'Off':
                MatrixFaderMuteCmdString = b'/mtx/'+ bytes(matrix, 'utf-8')+ b'/mix/on\x00\x00,i\x00\x00\x00\x00\x00\x01'
            self.__SetHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixFaderMute')

    def UpdateMatrixFaderMute(self, value, qualifier):

        mtrx = int(qualifier['Matrix']) 
        if 1<= mtrx <= 6:
            MatrixFaderMuteCmdString = '/mtx/{0:02}/mix/\x00\x00\x00\x00'.format(mtrx)
            self.__UpdateHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMatrixFaderMute')
        
    def __MatchMatrixFaderMute(self, match, tag):

        ValueStateValues = {
            '\x00'  : 'On', 
            '\x01' : 'Off',
        }

        Matrix = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        if value and 1 <= int(Matrix) <= 6:
            self.WriteStatus('MatrixFaderMute', value, {'Matrix' : Matrix})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
    
    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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
