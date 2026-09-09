''''

The code below includes concepts not normally included in AV systems programming.
As such, a Safety Pig has been included for your comfort.

                         _
 _._ _..._ .-',     _.._(`))
'-. `     '  /-._.-'    ',/
   )         \            '.
  / _    _    |             \
 |  a    a    /              |
 \   .-.                     ;
  '-('' ).-'       ,'       ;
     '-;           |      .'
        \           \    /
        | 7  .__  _.-\   \
        | |  |  ``/  /`  /
       /,_|  |   /,_/   /
          /,_/      '`-'

'''



## Begin ControlScript Import --------------------------------------------------
sys_allowed_flag = True
try:
    import sys,traceback
except:
    sys_allowed_flag = False
from extronlib import event as _event
from extronlib.device import UIDevice as _UIDevice
from extronlib.device import ProcessorDevice as _ProcessorDevice
from extronlib.device import SPDevice as _SPDevice
from extronlib.interface import (CircuitBreakerInterface as _CircuitBreakerInterface, ContactInterface as _ContactInterface,
    DanteInterface as _DanteInterface,DigitalInputInterface as _DigitalInputInterface, DigitalIOInterface as _DigitalIOInterface, EthernetClientInterface as _EthernetClientInterface,
    EthernetServerInterfaceEx as _EthernetServerInterfaceEx, FlexIOInterface as _FlexIOInterface, IRInterface as _IRInterface, PoEInterface as _PoEInterface,
    RelayInterface as _RelayInterface, SerialInterface as _SerialInterface, SWACReceptacleInterface as _SWACReceptacleInterface, SWPowerInterface as _SWPowerInterface,
    VolumeInterface as _VolumeInterface,SPInterface as _SPInterface,TallyInterface as _TallyInterface)
from extronlib.ui import Button as _Button, Knob as _Knob, Label as _Label, Level as _Level, Slider as _Slider
from extronlib.system import Timer as _Timer, Wait as _Wait, File as _File, SaveProgramLog as _SaveProgramLog, ProgramLog as _ProgramLog
from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
import queue as _queue
import json as _json

"""
Author: Jean-Luc Rioux
Company: Valley Communications
Last Modified Date: 2023-01-02
Version: 1.6.0.0
Minimum Pro Controller FW: 3.10

Changelog:
    v 1.0 - initial release
    v 1.1 - InterfaceWrapper : added support for SPIInterface
    v 1.2 - severe reworking :
        + added support for all interfaces in extronlib.interface except ClientObject and DanteInterface
        + reworked interface modules to make them easier to use, no longer require listening_port or friendly_name
            - these will be auto-generated for you if not supplied
    v 1.2.1 - some corrections to interface type handling.
    v 1.2.2 - added pacing when registering interfaces with debug client.
    v 1.3   - debug tool.py and client modifications.
        - debug client program now closes more gracefully upon exit.
        - for writestatus and set commands in debug tool, we now have type selection
        - corrected an issue preventing options from showing for SSH connections in client
        - corrected a typo in StatusReport class preventing the server from starting
    v 1.4   - debug tool.py and client modifications
        - added support for ProcessorDevice
        - added support for UIDevice
        - added support for VirtualUI
        - added disconnect function
        - added 'Save Current Logs' and 'Save Current Status' functions
        - added 'Save All Logs' and 'Save All Status' functions
        - cleaned up some formatting
    v 1.4.1  - debug tool.py modifications
        - fixed a 'reference before assignment issue'
        - changed commtype of serialoverethernetwrapper from 'Serial' to 'Ethernet' under the hood
        - network interface connect() now returns the result of the interface's connect() instad of None
        - surrounded problematic TP polling functions with try/catch
    v 1.4.2  - debug tool.py modifications
        - in tools.py added option to print or not to print into the trace window basic debug info for each wrapper instance.
        - in the client, option added to enable or disable the feature per device
        - in the client, added color-coding to online or offline devices.
            - if the property is not available, the text will be blue
            - if the device is 'Online' or 'Connected', the text will be green
            - if the device is 'Offline' or 'Disconnected' or 'Not Connected', the text will be red
    v 1.4.3  - debug client modifications
        - color indications on device connectivity has been corrected
    v 1.4.3.1 - tools.py modificadations
        - now has passive log to file features
            - set EnableFileLogging to True on any wrapped device/interface to enable the logging.
            - automatically manages RAM usage to prevent over 90% RAM usage
        - in cases of secondary processors defined, model information cannot be recalled.. surrounded this by a try/catch
        - now writes NVRAM, ProgramLogs, and DebugLogs to separate directories in storage.
        - ProgramLogSaver class no longer needs to be instantiated, it just begins upon import to namespace.
    v 1.4.3.2 - tools.py modifications
        - integrated DebugFileLogSaver to interface classes
            -this saves logs as csv files on the controller, manages storage utilization (max 90%)
    v 1.4.3.3 - tools.py modifications
        - corrected an issue retrieving instances of device modules from the wrapper
            - previously, it was retrieving the device module definition, not the instance of the module after Create_Device is run
    v 1.4.3.4 - tools.py modifications
        - polished the auto-reconnect feature so that it pushes to trace and logs for every attempt to connect
        - moved ModuleSubscribeWrapper to be a private class of __InterfaceWrapper
        - added an underscore to imports that users wont care about. this puts all of the ones relevant to implementation on top of the import list for intellisense
    v 1.4.3.5 - tools.py modifications
        - corrected connection feedback issue with SSH connections
    v 1.4.3.6 - tools.py modification
        - handled possible exceptions writing logs to file by preventing attempts to write bad data.
    v 1.4.3.7 - tools.py modification
        - corrected bug when adding an ID or panel in the VirtualTP device that already existed in the instance, no further items in the list would be added.
            now it passes over the duplicate item and continues processing the remainder of the list.
    v 1.4.3.8 - tools.py modification and debug tool modification
        - fixed passthru command for device modules.
    v 1.4.3.9 - tools.py modification
        - incorporated the use of the Queue class to process collection of logs for debug logging features to hopefully avoid race conditions.
    v 1.4.4.0 - tools.py modification and debug tool modification
        - added support to emulate button, knob, and slider events from virtualUI device.
        - put deleteoldestlog in a timer so that it more reliably keeps usage from filling up.
    v 1.4.4.0 - tools.py modification and debug tool modification
        - added support for SPDevice via SPDeviceWrapper
    v 1.4.4.1 - tools.py modification
        - correct an issue preventing SPI device modules from running Update/Set commands in modules
    v 1.5.0.0 - tools.py modification and debug tool modification
        - added DebugPrint class to tools.py and debug tool.
        - changed UI layout and flow in debug tool.
        - added checkbox tree implementation and filter to log view.
    v 1.5.0.1 - tools.py modification
        - improved debug information to logs.
        - added debug printing to happen via the DebugPrint class by default when using tools.py tools.
    v 1.6.0.0 - tools.py modification
        - Added DanteInterfaceWrapper.
"""












'''
creates a dictionary of devices with their values.  upon connection to the given ip port, prints the dictionary in json format to telnet interface.
also prints updates to these values as they occur.

example:

from tools import status_report


sr = status_report(3001)
sr.update('Display','ConnectionStatus','Connected')


'''
class status_report():
    def __init__(self,listening_port=2000,interface='AVLAN'):
        self.__listening_port = listening_port
        self.__clientCount = 0
        self.__fb_function = None
        self.__info = {}
        self.__serv= _EthernetServerInterfaceEx(self.__listening_port,'TCP',Interface=interface,MaxClients=5)
        self.__startServer()
        self.__startEvents()
    def __register(self,d:'str',s:'str'):
        self.__info[d] = {'statuses':{s:''}}
    def __send_single(self,d:'str',s:'str'):
        j = {}
        j[d] = {'statuses':{s:self.__info[d]['statuses'][s]}}
        data = _json.dumps(j)
        self.__send(data)
    def __send_all(self):
        data = _json.dumps(self.__info)
        self.__send(data)
    def __startServer(self):
        """Start the server.  Reattempt on failure after 1s."""
        print('StatusReport:startServer: port {} starting'.format(self.__listening_port))
        res = self.__serv.StartListen()
        if res != 'Listening':   # Port unavailable
            print('StatusReport:startServer: port {} unavailable: result={}'.format(self.__listening_port,res))
            _Wait(1, self.__startServer)
    def __send(self, string):
        if(self.__clientCount > 0):
            for client in self.__serv.Clients:
                client.Send('{0}'.format(string))
    def __startEvents(self):
        @_event(self.__serv, 'ReceiveData')
        def HandheReceiveFromServer(client,data:'bytes'):
            if self.__fb_function != None:
                data = data.decode()
                self.__fb_function(data)
        @_event(self.__serv, 'Connected')
        def HandleClientConnect(interface, state):
            self.__clientCount += 1
            print('status_report:Client connected to {0} ({1}).'.format(self.__listening_port,interface.IPAddress))
            self.__send_all()
        @_event(self.__serv, 'Disconnected')
        def HandleClientDisconnect(interface, state):
            self.__clientCount = 0
            print('status_report:Client disconnected from {0}).'.format(self.__listening_port))
            self.__serv.StopListen()
            self.__startServer()

    def Update(self,d:'str',s:'str',v):
        if d not in self.__info:
            self.__register(d,s)
        self.__info[d]['statuses'][s] = v
        if self.__clientCount > 0:
            self.__send_single(d,s)
    def SendCustom(self,data):
        self.__send(data)
    def SetFbFunction(self,f):
        self.__fb_function = f













'''
saves a dictionary of values (basic types only) to file as a json object, allows for manipulation of them and recovery.
the optional parameter 'auto_sync_time' allows for saving of the variables to file automatically on a regular interval. (in seconds)

multiple callback functions may be added as needed to make code more readable, not all variables need to be handled in the same callback.

example:

from tools import NonvolatileValues

#default startup values
var1 = ''
var2 = 0
var3 = [False,False]

nvram = NonvolatileValues('filename.dat')
def handle_nvram_var1_var2(values:'dict'):
    global var1
    global var2

    if 'var1key' in values:
        var1 = values['var1key']
    if 'var2key' in values:
        var2 = values['var2key']

def handle_nvram_var3(values:'dict'):
    global var3
    if 'var3key' in values:
        var3 = values['var3key']

nvram.AddSyncValuesFunction(handle_nvram_var1_var2)
nvram.AddSyncValuesFunction(handle_nvram_var3)
nvram.ReadValues()


def update_nvram():
    global var1
    global var2
    global var3
    var1 = 'new value'
    var2 = 1
    var3[1] = True

    nvram.SetValue('var1key',var1)
    nvram.SetValue('var2key',var2)
    nvram.SetValue('var3key',var3)
    nvram.SaveValues() # must be explicitly saved after updating if 'auto_sync_time' not used.
'''
class NonvolatileValues():
    if not _File.Exists('/NVRAM/'):
        _File.MakeDir('/NVRAM/')
    def __init__(self,filename:'str',auto_sync_time:'float'= None) -> None:
        self.__filename = '/NVRAM/{}'.format(filename)
        self.__auto_sync_time = auto_sync_time
        self.values = {}
        self.__syncvaluesfunctions = []

        if self.__auto_sync_time:
            @_Timer(self.__auto_sync_time)
            def auto_sync_function(timer,count):
                self.SaveValues()


    def ReadValues(self):
        f = None
        values = {}
        try:
            f = _File(self.__filename,'r')
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'ReadValues',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
        if f:
            try:
                values = _json.load(f)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:deleting corrupted file'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:deleting corrupted file'.format(__class__.__name__,'ReadValues',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                _File.DeleteFile(self.__filename)
            f.close()
        self.values = values
        if self.__syncvaluesfunctions:
            for f in self.__syncvaluesfunctions:
                f(self.values)

    def SetValue(self,id:'str',value):
        self.values[id] = value

    def GetValue(self,id:'str'):
        return self.values[id]

    def GetAllValues(self):
        if self.__syncvaluesfunctions:
            for f in self.__syncvaluesfunctions:
                f(self.values)

    def SaveValues(self):
        f = None
        try:
            f = _File(self.__filename,'w') #try writing
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'SaveValues',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
        if f:
            try:
                _json.dump(self.values,f)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'SaveValues',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            f.close()
        self.ReadValues()


    def AddSyncValuesFunction(self,func):
        self.__syncvaluesfunctions.append(func)












'''
Simply import this file into your main file to enable the logging.
This class creates one log file per boot and updates that particular log file whenever the program log changes. (checks for changes every 1 minute)
The check runs in its own thread so errors elsewhere in the program should not interfere with this logging.

implementation:
import ProgramLogSaver


'''

class ProgramLogSaver():
    if not _File.Exists('/ProgramLogs/'):
        _File.MakeDir('/ProgramLogs/')
    __now = _datetime.now()
    __nowstr = __now.strftime('%Y-%m-%d-%H-%M-%S')
    __filename = '/ProgramLogs/{}-{}.log'.format('ProgramLog',__nowstr)
    __cur_log = ''

    def __readdummyprogramlog():
        f = None
        log = None
        try:
            f = _File('/ProgramLogs/temp.log','r')
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__readdummyprogramlog',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
        if f:
            try:
                log = f.read()
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__readdummyprogramlog',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            f.close()
        return log


    def __saveprogramlog():
        try:
            with _File(ProgramLogSaver.__filename, 'w') as f:
                _SaveProgramLog(f)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__saveprogramlog',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)

    def __savedummyprogramlog():
        try:
            with _File('/ProgramLogs/temp.log', 'w') as f:
                _SaveProgramLog(f)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__savedummyprogramlog',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)

    def __checkprogramlog(timer,count):
        ProgramLogSaver.__savedummyprogramlog()
        log = ProgramLogSaver.__readdummyprogramlog()
        if log != ProgramLogSaver.__cur_log:
            ProgramLogSaver.__cur_log = log
            ProgramLogSaver.__saveprogramlog()
            print('ProgramLogSaver: new log saved')

    def EnableProgramLogSaver():
        ProgramLogSaver.__save_timer = _Timer(60,ProgramLogSaver.__checkprogramlog)
        ProgramLogSaver.__save_timer.Restart()










'''
This class creates hourly log files, appending a queue of date-timestamped logs to the file every minute.
The logs are stored in CSV format for easy import into spreadsheet software.

Used in combination with any of the class wrappers below, but can be used independantly with the AddLog function.
If SetProcessorAlias is not used, the logging WILL eventually completely fill device storage because usage wont be checked: this is bad.

implementation:
import DebugFileLogSaver # MUST be included somewhere in main file
DebugFileLogSaver.SetProcessorAlias('ProcessorAlias') # MUST be included somewhere in main file
#optional in case you wish new files not to be created exactly on the hour
DebugFileLogSaver.SetFileOffsetMinutes(15) # new file will be created 15 past the hour

'''
class DebugFileLogSaver():
    __init_log = 'Timestamp,Device Name,MessageType,Data'
    __cur_logs = [__init_log]
    __log_dump_time = False
    __cur_logs_queue = _queue.Queue()
    __offset_minutes = 0
    __processor_device = None #type:_ProcessorDevice

    if not _File.Exists('/DebugLogs/'):
        _File.MakeDir('/DebugLogs/')

    def __getfilename():
        now = _datetime.now()
        offset_minutes = _timedelta(minutes=DebugFileLogSaver.__offset_minutes)
        adj = now-offset_minutes
        adjstr = adj.strftime('%Y-%m-%d-%H')
        return '/DebugLogs/{}-{}.csv'.format('DebugLog',adjstr)

    def __deleteoldestlog():
        dirlist = _File.ListDir('/DebugLogs/')
        if len(dirlist):
            dirlist.sort()
            deletefilename = '/DebugLogs/{}'.format(dirlist[0])
            _File.DeleteFile(deletefilename)
            print('DebugFileLogSaver:RAM usage over 90%, deleted oldest file:{}'.format(deletefilename))

    def __dump_logs(timer,count):
        DebugFileLogSaver.__log_dump_time = True
    __save_timer = _Timer(60,__dump_logs)#__checklog)
    __save_timer.Restart()

    def __deleteoldestlogtimer(timer:'_Timer',count:'int'):
        try:
            usage = DebugFileLogSaver.__processor_device.UserUsage
        except Exception as e:
            DebugFileLogSaver.__deleteoldestlog()
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__deleteoldestlogtimer',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
            return
        try:
            usage_percent = usage[0] / usage[1]
        except:
            usage_percent = 0.0
        if usage_percent > 0.90:
            DebugFileLogSaver.__deleteoldestlog()
        else:
            timer.Stop()
    __deletelog_timer = _Timer(1,__deleteoldestlogtimer)

    def __checklogloop():
        while True:
            DebugFileLogSaver.__cur_logs.append(DebugFileLogSaver.__cur_logs_queue.get())
            if DebugFileLogSaver.__log_dump_time:
                DebugFileLogSaver.__log_dump_time = False
                size = DebugFileLogSaver.__cur_logs_queue.qsize()
                if size:
                    print('DebugFileLogSaver: logs outstanding in queue:{}'.format(size))
                if DebugFileLogSaver.__processor_device is not None:
                    DebugFileLogSaver.__deletelog_timer.Restart()
                else:
                    _ProgramLog('DebugFileLog is missing Processor Alias, use SetProcessorAlias() to rectify',Severity='warning')
                    DebugFileLogSaver.__cur_logs = [DebugFileLogSaver.__init_log]
                    return
                if len(DebugFileLogSaver.__cur_logs) > 1:
                    filename = DebugFileLogSaver.__getfilename()
                    f = None
                    try:
                        f = _File(filename, 'a')
                    except:
                        print('DebugFileLogSaver: Could not open file:{}'.format(filename))
                    if f:
                        try:
                            f.write('\n'.join(DebugFileLogSaver.__cur_logs))
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}'.format(__class__.__name__,'__checklogloop',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
                        f.close()
                    print('DebugFileLogSaver:added {} logs to file:{}'.format(len(DebugFileLogSaver.__cur_logs),filename))
                    DebugFileLogSaver.__cur_logs = [DebugFileLogSaver.__init_log]
    __save_wait = _Wait(1,__checklogloop)
    __save_wait.Restart()

    def AddLog(device='Undefined',message_type='Undefined',data=b''):
        data = repr(data)
        timestamp = str(_datetime.now())
        str_to_send = '{},{},{},{}'.format(timestamp,device,message_type,data)
        #DebugFileLogSaver.__cur_logs.append(str_to_send)
        DebugFileLogSaver.__cur_logs_queue.put(str_to_send)

    def SetFileOffsetMinutes(minutes:int):
        DebugFileLogSaver.__offset_minutes = minutes


    def SetProcessorAlias(processor_alias:str):
        DebugFileLogSaver.__processor_device = _ProcessorDevice(processor_alias)















"""
This class creates a listening server to assist in debugging communication.
This module supports MULTIPLE receivedata functions.
This can be useful if you wish to parse feedback outside the module.
It also automatically impliments the subscribe helper class.
For Dante, Ethernet, SSH, and Serial Over Ethernet connections, this class automatically maintains the connection for you.
reattempting every 10 seconds.


INSTRUCTIONS on integrating with an Extron authored module, top-down:
1.  No modifications to Extron's device module in nearly all cases. also works on custom modules done in the Extron module format.
2.  Implement the module as below:
    from tools import DebugServer,EthernetModuleWrapper
    DebugServer.EnableDebugServer('LAN') # include this line to enable collective debugging on a single port. options 'LAN','AVLAN'
    from opto_vp_UHD60_v1_0_1_0 import DeviceClass as projector_mod
    dev_projector = EthernetModuleWrapper(projector_mod,friendly_name='Projector')
    dev_projector.Create_Device('10.0.0.87',2023,Model='UHD60') #usual parameters defined in the extron module documentation
    #to utilize non-standard functions in the device's module
    example:
        dev_projector.DeviceModule.DeviceID=1
3.  Implement device and interface ports as below: if friendly_name parameter is not included, one will be auto-generated
    examples:
        processor = ProcessorDeviceWrapper('Alias',friendly_name='Processor 1')
        fio = FlexIOInterfaceWrapper(Processor,'FIO1',friendly_name='Flex IO 1')
        dio = DigitalIOInterfaceWrapper(Processor,'DIO1',friendly_name='Digital IO 1')
        di = DigitalInputInterfaceWrapper(Processor,'DII1',friendly_name='Digital Input 1')
        c = ContactInterfaceWrapper(Processor,'CII1',friendly_name='Contact 1')
        #if using ProcessorWrapper, use Processor.Device to pass the device inside the wrapper
        relay = RelayInterfaceWrapper(Processor.Device, 'RLY1',friendly_name='Relay 1')

3.  Implement control and feedback normally.
4.  For the @events of processors,interfaces, and ports, use SubscribeStatus('EventName',callbackFunction) instead

NOTES:
 - for module wrappers
    - In constructor, set auto_maintain_connection to False if you wish to handle network connections yourself.
    - In constructor, set time_between_commands to an integer > 0 to force command pacing to prevent device from choking on input. Do this after subscribing to feedback for the device.
"""
class DebugServer():    #class code
    __debug_server = None #type:_EthernetServerInterfaceEx
    __debug_instances = {'options':{}}
    __debug_server_buffer = ''
    __debug_server_password = 'p9oai23jr09p8fmvw98foweivmawthapw4t'
    __debug_server_logged_in = False
    __delim = '~END~\x0a'
    __debug_busy = False
    __debug_send_interface_list_timer = None
    __debug_options = {}
    __debug_nv_options = NonvolatileValues('DebugNVRAM.dat')

    def __debug_nv_sync_function():
        def f(values:'dict'):
            if 'options' in values:
                DebugServer.__debug_options = values['options']
        DebugServer.__debug_nv_options.AddSyncValuesFunction(f)
        DebugServer.__debug_nv_options.ReadValues()

    def EnableDebugServer(Interface='AVLAN'):
        DebugServer.__debug_nv_sync_function()
        if not DebugServer.__debug_server:
            DebugServer.__debug_server = _EthernetServerInterfaceEx(1988,'TCP',Interface=Interface,MaxClients=5)
            __debug_res = DebugServer.__debug_server.StartListen()
            if __debug_res != 'Listening':
                print('DebugServer EnableDebugServer: Failed : {}'.format(__debug_res))
            else:
                print('DebugServer EnableDebugServer: Succeeded on port {}'.format(Interface))

            @_event(DebugServer.__debug_server, 'ReceiveData')
            def HandheReceiveFromServer(client,data:'bytes'):
                DebugServer.__debug_server_buffer += data.decode()
                while DebugServer.__delim in DebugServer.__debug_server_buffer:
                    pos = DebugServer.__debug_server_buffer.index(DebugServer.__delim)
                    temp = DebugServer.__debug_server_buffer[:pos]
                    DebugServer.__debug_server_buffer = DebugServer.__debug_server_buffer[pos+len(DebugServer.__delim)-1]
                    if DebugServer.__debug_server_logged_in and '~Command~:' in temp:
                        pos = temp.index(':')
                        temp = temp[pos+1:]
                        pos = temp.index(':')
                        id = int(temp[:pos])
                        if id in DebugServer.__debug_instances.keys():
                            temp = temp[pos+1:]
                            DebugServer.__debug_instances[id]['instance'].HandleReceiveFromServer(None,temp)
                    elif DebugServer.__debug_server_logged_in and 'exit()' in temp:
                        for client in DebugServer.__debug_server.Clients:
                            client.Send('Disconnecting...{}'.format(DebugServer.__delim))
                            client.Disconnect()
                    elif DebugServer.__debug_server_logged_in and '~Option~' in temp:
                        pos = temp.index(':')
                        temp = temp[pos+1:]
                        pos = temp.index(':')
                        id = int(temp[:pos])
                        if id in DebugServer.__debug_instances.keys():
                            temp = temp[pos+1:]
                            DebugServer.__debug_instances[id]['instance'].HandleOptions(None,temp)
                    elif DebugServer.__debug_server_password in temp:
                        DebugServer.__debug_server_logged_in = True
                        DebugServer.__send_interface_list(None)

                DebugServer.__debug_server_buffer = ''


            @_event(DebugServer.__debug_server, 'Connected')
            def HandleClientConnect(interface, state):
                DebugServer.__debug_client_count = len(DebugServer.__debug_server.Clients)


            @_event(DebugServer.__debug_server, 'Disconnected')
            def HandleClientDisconnect(interface, state):
                DebugServer.__debug_client_count = len(DebugServer.__debug_server.Clients)

    def DisableDebugServer():
        if DebugServer.__debug_server:
            DebugServer.__debug_server_logged_in = False
            DebugServer.__debug_server.StopListen()
            for client in DebugServer.__debug_server.Clients:
                client.Disconnect()
            DebugServer.__debug_sever = None
        print('DebugServer:DisableDebug: Complete')

    def __send_interface_list(self):
        def t(timer:'_Timer',count:'int'):
            if self == None:
                instances = DebugServer.__debug_instances
                server = DebugServer.__debug_server
                delim = DebugServer.__delim
            else:
                instances = self._DebugServer__debug_instances
                server = self._DebugServer__debug_server
                delim = self._DebugServer__delim
            DebugServer.__debug_busy = True
            count = count-1
            result = {}
            keys = list(instances.keys())
            if 'options' in keys:
                keys.remove('options')
            keys.sort()
            if count < len(keys):
                key = keys[count]
                result[key] = {}
                result[key]['name'] = instances[key]['name']
                result[key]['options'] = instances[key]['options']
                result[key]['communication'] = {}
                interface = instances[key]['instance'].GetInterface()
                comm_type = instances[key]['instance'].GetInterfaceType()
                result[key]['type'] = comm_type
                result[key]['communication']['type'] = str(comm_type)
                if comm_type == 'Serial':
                    result[key]['status'] = instances[key]['instance'].device.Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['mode'] = str(interface.Mode)
                    result[key]['communication']['port'] = str(interface.Port)
                    result[key]['communication']['baud'] = '{},{},{},{}'.format(str(interface.Baud),str(interface.Data),str(interface.Parity),str(interface.Stop))
                elif comm_type in ['SerialOverEthernet','Ethernet','SSH']:
                    result[key]['status'] = instances[key]['instance'].device.Commands
                    result[key]['communication']['host'] = str(interface.Hostname)
                    result[key]['communication']['mode'] = str(interface.Protocol)
                    result[key]['communication']['port'] = str(interface.IPPort)
                    result[key]['communication']['serviceport'] = str(interface.ServicePort)
                    result[key]['communication']['credentials'] = str(interface.Credentials)
                elif comm_type in ['Dante']:
                    result[key]['status'] = instances[key]['instance'].device.Commands
                    result[key]['communication']['host'] = str(interface.Hostname)
                    result[key]['communication']['mode'] = str(interface.Protocol)
                    result[key]['communication']['dantedomainmanager'] = str(interface.DanteDomainManager)
                    result[key]['communication']['domain'] = str(interface.Domain)
                elif comm_type == 'SPI':
                    result[key]['status'] = instances[key]['instance'].device.Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                elif comm_type == 'Circuit Breaker':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Contact':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Digital Input':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                    result[key]['communication']['pullup'] = str(interface.Pullup)
                elif comm_type == 'Digital IO':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                    result[key]['communication']['mode'] = str(interface.Mode)
                    result[key]['communication']['pullup'] = str(interface.Pullup)
                elif comm_type == 'Flex IO':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                    result[key]['communication']['mode'] = str(interface.Mode)
                    result[key]['communication']['pullup'] = str(interface.Pullup)
                    result[key]['communication']['upper'] = str(interface.Upper)
                    result[key]['communication']['lower'] = str(interface.Lower)
                elif comm_type == 'IR':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                    result[key]['communication']['file'] = str(interface.File)
                elif comm_type == 'PoE':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Relay':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'SWAC Receptacle':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'SW Power':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Tally':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host.DeviceAlias)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Volume':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['host'] = str(interface.Host)
                    result[key]['communication']['port'] = str(interface.Port)
                elif comm_type == 'Processor':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['alias'] = str(interface.DeviceAlias)
                elif comm_type == 'SPDevice':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['alias'] = str(interface.DeviceAlias)
                elif comm_type == 'UI':
                    result[key]['status'] = instances[key]['instance'].Commands
                    result[key]['communication']['alias'] = str(interface.DeviceAlias)
                elif comm_type == 'VirtualUI':
                    result[key]['status'] = instances[key]['instance'].Commands
                elif comm_type == 'Print':
                    result[key]['status'] = instances[key]['instance'].Commands
                result2 = _json.dumps(result)
                #print('~~~~~~~~~~~~~ debug register device {}'.format(count))
                if server:
                    for client in server.Clients:
                        client.Send('~RegisterDevices~:{}{}'.format(result2,delim))
            else:
                DebugServer.__debug_busy = False
                #print('~~~~~~~~~~~~~ debug register device {} STOP'.format(count))
                timer.Stop()
                return
        if DebugServer.__debug_send_interface_list_timer == None:
            DebugServer.__debug_send_interface_list_timer = _Timer(0.2,t)
            #print('~~~~~~~~~~~~~ debug register CREATE')
        else:
            DebugServer.__debug_busy = False
            #print('~~~~~~~~~~~~~ debug register RESTART')
            DebugServer.__debug_send_interface_list_timer.Restart()
    def __send_interface_status(self,listening_port:'int',update:'dict'):
        to_send = {str(listening_port):update}
        result = _json.dumps(to_send)
        if self._DebugServer__debug_server:
            for client in self._DebugServer__debug_server.Clients:
                client.Send('~UpdateDevices~:{}:{}{}'.format(listening_port,result,self._DebugServer__delim))
    def __send_interface_communication(self,listening_port:'int',txt:'str'):
        if self._DebugServer__debug_server and self._DebugServer__debug_server_logged_in and not self._DebugServer__debug_busy:
            data = {listening_port:txt}
            for client in self._DebugServer__debug_server.Clients:
                client.Send('~UpdateDeviceComs~:{}{}'.format(_json.dumps(data),self._DebugServer__delim))
    def __send_interface_option(listening_port:'int',txt:'str'):
        if DebugServer.__debug_server and DebugServer.__debug_server_logged_in and not DebugServer.__debug_busy:
            data = {listening_port:txt}
            for client in DebugServer.__debug_server.Clients:
                client.Send('~Option~:{}{}'.format(_json.dumps(data),DebugServer.__delim))
    def __add_instance(self,listening_port:'int',instance:'object',friendly_name:'str',instance_type:'str'):
        listening_port = int(listening_port)
        if listening_port not in self._DebugServer__debug_instances.keys():
            self._DebugServer__debug_instances[listening_port] = {}
            self._DebugServer__debug_instances[listening_port]['name'] = friendly_name
            self._DebugServer__debug_instances[listening_port]['instance'] = instance
            self._DebugServer__debug_instances[listening_port]['type'] = instance_type
            try:
                print_to_trace_value = self._DebugServer__debug_options[str(listening_port)]['print to trace']
            except:
                print_to_trace_value = True
            if 'options' not in self._DebugServer__debug_instances[listening_port]:
                self._DebugServer__debug_instances[listening_port]['options'] = {}
            if 'print to trace' not in self._DebugServer__debug_instances[listening_port]['options']:
                self._DebugServer__debug_instances[listening_port]['options'] = {'print to trace':print_to_trace_value}
            temp = {'option':'print to trace','value':print_to_trace_value}
            DebugServer.__debug_instances[listening_port]['instance'].HandleOptions(None,'Option({})'.format(_json.dumps(temp)))
            self._DebugServer__send_interface_list()
    def __create_listening_port(self):
        return 1+len(self._DebugServer__debug_instances)
    def __update_nv_option(self,listening_port:'int',option:'str',value):
        listening_port = str(listening_port)
        if listening_port not in DebugServer.__debug_options:
            DebugServer.__debug_options[listening_port] = {}
        DebugServer.__debug_options[listening_port][option] = value
        DebugServer.__send_interface_option(listening_port,DebugServer.__debug_options[listening_port])
        DebugServer.__debug_nv_options.SetValue('options',DebugServer.__debug_options)
        DebugServer.__debug_nv_options.SaveValues()
    def __get_nv_option(self,listening_port):
        try:
            print_to_trace_value = self._DebugServer__debug_options[str(listening_port)]['print to trace']
        except:
            print_to_trace_value = True
        return print_to_trace_value

class _PrintWrapper(DebugServer):
    def __init__(self,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Print'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)

        self.__interface = self
        self.Commands = {'ConnectionStatus':{'Status':{'Live':'Online'}}}
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = 'command: {}({})'.format(self.__friendly_name,string)
        str_to_send = '{} {}'.format(timestamp,str_to_send)
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleOptions',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
    def Print(self,text):
        self.__print_to_trace('DebugPrint:{}'.format(text))
        self.__printToLog(self.__friendly_name,'Print', '{}'.format(text))
        self.__printToServer(text)

class DebugPrint():
    _instance = _PrintWrapper()
    def Print(text):
        DebugPrint._instance.Print(text)

class __InterfaceWrapper(DebugServer):
    def __init__(self,device_module,listening_port=0,friendly_name='',auto_maintain_connection=True,time_between_commands=0):
        self.__friendly_name = friendly_name
        self.__model = None
        self.device_module = device_module
        self.__sendandwait_busy = False
        self.__commands_to_send = [] #type:list[str]
        self.__t_command_pacer = None #type:_Timer
        self.__interface_type = None
        self.__interface_allow_connection = False
        self.__interface_connect_status = ''
        self.__auto_maintain_connection = auto_maintain_connection
        self.__interface_type = None
        self.__receiveBufferCallbacks = []
        self.__listening_port = listening_port
        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)

        self.device = None

        if time_between_commands > 0:
            self.__t_command_pacer = _Timer(time_between_commands,self.__fn_t_command_pacer())
            self.__t_command_pacer.Restart()

    def __fn_device_init(self,connectiontype:'str',interface):
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        mod = self.device_module
        self.__interface = interface
        class devclass(mod):
            def __init__(self):
                conntype = connectiontype
                if connectiontype == 'SerialOverEthernet':
                    conntype = 'Ethernet'
                if connectiontype == 'SSH':
                    conntype = 'Ethernet'
                self.ConnectionType = conntype
                mod.__init__(self)
        self.device = devclass()
        self.device.Send = self.Send
        self.device.SendAndWait = self.SendAndWait
        self.__subscriber = self.__ModuleSubscribeWrapper(self.device)
        self.device.SubscribeStatus = self.__subscriber.SubscribeStatus
        self.device.NewStatus = self.__replacement_newstatus
        self.device.Update = self.__replacement_update
        self.device.Set = self.__replacement_set
        self.device.Error = self.__replacement_error
        self.device.Discard = self.__replacement_discard
        if hasattr(self.device,'ReceiveData'):
            self.__receiveBufferCallbacks.append(self.device.ReceiveData)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)
        # Check if Model belongs to a subclass
        Model = self.__model
        if len(self.device.Models) > 0:
            if Model not in self.device.Models:
                print('Model mismatch')
            else:
                self.device.Models[Model]()
        self.device.OnDisconnected()
        self._InterfaceWrapper__startInterfaceEvents()
        if self.__interface_type in ['Ethernet','SerialOverEthernet','SSH','Dante']:
            self._InterfaceWrapper__startNetworkInterfaceEvents()
        if self.__interface_type in ['SPI']:
            self._InterfaceWrapper__startSPIInterfaceEvents()

    def __fn_t_command_pacer(self):
        def t(timer,count):
            if self.__sendandwait_busy:
                return
            if len(self.__commands_to_send):
                cmd = self.__commands_to_send.pop()
                self.__printToServer('>>{0}'.format(cmd))
                self.__printToLog(self.__friendly_name,'API,To Device',cmd)
                self.__interface.Send(cmd)
        return t

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    def __eval_string(self,text:'str'):
        text.replace('\\r','\\x0d')
        text.replace('\\n','\\x0a')
        while '\\x' in text:
            pos = text.find('\\x')
            temp = text[pos:pos+4]
            val = int(temp[2:],16)
            char = chr(val)
            text = text.replace(temp,char)
        return text

    def __startInterfaceEvents(self):
        if self.__interface is not None:
            #@_event(self.__interface, 'ReceiveData')
            def HandleReceiveFromInterface(interface,data):
                if data == None:
                    data = b''
                try:
                    decoded_data = repr(data)
                except:
                    decoded_data = b'failed to decode data'
                self.__printToServer('<<{}'.format(decoded_data))
                self.__printToLog(self.__friendly_name,'API,From Device',decoded_data)
                for function in self.__receiveBufferCallbacks:
                    function(self.__interface,data)
            self.__interface.ReceiveData = HandleReceiveFromInterface
    def __startNetworkInterfaceEvents(self):
        @_event(self.__interface,'Connected')
        def connecthandler(interface,state):
            self.__interface_connect_status = state
            self.__print_to_trace('__InterfaceWrapper:{}:network device {} {}'.format(self.__friendly_name,interface.Hostname,state))
            self.device.OnConnected()
        #self.__interface.Disconnected = self.__network_connection_disconnected()
        @_event(self.__interface,'Disconnected')
        def connecthandler(interface,state):
            self.__interface_connect_status = state
            self.__print_to_trace('__InterfaceWrapper:{}:network device {} {}'.format(self.__friendly_name,interface.Hostname,state))
            self.device.OnDisconnected()

        if self.__auto_maintain_connection:
            self.__t_network_maintain = _Timer(10,self.__network_connection_timer_function())

    def __startSPIInterfaceEvents(self):
        @_event(self.__interface,'Online')
        def connecthandler(interface,state):
            self.__interface_connect_status = state
            self.__print_to_trace('__InterfaceWrapper:{}:spi device {} {}'.format(self.__friendly_name,interface.Host,state))
            self.device.OnConnected()
        #self.__interface.Disconnected = self.__network_connection_disconnected()
        @_event(self.__interface,'Offline')
        def connecthandler(interface,state):
            self.__interface_connect_status = state
            self.__print_to_trace('__InterfaceWrapper:{}:spi device {} {}'.format(self.__friendly_name,interface.Host,state))
            self.device.OnDisconnected()

    def __network_connection_timer_function(self):
        def t(timer,count):
            if self.__interface:
                if self.__interface_connect_status != 'Connected' and self.__interface_allow_connection:
                    res = self.Connect()
        return t

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    @property
    def Device(self):
        return self.__interface
    @property
    def DeviceModule(self):
        return self.device

    def __replacement_newstatus(self,command,value,qualifier):
        update = {'command':command,'value':value,'qualifier':qualifier}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'event: Module({}) ~ {}({},{})'.format(self.__friendly_name,command,value,qualifier)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Event','{},{},{}'.format(command,value,qualifier))
        try:
            self.__subscriber.NewStatus(command,value,qualifier)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:NewStatus:{}:{}'.format(__class__.__name__,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'NewStatus',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
    def __replacement_error(self,message:'str'):
        print('Module: {}'.format(self.__friendly_name), 'Error Message: {}'.format(message), sep='\r\n')
    def __replacement_discard(self,message:'str'):
        print('Module: {}'.format(self.__friendly_name), 'Error Message: {}'.format(message), sep='\r\n')
    def __replacement_set(self, command, value, qualifier=None):
        try:
            method = getattr(self.DeviceModule, 'Set%s' % command)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:Set:{}:{}'.format(__class__.__name__,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Set',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
            return
        if method is not None and callable(method):
            try:
                if self.__interface_type in ['Serial','SPI']:
                    method(value, qualifier)
                elif self.device.connectionFlag:
                    method(value, qualifier)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:Set:{}:{}'.format(__class__.__name__,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Set',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
        else:
            print(command, 'does not support Set.')
    def __replacement_update(self, command, qualifier=None):
        try:
            method = getattr(self.DeviceModule, 'Update%s' % command)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:Update:{}:{}'.format(__class__.__name__,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Update',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
            return
        if method is not None and callable(method):
            try:
                if self.__interface_type in ['Serial','SPI']:
                    method(None, qualifier)
                elif self.device.connectionFlag:
                    method(None, qualifier)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:Update:{}:{}'.format(__class__.__name__,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Update',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
        else:
            print(command, 'does not support Update.')

    def Send(self, data):
        if self.__interface is not None:
            if self.__t_command_pacer:
                self.__commands_to_send.insert(0,data)
                return
            self.__printToServer('>>{0}'.format(data))
            self.__printToLog(self.__friendly_name,'API,To Device',data)
            self.__interface.Send(data)
        else:
            print('attempting to send but interface for port {} not defined'.format(self.__listening_port))
    def SendAndWait(self,commandstring,timeout=0.5,**args):
        if self.__interface is not None:
            self.__sendandwait_busy = True
            self.__printToServer('>>{0}'.format(commandstring))
            self.__printToLog(self.__friendly_name,'API,To Device',commandstring)
            ret = self.__interface.SendAndWait(commandstring,timeout,**args)
            self.__printToServer('<<{0}'.format(ret))
            self.__printToLog(self.__friendly_name,'API,From Device',ret)
            self.__sendandwait_busy = False
        else:
            print('attempting to send and wait but interface for port {} not defined'.format(self.__listening_port))
            return b''
        return ret
    def Disconnect(self):
        if self.device:
            if self.device.ConnectionType in ['Ethernet','SerialOverEthernet','SSH','Dante']:
                str_to_send = 'command: Module({}) ~ Disconnect'.format(self.__friendly_name)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Disconnect')
                self.__interface.Disconnect()
                self.device.OnDisconnected()
    def Connect(self):
        if self.device:
            if self.device.ConnectionType in ['Ethernet','SerialOverEthernet','SSH','Dante']:
                str_to_send = 'command: Module({}) ~ Connect'.format(self.__friendly_name)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Connect')
                self.__interface_allow_connection = True
                result = 'command: Module({}) ~ Connect Error : No Interface Defined'.format(self.__friendly_name)
                if self.__interface:
                    result = self.__interface.Connect()
                self.__print_to_trace('command: Module({}) ~ Connect Result : {}'.format(self.__friendly_name, result))
                return result
    def OnConnected(self):
        self.device.OnConnected()
    def OnDisconnected(self):
        self.device.OnDisconnected()
    def Set(self, command, value, qualifier=None):
        str_to_send = 'command: Module({}) ~ Set{}({},{})'.format(self.__friendly_name,command,value,qualifier)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Set{},{},{}'.format(command,value,qualifier))
        try:
            self.device.Set(command,value,qualifier)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Set',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
    def Update(self, command, qualifier=None):
        str_to_send = 'command: Module({}) ~ Update{}({})'.format(self.__friendly_name,command,qualifier)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Update{},{}'.format(command,qualifier))
        try:
            self.device.Update(command,qualifier)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Update',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
    def ReadStatus(self, command, qualifier=None):
        try:
            value = self.device.ReadStatus(command,qualifier)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'ReadStatus',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)
        return value
    def SubscribeStatus(self, command, qualifier=None, callback=None):
        if callback is not None:
            try:
                self.device.SubscribeStatus(command,qualifier,callback)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'SubscribeStatus',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)

    def addReceiveBufferCallback(self,function):
        self.receiveBuff__receiveBufferCallbackserCallbacks.append(function)
    def removeReceiveBufferCallback(self,function):
        self.__receiveBufferCallbacks.remove(function)

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Reinit()' in serverBuffer:
            try:
                if self.device.ConnectionType == 'Serial':
                    self.device.OnDisconnected()
                else:
                    self.__interface.Disconnect()
            except:
                self.device.OnDisconnected()
        elif 'Set(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Set:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:Set',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'command' in temp_dict:
                cmd = temp_dict['command']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
                if 'valuetype' in temp_dict:
                    if temp_dict['valuetype'] == 'Float':
                        try:
                            value = float(value)
                            if '-' in temp_dict['value'] and value > 0:
                                value = value * -1
                        except:
                            print('could not convert value to float')
            qualifier = None
            if 'qualifier' in temp_dict:
                qualifier = temp_dict['qualifier']
            if self.device != None:
                if qualifier is not None:
                    self.Set(cmd,value,qualifier)
                else:
                    self.Set(cmd,value)
        elif 'Update(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Update:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:Update',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'command' in temp_dict:
                cmd = temp_dict['command']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            qualifier = None
            if 'qualifier' in temp_dict:
                qualifier = temp_dict['qualifier']
            if self.device != None:
                if qualifier is not None:
                    self.Update(cmd,qualifier)
                else:
                    self.Update(cmd)
        elif 'WriteStatus(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:WriteStatus:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:WriteStatus',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'command' in temp_dict:
                cmd = temp_dict['command']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
                if 'valuetype' in temp_dict:
                    if temp_dict['valuetype'] == 'Float':
                        try:
                            value = float(value)
                            if '-' in temp_dict['value'] and value > 0:
                                value = value * -1
                        except:
                            print('could not convert value to float')
            qualifier = None
            if 'qualifier' in temp_dict:
                qualifier = temp_dict['qualifier']
            if self.device != None:
                if qualifier is not None:
                    self.device.WriteStatus(cmd,value,qualifier)
                else:
                    self.device.WriteStatus(cmd,value)
        elif 'Passthrough(' in serverBuffer:
            print('passthrough from debug server:{}'.format(serverBuffer))
            temp = serverBuffer[serverBuffer.find('(')+2:serverBuffer.rfind(')')-1]
            temp = self.__eval_string(temp)
            print('temp in passthrough:{}'.format(temp))
            self.Send(temp)

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)


    '''
    to allow for more dynamic programs, this class allows multiple event handlers to be attached to a status.  It will execute the handlers in the order that was subscribed

    ex:
    module.SubscribeStatus('EventName',qualifier,function1)
    module.SubscribeStatus('EventName',qualifier,function2)

    '''

    class __ModuleSubscribeWrapper():
        def __init__(self,mod,__debug_info=None):
            self.__debug_info = __debug_info
            self.mod = mod

        def NewStatus(self, command, value, qualifier):
            if self.__debug_info:
                print("{} : subscriber new status: {} {} {}".format(self.__debug_info,command,value,qualifier))
            if command in self.mod.Subscription:
                Subscribe = self.mod.Subscription[command]
                Method = Subscribe['method']
                Command = self.mod.Commands[command]
                if qualifier:
                    for Parameter in Command['Parameters']:
                        try:
                            Method = Method[qualifier[Parameter]]
                        except:
                            break
                if 'callback' in Method and Method['callback']:
                    if self.__debug_info:
                        print("{} : subscriber new status callbacks{}: {} {} {}".format(self.__debug_info,len(Method['callback']),command,value,qualifier))
                    for callback in Method['callback']:
                        callback(command, value, qualifier)

        def SubscribeStatus(self, command, qualifier, callback):

            Command = self.mod.Commands.get(command)
            if Command:
                if command not in self.mod.Subscription:
                    self.mod.Subscription[command] = {'method': {}}

                Subscribe = self.mod.Subscription[command]
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
                if 'callback' in Method.keys():
                    Method['callback'].append(callback)
                    if self.__debug_info:
                        print("{} : subscriber callback add {}: {} {}".format(self.__debug_info,len(Method['callback']),command,qualifier))
                else:
                    Method['callback'] = [callback]
                    if self.__debug_info:
                        print("{} : subscriber callback add {}: {} {}".format(self.__debug_info,len(Method['callback']),command,qualifier))
                Method['qualifier'] = qualifier
            else:
                print(command, 'does not exist in the module')

class SerialModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        self._InterfaceWrapper__interface_type = 'Serial'
        self._InterfaceWrapper__model = Model
        class SerialClass(_SerialInterface):
            def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232'):
                _SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
            def Error(self, message):
                portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
                print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
        interface = SerialClass(Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self._InterfaceWrapper__fn_device_init('Serial',interface)
class SerialOverEthernetModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        self._InterfaceWrapper__interface_type = 'SerialOverEthernet'
        self._InterfaceWrapper__model = Model
        class SerialOverEthernetClass(_EthernetClientInterface):
            def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0):
                _EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
            def Error(self, message):
                portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
                print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
            def Disconnect(self):
                _EthernetClientInterface.Disconnect(self)
        interface = SerialOverEthernetClass(Hostname, IPPort, Protocol, ServicePort)
        self._InterfaceWrapper__fn_device_init('SerialOverEthernet',interface)
class EthernetModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        self._InterfaceWrapper__interface_type = 'Ethernet'
        self._InterfaceWrapper__model = Model
        class EthernetClass(_EthernetClientInterface):
            def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0):
                _EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
            def Error(self, message):
                portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
                print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
            def Disconnect(self):
                _EthernetClientInterface.Disconnect(self)
        interface = EthernetClass(Hostname, IPPort, Protocol, ServicePort)
        self._InterfaceWrapper__fn_device_init('Ethernet',interface)
class DanteModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, DeviceName, Protocol='Extron', DanteDomainManager=None, Domain=None):
        self._InterfaceWrapper__interface_type = 'Dante'
        self._InterfaceWrapper__model = 'Dante'
        class DanteClass(_DanteInterface):
            def __init__(self, DeviceName, Protocol='Extron', DanteDomainManager=None, Domain=None):
                _DanteInterface.__init__(self, DeviceName, Protocol='Extron', DanteDomainManager=None, Domain=None)
            def Error(self, message):
                portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
                print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
            def Disconnect(self):
                _DanteInterface.Disconnect(self)
        interface = DanteClass(DeviceName, Protocol, DanteDomainManager, Domain)
        self._InterfaceWrapper__fn_device_init('Dante',interface)
class SSHModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        self._InterfaceWrapper__interface_type = 'SSH'
        self._InterfaceWrapper__model = Model
        class SSHClass(_EthernetClientInterface):
            def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None)):
                _EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
            def Error(self, message):
                portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
                print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
            def Disconnect(self):
                _EthernetClientInterface.Disconnect(self)
        interface = SSHClass(Hostname, IPPort, Protocol, ServicePort, Credentials)
        self._InterfaceWrapper__fn_device_init('SSH',interface)
class SPIModuleWrapper(__InterfaceWrapper):
    def Create_Device(self, spi, Model=None):
        self._InterfaceWrapper__interface_type = 'SPI'
        self._InterfaceWrapper__model = Model
        class SPIClass(_SPInterface):
            def __init__(self, spd):
                _SPInterface.__init__(self, spd)
            def Error(self, message):
                print('Module: {}'.format(__name__), 'Error Message: {}'.format(message[0]), sep='\r\n')
            def Discard(self, message):
                self.Error([message])
            def Disconnect(self):
                self.OnDisconnected()
        interface = SPIClass(spi)
        self._InterfaceWrapper__fn_device_init('Serial',interface) #spi modules use serial type apparently
class CircuitBreakerInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='CBR1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Circuit Breaker'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__statechanged_event_callbacks = []

        self.__interface = _CircuitBreakerInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: CircuitBreakerInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: CircuitBreakerInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'StateChanged')
        def handleStateChanged(interface,state):
            self.Commands['State']['Status']['Live'] = state
            update = {'command':'State','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: CircuitBreakerInterface({}) ~ State {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','StateChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'StateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'StateChanged':
            self.__statechanged_event_callbacks.append(function)

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class ContactInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='CII1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Contact'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__statechanged_event_callbacks = []

        self.__interface = _ContactInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: ContactInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: ContactInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'StateChanged')
        def handleStateChanged(interface,state):
            self.Commands['State']['Status']['Live'] = state
            update = {'command':'State','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: ContactInterface({}) ~ State {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','StateChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'StateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'StateChanged':
            self.__statechanged_event_callbacks.append(function)

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class DigitalInputInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='DII1',Pullup:'bool'=False,listening_port:'int'='',friendly_name:'str'=''):
        self.__interface_type = 'Digital Input'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__statechanged_event_callbacks = []

        self.__interface = _DigitalInputInterface(Host,Port,Pullup)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalInputInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalInputInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'StateChanged')
        def handleStateChanged(interface,state):
            self.Commands['State']['Status']['Live'] = state
            update = {'command':'State','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalInputInterface({}) ~ State {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','StateChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'StateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'StateChanged':
            self.__statechanged_event_callbacks.append(function)

    def Initialize(self,Pullup=None):
        if Pullup!=None:
            self.__interface.Initialize(Pullup=Pullup)
            str_to_send = 'command: DigitalInputInterface({}) ~ Initialize,{}'.format(self.__friendly_name,Pullup)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command', 'Initialize,{}'.format(Pullup))

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State
    @property
    def Pullup(self):
        return self.__interface.Pullup

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))

        if 'Initialize(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Initialize',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1']]
            if self.__interface:
                self.Initialize(temps[0])

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class DigitalIOInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='DIO1',Mode:'str'='DigitalInput',Pullup:'bool'=False,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Digital IO'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__statechanged_event_callbacks = []

        self.__interface = _DigitalIOInterface(Host,Port,Mode,Pullup)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalIOInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalIOInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'StateChanged')
        def handleStateChanged(interface,state):
            self.Commands['State']['Status']['Live'] = state
            update = {'command':'State','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: DigitalIOInterface({}) ~ State {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','StateChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'StateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def Initialize(self,Mode=None,Pullup=None):
        if Mode!=None:
            self.__interface.Initialize(Mode=Mode)
        if Pullup!=None:
            self.__interface.Initialize(Pullup=Pullup)
        str_to_send = 'command: DigitalIOInterface({}) ~ Initialize({},{})'.format(self.__friendly_name,Mode,Pullup)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command', 'Initialize,{},{}'.format(Mode,Pullup))

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'StateChanged':
            self.__statechanged_event_callbacks.append(function)

    def Pulse(self,duration):
        self.__interface.Pulse(duration)
        self.Commands['State']['Status']['Live'] = 'On'
        update = {'command':'State','value':'On','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: DigitalIOInterface({}) ~ Pulse(On {})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command', 'Pulse,{},{}'.format('On',duration))
        @_Wait(duration)
        def w():
            self.Commands['State']['Status']['Live'] = 'Off'
            update = {'command':'State','value':'Off','qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'command: DigitalIOInterface({}) ~ Pulse(Off)'.format(self.__friendly_name)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'MoDevicedule Command', 'Pulse,{}'.format('Off'))
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'Off':'Off','On':'On',0:'Off',1:'On'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: DigitalIOInterface({}) ~ SetState({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command', 'SetState,{}'.format(states[State]))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'On':'Off','Off':'On'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: DigitalIOInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command', 'Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State
    @property
    def Mode(self):
        return self.__interface.Mode
    @property
    def Pullup(self):
        return self.__interface.Pullup

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = temp_dict['value1']
            if temp in ['0','1']:
                temp = int(temp)
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Pulse(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Pulse:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Pulse',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = float(temp_dict['value1'])
            if self.__interface:
                self.Pulse(temp)
        if 'Initialize(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Initialize:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Initialize',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1'],temp_dict['value2']]
            if self.__interface:
                self.Initialize(temps[0],temps[1])
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Options',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class FlexIOInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='DIO1',Mode:'str'='DigitalInput',Pullup:'bool'=False,Upper:'float'=2.8,Lower:'float'=2.0,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Flex IO'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__statechanged_event_callbacks = []
        self.__analogvoltagechanged_event_callbacks = []

        self.__interface = _FlexIOInterface(Host,Port,Mode,Pullup,Upper,Lower)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}},
            'AnalogVoltage':{'Status':{'Live':self.__interface.AnalogVoltage}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: FlexIOInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: FlexIOInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'StateChanged')
        def handleStateChanged(interface,state):
            self.Commands['State']['Status']['Live'] = state
            update = {'command':'State','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: FlexIOInterface({}) ~ State {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','StateChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'StateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'AnalogVoltageChanged')
        def handleVoltageChanged(interface,state):
            self.Commands['AnalogVoltage']['Status']['Live'] = state
            update = {'command':'AnalogVoltage','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: FlexIOInterface({}) ~ AnalogVoltage {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','AnalogVoltageChanged,{}'.format(state))
            for f in self.__statechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'VoltageChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def Initialize(self,Mode=None,Pullup=None,Upper=None,Lower=None):
        if Mode!=None:
            self.__interface.Initialize(Mode=Mode)
        if Pullup!=None:
            self.__interface.Initialize(Pullup=Pullup)
        if Upper!=None:
            self.__interface.Initialize(Upper=float(Upper))
        if Lower!=None:
            self.__interface.Initialize(Lower=float(Lower))
        self.__printToServer('Initialize : Mode:{} Pullup:{} Upper:{} Lower:{}'.format(self.__interface.Mode,self.__interface.Pullup,self.__interface.Upper,self.__interface.Lower))
        self.__printToLog(self.__friendly_name,'Command','Initialize,{},{},{},{}'.format(self.__interface.Pullup,self.__interface.Upper,self.__interface.Lower))
    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'StateChanged':
            self.__statechanged_event_callbacks.append(function)
        if command == 'AnalogVoltageChanged':
            self.__analogvoltagechanged_event_callbacks.append(function)

    def Pulse(self,duration):
        self.__interface.Pulse(duration)
        self.__printToServer('Pulse : duration {}'.format(duration))
        self.Commands['State']['Status']['Live'] = 'On'
        update = {'command':'State','value':'On','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: FlexIOInterface({}) ~ Pulse(On {})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,On,{}'.format(duration))
        @_Wait(duration)
        def w():
            self.Commands['State']['Status']['Live'] = 'Off'
            update = {'command':'State','value':'Off','qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'command: FlexIOInterface({}) ~ Pulse(Off)'.format(self.__friendly_name)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','Pulse,Off')
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'Off':'Off','On':'On',0:'Off',1:'On'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: FlexIOInterface({}) ~ SetState({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(State))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'Off':'On','On':'Off'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: FlexIOInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State
    @property
    def Mode(self):
        return self.__interface.Mode
    @property
    def Pullup(self):
        return self.__interface.Pullup
    @property
    def Upper(self):
        return self.__interface.Upper
    @property
    def Lower(self):
        return self.__interface.Lower
    @property
    def AnalogVoltage(self):
        return self.__interface.AnalogVoltage

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = temp_dict['value1']
            if temp in ['0','1']:
                temp = int(temp)
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Pulse(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Pulse:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:Pulse',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            temp = float(temp)
            if self.__interface:
                self.Pulse(temp)
        if 'Initialize(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Initialize:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Initialize',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1'],temp_dict['value2'],temp_dict['value3'],temp_dict['value4']]
            if self.__interface:
                self.Initialize(temps[0],temps[1],temps[2],temps[3])
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Options',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class IRInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='IRS1',File:'str'='',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'IR'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True
        self.FileName = File

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []

        self.Commands = {
            'OnlineStatus':{'Status':{}},
            'LastCommand':{'Status':{}},
            'File':{'Status':{'Live':File}}
            }

        self.__interface = _IRInterface(Host,Port,File)

        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: IRInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: IRInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def Initialize(self,File=None):
        if File!=None:
            self.__interface.Initialize(File=File)
        self.__printToServer('Initialize : Mode:{} '.format(self.__interface.File))

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def PlayContinuous(self,irFunction):
        self.__interface.PlayContinuous(irFunction)
        self.Commands['LastCommand']['Status']['Live'] = irFunction
        str_to_send = 'command: IRInterface({}) ~ PlayContinuous({})'.format(self.__friendly_name,irFunction)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','PlayContinuous,{}'.format(irFunction))
    def PlayCount(self,irFunction,repeatCount=None):
        self.__interface.PlayCount(irFunction,repeatCount)
        self.Commands['LastCommand']['Status']['Live'] = irFunction
        str_to_send = 'command: IRInterface({}) ~ PlayCount({},{})'.format(self.__friendly_name,irFunction,repeatCount)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','PlayCount,{},{}'.format(irFunction,repeatCount))
    def PlayTime(self,irFunction,duration=None):
        self.__interface.PlayTime(irFunction,duration)
        self.Commands['LastCommand']['Status']['Live'] = irFunction
        str_to_send = 'command: IRInterface({}) ~ PlayTime({},{})'.format(self.__friendly_name,irFunction,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','PlayTime,{},{}'.format(irFunction,duration))
    def Stop(self):
        self.__interface.Stop()
        self.Commands['LastCommand']['Status']['Live'] = 'Close'
        str_to_send = 'command: IRInterface({}) ~ Stop()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Stop')


    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def File(self):
        return self.__interface.File

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'PlayContinuous(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:PlayContinuous:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:PlayContinuous',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            if self.__interface:
                self.PlayContinuous(temp_dict['value1'])
        elif 'PlayCount(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:PlayCount:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Playcount',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1'],temp_dict['value2']]
            if len(temps) == 1:
                temps.append(None)
            elif temps[1] == 'None':
                temps[1] = None
            else:
                temps[1] = int(temps[1])
            if self.__interface:
                self.PlayCount(temps[0],temps[1])
        elif 'PlayTime(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:PlayTime:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:PlayTime',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1'],temp_dict['value2']]
            if self.__interface:
                self.PlayTime(temps[0],float(temps[1]))
        elif 'Stop()' in serverBuffer:
            if self.__interface:
                self.Stop()
        elif 'Initialize(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Initialize:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Initialize',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1']]
            if self.__interface:
                self.Initialize(temps[0])

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Options',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class PoEInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='POE1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'PoE'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__powerstatuschanged_event_callbacks = []

        self.__currentload = None

        self.__interface = _PoEInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'PowerStatus':{'Status':{'Live':self.__interface.PowerStatus}},
            'CurrentLoad':{'Status':{'Live':self.__interface.CurrentLoad}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: PoEInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: PoEInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'PowerStatusChanged')
        def handlePowerStatusChanged(interface,state):
            self.Commands['PowerStatus']['Status']['Live'] = state
            update = {'command':'PowerStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: PoEInterface({}) ~ PowerStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','PowerStatusChanged,{}'.format(state))
            for f in self.__powerstatuschanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'PowerStatusChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)
        @_Timer(1)
        def t(timer,count):
            if self.__currentload != self.__interface.CurrentLoad:
                self.__currentload = self.__interface.CurrentLoad
                self.Commands['CurrentLoad']['Status']['Live'] = str(self.__interface.CurrentLoad)
                update = {'command':'CurrentLoad','value':str(self.__interface.CurrentLoad),'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'On':'On','Off':'Off',0:'Off',1:'On'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: PoEInterface({}) ~ SetState({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(State))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'On':'Off','Off':'On'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: PoEInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State
    @property
    def CurrentLoad(self):
        return self.__interface.CurrentLoad
    @property
    def PowerStatus(self):
        return self.__interface.PowerStatus

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Off':0,'On':1}
            temp=vals[temp_dict['value1']]
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class RelayInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='RLY1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Relay'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []

        self.__interface = _RelayInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: RelayInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: RelayInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def Pulse(self,duration):
        self.__interface.Pulse(duration)
        self.Commands['State']['Status']['Live'] = 'Close'
        update = {'command':'State','value':'Close','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: RelayInterface({}) ~ Pulse(On,{})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,On,{}'.format(duration))
        @_Wait(duration)
        def w():
            self.Commands['State']['Status']['Live'] = 'Open'
            update = {'command':'State','value':'Open','qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'command: RelayInterface({}) ~ Pulse(Off)'.format(self.__friendly_name)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','Pulse,Off')
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'Open':'Open','Close':'Close',0:'Open',1:'Close'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: RelayInterface({}) ~ SetState({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(states[State]))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'Open':'Close','Close':'Open'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: RelayInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Open':0,'Close':1}
            temp=vals[temp_dict['value1']]
            if self.__interface:
                self.SetState(temp)
        if 'Pulse(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Pulse:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Pulse',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = float(temp_dict['value1'])
            if self.__interface:
                self.Pulse(temp)
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class SWACReceptacleInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='SAC1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'SWAC Receptacle'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__currentchanged_event_callbacks = []

        self.__interface = _SWACReceptacleInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'Current': {'Status': {'Live':self.__interface.Current}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: SWACReceptacleInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: SWACReceptacleInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'CurrentChanged')
        def handleCurrentChanged(interface,state):
            self.Commands['Current']['Status']['Live'] = str(state)
            update = {'command':'Current','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: SWACReceptacleInterface({}) ~ CurrentChanged {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','CurrentChanged,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CurrentChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'CurrentChanged':
            self.__currentchanged_event_callbacks.append(function)
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'On':'On','Off':'Off',0:'Off',1:'On'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: SWACReceptacleInterface({}) ~ SetState({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(states[State]))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'On':'Off','Off':'On'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: SWACReceptacleInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State
    @property
    def Current(self):
        return self.__interface.Current

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Off':0,'On':1}
            temp=vals[temp_dict['value1']]
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class SWPowerInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='SPI1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'SW Power'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []

        self.__interface = _SWPowerInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }

        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: SWPowerInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: SWPowerInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def Pulse(self,duration):
        self.__interface.Pulse(duration)
        self.Commands['State']['Status']['Live'] = 'On'
        update = {'command':'State','value':'On','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: SWPowerInterface({}) ~ Pulse(On,{})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,On,{}'.format(duration))
        @_Wait(duration)
        def w():
            self.Commands['State']['Status']['Live'] = 'Off'
            update = {'command':'State','value':'Off','qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'command: SWPowerInterface({}) ~ Pulse(Off)'.format(self.__friendly_name)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,Off')
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'On':'On','Off':'Off',0:'On',1:'Off'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':'Off','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: SWPowerInterface({}) ~ State({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(states[State]))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'On':'Off','Off':'On'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'OnlineStatus','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: SWPowerInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Off':0,'On':1}
            temp=vals[temp_dict['value1']]
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Pulse(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Pulse:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Pulse',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = float(temp_dict['value1'])
            if self.__interface:
                self.Pulse(temp)
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class TallyInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='TAL1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Tally'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []

        self.__interface = _TallyInterface(Host,Port)
        self.Commands = {
            'State': {'Status': {'Live':self.__interface.State}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: TallyInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: TallyInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def Pulse(self,duration):
        self.__interface.Pulse(duration)
        self.Commands['State']['Status']['Live'] = 'On'
        update = {'command':'State','value':'On','qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: TallyInterface({}) ~ Pulse(On,{})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,On,{}'.format(duration))
        @_Wait(duration)
        def w():
            self.Commands['State']['Status']['Live'] = 'Off'
            update = {'command':'State','value':'Off','qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'command: TallyInterface({}) ~ Pulse(Off)'.format(self.__friendly_name)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Pulse,Off')
    def SetState(self,State):
        self.__interface.SetState(State)
        states = {'On':'On','Off':'Off',0:'On',1:'Off'}
        self.Commands['State']['Status']['Live'] = states[State]
        update = {'command':'State','value':states[State],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: TallyInterface({}) ~ State({})'.format(self.__friendly_name,states[State])
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetState,{}'.format(states[State]))
    def Toggle(self):
        self.__interface.Toggle()
        states = {'On':'Off','Off':'On'}
        self.Commands['State']['Status']['Live'] = states[self.Commands['State']['Status']['Live']]
        update = {'command':'State','value':states[self.Commands['State']['Status']['Live']],'qualifier':None}
        self._DebugServer__send_interface_status(self.__listening_port,update)
        str_to_send = 'command: TallyInterface({}) ~ Toggle()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Toggle')

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def State(self):
        return self.__interface.State

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'State(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:State:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:State',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Off':0,'On':1}
            temp=vals[temp_dict['value1']]
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetState(temp)
        if 'Pulse(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Pulse:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Pulse',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = float(temp_dict['value1'])
            if self.__interface:
                self.Pulse(temp)
        if 'Toggle()' in serverBuffer:
            if self.__interface:
                self.Toggle()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class VolumeInterfaceWrapper(DebugServer):
    def __init__(self,Host:'object',Port:'str'='VOL1',listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Volume'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []

        self.__interface = _VolumeInterface(Host,Port)
        self.__currentlevel = self.__interface.Level
        self.__currentmax = self.__interface.Max
        self.__currentmin = self.__interface.Min
        self.__currentsoftstart = self.__interface.SoftStart
        self.__currentmute = self.__interface.Mute

        self.Commands = {
            'Level':{'Status': {'Live':self.__interface.Level}},
            'Mute':{'Status': {'Live':self.__interface.Mute}},
            'Max':{'Status': {'Live':self.__interface.Max}},
            'Min':{'Status': {'Live':self.__interface.Min}},
            'SoftStart':{'Status': {'Live':self.__interface.SoftStart}},
            'OnlineStatus':{'Status':{}}
            }


        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: VolumeInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: VolumeInterface({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

        @_Timer(1)
        def t(timer,count):
            somethingchanged = False
            if self.__currentlevel != self.__interface.Level:
                somethingchanged = True
                self.__currentlevel = self.__interface.Level
                self.Commands['Level']['Status']['Live'] = self.__interface.Level
                update = {'command':'Level','value':self.Commands['Level']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: VolumeInterface({}) ~ Level {}'.format(self.__friendly_name,self.__currentlevel)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Level,{}'.format(self.__currentlevel))
            if self.__currentmax != self.__interface.Max:
                somethingchanged = True
                self.__currentmax = self.__interface.Max
                self.Commands['Max']['Status']['Live'] = self.__interface.Max
                update = {'command':'Max','value':self.Commands['Max']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: VolumeInterface({}) ~ Max {}'.format(self.__friendly_name,self.__currentmax)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Max,{}'.format(self.__currentmax))
            if self.__currentmin != self.__interface.Min:
                somethingchanged = True
                self.__currentmin = self.__interface.Min
                self.Commands['Min']['Status']['Live'] = self.__interface.Min
                update = {'command':'Min','value':self.Commands['Min']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: VolumeInterface({}) ~ Min {}'.format(self.__friendly_name,self.__currentmin)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Min,{}'.format(self.__currentmin))
            if self.__currentmute != self.__interface.Mute:
                somethingchanged = True
                self.__currentmute = self.__interface.Mute
                self.Commands['Mute']['Status']['Live'] = self.__interface.Mute
                update = {'command':'Mute','value':self.Commands['Mute']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: VolumeInterface({}) ~ Mute {}'.format(self.__friendly_name,self.__currentmute)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','Mute,{}'.format(self.__currentmute))
            if self.__currentsoftstart != self.__interface.SoftStart:
                somethingchanged = True
                self.__currentsoftstart = self.__interface.SoftStart
                self.Commands['SoftStart']['Status']['Live'] = self.__interface.SoftStart
                update = {'command':'SoftStart','value':self.Commands['SoftStart']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: VolumeInterface({}) ~ SoftStart {}'.format(self.__friendly_name,self.__currentsoftstart)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Command','SoftStart,{}'.format(self.__currentsoftstart))

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)

    def SetLevel(self,Level):
        self.__interface.SetLevel(Level)
        str_to_send = 'command: VolumeInterface({}) ~ SetLevel({})'.format(self.__friendly_name,Level)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetLevel,{}'.format(Level))
    def SetMute(self,Mute):
        self.__interface.SetMute(Mute)
        str_to_send = 'command: VolumeInterface({}) ~ SetMute({})'.format(self.__friendly_name,Mute)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetMute,{}'.format(Mute))
    def SetRange(self,Min,Max):
        self.__interface.SetRange(Min,Max)
        str_to_send = 'command: VolumeInterface({}) ~ SetRange({},{})'.format(self.__friendly_name,Min,Max)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetRange,{} {}'.format(Min,Max))
    def SetSoftStart(self,softstart):
        self.__interface.SetSoftStart(softstart)
        str_to_send = 'command: VolumeInterface({}) ~ SetSoftStart({})'.format(self.__friendly_name,softstart)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetSoftStart,{}'.format(softstart))

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def Host(self):
        return self.__interface.Host
    @property
    def Port(self):
        return self.__interface.Port
    @property
    def Level(self):
        return self.__interface.Level
    @property
    def Max(self):
        return self.__interface.Max
    @property
    def Min(self):
        return self.__interface.Min
    @property
    def Mute(self):
        return self.__interface.Mute
    @property
    def SoftStart(self):
        return self.__interface.SoftStart

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
        except:
            serverBuffer += data
        if 'Mute(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Mute:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:Mute',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            vals = {'0':0,'1':1,'Off':0,'On':1}
            temp=vals[temp_dict['value1']]
            if self.__interface and temp in [0,1,'On','Off']:
                self.SetMute(temp)
        if 'Level(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Level:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Level',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = float(temp_dict['value1'])
            if self.__interface:
                self.SetLevel(temp)
        if 'Range(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Range:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Range',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temps = [temp_dict['value1'],temp_dict['value2']]
            if self.__interface:
                self.SetLevel(temps[0],temps[1])
        if 'SoftStart(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SoftStart:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SoftStart',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp = temp_dict['value1']
            if self.__interface:
                self.SoftStart(temp)

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class ProcessorDeviceWrapper(DebugServer):
    def __init__(self,DeviceAlias:'str',PartNumber:'str'=None,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'Processor'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__combinedcurrent_event_callbacks = []
        self.__combinedloadstate_event_callbacks = []
        self.__combinedwattage_event_callbacks = []
        self.__executivemode_event_callbacks =[]

        self.__interface = _ProcessorDevice(DeviceAlias,PartNumber) #type:_ProcessorDevice
        self.device = self.__interface
        executivemode = 'Unavailable'
        combinedcurrent = 'Unavailable'
        combinedwattage = 'Unavailable'
        combinedloadstate = 'Unavailable'
        self.__model = self.__interface.ModelName
        self.Commands = {
            'ExecutiveMode':{'Status': {'Live':executivemode}},
            'Reboot':{'Status': {}},
            'CombinedCurrent':{'Status': {'Live':combinedcurrent}},
            'CombinedWattage':{'Status': {'Live':combinedwattage}},
            'CombinedLoadState':{'Status': {'Live':combinedloadstate}},
            'SystemSettings':{'Status': {'Live':self.__interface.SystemSettings}},
            'OnlineStatus':{'Status':{}},
            'FirmwareVersion':{'Status':{'Live':self.__interface.FirmwareVersion}},
            'LinkLicenses':{'Status':{'Live':self.__interface.LinkLicenses}},
            'DeviceAlias':{'Status':{'Live':self.__interface.DeviceAlias}},
            'ModelName':{'Status':{'Live':self.__interface.ModelName}},
            'PartNumber':{'Status':{'Live':self.__interface.PartNumber}},
            'SerialNumber':{'Status':{'Live':self.__interface.SerialNumber}},
            'UserUsage':{'Status':{'Live':self.__interface.UserUsage}},
            }

        self.__systemsettings = self.__interface.SystemSettings
        self.__userusage = self.__interface.UserUsage

        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: Processor({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: Processor({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        if hasattr(self.__interface,'CombinedCurrentChanged'):
            @_event(self.__interface,'CombinedCurrentChanged')
            def handleCombinedCurrentChanged(interface,state):
                self.Commands['CombinedCurrent']['Status']['Live'] = str(state)
                update = {'command':'CombinedCurrent','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedCurrent {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedCurrentChanged,{}'.format(state))
                for f in self.__combinedcurrent_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedCurrentChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
                if 'PCS1' in self.__model:
                    executivemode = self.__interface.ExecutiveMode
                    combinedcurrent = self.__interface.CombinedCurrent
                    combinedwattage = self.__interface.CombinedWattage
                    combinedloadstate = self.__interface.CombinedLoadState
                    @_event(self.__interface,'ExecutiveModeChanged')
                    def handleExecutiveModeChanged(interface,state):
                        self.Commands['ExecutiveMode']['Status']['Live'] = str(state)
                        update = {'command':'ExecutiveMode','value':state,'qualifier':None}
                        self._DebugServer__send_interface_status(self.__listening_port,update)
                        str_to_send = 'event: Processor({}) ~ ExecutiveMode {}'.format(self.__friendly_name,state)
                        self.__print_to_trace(str_to_send)
                        self.__printToServer(str_to_send)
                        self.__printToLog(self.__friendly_name,'Event','ExecutiveModeChanged,{}'.format(state))
                        for f in self.__executivemode_event_callbacks:
                            try:
                                f(interface,state)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'ExecutiveModeChanged',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
            @_event(self.__interface,'CombinedWattageChanged')
            def handleCombinedWattageChanged(interface,state):
                self.Commands['CombinedWattage']['Status']['Live'] = str(state)
                update = {'command':'CombinedWattage','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedWattage {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedWattageChanged,{}'.format(state))
                for f in self.__combinedwattage_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedWattageChange',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
            @_event(self.__interface,'CombinedLoadStateChanged')
            def handleCombinedLoadStateChanged(interface,state):
                self.Commands['CombinedLoadState']['Status']['Live'] = str(state)
                update = {'command':'CombinedLoadState','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedLoadState {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedLoadStateChanged,{}'.format(state))
                for f in self.__combinedloadstate_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedLoadStateChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)

        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

        @_Timer(1)
        def t(timer,count):
            somethingchanged = False
            if self.Commands['ExecutiveMode']['Status']['Live'] != 'Online':
                if self.__userusage != self.__interface.UserUsage:
                    somethingchanged = True
                    self.__userusage = self.__interface.UserUsage
                    self.Commands['UserUsage']['Status']['Live'] = self.__interface.UserUsage
                    update = {'command':'UserUsage','value':self.Commands['UserUsage']['Status']['Live'],'qualifier':None}
                    self._DebugServer__send_interface_status(self.__listening_port,update)
                    str_to_send = 'event: Processor({}) ~ UserUsage {}'.format(self.__friendly_name,self.__userusage)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Event','UserUsageChanged,{}'.format(self.__userusage))
                if self.__systemsettings != self.__interface.SystemSettings:
                    somethingchanged = True
                    self.__systemsettings = self.__interface.SystemSettings
                    self.Commands['SystemSettings']['Status']['Live'] = self.__interface.SystemSettings
                    update = {'command':'SystemSettings','value':self.Commands['SystemSettings']['Status']['Live'],'qualifier':None}
                    self._DebugServer__send_interface_status(self.__listening_port,update)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'CombinedCurrentChanged':
            self.__combinedcurrent_event_callbacks.append(function)
        if command == 'CombinedWattageChanged':
            self.__combinedwattage_event_callbacks.append(function)
        if command == 'CombinedLoadStateChanged':
            self.__combinedloadstate_event_callbacks.append(function)
        if command == 'ExecutiveModeChanged':
            self.__executivemode_event_callbacks.append(function)

    def SetExecutiveMode(self,Level):
        if 'PCS1' in self.__model:
            self.__interface.SetExecutiveMode(Level)
            str_to_send = 'command: Processor({}) ~ SetExecutiveMode({})'.format(self.__friendly_name,Level)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','SetExecutiveMode,{}'.format(Level))
    def Reboot(self):
        str_to_send = 'command: Processor({}) ~ Reboot()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Reboot')
        self.__interface.Reboot()
    def SaveProgramLog(self):
        str_to_send = 'command: Processor({}) ~ SaveProgramLog()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SaveProgramLog')
        dt = _datetime.now()
        filename = 'ProgramLog {}.txt'.format(dt.strftime('%Y-%m-%d %H%M%S'))
        try:
            with _File(filename, 'w') as f:
                _SaveProgramLog(f)
        except Exception as e:
            if sys_allowed_flag:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
            else:
                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'SaveProgramLog',e)
            print(err_msg)
            DebugPrint.Print(err_msg)
            _ProgramLog(err_msg)


    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def ExecutiveMode(self,ExecutiveMode):
        if self.__model == None:
            return
        if 'PCS1' in self.__model:
            return self.__interface.ExecutiveMode
        else:
            return 'Unavailable'
    @property
    def CombinedCurrent(self):
        return self.__interface.CombinedCurrent
    @property
    def CombinedLoadState(self):
        return self.__interface.CombinedLoadState
    @property
    def CombinedWattage(self):
        return self.__interface.CombinedWattage
    @property
    def CurrentLoad(self):
        return self.__interface.CurrentLoad
    @property
    def FirmwareVersion(self):
        return self.__interface.FirmwareVersion
    @property
    def Hostname(self):
        return self.__interface.Hostname
    @property
    def IPAddress(self):
        return self.__interface.IPAddress
    @property
    def LinkLicenses(self):
        return self.__interface.LinkLicenses
    @property
    def MACAddress(self):
        return self.__interface.MACAddress
    @property
    def ModelName(self):
        return self.__interface.ModelName
    @property
    def PartNumber(self):
        return self.__interface.PartNumber
    @property
    def SerialNumber(self):
        return self.__interface.SerialNumber
    @property
    def SystemSettings(self):
        return self.__interface.SystemSettings
    @property
    def UserUsage(self):
        return self.__interface.UserUsage

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
        except:
            serverBuffer += data
        if 'ExecutiveMode(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:ExecutiveMode:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:ExecutiveMode',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            try:
                temp=int(temp)
            except:
                temp = None
            if self.__interface and temp is not None:
                self.SetExecutiveMode(temp)
        if 'Reboot(' in serverBuffer:
            if self.__interface:
                self.Reboot()
        if 'SaveProgramLog(' in serverBuffer:
            if self.__interface:
                self.SaveProgramLog()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class SPDeviceWrapper(DebugServer):
    def __init__(self,DeviceAlias:'str',PartNumber:'str'=None,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'SPDevice'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__combinedcurrent_event_callbacks = []
        self.__combinedloadstate_event_callbacks = []
        self.__combinedwattage_event_callbacks = []

        self.__interface = _SPDevice(DeviceAlias,PartNumber) #type:_SPDevice
        self.device = self.__interface
        combinedcurrent = 'Unavailable'
        combinedwattage = 'Unavailable'
        combinedloadstate = 'Unavailable'
        self.__model = self.__interface.ModelName
        self.Commands = {
            'Reboot':{'Status': {}},
            'CombinedCurrent':{'Status': {'Live':combinedcurrent}},
            'CombinedWattage':{'Status': {'Live':combinedwattage}},
            'CombinedLoadState':{'Status': {'Live':combinedloadstate}},
            'SystemSettings':{'Status': {'Live':self.__interface.SystemSettings}},
            'OnlineStatus':{'Status':{}},
            'FirmwareVersion':{'Status':{'Live':self.__interface.FirmwareVersion}},
            'LinkLicenses':{'Status':{'Live':self.__interface.LinkLicenses}},
            'DeviceAlias':{'Status':{'Live':self.__interface.DeviceAlias}},
            'ModelName':{'Status':{'Live':self.__interface.ModelName}},
            'PartNumber':{'Status':{'Live':self.__interface.PartNumber}},
            'SerialNumber':{'Status':{'Live':self.__interface.SerialNumber}},
            }

        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: Processor({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = state
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: Processor({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        if hasattr(self.__interface,'CombinedCurrentChanged'):
            @_event(self.__interface,'CombinedCurrentChanged')
            def handleCombinedCurrentChanged(interface,state):
                self.Commands['CombinedCurrent']['Status']['Live'] = str(state)
                update = {'command':'CombinedCurrent','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedCurrent {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedCurrentChanged,{}'.format(state))
                for f in self.__combinedcurrent_event_callbacks:
                    f(interface,state)
                if 'PCS1' in self.__model:
                    executivemode = self.__interface.ExecutiveMode
                    combinedcurrent = self.__interface.CombinedCurrent
                    combinedwattage = self.__interface.CombinedWattage
                    combinedloadstate = self.__interface.CombinedLoadState
                    @_event(self.__interface,'ExecutiveModeChanged')
                    def handleExecutiveModeChanged(interface,state):
                        self.Commands['ExecutiveMode']['Status']['Live'] = str(state)
                        update = {'command':'ExecutiveMode','value':state,'qualifier':None}
                        self._DebugServer__send_interface_status(self.__listening_port,update)
                        str_to_send = 'event: Processor({}) ~ ExecutiveMode {}'.format(self.__friendly_name,state)
                        self.__print_to_trace(str_to_send)
                        self.__printToServer(str_to_send)
                        self.__printToLog(self.__friendly_name,'Event','ExecutiveModeChanged,{}'.format(state))
                        for f in self.__executivemode_event_callbacks:
                            try:
                                f(interface,state)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedCurrentChanged',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
            @_event(self.__interface,'CombinedWattageChanged')
            def handleCombinedWattageChanged(interface,state):
                self.Commands['CombinedWattage']['Status']['Live'] = str(state)
                update = {'command':'CombinedWattage','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedWattage {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedWattageChanged,{}'.format(state))
                for f in self.__combinedwattage_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedWattageChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
            @_event(self.__interface,'CombinedLoadStateChanged')
            def handleCombinedLoadStateChanged(interface,state):
                self.Commands['CombinedLoadState']['Status']['Live'] = str(state)
                update = {'command':'CombinedLoadState','value':state,'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: Processor({}) ~ CombinedLoadState {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','CombinedLoadStateChanged,{}'.format(state))
                for f in self.__combinedloadstate_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'CombinedLoadStateChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)

        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SubscribeStatus(self,command,function):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'CombinedCurrentChanged':
            self.__combinedcurrent_event_callbacks.append(function)
        if command == 'CombinedWattageChanged':
            self.__combinedwattage_event_callbacks.append(function)
        if command == 'CombinedLoadStateChanged':
            self.__combinedloadstate_event_callbacks.append(function)

    def Reboot(self):
        str_to_send = 'command: Processor({}) ~ Reboot()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Reboot')
        self.__interface.Reboot()


    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def CombinedCurrent(self):
        return self.__interface.CombinedCurrent
    @property
    def CombinedLoadState(self):
        return self.__interface.CombinedLoadState
    @property
    def CombinedWattage(self):
        return self.__interface.CombinedWattage
    @property
    def FirmwareVersion(self):
        return self.__interface.FirmwareVersion
    @property
    def Hostname(self):
        return self.__interface.Hostname
    @property
    def IPAddress(self):
        return self.__interface.IPAddress
    @property
    def LinkLicenses(self):
        return self.__interface.LinkLicenses
    @property
    def MACAddress(self):
        return self.__interface.MACAddress
    @property
    def ModelName(self):
        return self.__interface.ModelName
    @property
    def PartNumber(self):
        return self.__interface.PartNumber
    @property
    def SerialNumber(self):
        return self.__interface.SerialNumber
    @property
    def SystemSettings(self):
        return self.__interface.SystemSettings

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
        except:
            serverBuffer += data
        if 'Reboot(' in serverBuffer:
            if self.__interface:
                self.Reboot()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
class UIDeviceWrapper(DebugServer):
    def __init__(self,DeviceAlias:'str',PartNumber:'str'=None,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'UI'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.__online_event_callbacks = []
        self.__offline_event_callbacks = []
        self.__brightnesschanged_event_callbacks = []
        self.__hdcpstatuschanged_event_callbacks = []
        self.__inactivitychanged_event_callbacks = []
        self.__inputpresencechanged_event_callbacks =[]
        self.__lidchanged_event_callbacks =[]
        self.__lightchanged_event_callbacks =[]
        self.__motiondetected_event_callbacks =[]
        self.__overtemperaturechanged_event_callbacks =[]
        self.__overtemperaturewarning_event_callbacks =[]
        self.__overtemperaturewarningstatechanged_event_callbacks =[]
        self.__sleepchanged_event_callbacks =[]

        self.__interface = _UIDevice(DeviceAlias,PartNumber) #type:_UIDevice
        self.device = self.__interface
        #@_Wait(0.1)
        #def w():
        self.Commands = {
            'OnlineStatus':{'Status':{'Live':'Offline'}},
            'HDCPStatus':{'Parameters': ['Video Input'],'Status': {}},
            'InputPresence':{'Parameters': ['Video Input'],'Status': {}},
            'Mute':{'Parameters': ['Channel Name'],'Status': {}},
            'Volume':{'Parameters': ['Channel Name'],'Status': {}},
            'AutoBrightness':{'Status': {}},
            'Brightness':{'Status':{}},
            'DisplayTimer':{'Status':{}},
            'InactivityTime':{'Status':{}},
            'Input':{'Status':{}},
            'LEDBlinking':{'Status':{}},
            'LEDState':{'Status':{}},
            'MotionDecayTime':{'Status':{}},
            'SleepTimer':{'Status':{}},
            'WakeOnMotion':{'Status':{}},
            'AmbientLightValue':{'Status':{}},
            'DeviceAlias':{'Status':{}},
            'DisplayState':{'Status':{}},
            'DisplayTimerEnabled':{'Status':{}},
            'FirmwareVersion':{'Status':{}},
            'Inactivity':{'Status':{}},
            'LidState':{'Status':{}},
            'LightDetectedState':{'Status':{}},
            'LinkLicenses':{'Status':{}},
            'ModelName':{'Status':{}},
            'MotionState':{'Status':{}},
            'OverTemperature':{'Status':{}},
            'OverTemperatureWarningState':{'Status':{}},
            'PartNumber':{'Status':{}},
            'SerialNumber':{'Status':{}},
            'SleepState':{'Status':{}},
            'SleepTimerEnabled':{'Status':{}},
            'SystemSettings':{'Status':{}},
            'UserUsage':{'Status':{}},
            'WakeOnMotion':{'Status':{}},
            }
        self.__model = self.__interface.ModelName


        self.__systemsettings = None
        self.__userusage = None
        self.__autobrightness = None
        self.__displaystate = None
        self.__displaytimer = None
        self.__displaytimerenabled = None
        self.__inactivitytime = None
        self.__lightdetectedstate = None
        self.__motiondecaytime = None
        self.__sleeptimer = None
        self.__sleeptimerenabled = None
        self.__wakeonmotion = None

        self.__polling_timer = _Timer(5,self.__create_polling_timer())
        self.__polling_timer.Stop()

        self.__print_to_trace('UIDevice({}) init events start'.format(self.__friendly_name))
        @_event(self.__interface,'Online')
        def handleOnline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Online'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__online_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Online',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'Offline')
        def handleOffline(interface,state):
            self.Commands['OnlineStatus']['Status']['Live'] = 'Offline'
            update = {'command':'OnlineStatus','value':state,'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ OnlineStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','OnlineStatus,{}'.format(state))
            for f in self.__offline_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Offline',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'BrightnessChanged')
        def handlebrightness(interface,state):
            self.Commands['Brightness']['Status']['Live'] = str(state)
            update = {'command':'Brightness','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ Brightness {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','BrightnessChanged,{}'.format(state))
            for f in self.__brightnesschanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Brightness',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'HDCPStatusChanged')
        def handlehdcp(interface,state):
            self.Commands['HDCPStatus']['Status'][state[0]]['Live'] = str(state[1])
            update = {'command':'HDCPStatus','value':str(state[1]),'qualifier':{'Video Input':state[0]}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ HDCPStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','HDCPStatusChanged,{}'.format(state))
            for f in self.__hdcpstatuschanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HDCP',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'InactivityChanged')
        def handleinactivity(interface,state):
            self.Commands['Inactivity']['Status']['Live'] = str(state)
            update = {'command':'Inactivity','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ Inactivity {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','InactivityChanged,{}'.format(state))
            for f in self.__inactivitychanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'InputPresenceChanged')
        def handleinputpresence(interface,state):
            self.Commands['InputPresence']['Status'][state[0]]['Live'] = str(state[1])
            update = {'command':'InputPresence','value':str(state[1]),'qualifier':{'Video Input':state[0]}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ InputPresence {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','InputPresenceChanged,{}'.format(state))
            for f in self.__inputpresencechanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'InputPresenceChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'LidChanged')
        def handlelidstate(interface,state):
            self.Commands['LidState']['Status']['Live'] = str(state)
            update = {'command':'LidState','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ LidState {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','LidStateChanged,{}'.format(state))
            for f in self.__lidchanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'LidStateChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'LightChanged')
        def handlelight(interface,state):
            self.Commands['AmbientLightValue']['Status']['Live'] = str(state)
            update = {'command':'AmbientLightValue','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ AmbientLightValue {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','AmbientLightValueChanged,{}'.format(state))
            for f in self.__lightchanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'AmbientLightValueChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        @_event(self.__interface,'MotionDetected')
        def handlemotion(interface,state):
            self.Commands['MotionState']['Status']['Live'] = str(state)
            update = {'command':'MotionState','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ MotionDetection {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','MotionDetectionChanged,{}'.format(state))
            for f in self.__motiondetected_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'MotionDetectionChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        '''
        try:
            @_event(self.__interface,'OverTemperatureChanged')
            def handleovertemp(interface,state):
                return
                self.Commands['OverTemperature']['Status']['Live'] = str(state)
                update = {'command':'OverTemperature','value':str(state),'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ OverTemperature {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','OverTemperatureChanged,{}'.format(state))
                for f in self.__overtemperaturechanged_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'OverTemperatureChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
        except:
            pass
        try:
            @_event(self.__interface,'OverTemperatureWarning')
            def handleovertempwarn(interface,state):
                self.Commands['OverTemperatureWarning']['Status']['Live'] = str(state)
                update = {'command':'OverTemperatureWarning','value':str(state),'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ OverTemperatureWarning {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','OverTemperatureWarningChanged,{}'.format(state))
                for f in self.__overtemperaturewarning_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'OverTemperatureWarning',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
        except:
            pass
        try:
            @_event(self.__interface,'OverTemperatureWarningStateChanged')
            def handleovertempwarnstate(interface,state):
                self.Commands['OverTemperatureWarningState']['Status']['Live'] = str(state)
                update = {'command':'OverTemperatureWarningState','value':str(state),'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ OverTemperatureWarningState {}'.format(self.__friendly_name,state)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','OverTemperatureWarningStateChanged,{}'.format(state))
                for f in self.__overtemperaturewarningstatechanged_event_callbacks:
                    try:
                        f(interface,state)
                    except Exception as e:
                        if sys_allowed_flag:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                        else:
                            err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'OverTemperatureWarningStateChanged',e)
                        print(err_msg)
                        DebugPrint.Print(err_msg)
                        _ProgramLog(err_msg)
        except:
            pass
        '''
        @_event(self.__interface,'SleepChanged')
        def handlesleep(interface,state):
            self.Commands['SleepState']['Status']['Live'] = str(state)
            update = {'command':'SleepState','value':str(state),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ SleepStatus {}'.format(self.__friendly_name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','SleepStatusChanged,{}'.format(state))
            for f in self.__sleepchanged_event_callbacks:
                try:
                    f(interface,state)
                except Exception as e:
                    if sys_allowed_flag:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                    else:
                        err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'SleepChanged',e)
                    print(err_msg)
                    DebugPrint.Print(err_msg)
                    _ProgramLog(err_msg)
        self.__print_to_trace('UIDevice({}) init events end'.format(self.__friendly_name))
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)
        self.__init_values_wait = _Wait(10,self.__init_values())
        self.__init_values_wait.Restart()
        self.__print_to_trace('UIDevice({}) init complete'.format(self.__friendly_name))

    def __init_values(self):
        def w():
            self.__print_to_trace('UIDevice({}) init commands start'.format(self.__friendly_name))
            self.__systemsettings = self.__interface.SystemSettings
            self.__userusage = self.__interface.UserUsage
            self.__autobrightness = self.__interface.AutoBrightness
            self.__wakeonmotion = self.__interface.WakeOnMotion
            self.__motiondecaytime = self.__interface.MotionDecayTime
            if self.__model:
                brightness = self.__interface.Brightness
                displaytimer = self.__interface.DisplayTimer
                sleeptimer = self.__interface.SleepTimer
                ambientlight = self.__interface.AmbientLightValue
                displaystate = self.__interface.DisplayState
                displaytimerenabled = self.__interface.DisplayTimerEnabled
                lightdetectedstate = self.__interface.LightDetectedState
                sleepstate = self.__interface.SleepState
                sleeptimerenabled = self.__interface.SleepTimerEnabled
                volumemaster = self.__interface.GetVolume('Master')
                volumeclick = self.__interface.GetVolume('Click')
                volumesound = self.__interface.GetVolume('Sound')
                volumehdmi = self.__interface.GetVolume('HDMI')
                volumextp = self.__interface.GetVolume('XTP')
                mutemaster = self.__interface.GetMute('Master')
                muteclick = self.__interface.GetMute('Click')
                mutesound = self.__interface.GetMute('Sound')
                mutehdmi = self.__interface.GetMute('HDMI')
                mutextp = self.__interface.GetMute('XTP')
            else:
                brightness = 'Unavailable'
                displaytimer = 'Unavailable'
                sleeptimer = 'Unavailable'
                ambientlight = 'Unavailable'
                displaystate = 'Unavailable'
                displaytimerenabled = 'Unavailable'
                lightdetectedstate = 'Unavailable'
                sleepstate = 'Unavailable'
                sleeptimerenabled = 'Unavailable'
                volumemaster = 'Unavailable'
                volumeclick = 'Unavailable'
                volumesound = 'Unavailable'
                volumehdmi = 'Unavailable'
                volumextp = 'Unavailable'
                mutemaster = 'Unavailable'
                muteclick = 'Unavailable'
                mutesound = 'Unavailable'
                mutehdmi = 'Unavailable'
                mutextp = 'Unavailable'
            self.Commands['HDCPStatus']['Status'] = {'HDMI':{'Live':self.__interface.GetHDCPStatus('HDMI')},'XTP':{'Live':self.__interface.GetHDCPStatus('XTP')}}
            update = {'command':'HDCPStatus','value':str(self.Commands['HDCPStatus']['Status']['HDMI']['Live']),'qualifier':{'Video Input':'HDMI'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'HDCPStatus','value':str(self.Commands['HDCPStatus']['Status']['XTP']['Live']),'qualifier':{'Video Input':'XTP'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['InputPresence']['Status'] = {'HDMI':{'Live':self.__interface.GetHDCPStatus('HDMI')},'XTP':{'Live':self.__interface.GetHDCPStatus('XTP')}}
            update = {'command':'InputPresence','value':str(self.Commands['InputPresence']['Status']['HDMI']['Live']),'qualifier':{'Video Input':'HDMI'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'InputPresence','value':str(self.Commands['InputPresence']['Status']['XTP']['Live']),'qualifier':{'Video Input':'XTP'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['Mute']['Status'] = {
                    'Master':{'Live':mutemaster},
                    'Click':{'Live':muteclick},
                    'Sound':{'Live':mutesound},
                    'HDMI':{'Live':mutehdmi},
                    'XTP':{'Live':mutextp}}
            update = {'command':'Mute','value':str(mutemaster),'qualifier':{'Channel Name':'Master'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Mute','value':str(muteclick),'qualifier':{'Channel Name':'Click'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Mute','value':str(mutesound),'qualifier':{'Channel Name':'Sound'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Mute','value':str(mutehdmi),'qualifier':{'Channel Name':'HDMI'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Mute','value':str(mutextp),'qualifier':{'Channel Name':'XTP'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['Volume']['Status'] = {
                    'Master':{'Live':volumemaster},
                    'Click':{'Live':volumeclick},
                    'Sound':{'Live':volumesound},
                    'HDMI':{'Live':volumehdmi},
                    'XTP':{'Live':volumextp}}
            update = {'command':'Volume','value':str(mutemaster),'qualifier':{'Channel Name':'Master'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Volume','value':str(muteclick),'qualifier':{'Channel Name':'Click'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Volume','value':str(mutesound),'qualifier':{'Channel Name':'Sound'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Volume','value':str(mutehdmi),'qualifier':{'Channel Name':'HDMI'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            update = {'command':'Volume','value':str(mutextp),'qualifier':{'Channel Name':'XTP'}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['AutoBrightness']['Status'] = {'Live':self.__interface.AutoBrightness}
            update = {'command':'AutoBrightness','value':str(self.Commands['AutoBrightness']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['Brightness']['Status'] = {'Live':brightness}
            update = {'command':'Brightness','value':str(self.Commands['Brightness']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['DisplayTimer']['Status'] = {'Live':displaytimer}
            update = {'command':'DisplayTimer','value':str(self.Commands['DisplayTimer']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['MotionDecayTime']['Status'] = {'Live':self.__interface.MotionDecayTime}
            update = {'command':'MotionDecayTime','value':str(self.Commands['MotionDecayTime']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['SleepTimer']['Status'] = {'Live':sleeptimer}
            update = {'command':'SleepTimer','value':str(self.Commands['SleepTimer']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['WakeOnMotion']['Status'] = {'Live':self.__interface.WakeOnMotion}
            update = {'command':'WakeOnMotion','value':str(self.Commands['WakeOnMotion']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['AmbientLightValue']['Status'] = {'Live':ambientlight}
            update = {'command':'AmbientLightValue','value':str(self.Commands['AmbientLightValue']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['DeviceAlias']['Status'] = {'Live':self.__interface.DeviceAlias}
            update = {'command':'DeviceAlias','value':str(self.Commands['DeviceAlias']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['DisplayState']['Status'] = {'Live':displaystate}
            update = {'command':'DisplayState','value':str(self.Commands['DisplayState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['DisplayTimerEnabled']['Status'] = {'Live':displaytimerenabled}
            update = {'command':'DisplayTimerEnabled','value':str(self.Commands['DisplayTimerEnabled']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['FirmwareVersion']['Status'] = {'Live':self.__interface.FirmwareVersion}
            update = {'command':'FirmwareVersion','value':str(self.Commands['FirmwareVersion']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['LidState']['Status'] = {'Live':self.__interface.LidState}
            update = {'command':'LidState','value':str(self.Commands['LidState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['LightDetectedState']['Status'] = {'Live':lightdetectedstate}
            update = {'command':'LightDetectedState','value':str(self.Commands['LightDetectedState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['LinkLicenses']['Status'] = {'Live':self.__interface.LinkLicenses}
            update = {'command':'LinkLicenses','value':str(self.Commands['LinkLicenses']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['ModelName']['Status'] = {'Live':self.__interface.ModelName}
            update = {'command':'ModelName','value':str(self.Commands['ModelName']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.Commands['MotionState']['Status'] = {'Live':self.__interface.MotionState}
            update = {'command':'MotionState','value':str(self.Commands['MotionState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            '''
            try:
                self.Commands['OverTemperature']['Status'] = {'Live':self.__interface.OverTemperature}
            except:
                self.Commands['OverTemperature']['Status'] = {'Live':None}
            update = {'command':'OverTemperature','value':str(self.Commands['OverTemperature']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['OverTemperatureWarningState']['Status'] = {'Live':self.__interface.OverTemperatureWarningState}
            except:
                self.Commands['OverTemperatureWarningState']['Status'] = {'Live':None}
            update = {'command':'OverTemperatureWarningState','value':str(self.Commands['OverTemperatureWarningState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            '''
            try:
                self.Commands['PartNumber']['Status'] = {'Live':self.__interface.PartNumber}
            except:
                self.Commands['PartNumber']['Status'] = {'Live':None}
            update = {'command':'PartNumber','value':str(self.Commands['PartNumber']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['SerialNumber']['Status'] = {'Live':self.__interface.SerialNumber}
            except:
                self.Commands['SerialNumber']['Status'] = {'Live':None}
            update = {'command':'SerialNumber','value':str(self.Commands['SerialNumber']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['SleepState']['Status'] = {'Live':sleepstate}
            except:
                self.Commands['SleepState']['Status'] = {'Live':None}
            update = {'command':'SleepState','value':str(self.Commands['SleepState']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['SleepTimerEnabled']['Status'] = {'Live':sleeptimerenabled}
            except:
                self.Commands['SleepTimerEnabled']['Status'] = {'Live':None}
            update = {'command':'SleepTimerEnabled','value':str(self.Commands['SleepTimerEnabled']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['SystemSettings']['Status'] = {'Live':self.__interface.SystemSettings}
            except:
                self.Commands['SystemSettings']['Status'] = {'Live':None}
            update = {'command':'SystemSettings','value':str(self.Commands['SystemSettings']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            try:
                self.Commands['UserUsage']['Status'] = {'Live':self.__interface.UserUsage}
            except:
                self.Commands['UserUsage']['Status'] = {'Live':None}
            update = {'command':'UserUsage','value':str(self.Commands['UserUsage']['Status']['Live']),'qualifier':None}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            self.__print_to_trace('UIDevice({}) init commands end'.format(self.__friendly_name))
            self.__polling_timer.Restart()
        return w
    def __create_polling_timer(self):
        def t(timer,count):
            somethingchanged = False
            if self.__userusage != self.__interface.UserUsage:
                somethingchanged = True
                self.__userusage = self.__interface.UserUsage
                self.Commands['UserUsage']['Status']['Live'] = self.__interface.UserUsage
                update = {'command':'UserUsage','value':self.Commands['UserUsage']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ UserUsage {}'.format(self.__friendly_name,self.__userusage)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','UserUsage,{}'.format(self.__userusage))
            if self.__systemsettings != self.__interface.SystemSettings:
                somethingchanged = True
                self.__systemsettings = self.__interface.SystemSettings
                self.Commands['SystemSettings']['Status']['Live'] = self.__interface.SystemSettings
                update = {'command':'SystemSettings','value':self.Commands['SystemSettings']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
            if self.__autobrightness != self.__interface.AutoBrightness:
                somethingchanged = True
                self.__autobrightness = self.__interface.AutoBrightness
                self.Commands['AutoBrightness']['Status']['Live'] = self.__interface.AutoBrightness
                update = {'command':'AutoBrightness','value':self.Commands['AutoBrightness']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ AutoBrightness {}'.format(self.__friendly_name,self.__autobrightness)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','AutoBrightnessChanged,{}'.format(self.__autobrightness))
            if self.__model:
                try:
                    displaystate = self.__interface.DisplayState
                except:
                    displaystate = 'Unavailable'
            else:
                displaystate = 'Unavailable'
            if self.__displaystate != displaystate:
                somethingchanged = True
                self.__displaystate = displaystate
                self.Commands['DisplayState']['Status']['Live'] = displaystate
                update = {'command':'DisplayState','value':self.Commands['DisplayState']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ DisplayState {}'.format(self.__friendly_name,displaystate)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','DisplayStateChanged,{}'.format(displaystate))
            if self.__model:
                try:
                    displaytimer = self.__interface.DisplayTimer
                except:
                    displaytimer = 'Unavailable'
            else:
                displaytimer = 'Unavailable'
            if self.__displaytimer != displaytimer:
                somethingchanged = True
                self.__displaytimer = displaytimer
                self.Commands['DisplayTimer']['Status']['Live'] = displaytimer
                update = {'command':'DisplayTimer','value':self.Commands['DisplayTimer']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ DisplayTimer {}'.format(self.__friendly_name,displaytimer)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','DisplayTimerChanged,{}'.format(displaytimer))
            if self.__model:
                try:
                    displaytimerenabled = self.__interface.DisplayTimerEnabled
                except:
                    displaytimerenabled = 'Unavailable'
            else:
                displaytimerenabled = 'Unavailable'
            if self.__displaytimerenabled != displaytimerenabled:
                somethingchanged = True
                self.__displaytimerenabled = displaytimerenabled
                self.Commands['DisplayTimerEnabled']['Status']['Live'] = displaytimerenabled
                update = {'command':'DisplayTimerEnabled','value':self.Commands['DisplayTimerEnabled']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ DisplayTimerEnabled {}'.format(self.__friendly_name,displaytimerenabled)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','DisplayTimerEnabledChanged,{}'.format(displaytimerenabled))
            try:
                inactivitytime = self.__interface.InactivityTime
            except:
                inactivitytime = 'Not Set'
            if self.__inactivitytime != inactivitytime:
                somethingchanged = True
                self.__inactivitytime = inactivitytime
                self.Commands['InactivityTime']['Status']['Live'] = inactivitytime
                update = {'command':'InactivityTime','value':self.Commands['InactivityTime']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ InactivityTime {}'.format(self.__friendly_name,inactivitytime)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','InactivityTime,{}'.format(inactivitytime))
            if self.__model:
                try:
                    lightdetectedstate = self.__interface.LightDetectedState
                except:
                    lightdetectedstate = 'Unavailable'
            else:
                lightdetectedstate = 'Unavailable'
            if self.__lightdetectedstate != lightdetectedstate:
                somethingchanged = True
                self.__lightdetectedstate = lightdetectedstate
                self.Commands['LightDetectedState']['Status']['Live'] = lightdetectedstate
                update = {'command':'LightDetectedState','value':self.Commands['LightDetectedState']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ LightDetectedState {}'.format(self.__friendly_name,lightdetectedstate)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','LightDetectedStateChanged,{}'.format(lightdetectedstate))
            if self.__motiondecaytime != self.__interface.MotionDecayTime:
                somethingchanged = True
                self.__motiondecaytime = self.__interface.SystemMotionDecayTimeSettings
                self.Commands['MotionDecayTime']['Status']['Live'] = self.__interface.MotionDecayTime
                update = {'command':'MotionDecayTime','value':self.Commands['MotionDecayTime']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ MotionDecayTime {}'.format(self.__friendly_name,self.__motiondecaytime)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','MotionDecayTimeChanged,{}'.format(self.__motiondecaytime))
            if self.__model:
                try:
                    sleeptimer = self.__interface.SleepTimer
                except:
                    sleeptimer = 'Unavailable'
            else:
                sleeptimer = 'Unavailable'
            if self.__sleeptimer != sleeptimer:
                somethingchanged = True
                self.__sleeptimer = sleeptimer
                self.Commands['SleepTimer']['Status']['Live'] = sleeptimer
                update = {'command':'SleepTimer','value':self.Commands['SleepTimer']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ SleepTimer {}'.format(self.__friendly_name,sleeptimer)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','SleepTimerChanged,{}'.format(sleeptimer))
            if self.__model:
                try:
                    sleeptimerenabled = self.__interface.SleepTimerEnabled
                except:
                    sleeptimerenabled = 'Unavailable'
            else:
                sleeptimerenabled = 'Unavailable'
            if self.__sleeptimerenabled != sleeptimerenabled:
                somethingchanged = True
                self.__sleeptimerenabled = sleeptimerenabled
                self.Commands['SleepTimerEnabled']['Status']['Live'] = sleeptimerenabled
                update = {'command':'SleepTimerEnabled','value':self.Commands['SleepTimerEnabled']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ SleepTimerEnabled {}'.format(self.__friendly_name,sleeptimerenabled)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','SleepTimerEnabledChanged,{}'.format(sleeptimerenabled))
            if self.__wakeonmotion != self.__interface.WakeOnMotion:
                somethingchanged = True
                self.__wakeonmotion = self.__interface.WakeOnMotion
                self.Commands['WakeOnMotion']['Status']['Live'] = self.__interface.WakeOnMotion
                update = {'command':'WakeOnMotion','value':self.Commands['WakeOnMotion']['Status']['Live'],'qualifier':None}
                self._DebugServer__send_interface_status(self.__listening_port,update)
                str_to_send = 'event: UI({}) ~ WakeOnMotion {}'.format(self.__friendly_name,self.__wakeonmotion)
                self.__print_to_trace(str_to_send)
                self.__printToServer(str_to_send)
                self.__printToLog(self.__friendly_name,'Event','WakeOnMotionChanged,{}'.format(self.__wakeonmotion))
        return t

    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type
    def GetHDCPStatus(self,videoInput:'str'):
        return self.__interface.GetHDCPStatus(videoInput)
    def GetMute(self,name:'str'):
        v = self.__interface.GetMute(name)
        if v != self.Commands['Mute']['Status'][name]['Live']:
            self.Commands['Mute']['Status'][name]['Live'] = v
            update = {'command':'Mute','value':v,'qualifier':{'Channel Name':name}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ Mute {} {}'.format(self.__friendly_name,name,v)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','MuteChanged,{}'.format(v))
        return v
    def GetVolume(self,name:'str'):
        v = self.__interface.GetVolume(name)
        if str(v) != self.Commands['Volume']['Status'][name]['Live']:
            self.Commands['Volume']['Status'][name]['Live'] = str(v)
            update = {'command':'Volume','value':str(v),'qualifier':{'Channel Name':name}}
            self._DebugServer__send_interface_status(self.__listening_port,update)
            str_to_send = 'event: UI({}) ~ Volume {} {}'.format(self.__friendly_name,name,v)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Event','VolumeChanged,{}'.format(v))
        return v
    def HideAllPopups(self):
        self.__interface.HideAllPopups()
        str_to_send = 'command: UI({}) ~ HideAllPopups()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HideAllPopups')
    def HidePopup(self,popup:'str'):
        self.__interface.HidePopup(popup)
        str_to_send = 'command: UI({}) ~ HidePopup({})'.format(self.__friendly_name,popup)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HidePopup,{}'.format(popup))
    def HidePopupGroup(self,group:'int'):
        self.__interface.HidePopupGroup(group)
        str_to_send = 'command: UI({}) ~ HidePopupGroup({})'.format(self.__friendly_name,group)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HidePopupGroup,{}'.format(group))
    def PlaySound(self,filename:'str'):
        self.__interface.PlaySound(filename)
        str_to_send = 'command: UI({}) ~ PlaySound({})'.format(self.__friendly_name,filename)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','PlaySound,{}'.format(filename))
    def Reboot(self):
        str_to_send = 'command: UI({}) ~ Reboot()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Reboot')
        self.__interface.Reboot()
    def SetAutoBrightness(self,state:'bool'):
        self.__interface.SetAutoBrightness(state)
        str_to_send = 'command: UI({}) ~ SetAutoBrightness({})'.format(self.__friendly_name,state)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetAutoBrightness,{}'.format(state))
    def SetBrightness(self,level:'int'):
        self.__interface.SetBrightness(level)
        str_to_send = 'command: UI({}) ~ SetBrightness({})'.format(self.__friendly_name,level)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetBrightness,{}'.format(level))
    def SetDisplayTimer(self,state:'bool',timeout:'int'):
        self.__interface.SetDisplayTimer(state)
        str_to_send = 'command: UI({}) ~ SetDisplayTimer({},{})'.format(self.__friendly_name,state,timeout)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetDisplayTimer,{},{}'.format(state,timeout))
    def SetInactivityTime(self,times:'list[int]'):
        self.__interface.SetInactivityTime(times)
        str_to_send = 'command: UI({}) ~ SetInactivityTime({})'.format(self.__friendly_name,times)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetDisplayTimer,{}'.format(times))
    def SetInput(self,videoInput:'str'):
        self.__interface.SetInput(videoInput)
        str_to_send = 'command: UI({}) ~ SetInput({})'.format(self.__friendly_name,videoInput)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetInput,{}'.format(videoInput))
    def SetLEDBlinking(self,ledId:'int',rate:'str',stateList:'list[str]'):
        self.__interface.SetLEDBlinking(ledId,rate,stateList)
        str_to_send = 'command: UI({}) ~ SetLEDBlinking({},{},{})'.format(self.__friendly_name,ledId,rate,stateList)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetLEDBlinking,{},{},{}'.format(ledId,rate,stateList))
    def SetLEDState(self,ledId:'int',state:'str'):
        self.__interface.SetLEDState(ledId,state)
        str_to_send = 'command: UI({}) ~ SetLEDState({},{})'.format(self.__friendly_name,ledId,state)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetLEDState,{},{}'.format(ledId,state))
    def SetMute(self,name:'str',mute:'str'):
        self.__interface.SetMute(name,mute)
        str_to_send = 'command: UI({}) ~ SetMute({},{})'.format(self.__friendly_name,name,mute)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetMute,{},{}'.format(name,mute))
    def SetSleepTimer(self,state:'bool',duration:'int'=None):
        self.__interface.SetSleepTimer(state,duration)
        str_to_send = 'command: UI({}) ~ SetSleepTimer({},{})'.format(self.__friendly_name,state,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetSleepTimer,{},{}'.format(state,duration))
    def SetMotionDecayTime(self,duration:'int'):
        self.__interface.SetMotionDecayTime(duration)
        str_to_send = 'command: UI({}) ~ SetMotionDecayTime({},{})'.format(self.__friendly_name,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetMotionDecayTime,{}'.format(duration))
    def SetVolume(self,name:'str',level:'int'):
        self.__interface.SetVolume(name,level)
        str_to_send = 'command: UI({}) ~ SetVolume({},{})'.format(self.__friendly_name,name,level)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetVolume,{},{}'.format(name,level))
    def SetWakeOnMotion(self,state:'bool'):
        self.__interface.SetWakeOnMotion(state)
        str_to_send = 'command: UI({}) ~ SetWakeOnMotion({})'.format(self.__friendly_name,state)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetWakeOnMotion,{}'.format(state))
    def ShowPage(self,page:'str'):
        self.__interface.ShowPage(page)
        str_to_send = 'command: UI({}) ~ ShowPage({})'.format(self.__friendly_name,page)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','ShowPage,{}'.format(page))
    def ShowPopup(self,popup:'str',duration:'int'=0):
        self.__interface.ShowPopup(popup,duration)
        str_to_send = 'command: UI({}) ~ ShowPopup({},{})'.format(self.__friendly_name,popup,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','ShowPopup,{},{}'.format(popup,duration))
    def Sleep(self):
        self.__interface.Sleep()
        str_to_send = 'command: UI({}) ~ Sleep()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Sleep')
    def StopSound(self):
        self.__interface.SetMotionDecayTime()
        str_to_send = 'command: UI({}) ~ StopSound()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','StopSound')
    def Wake(self):
        self.__interface.Wake()
        str_to_send = 'command: UI({}) ~ Wake()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Wake')

    def SubscribeStatus(self,command:'str',function:'object'):
        if command == 'Online':
            self.__online_event_callbacks.append(function)
        if command == 'Offline':
            self.__offline_event_callbacks.append(function)
        if command == 'BrightnessChanged':
            self.__brightnesschanged_event_callbacks.append(function)
        if command == 'HDCPStatusChanged':
            self.__hdcpstatuschanged_event_callbacks.append(function)
        if command == 'InactivityChanged':
            self.__inactivitychanged_event_callbacks.append(function)
        if command == 'InputPresenceChanged':
            self.__inputpresencechanged_event_callbacks.append(function)
        if command == 'LidChanged':
            self.__lidchanged_event_callbacks.append(function)
        if command == 'LightChanged':
            self.__lightchanged_event_callbacks.append(function)
        if command == 'MotionDetected':
            self.__motiondetected_event_callbacks.append(function)
        '''
        if command == 'OverTemperatureChanged':
            self.__overtemperaturechanged_event_callbacks.append(function)
        if command == 'OverTemperatureWarning':
            self.__overtemperaturewarning_event_callbacks.append(function)
        if command == 'OverTemperatureWarningStateChanged':
            self.__overtemperaturewarningstatechanged_event_callbacks.append(function)
        '''
        if command == 'SleepChanged':
            self.__sleepchanged_event_callbacks.append(function)

    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    @property
    def Device(self):
        return self.__interface
    @property
    def AmbientLightValue(self):
        if self.__model:
            return self.__interface.AmbientLightValue
        else:
            return 'Unavailable'
    @property
    def AutoBrightness(self):
        return self.__interface.AutoBrightness
    @property
    def Brightness(self):
        if self.__model:
            return self.__interface.Brightness
        else:
            return -1
    @property
    def DeviceAlias(self):
        return self.__interface.DeviceAlias
    @property
    def DisplayState(self):
        return self.__interface.DisplayState
    @property
    def DisplayTimer(self):
        if self.__model:
            return self.__interface.DisplayTimer
        else:
            return 'Unavailable'
    @property
    def DisplayTimerEnabled(self):
        if self.__model:
            return self.__interface.DisplayTimerEnabled
        else:
            return 'Unavailable'
    @property
    def FirmwareVersion(self):
        return self.__interface.FirmwareVersion
    @property
    def Hostname(self):
        return self.__interface.Hostname
    @property
    def IPAddress(self):
        return self.__interface.IPAddress
    @property
    def InactivityTime(self):
        try:
            return self.__interface.InactivityTime
        except:
            return 'Unavailable'
    @property
    def LidState(self):
        return self.__interface.LidState
    @property
    def LightDetectedState(self):
        if self.__model:
            return self.__interface.LightDetectedState
        else:
            return 'Unavailable'
    @property
    def LinkLicenses(self):
        return self.__interface.LinkLicenses
    @property
    def MACAddress(self):
        return self.__interface.MACAddress
    @property
    def ModelName(self):
        return self.__interface.ModelName
    @property
    def MotionDecayTime(self):
        return self.__interface.MotionDecayTime
    @property
    def MotionState(self):
        return self.__interface.MotionState
    @property
    def OverTemperature(self):
        try:
            return None#return self.__interface.OverTemperature
        except:
            return None
    @property
    def PartNumber(self):
        return self.__interface.PartNumber
    @property
    def SerialNumber(self):
        return self.__interface.SerialNumber
    @property
    def SleepState(self):
        if self.__model:
            return self.__interface.SleepState
        else:
            return 'Unavailable'
    @property
    def SleepTimer(self):
        if self.__model:
            return self.__interface.SleepTimer
        else:
            return 'Unavailable'
    @property
    def SleepTimerEnabled(self):
        if self.__model:
            return self.__interface.SleepTimerEnabled
        else:
            return 'Unavailable'
    @property
    def SystemSettings(self):
        return self.__interface.SystemSettings
    @property
    def UserUsage(self):
        return self.__interface.UserUsage
    @property
    def WakeOnMotion(self):
        return self.__interface.WakeOnMotion

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
        except:
            serverBuffer += data
        if 'ShowPage(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:ShowPage:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'ShowPage',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            if self.__interface and temp:
                self.ShowPage(temp)
        if 'ShowPopup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:ShowPopup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'ShowPopup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            temp2=temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = 0
            if self.__interface and temp1:
                self.ShowPopup(temp1,temp2)
        if 'HidePopupGroup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:HidePopupGroup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HidePopupGroup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            try:
                temp = int(temp)
            except:
                temp = None
            if self.__interface and temp:
                self.HidePopupGroup(temp)
        if 'HidePopup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:HidePopup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HidePopup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            if self.__interface and temp:
                self.HidePopup(temp)
        if 'HideAllPopups(' in serverBuffer:
            if self.__interface:
                self.HideAllPopups()
        if 'Wake(' in serverBuffer:
            if self.__interface:
                self.Wake()
        if 'Sleep(' in serverBuffer:
            if self.__interface:
                self.Sleep()
        if 'Reboot(' in serverBuffer:
            if self.__interface:
                self.Reboot()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)









"""
It is highly advised that after each combination of panels re-send indirect
Text fields,button states, visibility, other settings, popups, and page flips.
Items in combined panels do NOT sync with the combination process unless a sync
function is supplied.
Time required varies depending on how many items there are to combine.

Any panel or ID can be supplied either one at a time or as a list


example: adds panels to room, creates button events for 15 buttons, removes one of the panels from room,
adds new panel to room


Rm = VirtualUI(friendly_name='Virtual TP 1)
Rm.AddPanel([tp1,tp2]) # if using UIWrapper, use tp1.Device and tp2.Device

def foo1(button,state):
    pass
Rm.SetFunction(1,foo1,'Pressed',isMomentary=True) # include isMomentary parameter if you want automatic press/release feedback

def foo2(button,state):
    pass
Rm.SetFunction([range(2,16)],foo2,'Pressed',isMomentary=True)  # isMomentary is optional, default is false
Rm.SetFunction([range(2,16)],foo2,'Repeated')


def sync_panel_feedback(): #must have no parameters
    # do stuff to update pages, text, and button feedback across all attached panels
    # this will be called when using AddPanel
Rm.SetSyncFunction(sync_panel_feedback)

Rm.RemovePanel(tp2)
Rm.AddPanel(tp3)


"""
class VirtualUI(DebugServer):
    def __init__(self,listening_port:'int'=0,friendly_name:'str'=''):
        self.__interface_type = 'VirtualUI'
        self.__listening_port = listening_port
        self.__friendly_name = friendly_name
        if not self.__listening_port:
            self.__listening_port = self._DebugServer__create_listening_port()
        if not self.__friendly_name:
            self.__friendly_name = '{} {}'.format(self.__interface_type,self.__listening_port)

        self.EnableFileLogging = True

        self.__interface = self
        self.Commands = {}
        self._DebugServer__add_instance(self.__listening_port,self,self.__friendly_name,self.__interface_type)

        self.__enable_print_to_trace = self._DebugServer__get_nv_option(self.__listening_port)
        self.devTPs = [] #type:list[_UIDevice]

        self.__btns = [] #type:list[list[_Button]]
        self.__btnIDs = [] #type:list[list[int]]
        self.__btnHoldTimes = {} #type:list[list[float]]
        self.__btnRepeatTimes = {} #type:list[list[float]]
        self.__btnPushFunctions = {} #type:list[list[object]]
        self.__btnReleaseFunctions = {} #type:list[list[object]]
        self.__btnHoldFunctions = {} #type:list[list[object]]
        self.__btnTapFunctions = {} #type:list[list[object]]
        self.__btnRepeatFunctions = {} #type:list[list[object]]

        self.__knobs = [] #type:list[list[_Knob]]
        self.__knobIDs = [] #type:list[list[int]]
        self.__knobTurnFunctions = {} #type:list[list[object]]

        self.__lbls = [] #type:list[list[_Label]]
        self.__lblIDs = [] #type:list[list[int]]

        self.__lvls = [] #type:list[list[_Level]]
        self.__lvlIDs = [] #type:list[list[int]]


        self.__sliders =[] #type:list[list[_Slider]]
        self.__sliderIDs = [] #type:list[list[int]]
        self.__sliderChangedFunctions = {} #type:list[list[object]]
        self.__sliderPressedFunctions = {} #type:list[list[object]]
        self.__sliderReleasedFunctions = {} #type:list[list[object]]


        self.__SyncFunctions = [] #type:list[object]


    def GetInterface(self):
        return self.__interface
    def GetInterfaceType(self):
        return self.__interface_type

    def SetSyncFunction(self,function):
        self.__SyncFunctions.append(function)

    # this function adds a panel or list of panels to the virtual panel, then defines the buttons actions for the newly added panel
    def AddPanel(self,tps:'list[_UIDevice]'):
        tpList = [] #type:list[_UIDevice]
        if type(tps) is type([]):
            tpList.extend(tps)
        else:
            tpList.append(tps)

        for tp in tpList:
            if tp in self.devTPs:
                continue
            self.devTPs.append(tp)
            self.__btns.append({})
            self.__knobs.append({})
            self.__lbls.append({})
            self.__lvls.append({})
            self.__sliders.append({})
            str_to_send = 'config:VirtualUI({}) AddPanel({})'.format(self.__friendly_name,tp.DeviceAlias)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','AddPanel,{}'.format(tp.DeviceAlias))
            #create the button list for the new panel
            for itemID in self.__btnIDs:
                self.__btns[self.devTPs.index(tp)][itemID] = _Button(tp,itemID,self.__btnHoldTimes[itemID],self.__btnRepeatTimes[itemID])
            #define button events for new panel based on virtual panel vars
            for itemID in self.__btnPushFunctions.keys():
                @_event(self.__btns[self.devTPs.index(tp)][itemID],'Pressed')
                def Pressed(button,state):
                    for func in self.__btnPushFunctions[button.ID]:
                        try:
                            func(button,state)
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Pressed',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
            for itemID in self.__btnReleaseFunctions.keys():
                @_event(self.__btns[self.devTPs.index(tp)][itemID],'Released')
                def Released(button,state):
                    for func in self.__btnReleaseFunctions[button.ID]:
                        try:
                            func(button,state)
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Released',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
            for itemID in self.__btnHoldFunctions.keys():
                @_event(self.__btns[self.devTPs.index(tp)][itemID],'Held')
                def Held(button,state):
                    for func in self.__btnHoldFunctions[button.ID]:
                        try:
                            func(button,state)
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Held',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
            for itemID in self.__btnTapFunctions.keys():
                @_event(self.__btns[self.devTPs.index(tp)][itemID],'Tapped')
                def Tapped(button,state):
                    for func in self.__btnTapFunctions[button.ID]:
                        try:
                            func(button,state)
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Tapped',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
            for itemID in self.__btnRepeatFunctions.keys():
                @_event(self.__btns[self.devTPs.index(tp)][itemID],'Repeated')
                def Repeated(button,state):
                    for func in self.__btnRepeatFunctions[button.ID]:
                        try:
                            func(button,state)
                        except Exception as e:
                            if sys_allowed_flag:
                                err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,traceback.format_exc())
                            else:
                                err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Repeated',e)
                            print(err_msg)
                            DebugPrint.Print(err_msg)
                            _ProgramLog(err_msg)
            #create the knob list for the new panel
            for itemID in self.__knobIDs:
                self.__knobs[self.devTPs.index(tp)][itemID] = _Knob(tp,itemID)
                #define knob events for new panel based on virtual panel vars
                if itemID in self.__knobTurnFunctions.keys():
                    @_event(self.__knobs[self.devTPs.index(tp)][itemID],'Turned')
                    def Turned(knob,direction):
                        for func in self.__knobTurnFunctions[knob.ID]:
                            try:
                                func(knob,direction)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Knob:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,knob.ID,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Turned',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)


            #create the label list for the new panel
            for itemID in self.__lblIDs:
                self.__lbls[self.devTPs.index(tp)][itemID] = _Label(tp,itemID)

            #create the level list for the new panel
            for itemID in self.__lvlIDs:
                self.__lvls[self.devTPs.index(tp)][itemID] = _Level(tp,itemID)

            #create the slider list for the new panel
            for itemID in self.__sliderIDs:
                self.__sliders[self.devTPs.index(tp)][itemID] = _Slider(tp,itemID)
                #define slider events for new panel based on virtual panel vars
                if itemID in self.__sliderChangedFunctions.keys():
                    @_event(self.__sliders[self.devTPs.index(tp)][itemID],'Changed')
                    def Changed(slider,state,value):
                        for func in self.__sliderChangedFunctions[slider.ID]:
                            try:
                                func(slider,state,value)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Slider:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,slider.ID,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Changed',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)

                if itemID in self.__sliderPressedFunctions.keys():
                    @_event(self.__sliders[self.devTPs.index(tp)][itemID],'Pressed')
                    def Pressed(slider,state,value):
                        for func in self.__sliderPressedFunctions[slider.ID]:
                            try:
                                func(slider,state,value)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Slider:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,slider.ID,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Pressed',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
                if itemID in self.__sliderReleasedFunctions.keys():
                    @_event(self.__sliders[self.devTPs.index(tp)][itemID],'Released')
                    def Released(slider,state,value):
                        for func in self.__sliderReleasedFunctions[slider.ID]:
                            try:
                                func(slider,state,value)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Slider:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,slider.ID,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Released',e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)

        #resync panels for virtual panel
        if len(self.__SyncFunctions) > 0:
            for func in self.__SyncFunctions:
                func()

    # this function removes a panel or list of panels from the virtual panel
    def RemovePanel(self,tps:'_UIDevice'):
        tpList = []
        if type(tps) is type([]):
            tpList.extend(tps)
        else:
            tpList.append(tps)
        for tp in tpList:
            str_to_send = 'config: VirtualUI({}) ~ RemovePanel({})'.format(self.__friendly_name,tp.DeviceAlias)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','RemovePanel,{}'.format(tp.DeviceAlias))
            del self.__btns[self.devTPs.index(tp)]
            del self.__knobs[self.devTPs.index(tp)]
            del self.__lbls[self.devTPs.index(tp)]
            del self.__lvls[self.devTPs.index(tp)]
            del self.__sliders[self.devTPs.index(tp)]
            self.devTPs.remove(tp)

    def RemoveAllPanels(self):
        for tp in self.devTPs:
            str_to_send = 'config: VirtualUI({}) ~ RemovePanel({})'.format(self.__friendly_name,tp.DeviceAlias)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','RemovePanel,{}'.format(tp.DeviceAlias))
            del self.__btns[self.devTPs.index(tp)]
            del self.__knobs[self.devTPs.index(tp)]
            del self.__lbls[self.devTPs.index(tp)]
            del self.__lvls[self.devTPs.index(tp)]
            del self.__sliders[self.devTPs.index(tp)]
            self.devTPs.remove(tp)

    # panel navigation functions
    def HideAllPopups(self):
        for tp in self.devTPs:
            tp.HideAllPopups()
        str_to_send = 'command: VirtualUI({}) ~ HideAllPopups()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HideAllPopups')
    def HidePopup(self,value:str):
        for tp in self.devTPs:
            tp.HidePopup(value)
        str_to_send = 'command: VirtualUI({}) ~ HidePopup({})'.format(self.__friendly_name,value)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HidePopup,{}'.format(value))
    def HidePopupGroup(self,value:str):
        for tp in self.devTPs:
            tp.HidePopupGroup(value)
        str_to_send = 'command: VirtualUI({}) ~ HidePopupGroup({})'.format(self.__friendly_name,value)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','HidePopupGroup,{}'.format(value))
    def ShowPage(self,value:str):
        for tp in self.devTPs:
            tp.ShowPage(value)
        str_to_send = 'command: VirtualUI({}) ~ ShowPage({})'.format(self.__friendly_name,value)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','ShowPage,{}'.format(value))
    def ShowPopup(self,value:str,duration:int=0):
        for tp in self.devTPs:
            tp.ShowPopup(value,duration)
        str_to_send = 'command: VirtualUI({}) ~ ShowPopup({},{})'.format(self.__friendly_name,value,duration)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','ShowPopup,{},{}'.format(value,duration))
    def Wake(self):
        for tp in self.devTPs:
            tp.Wake()
        str_to_send = 'command: VirtualUI({}) ~ Wake()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Wake')
    def Sleep(self):
        for tp in self.devTPs:
            tp.Sleep()
        str_to_send = 'command: VirtualUI({}) ~ Sleep()'.format(self.__friendly_name)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','Sleep')
    def __create_default_button_event_handler(self):
        def e(button:'_Button',state:'str'):
            str_to_send = 'event: VirtualUI({}) ~ Button({},{}) {}'.format(button.Host,button.ID,button.Name,state)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Command','Button,{},{},{},{}'.format(button.Host,button.ID,button.Name,state))
        return e
    # this function adds buttons to the data for the virtual panel
    def AddButton(self,itemIDs,holdTime:float=None,repeatTime:float=None,isMomentary:bool=False):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                print('VirtualUI({}) ~ AddButton() ~ ID{}: ID already in button ID list'.format(self.__friendly_name,itemID))
                continue
            self.__btnIDs.append(itemID)
            self.__btnHoldTimes[itemID] = holdTime
            self.__btnRepeatTimes[itemID] = repeatTime
            '''
            self.__btnPushFunctions[itemID] = [self.__create_default_button_event_handler()]
            self.__btnReleaseFunctions[itemID] = [self.__create_default_button_event_handler()]
            self.__btnHoldFunctions[itemID] = [self.__create_default_button_event_handler()]
            self.__btnTapFunctions[itemID] = [self.__create_default_button_event_handler()]
            self.__btnRepeatFunctions[itemID] = [self.__create_default_button_event_handler()]
            '''
            for tp in self.devTPs:
                self.__btns[self.devTPs.index(tp)][itemID] = _Button(tp,itemID,holdTime,repeatTime)

            self.SetFunction(itemID,self.__create_default_button_event_handler(),'Pressed')
            self.SetFunction(itemID,self.__create_default_button_event_handler(),'Released')
            self.SetFunction(itemID,self.__create_default_button_event_handler(),'Held')
            self.SetFunction(itemID,self.__create_default_button_event_handler(),'Tapped')
            self.SetFunction(itemID,self.__create_default_button_event_handler(),'Repeated')

            if isMomentary:
                def pressed(button:'_Button',state):
                    button.SetState(1)
                def released(button:'_Button',state):
                    button.SetState(0)
                self.SetFunction(itemID,pressed,'Pressed')
                self.SetFunction(itemID,released,'Released')
                self.SetFunction(itemID,released,'Held')
                self.SetFunction(itemID,released,'Tapped')
    def GetButton(self,itemID):
        btnlist = []
        for blist in self.__btns:
            if itemID in blist:
                btnlist.append(blist[itemID])
        return btnlist
    def __create_default_knob_event_handler(self):
        def e(knob:'_Knob',direction:'int'):
            str_to_send = 'event: VirtualUI({}) ~ Knob({},{}) ~ Turned({})'.format(knob.Host,knob.ID,knob.Name,direction)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
        return e
    # this function adds knobs to the data for the virtual panel
    def AddKnob(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__knobIDs:
                continue
            self.__knobIDs.append(itemID)
            #self.__knobTurnFunctions[itemID] = [self.__create_default_knob_event_handler()]
            for tp in self.devTPs:
                self.__knobs[self.devTPs.index(tp)][itemID] = _Knob(tp,itemID)
            self.SetFunction(itemID,self.__create_default_knob_event_handler(),'Turned')
    def GetKnob(self,itemID):
        btnlist = []
        for blist in self.__knobs:
            if itemID in blist:
                btnlist.append(blist[itemID])
        return btnlist
    # this function adds knobs to the data for the virtual panel
    def AddLevel(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__lvlIDs:
                continue
            self.__lvlIDs.append(itemID)
            for tp in self.devTPs:
                self.__lvls[self.devTPs.index(tp)][itemID] = _Level(tp,itemID)
    def GetLevel(self,itemID):
        btnlist = []
        for blist in self.__lvls:
            if itemID in blist:
                btnlist.append(blist[itemID])
        return btnlist
    def __create_default_slider_event_handler(self):
        def e(slider:'_Slider',state:'str',value:'int'):
            str_to_send = 'event: VirtualUI({}) ~ Slider({},{}) ~ {}({})'.format(slider.Host,slider.ID,slider.Name,state,value)
            self.__print_to_trace(str_to_send)
            self.__printToServer(str_to_send)
        return e
    # this function adds sliders to the date for the virtual panel
    def AddSlider(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__sliderIDs:
                continue
            self.__sliderIDs.append(itemID)
            '''
            self.__sliderChangedFunctions[itemID] = [self.__create_default_slider_event_handler()]
            self.__sliderPressedFunctions[itemID] = [self.__create_default_slider_event_handler()]
            self.__sliderReleasedFunctions[itemID] = [self.__create_default_slider_event_handler()]
            '''
            for tp in self.devTPs:
                self.__sliders[self.devTPs.index(tp)][itemID] = _Slider(tp,itemID)
            self.SetFunction(itemID,self.__create_default_slider_event_handler(),'Changed')
            self.SetFunction(itemID,self.__create_default_slider_event_handler(),'Pressed')
            self.SetFunction(itemID,self.__create_default_slider_event_handler(),'Released')
    def GetSlider(self,itemID):
        btnlist = []
        for blist in self.__sliders:
            if itemID in blist:
                btnlist.append(blist[itemID])
        return btnlist

    # this function adds knobs to the data for the virtual panel
    def AddLabel(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__lblIDs:
                continue
            self.__lblIDs.append(itemID)
            for tp in self.devTPs:
                self.__lbls[self.devTPs.index(tp)][itemID] = _Label(tp,itemID)
    def GetLabel(self,itemID):
        btnlist = []
        for blist in self.__lbls:
            if itemID in blist:
                btnlist.append(blist[itemID])
        return btnlist
    # associates a button with given ID with a function for pressed action for each TP in virtual panel
    def SetFunction(self,itemIDs:'list[int]',function,trigger:str):
        idList = []
        func_list = None
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                if trigger == 'Pressed':
                    if itemID in self.__btnPushFunctions.keys():
                        if function not in self.__btnPushFunctions[itemID]:
                            self.__btnPushFunctions[itemID].append(function)
                    else:
                        self.__btnPushFunctions[itemID] = [function]
                    func_list = self.__btnPushFunctions[itemID]
                elif trigger == 'Released':
                    if itemID in self.__btnReleaseFunctions.keys():
                        if function not in self.__btnReleaseFunctions[itemID]:
                            self.__btnReleaseFunctions[itemID].append(function)
                    else:
                        self.__btnReleaseFunctions[itemID] = [function]
                    func_list = self.__btnReleaseFunctions[itemID]
                elif trigger == 'Held':
                    if itemID in self.__btnHoldFunctions.keys():
                        if function not in self.__btnHoldFunctions[itemID]:
                            self.__btnHoldFunctions[itemID].append(function)
                    else:
                        self.__btnHoldFunctions[itemID] = [function]
                    func_list = self.__btnHoldFunctions[itemID]
                elif trigger == 'Tapped':
                    if itemID in self.__btnTapFunctions.keys():
                        if function not in self.__btnTapFunctions[itemID]:
                            self.__btnTapFunctions[itemID].append(function)
                    else:
                        self.__btnTapFunctions[itemID] = [function]
                    func_list = self.__btnTapFunctions[itemID]
                elif trigger == 'Repeated':
                    if itemID in self.__btnRepeatFunctions.keys():
                        if function not in self.__btnRepeatFunctions[itemID]:
                            self.__btnRepeatFunctions[itemID].append(function)
                    else:
                        self.__btnRepeatFunctions[itemID] = [function]
                    func_list = self.__btnRepeatFunctions[itemID]
                for tp in self.devTPs:
                    @_event(self.__btns[self.devTPs.index(tp)][itemID],trigger)
                    def stuff(button,state):
                        for func in func_list:
                            try:
                                func(button,state)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Button:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,button.ID,state,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,trigger,e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
            elif itemID in self.__knobIDs:
                if trigger == 'Turned':
                    if itemID in self.__knobTurnFunctions.keys():
                        if function not in self.__knobTurnFunctions[itemID]:
                            self.__knobTurnFunctions[itemID].append(function)
                    else:
                        self.__knobTurnFunctions[itemID] = [function]
                    func_list = self.__knobTurnFunctions[itemID]
                for tp in self.devTPs:
                    @_event(self.__knobs[self.devTPs.index(tp)][itemID],trigger)
                    def stuff(knob,direction):
                        for func in func_list:
                            try:
                                func(knob,direction)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Knob:{}:Turned:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,knob.ID,direction,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,trigger,e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
            elif itemID in self.__sliderIDs:
                if trigger == 'Changed':
                    if itemID in self.__sliderChangedFunctions.keys():
                        if function not in self.__sliderChangedFunctions[itemID]:
                            self.__sliderChangedFunctions[itemID].append(function)
                    else:
                        self.__sliderChangedFunctions[itemID] = [function]
                    func_list = self.__sliderChangedFunctions[itemID]
                if trigger == 'Pressed':
                    if itemID in self.__sliderPressedFunctions.keys():
                        if function not in self.__sliderPressedFunctions[itemID]:
                            self.__sliderPressedFunctions[itemID].append(function)
                    else:
                        self.__sliderPressedFunctions[itemID] = [function]
                    func_list = self.__sliderPressedFunctions[itemID]
                if trigger == 'Released':
                    if itemID in self.__sliderReleasedFunctions.keys():
                        if function not in self.__sliderReleasedFunctions[itemID]:
                            self.__sliderReleasedFunctions[itemID].append(function)
                    else:
                        self.__sliderReleasedFunctions[itemID] = [function]
                    func_list = self.__sliderReleasedFunctions[itemID]
                for tp in self.devTPs:
                    @_event(self.__sliders[self.devTPs.index(tp)][itemID],trigger)
                    def stuff(slider,state,value):
                        for func in func_list:
                            try:
                                func(slider,state)
                            except Exception as e:
                                if sys_allowed_flag:
                                    err_msg = 'EXCEPTION:{}:{}:{}:Knob:{}:{}:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,slider.ID,state,traceback.format_exc())
                                else:
                                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,trigger,e)
                                print(err_msg)
                                DebugPrint.Print(err_msg)
                                _ProgramLog(err_msg)
            else:
                print('Setfunction Failed : invalid ID ',str(itemID))

    # modify values of items for each panel by ID number or name
    def SetState(self,itemIDs:'list[int]',value:int):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__btns[self.devTPs.index(tp)][itemID]
                    item.SetState(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetState({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetState{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetState Failed : invalid ID ',str(itemID))
    def SetText(self,itemIDs:'list[int]',value:str):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__btns[self.devTPs.index(tp)][itemID]
                    item.SetText(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetText({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetText{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            elif itemID in self.__lblIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__lbls[self.devTPs.index(tp)][itemID]
                    item.SetText(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetText({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetText,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetText Failed : invalid ID ',str(itemID))
    def SetBlinking(self,itemIDs:'list[int]',rate:str,value:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__btns[self.devTPs.index(tp)][itemID]
                    item.SetBlinking(rate,value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetBlinking({},{})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,rate,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','Blinking,{},{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,rate,value))
            else:
                print('SetBlinking Failed : invalid ID ',str(itemID))
    def SetLevel(self,itemIDs:'list[int]',value:int):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__lvlIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__lvls[self.devTPs.index(tp)][itemID]
                    item.SetLevel(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetLevel({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetLevel,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetLevel Failed : invalid ID ',str(itemID))
    def SetFill(self,itemIDs:'list[int]',value:int):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__sliderIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__sliders[self.devTPs.index(tp)][itemID]
                    item.SetFill(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetFill({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetFill,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetFill Failed : invalid ID ',str(itemID))

    def SetEnable(self,itemIDs:'list[int]',value:bool):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__btns[self.devTPs.index(tp)][itemID]
                    item.SetEnable(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetEnable({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetEnable,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            elif itemID in self.__sliderIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__sliders[self.devTPs.index(tp)][itemID]
                    item.SetEnable(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetEnable({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetEnable,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetEnable Failed : invalid ID ',str(itemID))
    def SetVisible(self,itemIDs:'list[int]',value:bool):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__btns[self.devTPs.index(tp)][itemID]
                    item.SetVisible(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetVisible({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetVisible,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            elif itemID in self.__lblIDs:
                item = None
                for tp in self.devTPs:
                    self.__lbls[self.devTPs.index(tp)][itemID].SetVisible(value)
                    item = self.__lbls[self.devTPs.index(tp)][itemID]
                    item.SetVisible(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetVisible({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetVisible,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            elif itemID in self.__lvlIDs:
                item = None
                for tp in self.devTPs:
                    self.__lvls[self.devTPs.index(tp)][itemID].SetVisible(value)
                    item = self.__lvls[self.devTPs.index(tp)][itemID]
                    item.SetVisible(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetVisible({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetVisible,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            elif itemID in self.__sliderIDs:
                item = None
                for tp in self.devTPs:
                    self.__sliders[self.devTPs.index(tp)][itemID].SetVisible(value)
                    item = self.__sliders[self.devTPs.index(tp)][itemID]
                    item.SetVisible(value)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetVisible({})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,value)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetVisible,{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,value))
            else:
                print('SetVisible Failed : invalid ID ',str(itemID))
    def SetRange(self,itemIDs:'list[int]',minimum:int,maximum:int,step:int = 1):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            item = None
            if itemID in self.__lvlIDs:
                for tp in self.devTPs:
                    item = self.__lvls[self.devTPs.index(tp)][itemID]
                    item.SetRange(minimum,maximum,step)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetRange({},{},{})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,minimum,maximum,step)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetRange,{},{},{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,minimum,maximum,step))
            elif itemID in self.__sliderIDs:
                item = None
                for tp in self.devTPs:
                    item = self.__sliders[self.devTPs.index(tp)][itemID]
                    item.SetRange(minimum,maximum,step)
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ SetRange({},{},{})'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name,minimum,maximum,step)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SetState,{},{},{},{},{},{}'.format(type(item).__name__,item.ID,item.Name,minimum,maximum,step))
            else:
                print('SetRange Failed : invalid ID ',str(itemID))
    def Dec(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__lvlIDs:
                item = None
                for tp in self.devTPs:
                    self.__lvls[self.devTPs.index(tp)][itemID].Dec()
                    item = self.__lvls[self.devTPs.index(tp)][itemID]
                    item.Dec()
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ Dec()'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','Dec,{},{},{}'.format(type(item).__name__,item.ID,item.Name))
            else:
                print('Dec Failed : invalid ID ',str(itemID))
    def Inc(self,itemIDs:'list[int]'):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__lvlIDs:
                item = None
                for tp in self.devTPs:
                    self.__lvls[self.devTPs.index(tp)][itemID].Inc()
                    item = self.__lvls[self.devTPs.index(tp)][itemID]
                    item.Inc()
                if item:
                    str_to_send = 'command: VirtualUI({}) ~ {}({},{}) ~ Inc()'.format(self.__friendly_name,type(item).__name__,item.ID,item.Name)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','Inc,{},{},{}'.format(type(item).__name__,item.ID,item.Name))
            else:
                print('Inc Failed : invalid ID ',str(itemID))

    def SimulateAction(self,itemID:int,action:str,value:str=None):
        str_to_send = 'command: VirtualUI({}) ~ Button({}) ~ SimulateAction ~ {}'.format(self.__friendly_name,itemID,action)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        func = None
        if len(self.__btnIDs):
            if itemID in self.__btnIDs:
                try:
                    func = getattr(self.__btns[0][itemID], '%s' % action)(self.__btns[0][itemID],action)
                except AttributeError:
                    str_to_send = 'command: VirtualUI({}) ~ Button({}) ~ SimulateAction ~ Does Not Support {}'.format(self.__friendly_name,itemID,action)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SimulateAction,Button,{},{}'.format(type(self.__btns[0][itemID]).__name__,itemID,action))
                return
        if len(self.__knobIDs):
            if itemID in self.__knobIDs:
                try:
                    func = getattr(self.__knobs[0][itemID], '%s' % action)(self.__knobs[0][itemID],action)
                except AttributeError:
                    str_to_send = 'command: VirtualUI({}) ~ Knob({}) ~ SimulateAction ~ Does Not Support {}'.format(self.__friendly_name,itemID,action)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SimulateAction,Knob,{},{}'.format(type(self.__knobIDs[0][itemID]).__name__,itemID,action))
                return
        if len(self.__sliderIDs):
            if itemID in self.__sliderIDs:
                try:
                    if action is not 'Changed':
                        func = getattr(self.__sliders[0][itemID], '%s' % action)(self.__sliders[0][itemID],action)
                    else:
                        func = getattr(self.__sliders[0][itemID], '%s' % action)(self.__sliders[0][itemID],action,value)
                except AttributeError:
                    str_to_send = 'command: VirtualUI({}) ~ Slider({}) ~ SimulateAction ~ Does Not Support {}'.format(self.__friendly_name,itemID,action)
                    self.__print_to_trace(str_to_send)
                    self.__printToServer(str_to_send)
                    self.__printToLog(self.__friendly_name,'Command','SimulateAction,Slider,{},{}'.format(type(self.__sliderIDs[0][itemID]).__name__,itemID,action))
                return
        str_to_send = 'command: VirtualUI({}) ~ Slider({}) ~ SimulateAction ~ {} ERROR : ID not found'.format(self.__friendly_name,itemID,action)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SimulateAction,Button,{},{}'.format(type(self.__sliderIDs[0][itemID]).__name__,itemID,action))

    def SetCurrent(self,btnIDs:'list[int]',item:int):
        for btnID in btnIDs:
            if btnID == item:
                self.SetState(btnID,1)
            else:
                self.SetState(btnID,0)
        str_to_send = 'command: VirtualUI({}) ~ Button({}) ~ SetCurrent({},{})'.format(self.__friendly_name,type(item).__name__,btnIDs,item)
        self.__print_to_trace(str_to_send)
        self.__printToServer(str_to_send)
        self.__printToLog(self.__friendly_name,'Command','SetCurrent,{},{},{}'.format(type(item).__name__,btnIDs,item))

    # modify values of items for each panel by ID number or name
    def TriggerEvent(self,itemIDs:'list[int]',value:int):
        idList = []
        if type(itemIDs) is type([]):
            idList.extend(itemIDs)
        else:
            idList.append(itemIDs)
        for itemID in idList:
            if itemID in self.__btnIDs:
                btn = self.GetButton(itemID)
                if value == 'Pressed':
                    if itemID in self.__btnPushFunctions:
                        for function in self.__btnPushFunctions[itemID]:
                            function(btn,'Pressed')
                elif value == 'Released':
                    if itemID in self.__btnReleaseFunctions:
                        for function in self.__btnReleaseFunctions[itemID]:
                            function(btn,'Pressed')
                elif value == 'Repeated':
                    if itemID in self.__btnRepeatFunctions:
                        for function in self.__btnRepeatFunctions[itemID]:
                            function(btn,'Pressed')
                elif value == 'Held':
                    if itemID in self.__btnHoldFunctions:
                        for function in self.__btnHoldFunctions[itemID]:
                            function(btn,'Pressed')
                elif value == 'Tapped':
                    if itemID in self.__btnTapFunctions:
                        for function in self.__btnTapFunctions[itemID]:
                            function(btn,'Pressed')
                else:
                    print('command: VirtualUI({}) ~ TriggerEvent({},{}) Failed ~ Invalid Event Type'.format(self.__friendly_name,itemIDs,value))
            else:
                print('command: VirtualUI({}) ~ TriggerEvent({},{}) Failed ~ Invalid ID'.format(self.__friendly_name,itemIDs,value))


    def __printToLog(self,device,message_type,data):
        if(self.EnableFileLogging):
            DebugFileLogSaver.AddLog(device,message_type,data)

    def __printToServer(self,string):
        timestamp = str(_datetime.now())
        str_to_send = repr(string)
        str_to_send = '{} {}'.format(timestamp,str_to_send[1:])
        self._DebugServer__send_interface_communication(self.__listening_port,str_to_send)

    def HandleReceiveFromServer(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
        except:
            serverBuffer += data
        if 'SetState(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetState:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetState',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2 = temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = -1
            if self.__interface and temp1 and temp2>=0:
                self.SetState(temp1,temp2)
        if 'SetText(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetText:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetText',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2 = temp_dict['value2']
            if self.__interface and temp1:
                self.SetText(temp1,temp2)
        if 'SetBlinking(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetBlinking:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetBlinking',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            temp3=temp_dict['value3']
            try:
                temp3 = [int(i) for i in temp3]
            except:
                temp3 = None
            if self.__interface and temp1 and temp2 and temp3:
                self.SetBlinking(temp1,temp2,temp3)
        if 'SetLevel(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetLevel:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetLevel',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = -1
            if self.__interface and temp1 and temp2>=0:
                self.SetLevel(temp1,temp2)
        if 'SetFill(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetFill:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetFill',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = -1
            if self.__interface and temp1 and temp2>=0:
                self.SetFill(temp1,temp2)
        if 'SetEnable(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetEnable:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetEnable',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            vals = {'True':True,'False':False}
            if temp2 not in vals:
                temp2 = None
            if self.__interface and temp1 and temp2 in ['True','False']:
                self.SetEnable(temp1,vals[temp2])
        if 'SetVisible(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:SetVisible:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:SetVisible',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            vals = {'True':True,'False':False}
            if temp2 not in vals:
                temp2 = None
            if self.__interface and temp1 and temp2 in ['True','False']:
                self.SetVisible(temp1,vals[temp2])
        if 'SetRange(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                err_msg = 'EXCEPTION:{}:{}:{}:SetRange:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            temp2=temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = -1000
            temp3=temp_dict['value3']
            try:
                temp3 = int(temp3)
            except:
                temp3 = -1000
            temp4=temp_dict['value4']
            try:
                temp4 = int(temp4)
            except:
                temp4 = 1
            if self.__interface and temp1 and temp2>-1000 and temp3>-1000 and temp4>0:
                self.SetRange(temp1,temp2,temp3,temp4)
        if 'Dec(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Dec:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Dec',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            if self.__interface and temp1:
                self.Dec(temp1)
        if 'Inc(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Inc:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Inc',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            try:
                temp1 = [int(i) for i in temp1]
            except:
                temp1 = None
            if self.__interface and temp1:
                self.Inc(temp1)
        if 'Emulate(' in serverBuffer:
            print('in emulate button')
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Emulate:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:Emulate',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            print('in emulate button:{}'.format(temp_dict))
            temp1 = temp_dict['value1']
            temp2 = temp_dict['value2']
            temp3 = temp_dict['value3']
            try:
                temp1 = int(temp1)
                temp3 = int(temp3)
            except:
                return
            if self.__interface and temp1 and temp2:
                self.SimulateAction(temp1,temp2,temp3)
        if 'ShowPage(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:ShowPage:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:ShowPage',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            if self.__interface and temp:
                self.ShowPage(temp)
        if 'ShowPopup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:ShowPopup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:ShowPopup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp1=temp_dict['value1']
            temp2=temp_dict['value2']
            try:
                temp2 = int(temp2)
            except:
                temp2 = 0
            if self.__interface and temp1:
                self.ShowPopup(temp1,temp2)
        if 'HidePopupGroup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:HidePopupGroup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleReceiveFromServer:HidePopupGroup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            try:
                temp = int(temp)
            except:
                return
            if self.__interface and temp >= 0:
                self.HidePopupGroup(temp)
        if 'HidePopup(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:HidePopup:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'HandleRecieveFromServer:HidePopup',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
                return
            temp=temp_dict['value1']
            if self.__interface and temp:
                self.HidePopup(temp)
        if 'HideAllPopups(' in serverBuffer:
            if self.__interface:
                self.HideAllPopups()

    def HandleOptions(self,client,data:'bytes'):
        serverBuffer = ''
        try:
            serverBuffer += data.decode()
            #print('module recieve data:{}'.format(data.decode()))
        except:
            serverBuffer += data
            #print('module recieve data:{}'.format(data))
        if 'Option(' in serverBuffer:
            temp = serverBuffer[serverBuffer.find('(')+1:serverBuffer.rfind(')')]
            temp_dict = {}
            try:
                temp_dict = _json.loads(temp)
            except Exception as e:
                if sys_allowed_flag:
                    err_msg = 'EXCEPTION:{}:{}:{}:Option:{}'.format(__class__.__name__,sys._getframe().f_code.co_name,self.__friendly_name,traceback.format_exc())
                else:
                    err_msg = 'EXCEPTION:{}:{}:{}:{}'.format(__class__.__name__,self.__friendly_name,'Option',e)
                print(err_msg)
                DebugPrint.Print(err_msg)
                _ProgramLog(err_msg)
            cmd = ''
            if 'option' in temp_dict:
                cmd = temp_dict['option']
            value = ''
            if 'value' in temp_dict:
                value = temp_dict['value']
            if cmd == 'print to trace':
                self.__enable_print_to_trace = value
            str_to_send = 'command: Module({}) ~ PrintToTrace({})'.format(self.__friendly_name,value)
            print(str_to_send)
            self.__printToServer(str_to_send)
            self.__printToLog(self.__friendly_name,'Option', 'PrintToTrace,{}'.format(value))
            self._DebugServer__update_nv_option(self.__listening_port,cmd,value)
    def __print_to_trace(self,value):
        if self.__enable_print_to_trace:
            print(value)
