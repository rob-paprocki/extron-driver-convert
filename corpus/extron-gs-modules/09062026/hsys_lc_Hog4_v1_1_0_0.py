from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'GoCueinCuelist': {'Parameters':['Cuelist'], 'Status': {}},
            'GoCuelist': { 'Status': {}},
            'GoMacro': { 'Status': {}},
            'GoScene': { 'Status': {}},
            'HaltCuelist': { 'Status': {}},
            'HaltMacro': { 'Status': {}},
            'HaltScene': { 'Status': {}},
            'ReleaseCuelist': { 'Status': {}},
            'ReleaseMacro': { 'Status': {}},
            'ReleaseScene': { 'Status': {}},
            'ResumeCuelist': { 'Status': {}},
            'ResumeMacro': { 'Status': {}},
            'ResumeScene': { 'Status': {}},
        }

    def pad(self, value):

        if not isinstance(value, str):
            raise ValueError()

        to_pad = 4 - (len(value) % 4)
        return (value + ('\x00' * to_pad)).encode(encoding='iso-8859-1')

    def build_set_string(self, command):

        try:
            command = self.pad(command)
            command += b',f\x00\x00\x00\x00\x00\x00'
            return command

        except ValueError:
            self.Discard('Invalid Command')

    def SetGoCueinCuelist(self, value, qualifier):

        if 1 <= value <= 32768 and 1 <= qualifier['Cuelist'] <= 32768:
            GoCueinCuelistCmdString = self.build_set_string('/hog/playback/go/0/{0}.{1}'.format(qualifier['Cuelist'], value))
            self.__SetHelper('GoCueinCuelist', GoCueinCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoCueinCuelist')

    def SetGoCuelist(self, value, qualifier):

        if 1 <= value <= 32768:
            GoCuelistCmdString = self.build_set_string('/hog/playback/go/0/{}'.format(value))
            self.__SetHelper('GoCuelist', GoCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoCuelist')

    def SetGoMacro(self, value, qualifier):

        if 1 <= value <= 32768:
            GoMacroCmdString = self.build_set_string('/hog/playback/go/2/{}'.format(value))
            self.__SetHelper('GoMacro', GoMacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoMacro')

    def SetGoScene(self, value, qualifier):

        if 1 <= value <= 32768:
            GoSceneCmdString = self.build_set_string('/hog/playback/go/1/{}'.format(value))
            self.__SetHelper('GoScene', GoSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGoScene')

    def SetHaltCuelist(self, value, qualifier):

        if 1 <= value <= 32768:
            HaltCuelistCmdString = self.build_set_string('/hog/playback/halt/0/{}'.format(value))
            self.__SetHelper('HaltCuelist', HaltCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHaltCuelist')

    def SetHaltMacro(self, value, qualifier):

        if 1 <= value <= 32768:
            HaltMacroCmdString = self.build_set_string('/hog/playback/halt/2/{}'.format(value))
            self.__SetHelper('HaltMacro', HaltMacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHaltMacro')

    def SetHaltScene(self, value, qualifier):

        if 1 <= value <= 32768:
            HaltSceneCmdString = self.build_set_string('/hog/playback/halt/1/{}'.format(value))
            self.__SetHelper('HaltScene', HaltSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHaltScene')

    def SetReleaseCuelist(self, value, qualifier):

        if 1 <= value <= 32768:
            ReleaseCuelistCmdString = self.build_set_string('/hog/playback/release/0/{}'.format(value))
            self.__SetHelper('ReleaseCuelist', ReleaseCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleaseCuelist')

    def SetReleaseMacro(self, value, qualifier):

        if 1 <= value <= 32768:
            ReleaseMacroCmdString = self.build_set_string('/hog/playback/release/2/{}'.format(value))
            self.__SetHelper('ReleaseMacro', ReleaseMacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleaseMacro')

    def SetReleaseScene(self, value, qualifier):

        if 1 <= value <= 32768:
            ReleaseSceneCmdString = self.build_set_string('/hog/playback/release/1/{}'.format(value))
            self.__SetHelper('ReleaseScene', ReleaseSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReleaseScene')
            
    def SetResumeCuelist(self, value, qualifier):

        if 1 <= value <= 32768:
            ResumeCuelistCmdString = self.build_set_string('/hog/playback/resume/0/{}'.format(value))
            self.__SetHelper('ResumeCuelist', ResumeCuelistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResumeCuelist')

    def SetResumeMacro(self, value, qualifier):

        if 1 <= value <= 32768:
            ResumeMacroCmdString = self.build_set_string('/hog/playback/resume/2/{}'.format(value))
            self.__SetHelper('ResumeMacro', ResumeMacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResumeMacro')

    def SetResumeScene(self, value, qualifier):

        if 1 <= value <= 32768:
            ResumeSceneCmdString = self.build_set_string('/hog/playback/resume/1/{}'.format(value))
            self.__SetHelper('ResumeScene', ResumeSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResumeScene')

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])