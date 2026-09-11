from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'BlackOut': {'Status': {}},
            'EditScene': {'Status': {}},
            'DMXChannelFade': {'Parameters': ['Channel'], 'Status': {}},
            'LiveMode': {'Status': {}},
            'PlayShow': {'Status': {}},
            'Record': {'Status': {}},
            'Show': {'Status': {}},
        }


        self.FaderValues = {
            0: b'\x00\x00',
            1: b'\x3F\x80',
            2: b'\x40\x00',
            3: b'\x40\x40',
            4: b'\x40\x80',
            5: b'\x40\xA0',
            6: b'\x40\xC0',
            7: b'\x40\xE0',
            8: b'\x41\x00',
            9: b'\x41\x10',
            10: b'\x41\x20',
            11: b'\x41\x30',
            12: b'\x41\x40',
            13: b'\x41\x50',
            14: b'\x41\x60',
            15: b'\x41\x70',
            16: b'\x41\x80',
            17: b'\x41\x88',
            18: b'\x41\x90',
            19: b'\x41\x98',
            20: b'\x41\xA0',
            21: b'\x41\xA8',
            22: b'\x41\xB0',
            23: b'\x41\xB8',
            24: b'\x41\xC0',
            25: b'\x41\xC8',
            26: b'\x41\xD0',
            27: b'\x41\xD8',
            28: b'\x41\xE0',
            29: b'\x41\xE8',
            30: b'\x41\xF0',
            31: b'\x41\xF8',
            32: b'\x42\x00',
            33: b'\x42\x04',
            34: b'\x42\x08',
            35: b'\x42\x0C',
            36: b'\x42\x10',
            37: b'\x42\x14',
            38: b'\x42\x18',
            39: b'\x42\x1C',
            40: b'\x42\x20',
            41: b'\x42\x24',
            42: b'\x42\x28',
            43: b'\x42\x2C',
            44: b'\x42\x30',
            45: b'\x42\x34',
            46: b'\x42\x38',
            47: b'\x42\x3C',
            48: b'\x42\x40',
            49: b'\x42\x44',
            50: b'\x42\x48',
            51: b'\x42\x4C',
            52: b'\x42\x50',
            53: b'\x42\x54',
            54: b'\x42\x58',
            55: b'\x42\x5C',
            56: b'\x42\x50',
            57: b'\x42\x64',
            58: b'\x42\x68',
            59: b'\x42\x6C',
            60: b'\x42\x60',
            61: b'\x42\x74',
            62: b'\x42\x78',
            63: b'\x42\x7C',
            64: b'\x42\x80',
            65: b'\x42\x82',
            66: b'\x42\x84',
            67: b'\x42\x86',
            68: b'\x42\x88',
            69: b'\x42\x8A',
            70: b'\x42\x8C',
            71: b'\x42\x8E',
            72: b'\x42\x90',
            73: b'\x42\x92',
            74: b'\x42\x94',
            75: b'\x42\x96',
            76: b'\x42\x98',
            77: b'\x42\x9A',
            78: b'\x42\x9C',
            79: b'\x42\x9E',
            80: b'\x42\xA0',
            81: b'\x42\xA2',
            82: b'\x42\xA4',
            83: b'\x42\xA6',
            84: b'\x42\xA8',
            85: b'\x42\xAA',
            86: b'\x42\xAC',
            87: b'\x42\xAE',
            88: b'\x42\xB0',
            89: b'\x42\xB2',
            90: b'\x42\xB4',
            91: b'\x42\xB6',
            92: b'\x42\xB8',
            93: b'\x42\xBA',
            94: b'\x42\xBC',
            95: b'\x42\xBE',
            96: b'\x42\xC0',
            97: b'\x42\xC2',
            98: b'\x42\xC4',
            99: b'\x42\xC6',
            100: b'\x42\xC8',
            101: b'\x42\xCA',
            102: b'\x42\xCC',
            103: b'\x42\xCE',
            104: b'\x42\xD0',
            105: b'\x42\xD2',
            106: b'\x42\xD4',
            107: b'\x42\xD6',
            108: b'\x42\xD8',
            109: b'\x42\xDA',
            110: b'\x42\xDC',
            111: b'\x42\xDE',
            112: b'\x42\xE0',
            113: b'\x42\xE2',
            114: b'\x42\xE4',
            115: b'\x42\xE6',
            116: b'\x42\xE8',
            117: b'\x42\xEA',
            118: b'\x42\xEC',
            119: b'\x42\xEE',
            120: b'\x42\xF0',
            121: b'\x42\xF2',
            122: b'\x42\xF4',
            123: b'\x42\xF6',
            124: b'\x42\xF8',
            125: b'\x42\xFA',
            126: b'\x42\xFC',
            127: b'\x42\xFE',
            128: b'\x43\x00',
            129: b'\x43\x01',
            130: b'\x43\x02',
            131: b'\x43\x03',
            132: b'\x43\x04',
            133: b'\x43\x05',
            134: b'\x43\x06',
            135: b'\x43\x07',
            136: b'\x43\x08',
            137: b'\x43\x09',
            138: b'\x43\x0A',
            139: b'\x43\x0B',
            140: b'\x43\x0C',
            141: b'\x43\x0D',
            142: b'\x43\x0E',
            143: b'\x43\x0F',
            144: b'\x43\x10',
            145: b'\x43\x11',
            146: b'\x43\x12',
            147: b'\x43\x13',
            148: b'\x43\x14',
            149: b'\x43\x15',
            150: b'\x43\x16',
            151: b'\x43\x17',
            152: b'\x43\x18',
            153: b'\x43\x19',
            154: b'\x43\x1A',
            155: b'\x43\x1B',
            156: b'\x43\x1C',
            157: b'\x43\x1D',
            158: b'\x43\x1E',
            159: b'\x43\x1F',
            160: b'\x43\x20',
            161: b'\x43\x21',
            162: b'\x43\x22',
            163: b'\x43\x23',
            164: b'\x43\x24',
            165: b'\x43\x25',
            166: b'\x43\x26',
            167: b'\x43\x27',
            168: b'\x43\x28',
            169: b'\x43\x29',
            170: b'\x43\x2A',
            171: b'\x43\x2B',
            172: b'\x43\x2C',
            173: b'\x43\x2D',
            174: b'\x43\x2E',
            175: b'\x43\x2F',
            176: b'\x43\x30',
            177: b'\x43\x31',
            178: b'\x43\x32',
            179: b'\x43\x33',
            180: b'\x43\x34',
            181: b'\x43\x35',
            182: b'\x43\x36',
            183: b'\x43\x37',
            184: b'\x43\x38',
            185: b'\x43\x39',
            186: b'\x43\x3A',
            187: b'\x43\x3B',
            188: b'\x43\x3C',
            189: b'\x43\x3D',
            190: b'\x43\x3E',
            191: b'\x43\x3F',
            192: b'\x43\x40',
            193: b'\x43\x41',
            194: b'\x43\x42',
            195: b'\x43\x43',
            196: b'\x43\x44',
            197: b'\x43\x45',
            198: b'\x43\x46',
            199: b'\x43\x47',
            200: b'\x43\x48',
            201: b'\x43\x49',
            202: b'\x43\x4A',
            203: b'\x43\x4B',
            204: b'\x43\x4C',
            205: b'\x43\x4D',
            206: b'\x43\x4E',
            207: b'\x43\x4F',
            208: b'\x43\x50',
            209: b'\x43\x51',
            210: b'\x43\x52',
            211: b'\x43\x53',
            212: b'\x43\x54',
            213: b'\x43\x55',
            214: b'\x43\x56',
            215: b'\x43\x57',
            216: b'\x43\x58',
            217: b'\x43\x59',
            218: b'\x43\x5A',
            219: b'\x43\x5B',
            220: b'\x43\x5C',
            221: b'\x43\x5D',
            222: b'\x43\x5E',
            223: b'\x43\x5F',
            224: b'\x43\x60',
            225: b'\x43\x61',
            226: b'\x43\x62',
            227: b'\x43\x63',
            228: b'\x43\x64',
            229: b'\x43\x65',
            230: b'\x43\x66',
            231: b'\x43\x67',
            232: b'\x43\x68',
            233: b'\x43\x69',
            234: b'\x43\x6A',
            235: b'\x43\x6B',
            236: b'\x43\x6C',
            237: b'\x43\x6D',
            238: b'\x43\x6E',
            239: b'\x43\x6F',
            240: b'\x43\x70',
            241: b'\x43\x71',
            242: b'\x43\x72',
            243: b'\x43\x73',
            244: b'\x43\x74',
            245: b'\x43\x75',
            246: b'\x43\x76',
            247: b'\x43\x77',
            248: b'\x43\x78',
            249: b'\x43\x79',
            250: b'\x43\x7A',
            251: b'\x43\x7B',
            252: b'\x43\x7C',
            253: b'\x43\x7D',
            254: b'\x43\x7E',
            255: b'\x43\x7F'
        }

    def __ConstraintChecker(self, *args):

        try:
            for x in args:
                if not(x['Min'] <= int(x['Value']) <= x['Max']):
                    return False
            return True
        except:
            return False
    def SetBlackOut(self, value, qualifier):

        ValueStateValues = {
            'On': b'/dmx/set/black_out\x00\x00,f\x00\x00\x3F\x80\x00\x00',
            'Off': b'/dmx/set/black_out\x00\x00,f\x00\x00\x00\x00\x00\x00'
        }
        BlackOutCmdString = ValueStateValues[value]
        self.__SetHelper('BlackOut', BlackOutCmdString, value, qualifier)
    def SetDMXChannelFade(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 24,
            'Value': qualifier['Channel']
        }
        DMXChannelFadeCmdString = ''
        if self.__ConstraintChecker(ChannelConstraints) and value in self.FaderValues:
            if 1 <= int(ChannelConstraints['Value']) <= 9:
                DMXChannelFadeCmdString = b''.join([b'/dmx/set/ch/', ChannelConstraints['Value'].encode(), b'\x00\x00\x00,f\x00\x00', self.FaderValues[value], b'\x00\x00'])
            elif 10 <= int(ChannelConstraints['Value']) <= 24:
                DMXChannelFadeCmdString = b''.join([b'/dmx/set/ch/', ChannelConstraints['Value'].encode(), b'\x00\x00,f\x00\x00', self.FaderValues[value], b'\x00\x00'])
            if DMXChannelFadeCmdString:
                self.__SetHelper('DMXChannelFade', DMXChannelFadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDMXChannelFade')

    def SetEditScene(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100,
            'Value': int(value)
        }

        if self.__ConstraintChecker(ValueConstraints):
            EditSceneCmdString = b''.join([b'/dmx/edit/scene\x00\x00,i\x00\x00\x00\x00\x00', ValueConstraints['Value'].to_bytes(1, 'big')])
            self.__SetHelper('EditScene', EditSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEditScene')
    def SetLiveMode(self, value, qualifier):

        LiveModeCmdString = b'/dmx/edit/goLive\x00\x00\x00\x00,f\x00\x00\x3F\x80\x00\x00'
        self.__SetHelper('LiveMode', LiveModeCmdString, value, qualifier)
    def SetPlayShow(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 255,
            'Value': int(value)
        }
        if self.__ConstraintChecker(ValueConstraints):
            PlayShowCmdString = b''.join([b'/dmx/play/show\x00\x00,i\x00\x00\x00\x00\x00', ValueConstraints['Value'].to_bytes(1, 'big')])
            self.__SetHelper('PlayShow', PlayShowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayShow')
    def SetRecord(self, value, qualifier):

        RecordCmdString = b'/dmx/edit/rec\x00\x00\x00\x00,f\x00\x00\x3F\x80\x00\x00'
        self.__SetHelper('Record', RecordCmdString, value, qualifier)
    def SetShow(self, value, qualifier):

        ValueStateValues = {
            'Stop': b'/dmx/play/show/stop\x00,f\x00\x00\x3F\x80\x00\x00',
            'Next': b'/dmx/play/show/next\x00,f\x00\x00\x3F\x80\x00\x00',
            'Previous': b'/dmx/play/show/prev\x00,f\x00\x00\x3F\x80\x00\x00'
        }
        ShowCmdString = ValueStateValues[value]
        self.__SetHelper('Show', ShowCmdString, value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        self.Send(commandstring)

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
