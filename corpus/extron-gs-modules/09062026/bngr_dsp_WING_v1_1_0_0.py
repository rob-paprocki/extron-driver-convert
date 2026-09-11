from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AuxInFaderLevel': {'Parameters':['Aux In'], 'Status': {}},
            'AuxInFaderMute': {'Parameters':['Aux In'], 'Status': {}},
            'BusFaderLevel': {'Parameters':['Bus'], 'Status': {}},
            'BusFaderMute': {'Parameters':['Bus'], 'Status': {}},
            'ChannelFaderLevel': {'Parameters':['Channel'], 'Status': {}},
            'ChannelFaderMute': {'Parameters':['Channel'], 'Status': {}},
            'DCAFaderLevel': {'Parameters':['DCA'], 'Status': {}},
            'DCAFaderMute': {'Parameters':['DCA'], 'Status': {}},
            'FXReturnFaderLevel': {'Parameters':['FX Return'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'MainFaderLevel': {'Parameters':['Main'], 'Status': {}},
            'MainFaderMute': {'Parameters':['Main'], 'Status': {}},
            'MatrixFaderLevel': {'Parameters':['Matrix'], 'Status': {}},
            'MatrixFaderMute': {'Parameters':['Matrix'], 'Status': {}},
        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'/aux/([1-8])/fdr\x00\x00,sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchAuxInFaderLevel, None)
            self.AddMatchString(re.compile(b'/aux/([1-8])/mute\x00,sfi\x00\x00\x00\x00([01])\x00'), self.__MatchAuxInFaderMute, None)
            self.AddMatchString(re.compile(b'/bus/(\d{1,2})/fdr\x00{1,4},sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchBusFaderLevel, None)
            self.AddMatchString(re.compile(b'/bus/(\d{1,2})/mute\x00{1,4},sfi\x00\x00\x00\x00([01])\x00'), self.__MatchBusFaderMute, None)
            self.AddMatchString(re.compile(b'/ch/(\d{1,2})/fdr\x00{1,3},sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchChannelFaderLevel, None)
            self.AddMatchString(re.compile(b'/ch/(\d{1,2})/mute\x00{1,2},sfi\x00\x00\x00\x00([01])\x00'), self.__MatchChannelFaderMute, None)
            self.AddMatchString(re.compile(b'/dca/(\d{1,2})/fdr\x00{1,2},sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchDCAFaderLevel, None)
            self.AddMatchString(re.compile(b'/dca/(\d{1,2})/mute\x00{1,4},sfi\x00\x00\x00\x00([01])\x00'), self.__MatchDCAFaderMute, None)
            self.AddMatchString(re.compile(b'/fx/(\d{1,2})/fxmix\x00{1,4},sff\x00\x00\x00\x00(\d{1,3})\x00'), self.__MatchFXReturnFaderLevel, None)
            self.AddMatchString(re.compile(b'/mgrp/([1-8])/mute\x00\x00\x00\x00,sfi\x00\x00\x00\x00([01])\x00'), self.__MatchGroupMute, None)
            self.AddMatchString(re.compile(b'/main/([1-4])/fdr\x00,sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchMainFaderLevel, None)
            self.AddMatchString(re.compile(b'/main/([1-4])/mute\x00\x00\x00\x00,sfi\x00\x00\x00\x00([01])\x00'), self.__MatchMainFaderMute, None)
            self.AddMatchString(re.compile(b'/mtx/([1-8])/fdr\x00\x00,sff\x00\x00\x00\x00(-oo|-?[0-9]{1,2}.[0-9])\x00'), self.__MatchMatrixFaderLevel, None)
            self.AddMatchString(re.compile(b'/mtx/([1-8])/mute\x00,sfi\x00\x00\x00\x00([01])\x00'), self.__MatchMatrixFaderMute, None)

    def SetAuxInFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Aux In']) <= 8 and -90.0 <= value <= 10.0:
            AuxInFaderLevelCmdString = '/aux/{0}/\x00,s\x00\x00fdr={1}'.format(qualifier['Aux In'], round(float(value), 1))
            self.__SetHelper('AuxInFaderLevel', AuxInFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxInFaderLevel')

    def UpdateAuxInFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Aux In']) <= 8:
            AuxInFaderLevelCmdString = '/aux/{}/fdr'.format(qualifier['Aux In'])
            self.__UpdateHelper('AuxInFaderLevel', AuxInFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAuxInFaderLevel')

    def __MatchAuxInFaderLevel(self, match, tag):

        qualifier = {'Aux In' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('AuxInFaderLevel', value, qualifier)

    def SetAuxInFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Aux In']) <= 8 and value in ValueStateValues:
            AuxInFaderMuteCmdString = '/aux/{0}/\x00,s\x00\x00mute={1}'.format(qualifier['Aux In'], ValueStateValues[value])
            self.__SetHelper('AuxInFaderMute', AuxInFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAuxInFaderMute')

    def UpdateAuxInFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['Aux In']) <= 8:
            AuxInFaderMuteCmdString = '/aux/{}/mute'.format(qualifier['Aux In'])
            self.__UpdateHelper('AuxInFaderMute', AuxInFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAuxInFaderMute')

    def __MatchAuxInFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Aux In' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AuxInFaderMute', value, qualifier)

    def SetBusFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Bus']) <= 16 and -90.0 <= value <= 10.0:
            if int(qualifier['Bus']) >= 10:
                BusFaderLevelCmdString = '/bus/{0}/\x00\x00\x00\x00,s\x00\x00fdr={1}'.format(qualifier['Bus'], round(float(value), 1))
            else:
                BusFaderLevelCmdString = '/bus/{0}/\x00,s\x00\x00fdr={1}'.format(qualifier['Bus'], round(float(value), 1))
            self.__SetHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusFaderLevel')

    def UpdateBusFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Bus']) <= 16:
            BusFaderLevelCmdString = '/bus/{}/fdr'.format(qualifier['Bus'])
            self.__UpdateHelper('BusFaderLevel', BusFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusFaderLevel')

    def __MatchBusFaderLevel(self, match, tag):

        qualifier = {'Bus' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('BusFaderLevel', value, qualifier)

    def SetBusFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Bus']) <= 16 and value in ValueStateValues:
            if int(qualifier['Bus']) >= 10:
                BusFaderMuteCmdString = '/bus/{0}/\x00\x00\x00\x00,s\x00\x00mute={1}'.format(qualifier['Bus'], ValueStateValues[value])
            else:
                BusFaderMuteCmdString = '/bus/{0}/\x00,s\x00\x00mute={1}'.format(qualifier['Bus'], ValueStateValues[value])
            self.__SetHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBusFaderMute')

    def UpdateBusFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['Bus']) <= 16:
            BusFaderMuteCmdString = '/bus/{}/mute'.format(qualifier['Bus'])
            self.__UpdateHelper('BusFaderMute', BusFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBusFaderMute')

    def __MatchBusFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Bus' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('BusFaderMute', value, qualifier)

    def SetChannelFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 40 and -90.0 <= value <= 10.0:
            if int(qualifier['Channel']) >= 10:
                InputGainCmdString = '/ch/{0}/\x00,s\x00\x00fdr={1}'.format(qualifier['Channel'], round(float(value), 1))
            else:
                InputGainCmdString = '/ch/{0}/\x00\x00,s\x00\x00fdr={1}'.format(qualifier['Channel'], round(float(value), 1))

            self.__SetHelper('ChannelFaderLevel', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelFaderLevel')

    def UpdateChannelFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 40:
            ChannelFaderLevelCmdString = '/ch/{}/fdr'.format(qualifier['Channel'])
            self.__UpdateHelper('ChannelFaderLevel', ChannelFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelFaderLevel')

    def __MatchChannelFaderLevel(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('ChannelFaderLevel', value, qualifier)

    def SetChannelFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Channel']) <= 40 and value in ValueStateValues:
            if int(qualifier['Channel']) >= 10:
                InputMuteCmdString = '/ch/{0}/\x00,s\x00\x00mute={1}'.format(qualifier['Channel'], ValueStateValues[value])
            else:
                InputMuteCmdString = '/ch/{0}/\x00\x00,s\x00\x00mute={1}'.format(qualifier['Channel'], ValueStateValues[value])
            self.__SetHelper('ChannelFaderMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelFaderMute')
    def UpdateChannelFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 40:
            ChannelFaderMuteCmdString = '/ch/{}/mute'.format(qualifier['Channel'])
            self.__UpdateHelper('ChannelFaderMute', ChannelFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelFaderMute')

    def __MatchChannelFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Channel' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ChannelFaderMute', value, qualifier)

    def SetDCAFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 16 and -90.0 <= value <= 10.0:
            if int(qualifier['DCA']) >= 10:
                DCAFaderLevelCmdString = '/dca/{0}/\x00\x00\x00\x00,s\x00\x00fdr={1}'.format(qualifier['DCA'], round(float(value), 1))
            else:
                DCAFaderLevelCmdString = '/dca/{0}/\x00,s\x00\x00fdr={1}'.format(qualifier['DCA'], round(float(value), 1))
            self.__SetHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderLevel')

    def UpdateDCAFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 16:
            DCAFaderLevelCmdString = '/dca/{}/fdr'.format(qualifier['DCA'])
            self.__UpdateHelper('DCAFaderLevel', DCAFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderLevel')

    def __MatchDCAFaderLevel(self, match, tag):

        qualifier = {'DCA' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('DCAFaderLevel', value, qualifier)

    def SetDCAFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['DCA']) <= 16 and value in ValueStateValues:
            if int(qualifier['DCA']) >= 10:
                DCAFaderMuteCmdString = '/dca/{0}/\x00\x00\x00\x00,s\x00\x00mute={1}'.format(qualifier['DCA'], ValueStateValues[value])
            else:
                DCAFaderMuteCmdString = '/dca/{0}/\x00,s\x00\x00mute={1}'.format(qualifier['DCA'], ValueStateValues[value])
            self.__SetHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDCAFaderMute')

    def UpdateDCAFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['DCA']) <= 16:
            DCAFaderMuteCmdString = '/dca/{}/mute'.format(qualifier['DCA'])
            self.__UpdateHelper('DCAFaderMute', DCAFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDCAFaderMute')

    def __MatchDCAFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'DCA' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DCAFaderMute', value, qualifier)

    def SetFXReturnFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['FX Return']) <= 16 and 0 <= value <= 100:
            if int(qualifier['FX Return']) >= 10:
                FXReturnFaderLevelCmdString = '/fx/{0}/\x00,s\x00\x00fxmix={1}'.format(qualifier['FX Return'], value)
            else:
                FXReturnFaderLevelCmdString = '/fx/{0}/\x00\x00,s\x00\x00fxmix={1}'.format(qualifier['FX Return'], value)
            self.__SetHelper('FXReturnFaderLevel', FXReturnFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFXReturnFaderLevel')

    def UpdateFXReturnFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['FX Return']) <= 16:
            FXReturnFaderLevelCmdString = '/fx/{}/fxmix'.format(qualifier['FX Return'])
            self.__UpdateHelper('FXReturnFaderLevel', FXReturnFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFXReturnFaderLevel')

    def __MatchFXReturnFaderLevel(self, match, tag):

        qualifier = {'FX Return' : match.group(1).decode()}
        value = int(match.group(2).decode())
        if 0 <= value <= 100:
            self.WriteStatus('FXReturnFaderLevel', value, qualifier)

    def SetGroupMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Group']) <= 8 and value in ValueStateValues:
            GroupMuteCmdString = '/mgrp/{0}/\x00\x00\x00\x00,s\x00\x00mute={1}'.format(qualifier['Group'], ValueStateValues[value])
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        if 1 <= int(qualifier['Group']) <= 8:
            GroupMuteCmdString = '/mgrp/{}/mute'.format(qualifier['Group'])
            self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def __MatchGroupMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Group' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GroupMute', value, qualifier)

    def SetMainFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Main']) <= 4 and -90.0 <= value <= 10.0:
            MainFaderCmdstring = '/main/{0}/\x00\x00\x00\x00,s\x00\x00fdr={1}'.format(qualifier['Main'], round(float(value), 1))
            self.__SetHelper('MainFaderLevel', MainFaderCmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainFaderLevel')

    def UpdateMainFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Main']) <= 4:
            MainFaderLevelCmdString = '/main/{}/fdr'.format(qualifier['Main'])
            self.__UpdateHelper('MainFaderLevel', MainFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMainFaderLevel')

    def __MatchMainFaderLevel(self, match, tag):

        qualifier = {'Main' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('MainFaderLevel', value, qualifier)

    def SetMainFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Main']) <= 4 and value in ValueStateValues:
            MainMuteCmdString = '/main/{0}/\x00\x00\x00\x00,s\x00\x00mute={1}'.format(qualifier['Main'], ValueStateValues[value])
            self.__SetHelper('MainFaderMute', MainMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMainFaderMute')

    def UpdateMainFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['Main']) <= 4:
            MainFaderMuteCmdString = '/main/{}/mute'.format(qualifier['Main'])
            self.__UpdateHelper('MainFaderMute', MainFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMainFaderMute')

    def __MatchMainFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Main' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MainFaderMute', value, qualifier)

    def SetMatrixFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Matrix']) <= 8 and -90.0 <= value <= 10.0:
            MatrixFaderLevelCmdString = '/mtx/{0}/\x00,s\x00\x00fdr={1}'.format(qualifier['Matrix'], round(float(value), 1))
            self.__SetHelper('MatrixFaderLevel', MatrixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderLevel')

    def UpdateMatrixFaderLevel(self, value, qualifier):

        if 1 <= int(qualifier['Matrix']) <= 8:
            MatrixFaderLevelCmdString = '/mtx/{}/fdr'.format(qualifier['Matrix'])
            self.__UpdateHelper('MatrixFaderLevel', MatrixFaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixFaderLevel')

    def __MatchMatrixFaderLevel(self, match, tag):

        qualifier = {'Matrix' : match.group(1).decode()}
        value = match.group(2).decode()
        value = -90.0 if value == '-oo' else float(value)
        if -90.0 <= value <= 10.0:
            self.WriteStatus('MatrixFaderLevel', value, qualifier)

    def SetMatrixFaderMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Matrix']) <= 8 and value in ValueStateValues:
            MatrixFaderMuteCmdString = '/mtx/{0}/\x00,s\x00\x00mute={1}'.format(qualifier['Matrix'], ValueStateValues[value])
            self.__SetHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixFaderMute')

    def UpdateMatrixFaderMute(self, value, qualifier):

        if 1 <= int(qualifier['Matrix']) <= 8:
            MatrixFaderMuteCmdString = '/mtx/{}/mute'.format(qualifier['Matrix'])
            self.__UpdateHelper('MatrixFaderMute', MatrixFaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrixFaderMute')

    def __MatchMatrixFaderMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Matrix' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MatrixFaderMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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