from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
                 'AudioMute': {'Status': {}},
                 'ExecutiveMode': {'Status': {}},
                 'FollowSubMode': {'Status': {}},
                 'Input': {'Status': {}},
                 'InputSeparateSwitcherMode': {'Parameters': ['Group'], 'Status': {}},
                 'MicVolume': {'Status': {}},
                 'MicMix': {'Status': {}},
                 'MicTalkOverThreshold': {'Status': {}},
                 'PhantomPower': {'Status': {}},
                 'ProgramAudioBreakaway': {'Status': {}},
                 'ProgramAudioDuckingLevel': {'Status': {}},
                 'ProgramVolume': {'Status': {}},
                 'SwitcherMode': {'Status': {}},
                 }

        if self.Unidirectional == 'False':
            self._InputRegex = re.compile(r'Mod(?P<mode>1|2) 1G(?P<vga_in>[0-4]) 2G(?P<svid_in>[0-4]) 3G(?P<vid_in>[0-4]) 4G=(?P<single_in>[1-3]G[0-4])\n\r')

    def SetAudioMute(self, value, qualifier):

        amute_cmd = {
            'Off': '0Z',
            'On': '1Z'
        }

        self.__SetHelper('AudioMute', amute_cmd[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        amute_states = {
                        '0': 'Off',
                        '1': 'On'
                        }

        res = self.__UpdateHelper('AudioMute', 'Z', value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', amute_states[res[0]], None)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected response'])

    def SetExecutiveMode(self, value, qualifier):

        lock_cmds = {
                      'Off': '0X',
                      'Mode 1': '1X',
                      'Mode 2': '2X'
                    }

        self.__SetHelper('ExecutiveMode', lock_cmds[value], value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        lock_states = {
                          '0': 'Off',
                          '1': 'Mode 1',
                          '2': 'Mode 2'
                        }

        res = self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)
        if res:
            try:
                self.WriteStatus('ExecutiveMode', lock_states[res[0]], None)
            except KeyError:
                self.Error(['Executive Mode: Invalid/Unexpected response'])

    def SetFollowSubMode(self, value, qualifier):

        fsm_cmd = {
                   'On': '1*4#',
                   'Off': '0*4#'
                  }

        self.__SetHelper('FollowSubMode', fsm_cmd[value], value, qualifier)

    def UpdateFollowSubMode(self, value, qualifier):

        fsm_states = {
                       '0': 'Off',
                       '1': 'On'
                     }

        res = self.__UpdateHelper('FollowSubMode', '4#', value, qualifier)
        if res:
            if res.startswith('Fsm'):
                try:
                    self.WriteStatus('FollowSubMode', fsm_states[res[3]], None)
                except (KeyError, IndexError):
                    self.Error(['Follow Sub Mode: Invalid/Unexpected response'])

    def SetInput(self, value, qualifier):

        input_cmds = {
                  '0': '0!',
                  '1': '1!',
                  '2': '2!',
                  '3': '3!',
                  '4': '4!',
                  '5': '5!',
                  '6': '6!',
                  '7': '7!',
                  '8': '8!',
                  '9': '9!',
                  '10': '10!',
                  '11': '11!',
                  '12': '12!'
                  }

        self.__SetHelper('Input', input_cmds[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        smode_states = {
                         '1': 'Single',
                         '2': 'Separate'
                        }

        inputs = {
                  0: '0',
                  1: '1',
                  2: '2',
                  3: '3',
                  4: '4',
                  5: '5',
                  6: '6',
                  7: '7',
                  8: '8',
                  9: '9',
                  10: '10',
                  11: '11',
                  12: '12'
                  }

        prog_aud_in = {
                       1: 'VGA 1',
                       2: 'VGA 2',
                       3: 'VGA 3',
                       4: 'VGA 4',
                       5: 'S-Video 1',
                       6: 'S-Video 2',
                       7: 'S-Video 3',
                       8: 'S-Video 4',
                       9: 'Video 1',
                       10: 'Video 2',
                       11: 'Video 3',
                       12: 'Video 4'
                       }

        res = self.__UpdateHelper('Input', 'I', value, qualifier)
        if res:
            match=self._InputRegex.match(res)
            if(match):

                mode=smode_states[match.group('mode')]
                self.WriteStatus('SwitcherMode', mode, None)

                in_group=int(match.group('single_in')[0])
                in_num=int(match.group('single_in')[2])
                input_number=4 * (in_group - 1) + in_num

                if not (0 <= input_number <= 12):
                    self.Error(['Input: Invalid/Unexpected response'])
                    return

                if mode is 'Single':
                    self.WriteStatus('Input', inputs[input_number], None)
                    self.WriteStatus('InputSeparateSwitcherMode', 'Not Applicable', {'Group': 'VGA'})
                    self.WriteStatus('InputSeparateSwitcherMode', 'Not Applicable', {'Group': 'S-Video'})
                    self.WriteStatus('InputSeparateSwitcherMode', 'Not Applicable', {'Group': 'Video'})
                    self.WriteStatus('ProgramAudioBreakaway', 'Not Applicable', None)
                else:
                    self.WriteStatus('Input', 'Not Applicable', None)
                    self.WriteStatus('InputSeparateSwitcherMode', inputs[int(match.group('vga_in'))], {'Group': 'VGA'})
                    self.WriteStatus('InputSeparateSwitcherMode', inputs[int(match.group('svid_in'))], {'Group': 'S-Video'})
                    self.WriteStatus('InputSeparateSwitcherMode', inputs[int(match.group('vid_in'))], {'Group': 'Video'})
                    if in_num > 0:
                        self.WriteStatus('ProgramAudioBreakaway', prog_aud_in[input_number], None)
                    else:
                        self.WriteStatus('ProgramAudioBreakaway', '0', None)
            else:
                self.Error(['Input: Invalid/Unexpected response'])

    def SetInputSeparateSwitcherMode(self, value, qualifier):

        GroupStates={
            'VGA': '1',
            'S-Video': '2',
            'Video': '3'
        }

        input_cmds = {
                  '0'   : '0!',
                  '1'   : '1!',
                  '2'   : '2!',
                  '3'   : '3!',
                  '4'   : '4!',
                  }
        group = qualifier['Group']
        InputSeparateSwitcherModeCmdString = '{}*{}'.format(group, input_cmds[value])
        self.__SetHelper('InputSeparateSwitcherMode', InputSeparateSwitcherModeCmdString, value, qualifier)
    def SetMicMix(self, value, qualifier):

        mix_cmd = {
                   'On'  : '1M',
                   'Off' : '0M'
                  }

        self.__SetHelper('MicMix', mix_cmd[value], value, qualifier)
    def UpdateMicMix(self, value, qualifier):

        mix_states = {
                       '0' : 'Off',
                       '1' : 'On'
                     }

        res = self.__UpdateHelper('MicMix', 'M', value, qualifier)
        if res and res.strip().isnumeric():

            self.WriteStatus('MicMix', mix_states[res[0]], None)           
        else:
            self.Error(['Mic Mix: Invalid/Unexpected response'])
    
    def SetMicTalkOverThreshold(self, value, qualifier):

        threshold_range = {
                           'min' : 0,
                           'max' : 15
                          }
        
        if threshold_range['min'] <= value <= threshold_range['max']:
            self.__SetHelper('MicTalkOverThreshold', '{0}*2#'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicTalkOverThreshold')
    def UpdateMicTalkOverThreshold(self, value, qualifier):

        res = self.__UpdateHelper('MicTalkOverThreshold', '2#', value, qualifier)
        if res and res.strip().isnumeric():

            self.WriteStatus('MicTalkOverThreshold', int(res), None)            
        else:
            self.Error(['Mic Talk Over Threshold: Invalid/Unexpected response'])            
    
    def SetMicVolume(self, value, qualifier):

        level_range = {
                        'min' : -66,
                        'max' : 12
                        }
        
        if level_range['min'] <= value <= level_range['max']:

            sis_cmd = 'g'
            if value > -1: 
                sis_cmd = 'G'

            self.__SetHelper('MicVolume', '16*{0}{1}'.format(abs(value), sis_cmd), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicVolume')
    def UpdateMicVolume(self, value, qualifier):

        res = self.__UpdateHelper('MicVolume', '16G', value, qualifier)
        if res:
            res = res.strip()


            try:
                if res[1:].isnumeric():
                    self.WriteStatus('MicVolume', int(res), None)                   
            except (IndexError,ValueError):
                self.Error(['Mic Volume: Invalid/Unexpected response'])            

    def SetPhantomPower(self, value, qualifier):

        ppower_cmd = {
                      'On'  : '1*57#',
                      'Off' : '0*57#'
                      }

        self.__SetHelper('PhantomPower', ppower_cmd[value], value, qualifier)
    def UpdatePhantomPower(self, value, qualifier):

        ppower_states = {
                         '0' : 'Off',
                         '1' : 'On'
                        }

        res = self.__UpdateHelper('PhantomPower', '57#', value, qualifier)
        if res:
            if res.startswith('Mfp'):
                try:
                    self.WriteStatus('PhantomPower', ppower_states[res[3]], None)                   
                except (KeyError, IndexError):                  
                    self.Error(['Phantom Power: Invalid/Unexpected response'])
   
    def SetProgramVolume(self, value, qualifier):

        volume_range = {
                        'min' : 0,
                        'max' : 100
                        }
        
        if volume_range['min'] <= value <= volume_range['max']:
            self.__SetHelper('ProgramVolume', '{0}V'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramVolume')
    def UpdateProgramVolume(self, value, qualifier):

        res = self.__UpdateHelper('ProgramVolume', 'V', value, qualifier)
        if res:
            try:
                if res.startswith('Vol'):
                    self.WriteStatus('ProgramVolume', int(res[3:]), None)                   
            except (IndexError, ValueError):
                self.Error(['Program Volume: Invalid/Unexpected response'])       

    def SetProgramAudioDuckingLevel(self, value, qualifier):

        level_range = {
                        'min' : 0,
                        'max' : 30
                        }
        
        if level_range['min'] <= value <= level_range['max']:
            self.__SetHelper('ProgramAudioDuckingLevel', '{0}*58#'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramAudioDuckingLevel')
    def UpdateProgramAudioDuckingLevel(self, value, qualifier):

        res = self.__UpdateHelper('ProgramAudioDuckingLevel', '58#', value, qualifier)
        if res:
            res = res.strip()
            try:
                if res.startswith('Adl') and res[3:].isnumeric:
                    self.WriteStatus('ProgramAudioDuckingLevel', int(res[3:]), None)                   
            except (IndexError, ValueError):
                self.Error(['Program Audio Ducking Level: Invalid/Unexpected response'])
            
    def SetProgramAudioBreakaway(self, value, qualifier):

        prog_aud_in = {
                       'VGA 1'     : '1*1$',
                       'VGA 2'     : '1*2$',
                       'VGA 3'     : '1*3$',
                       'VGA 4'     : '1*4$',
                       'S-Video 1' : '2*1$',
                       'S-Video 2' : '2*2$',
                       'S-Video 3' : '2*3$',
                       'S-Video 4' : '2*4$',
                       'Video 1'   : '3*1$',
                       'Video 2'   : '3*2$',
                       'Video 3'   : '3*3$',
                       'Video 4'   : '3*4$'
                       }
        
        self.__SetHelper('ProgramAudioBreakaway', prog_aud_in[value], value, qualifier)
    def SetSwitcherMode(self, value, qualifier):

        smode_cmd = {
                      'Single'   : '1*1#',
                      'Separate' : '2*1#'
                      }

        self.__SetHelper('SwitcherMode', smode_cmd[value], value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        errors = {
                  'E01\r\n' : 'Invalid input channel number',
                  'E10\r\n' : 'Invalid command',
                  'E13\r\n' : 'Invalid value'
                  }

        if response in errors.keys():
            self.Error(['{}: {}'.format(sourceCmdName,errors[response])])
            return ''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
        if not res:
            return ''
        else:
            return self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        
        if self.Unidirectional == 'False':

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n' if command != 'Input' else b'\n\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

