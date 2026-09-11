from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
from math import floor


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Level': {'Parameters': ['MIDI Channel', 'Source', 'Destination'], 'Status': {}},
            'Mute': {'Parameters': ['MIDI Channel', 'Source'], 'Status': {}},
            'SceneRecall': {'Parameters': ['MIDI Channel'], 'Status': {}},
        }

        self.MIDIChannelStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            '11': 'A',
            '12': 'B',
            '13': 'C',
            '14': 'D',
            '15': 'E',
            '16': 'F'
        }
        self.LevelData = {
            'Input 1, LR': [64, 0], 'Input 1, AUX 1': [64, 68], 'Input 1, AUX 2': [64, 69], 'Input 1, AUX 3': [64, 70], 'Input 1, AUX 4': [64, 71], 'Input 1, AUX 5': [64, 72],
            'Input 1, AUX 6': [64, 73], 'Input 1, AUX 7': [64, 74], 'Input 1, AUX 8': [64, 75], 'Input 1, AUX 9': [64, 76], 'Input 1, AUX 10': [64, 77], 'Input 1, AUX 11': [64, 78],
            'Input 1, AUX 12': [64, 79], 'Input 2, LR': [64, 1], 'Input 2, AUX 1': [64, 80], 'Input 2, AUX 2': [64, 81], 'Input 2, AUX 3': [64, 82], 'Input 2, AUX 4': [64, 83],
            'Input 2, AUX 5': [64, 84], 'Input 2, AUX 6': [64, 85], 'Input 2, AUX 7': [64, 86], 'Input 2, AUX 8': [64, 87], 'Input 2, AUX 9': [64, 88], 'Input 2, AUX 10': [64, 89],
            'Input 2, AUX 11': [64, 90], 'Input 2, AUX 12': [64, 91], 'Input 3, LR': [64, 2], 'Input 3, AUX 1': [64, 92], 'Input 3, AUX 2': [64, 93], 'Input 3, AUX 3': [64, 94],
            'Input 3, AUX 4': [64, 95], 'Input 3, AUX 5': [64, 96], 'Input 3, AUX 6': [64, 97], 'Input 3, AUX 7': [64, 98], 'Input 3, AUX 8': [64, 99], 'Input 3, AUX 9': [64, 100],
            'Input 3, AUX 10': [64, 101], 'Input 3, AUX 11': [64, 102], 'Input 3, AUX 12': [64, 103], 'Input 4, LR': [64, 3], 'Input 4, AUX 1': [64, 104], 'Input 4, AUX 2': [64, 105],
            'Input 4, AUX 3': [64, 106], 'Input 4, AUX 4': [64, 107], 'Input 4, AUX 5': [64, 108], 'Input 4, AUX 6': [64, 109], 'Input 4, AUX 7': [64, 110], 'Input 4, AUX 8': [64, 111],
            'Input 4, AUX 9': [64, 112], 'Input 4, AUX 10': [64, 113], 'Input 4, AUX 11': [64, 114], 'Input 4, AUX 12': [64, 115], 'Input 5, LR': [64, 4], 'Input 5, AUX 1': [64, 116],
            'Input 5, AUX 2': [64, 117], 'Input 5, AUX 3': [64, 118], 'Input 5, AUX 4': [64, 119], 'Input 5, AUX 5': [64, 120], 'Input 5, AUX 6': [64, 121], 'Input 5, AUX 7': [64, 122],
            'Input 5, AUX 8': [64, 123], 'Input 5, AUX 9': [64, 124], 'Input 5, AUX 10': [64, 125], 'Input 5, AUX 11': [64, 126], 'Input 5, AUX 12': [64, 127], 'Input 6, LR': [64, 5],
            'Input 6, AUX 1': [65, 0], 'Input 6, AUX 2': [65, 1], 'Input 6, AUX 3': [65, 2], 'Input 6, AUX 4': [65, 3], 'Input 6, AUX 5': [65, 4], 'Input 6, AUX 6': [65, 5],
            'Input 6, AUX 7': [65, 6], 'Input 6, AUX 8': [65, 7], 'Input 6, AUX 9': [65, 8], 'Input 6, AUX 10': [65, 9], 'Input 6, AUX 11': [65, 10], 'Input 6, AUX 12': [65, 11],
            'Input 7, LR': [64, 6], 'Input 7, AUX 1': [65, 12], 'Input 7, AUX 2': [65, 13], 'Input 7, AUX 3': [65, 14], 'Input 7, AUX 4': [65, 15], 'Input 7, AUX 5': [65, 16],
            'Input 7, AUX 6': [65, 17], 'Input 7, AUX 7': [65, 18], 'Input 7, AUX 8': [65, 19], 'Input 7, AUX 9': [65, 20], 'Input 7, AUX 10': [65, 21], 'Input 7, AUX 11': [65, 22],
            'Input 7, AUX 12': [65, 23], 'Input 8, LR': [64, 7], 'Input 8, AUX 1': [65, 24], 'Input 8, AUX 2': [65, 25], 'Input 8, AUX 3': [65, 26], 'Input 8, AUX 4': [65, 27],
            'Input 8, AUX 5': [65, 28], 'Input 8, AUX 6': [65, 29], 'Input 8, AUX 7': [65, 30], 'Input 8, AUX 8': [65, 31], 'Input 8, AUX 9': [65, 32], 'Input 8, AUX 10': [65, 33],
            'Input 8, AUX 11': [65, 34], 'Input 8, AUX 12': [65, 35], 'Input 9, LR': [64, 8], 'Input 9, AUX 1': [65, 36], 'Input 9, AUX 2': [65, 37], 'Input 9, AUX 3': [65, 38],
            'Input 9, AUX 4': [65, 39], 'Input 9, AUX 5': [65, 40], 'Input 9, AUX 6': [65, 41], 'Input 9, AUX 7': [65, 42], 'Input 9, AUX 8': [65, 43], 'Input 9, AUX 9': [65, 44],
            'Input 9, AUX 10': [65, 45], 'Input 9, AUX 11': [65, 46], 'Input 9, AUX 12': [65, 47], 'Input 10, LR': [64, 9], 'Input 10, AUX 1': [65, 48], 'Input 10, AUX 2': [65, 49],
            'Input 10, AUX 3': [65, 50], 'Input 10, AUX 4': [65, 51], 'Input 10, AUX 5': [65, 52], 'Input 10, AUX 6': [65, 53], 'Input 10, AUX 7': [65, 54], 'Input 10, AUX 8': [65, 55],
            'Input 10, AUX 9': [65, 56], 'Input 10, AUX 10': [65, 57], 'Input 10, AUX 11': [65, 58], 'Input 10, AUX 12': [65, 59], 'Input 11, LR': [64, 10], 'Input 11, AUX 1': [65, 60],
            'Input 11, AUX 2': [65, 61], 'Input 11, AUX 3': [65, 62], 'Input 11, AUX 4': [65, 63], 'Input 11, AUX 5': [65, 64], 'Input 11, AUX 6': [65, 65], 'Input 11, AUX 7': [65, 66],
            'Input 11, AUX 8': [65, 67], 'Input 11, AUX 9': [65, 68], 'Input 11, AUX 10': [65, 69], 'Input 11, AUX 11': [65, 70], 'Input 11, AUX 12': [65, 71], 'Input 12, LR': [64, 11],
            'Input 12, AUX 1': [65, 72], 'Input 12, AUX 2': [65, 73], 'Input 12, AUX 3': [65, 74], 'Input 12, AUX 4': [65, 75], 'Input 12, AUX 5': [65, 76], 'Input 12, AUX 6': [65, 77],
            'Input 12, AUX 7': [65, 78], 'Input 12, AUX 8': [65, 79], 'Input 12, AUX 9': [65, 80], 'Input 12, AUX 10': [65, 81], 'Input 12, AUX 11': [65, 82], 'Input 12, AUX 12': [65, 83],
            'Input 13, LR': [64, 12], 'Input 13, AUX 1': [65, 84], 'Input 13, AUX 2': [65, 85], 'Input 13, AUX 3': [65, 86], 'Input 13, AUX 4': [65, 87], 'Input 13, AUX 5': [65, 88],
            'Input 13, AUX 6': [65, 89], 'Input 13, AUX 7': [65, 90], 'Input 13, AUX 8': [65, 91], 'Input 13, AUX 9': [65, 92], 'Input 13, AUX 10': [65, 93], 'Input 13, AUX 11': [65, 94],
            'Input 13, AUX 12': [65, 95], 'Input 14, LR': [64, 13], 'Input 14, AUX 1': [65, 96], 'Input 14, AUX 2': [65, 97], 'Input 14, AUX 3': [65, 98], 'Input 14, AUX 4': [65, 99],
            'Input 14, AUX 5': [65, 100], 'Input 14, AUX 6': [65, 101], 'Input 14, AUX 7': [65, 102], 'Input 14, AUX 8': [65, 103], 'Input 14, AUX 9': [65, 104], 'Input 14, AUX 10': [65, 105],
            'Input 14, AUX 11': [65, 106], 'Input 14, AUX 12': [65, 107], 'Input 15, LR': [64, 14], 'Input 15, AUX 1': [65, 108], 'Input 15, AUX 2': [65, 109], 'Input 15, AUX 3': [65, 110],
            'Input 15, AUX 4': [65, 111], 'Input 15, AUX 5': [65, 112], 'Input 15, AUX 6': [65, 113], 'Input 15, AUX 7': [65, 114], 'Input 15, AUX 8': [65, 115], 'Input 15, AUX 9': [65, 116],
            'Input 15, AUX 10': [65, 117], 'Input 15, AUX 11': [65, 118], 'Input 15, AUX 12': [65, 119], 'Input 16, LR': [64, 15], 'Input 16, AUX 1': [65, 120], 'Input 16, AUX 2': [65, 121],
            'Input 16, AUX 3': [65, 122], 'Input 16, AUX 4': [65, 123], 'Input 16, AUX 5': [65, 124], 'Input 16, AUX 6': [65, 125], 'Input 16, AUX 7': [65, 126], 'Input 16, AUX 8': [65, 127],
            'Input 16, AUX 9': [66, 0], 'Input 16, AUX 10': [66, 1], 'Input 16, AUX 11': [66, 2], 'Input 16, AUX 12': [66, 3], 'Input 17, LR': [64, 16], 'Input 17, AUX 1': [66, 4],
            'Input 17, AUX 2': [66, 5], 'Input 17, AUX 3': [66, 6], 'Input 17, AUX 4': [66, 7], 'Input 17, AUX 5': [66, 8], 'Input 17, AUX 6': [66, 9], 'Input 17, AUX 7': [66, 10],
            'Input 17, AUX 8': [66, 11], 'Input 17, AUX 9': [66, 12], 'Input 17, AUX 10': [66, 13], 'Input 17, AUX 11': [66, 14], 'Input 17, AUX 12': [66, 15], 'Input 18, LR': [64, 17],
            'Input 18, AUX 1': [66, 16], 'Input 18, AUX 2': [66, 17], 'Input 18, AUX 3': [66, 18], 'Input 18, AUX 4': [66, 19], 'Input 18, AUX 5': [66, 20], 'Input 18, AUX 6': [66, 21],
            'Input 18, AUX 7': [66, 22], 'Input 18, AUX 8': [66, 23], 'Input 18, AUX 9': [66, 24], 'Input 18, AUX 10': [66, 25], 'Input 18, AUX 11': [66, 26], 'Input 18, AUX 12': [66, 27],
            'Input 19, LR': [64, 18], 'Input 19, AUX 1': [66, 28], 'Input 19, AUX 2': [66, 29], 'Input 19, AUX 3': [66, 30], 'Input 19, AUX 4': [66, 31], 'Input 19, AUX 5': [66, 32],
            'Input 19, AUX 6': [66, 33], 'Input 19, AUX 7': [66, 34], 'Input 19, AUX 8': [66, 35], 'Input 19, AUX 9': [66, 36], 'Input 19, AUX 10': [66, 37], 'Input 19, AUX 11': [66, 38],
            'Input 19, AUX 12': [66, 39], 'Input 20, LR': [64, 19], 'Input 20, AUX 1': [66, 40], 'Input 20, AUX 2': [66, 41], 'Input 20, AUX 3': [66, 42], 'Input 20, AUX 4': [66, 43],
            'Input 20, AUX 5': [66, 44], 'Input 20, AUX 6': [66, 45], 'Input 20, AUX 7': [66, 46], 'Input 20, AUX 8': [66, 47], 'Input 20, AUX 9': [66, 48], 'Input 20, AUX 10': [66, 49],
            'Input 20, AUX 11': [66, 50], 'Input 20, AUX 12': [66, 51], 'Input 21, LR': [64, 20], 'Input 21, AUX 1': [66, 52], 'Input 21, AUX 2': [66, 53], 'Input 21, AUX 3': [66, 54],
            'Input 21, AUX 4': [66, 55], 'Input 21, AUX 5': [66, 56], 'Input 21, AUX 6': [66, 57], 'Input 21, AUX 7': [66, 58], 'Input 21, AUX 8': [66, 59], 'Input 21, AUX 9': [66, 60],
            'Input 21, AUX 10': [66, 61], 'Input 21, AUX 11': [66, 62], 'Input 21, AUX 12': [66, 63], 'Input 22, LR': [64, 21], 'Input 22, AUX 1': [66, 64], 'Input 22, AUX 2': [66, 65],
            'Input 22, AUX 3': [66, 66], 'Input 22, AUX 4': [66, 67], 'Input 22, AUX 5': [66, 68], 'Input 22, AUX 6': [66, 69], 'Input 22, AUX 7': [66, 70], 'Input 22, AUX 8': [66, 71],
            'Input 22, AUX 9': [66, 72], 'Input 22, AUX 10': [66, 73], 'Input 22, AUX 11': [66, 74], 'Input 22, AUX 12': [66, 75], 'Input 23, LR': [64, 22], 'Input 23, AUX 1': [66, 76],
            'Input 23, AUX 2': [66, 77], 'Input 23, AUX 3': [66, 78], 'Input 23, AUX 4': [66, 79], 'Input 23, AUX 5': [66, 80], 'Input 23, AUX 6': [66, 81], 'Input 23, AUX 7': [66, 82],
            'Input 23, AUX 8': [66, 83], 'Input 23, AUX 9': [66, 84], 'Input 23, AUX 10': [66, 85], 'Input 23, AUX 11': [66, 86], 'Input 23, AUX 12': [66, 87], 'Input 24, LR': [64, 23],
            'Input 24, AUX 1': [66, 88], 'Input 24, AUX 2': [66, 89], 'Input 24, AUX 3': [66, 90], 'Input 24, AUX 4': [66, 91], 'Input 24, AUX 5': [66, 92], 'Input 24, AUX 6': [66, 93],
            'Input 24, AUX 7': [66, 94], 'Input 24, AUX 8': [66, 95], 'Input 24, AUX 9': [66, 96], 'Input 24, AUX 10': [66, 97], 'Input 24, AUX 11': [66, 98], 'Input 24, AUX 12': [66, 99],
            'Input 25, LR': [64, 24], 'Input 25, AUX 1': [66, 100], 'Input 25, AUX 2': [66, 101], 'Input 25, AUX 3': [66, 102], 'Input 25, AUX 4': [66, 103], 'Input 25, AUX 5': [66, 104],
            'Input 25, AUX 6': [66, 105], 'Input 25, AUX 7': [66, 106], 'Input 25, AUX 8': [66, 107], 'Input 25, AUX 9': [66, 108], 'Input 25, AUX 10': [66, 109], 'Input 25, AUX 11': [66, 110],
            'Input 25, AUX 12': [66, 111], 'Input 26, LR': [64, 25], 'Input 26, AUX 1': [66, 112], 'Input 26, AUX 2': [66, 113], 'Input 26, AUX 3': [66, 114], 'Input 26, AUX 4': [66, 115],
            'Input 26, AUX 5': [66, 116], 'Input 26, AUX 6': [66, 117], 'Input 26, AUX 7': [66, 118], 'Input 26, AUX 8': [66, 119], 'Input 26, AUX 9': [66, 120], 'Input 26, AUX 10': [66, 121],
            'Input 26, AUX 11': [66, 122], 'Input 26, AUX 12': [66, 123], 'Input 27, LR': [64, 26], 'Input 27, AUX 1': [66, 124], 'Input 27, AUX 2': [66, 125], 'Input 27, AUX 3': [66, 126],
            'Input 27, AUX 4': [66, 127], 'Input 27, AUX 5': [67, 0], 'Input 27, AUX 6': [67, 1], 'Input 27, AUX 7': [67, 2], 'Input 27, AUX 8': [67, 3], 'Input 27, AUX 9': [67, 4],
            'Input 27, AUX 10': [67, 5], 'Input 27, AUX 11': [67, 6], 'Input 27, AUX 12': [67, 7], 'Input 28, LR': [64, 27], 'Input 28, AUX 1': [67, 8], 'Input 28, AUX 2': [67, 9],
            'Input 28, AUX 3': [67, 10], 'Input 28, AUX 4': [67, 11], 'Input 28, AUX 5': [67, 12], 'Input 28, AUX 6': [67, 13], 'Input 28, AUX 7': [67, 14], 'Input 28, AUX 8': [67, 15],
            'Input 28, AUX 9': [67, 16], 'Input 28, AUX 10': [67, 17], 'Input 28, AUX 11': [67, 18], 'Input 28, AUX 12': [67, 19], 'Input 29, LR': [64, 28], 'Input 29, AUX 1': [67, 20],
            'Input 29, AUX 2': [67, 21], 'Input 29, AUX 3': [67, 22], 'Input 29, AUX 4': [67, 23], 'Input 29, AUX 5': [67, 24], 'Input 29, AUX 6': [67, 25], 'Input 29, AUX 7': [67, 26],
            'Input 29, AUX 8': [67, 27], 'Input 29, AUX 9': [67, 28], 'Input 29, AUX 10': [67, 29], 'Input 29, AUX 11': [67, 30], 'Input 29, AUX 12': [67, 31], 'Input 30, LR': [64, 29],
            'Input 30, AUX 1': [67, 32], 'Input 30, AUX 2': [67, 33], 'Input 30, AUX 3': [67, 34], 'Input 30, AUX 4': [67, 35], 'Input 30, AUX 5': [67, 36], 'Input 30, AUX 6': [67, 37],
            'Input 30, AUX 7': [67, 38], 'Input 30, AUX 8': [67, 39], 'Input 30, AUX 9': [67, 40], 'Input 30, AUX 10': [67, 41], 'Input 30, AUX 11': [67, 42], 'Input 30, AUX 12': [67, 43],
            'Input 31, LR': [64, 30], 'Input 31, AUX 1': [67, 44], 'Input 31, AUX 2': [67, 45], 'Input 31, AUX 3': [67, 46], 'Input 31, AUX 4': [67, 47], 'Input 31, AUX 5': [67, 48],
            'Input 31, AUX 6': [67, 49], 'Input 31, AUX 7': [67, 50], 'Input 31, AUX 8': [67, 51], 'Input 31, AUX 9': [67, 52], 'Input 31, AUX 10': [67, 53], 'Input 31, AUX 11': [67, 54],
            'Input 31, AUX 12': [67, 55], 'Input 32, LR': [64, 31], 'Input 32, AUX 1': [67, 56], 'Input 32, AUX 2': [67, 57], 'Input 32, AUX 3': [67, 58], 'Input 32, AUX 4': [67, 59],
            'Input 32, AUX 5': [67, 60], 'Input 32, AUX 6': [67, 61], 'Input 32, AUX 7': [67, 62], 'Input 32, AUX 8': [67, 63], 'Input 32, AUX 9': [67, 64], 'Input 32, AUX 10': [67, 65],
            'Input 32, AUX 11': [67, 66], 'Input 32, AUX 12': [67, 67], 'Input 33, LR': [64, 32], 'Input 33, AUX 1': [67, 68], 'Input 33, AUX 2': [67, 69], 'Input 33, AUX 3': [67, 70],
            'Input 33, AUX 4': [67, 71], 'Input 33, AUX 5': [67, 72], 'Input 33, AUX 6': [67, 73], 'Input 33, AUX 7': [67, 74], 'Input 33, AUX 8': [67, 75], 'Input 33, AUX 9': [67, 76],
            'Input 33, AUX 10': [67, 77], 'Input 33, AUX 11': [67, 78], 'Input 33, AUX 12': [67, 79], 'Input 34, LR': [64, 33], 'Input 34, AUX 1': [67, 80], 'Input 34, AUX 2': [67, 81],
            'Input 34, AUX 3': [67, 82], 'Input 34, AUX 4': [67, 83], 'Input 34, AUX 5': [67, 84], 'Input 34, AUX 6': [67, 85], 'Input 34, AUX 7': [67, 86], 'Input 34, AUX 8': [67, 87],
            'Input 34, AUX 9': [67, 88], 'Input 34, AUX 10': [67, 89], 'Input 34, AUX 11': [67, 90], 'Input 34, AUX 12': [67, 91], 'Input 35, LR': [64, 34], 'Input 35, AUX 1': [67, 92],
            'Input 35, AUX 2': [67, 93], 'Input 35, AUX 3': [67, 94], 'Input 35, AUX 4': [67, 95], 'Input 35, AUX 5': [67, 96], 'Input 35, AUX 6': [67, 97], 'Input 35, AUX 7': [67, 98],
            'Input 35, AUX 8': [67, 99], 'Input 35, AUX 9': [67, 100], 'Input 35, AUX 10': [67, 101], 'Input 35, AUX 11': [67, 102], 'Input 35, AUX 12': [67, 103], 'Input 36, LR': [64, 35],
            'Input 36, AUX 1': [67, 104], 'Input 36, AUX 2': [67, 105], 'Input 36, AUX 3': [67, 106], 'Input 36, AUX 4': [67, 107], 'Input 36, AUX 5': [67, 108], 'Input 36, AUX 6': [67, 109],
            'Input 36, AUX 7': [67, 110], 'Input 36, AUX 8': [67, 111], 'Input 36, AUX 9': [67, 112], 'Input 36, AUX 10': [67, 113], 'Input 36, AUX 11': [67, 114], 'Input 36, AUX 12': [67, 115],
            'Input 37, LR': [64, 36], 'Input 37, AUX 1': [67, 116], 'Input 37, AUX 2': [67, 117], 'Input 37, AUX 3': [67, 118], 'Input 37, AUX 4': [67, 119], 'Input 37, AUX 5': [67, 120],
            'Input 37, AUX 6': [67, 121], 'Input 37, AUX 7': [67, 122], 'Input 37, AUX 8': [67, 123], 'Input 37, AUX 9': [67, 124], 'Input 37, AUX 10': [67, 125], 'Input 37, AUX 11': [67, 126],
            'Input 37, AUX 12': [67, 127], 'Input 38, LR': [64, 37], 'Input 38, AUX 1': [68, 0], 'Input 38, AUX 2': [68, 1], 'Input 38, AUX 3': [68, 2], 'Input 38, AUX 4': [68, 3],
            'Input 38, AUX 5': [68, 4], 'Input 38, AUX 6': [68, 5], 'Input 38, AUX 7': [68, 6], 'Input 38, AUX 8': [68, 7], 'Input 38, AUX 9': [68, 8], 'Input 38, AUX 10': [68, 9],
            'Input 38, AUX 11': [68, 10], 'Input 38, AUX 12': [68, 11], 'Input 39, LR': [64, 38], 'Input 39, AUX 1': [68, 12], 'Input 39, AUX 2': [68, 13], 'Input 39, AUX 3': [68, 14],
            'Input 39, AUX 4': [68, 15], 'Input 39, AUX 5': [68, 16], 'Input 39, AUX 6': [68, 17], 'Input 39, AUX 7': [68, 18], 'Input 39, AUX 8': [68, 19], 'Input 39, AUX 9': [68, 20],
            'Input 39, AUX 10': [68, 21], 'Input 39, AUX 11': [68, 22], 'Input 39, AUX 12': [68, 23], 'Input 40, LR': [64, 39], 'Input 40, AUX 1': [68, 24], 'Input 40, AUX 2': [68, 25],
            'Input 40, AUX 3': [68, 26], 'Input 40, AUX 4': [68, 27], 'Input 40, AUX 5': [68, 28], 'Input 40, AUX 6': [68, 29], 'Input 40, AUX 7': [68, 30], 'Input 40, AUX 8': [68, 31],
            'Input 40, AUX 9': [68, 32], 'Input 40, AUX 10': [68, 33], 'Input 40, AUX 11': [68, 34], 'Input 40, AUX 12': [68, 35], 'Input 41, LR': [64, 40], 'Input 41, AUX 1': [68, 36],
            'Input 41, AUX 2': [68, 37], 'Input 41, AUX 3': [68, 38], 'Input 41, AUX 4': [68, 39], 'Input 41, AUX 5': [68, 40], 'Input 41, AUX 6': [68, 41], 'Input 41, AUX 7': [68, 42],
            'Input 41, AUX 8': [68, 43], 'Input 41, AUX 9': [68, 44], 'Input 41, AUX 10': [68, 45], 'Input 41, AUX 11': [68, 46], 'Input 41, AUX 12': [68, 47], 'Input 42, LR': [64, 41],
            'Input 42, AUX 1': [68, 48], 'Input 42, AUX 2': [68, 49], 'Input 42, AUX 3': [68, 50], 'Input 42, AUX 4': [68, 51], 'Input 42, AUX 5': [68, 52], 'Input 42, AUX 6': [68, 53],
            'Input 42, AUX 7': [68, 54], 'Input 42, AUX 8': [68, 55], 'Input 42, AUX 9': [68, 56], 'Input 42, AUX 10': [68, 57], 'Input 42, AUX 11': [68, 58], 'Input 42, AUX 12': [68, 59],
            'Input 43, LR': [64, 42], 'Input 43, AUX 1': [68, 60], 'Input 43, AUX 2': [68, 61], 'Input 43, AUX 3': [68, 62], 'Input 43, AUX 4': [68, 63], 'Input 43, AUX 5': [68, 64],
            'Input 43, AUX 6': [68, 65], 'Input 43, AUX 7': [68, 66], 'Input 43, AUX 8': [68, 67], 'Input 43, AUX 9': [68, 68], 'Input 43, AUX 10': [68, 69], 'Input 43, AUX 11': [68, 70],
            'Input 43, AUX 12': [68, 71], 'Input 44, LR': [64, 43], 'Input 44, AUX 1': [68, 72], 'Input 44, AUX 2': [68, 73], 'Input 44, AUX 3': [68, 74], 'Input 44, AUX 4': [68, 75],
            'Input 44, AUX 5': [68, 76], 'Input 44, AUX 6': [68, 77], 'Input 44, AUX 7': [68, 78], 'Input 44, AUX 8': [68, 79], 'Input 44, AUX 9': [68, 80], 'Input 44, AUX 10': [68, 81],
            'Input 44, AUX 11': [68, 82], 'Input 44, AUX 12': [68, 83], 'Input 45, LR': [64, 44], 'Input 45, AUX 1': [68, 84], 'Input 45, AUX 2': [68, 85], 'Input 45, AUX 3': [68, 86],
            'Input 45, AUX 4': [68, 87], 'Input 45, AUX 5': [68, 88], 'Input 45, AUX 6': [68, 89], 'Input 45, AUX 7': [68, 90], 'Input 45, AUX 8': [68, 91], 'Input 45, AUX 9': [68, 92],
            'Input 45, AUX 10': [68, 93], 'Input 45, AUX 11': [68, 94], 'Input 45, AUX 12': [68, 95], 'Input 46, LR': [64, 45], 'Input 46, AUX 1': [68, 96], 'Input 46, AUX 2': [68, 97],
            'Input 46, AUX 3': [68, 98], 'Input 46, AUX 4': [68, 99], 'Input 46, AUX 5': [68, 100], 'Input 46, AUX 6': [68, 101], 'Input 46, AUX 7': [68, 102], 'Input 46, AUX 8': [68, 103],
            'Input 46, AUX 9': [68, 104], 'Input 46, AUX 10': [68, 105], 'Input 46, AUX 11': [68, 106], 'Input 46, AUX 12': [68, 107], 'Input 47, LR': [64, 46], 'Input 47, AUX 1': [68, 108],
            'Input 47, AUX 2': [68, 109], 'Input 47, AUX 3': [68, 110], 'Input 47, AUX 4': [68, 111], 'Input 47, AUX 5': [68, 112], 'Input 47, AUX 6': [68, 113], 'Input 47, AUX 7': [68, 114],
            'Input 47, AUX 8': [68, 115], 'Input 47, AUX 9': [68, 116], 'Input 47, AUX 10': [68, 117], 'Input 47, AUX 11': [68, 118], 'Input 47, AUX 12': [68, 119], 'Input 48, LR': [64, 47],
            'Input 48, AUX 1': [68, 120], 'Input 48, AUX 2': [68, 121], 'Input 48, AUX 3': [68, 122], 'Input 48, AUX 4': [68, 123], 'Input 48, AUX 5': [68, 124], 'Input 48, AUX 6': [68, 125],
            'Input 48, AUX 7': [68, 126], 'Input 48, AUX 8': [68, 127], 'Input 48, AUX 9': [69, 0], 'Input 48, AUX 10': [69, 1], 'Input 48, AUX 11': [69, 2], 'Input 48, AUX 12': [69, 3],
            'Group 1, LR': [64, 48], 'Group 1, AUX 1': [69, 4], 'Group 1, AUX 2': [69, 5], 'Group 1, AUX 3': [69, 6], 'Group 1, AUX 4': [69, 7], 'Group 1, AUX 5': [69, 8], 'Group 1, AUX 6': [69, 9],
            'Group 1, AUX 7': [69, 10], 'Group 1, AUX 8': [69, 11], 'Group 1, AUX 9': [69, 12], 'Group 1, AUX 10': [69, 13], 'Group 1, AUX 11': [69, 14], 'Group 2, LR': [64, 49],
            'Group 2, AUX 1': [69, 16], 'Group 2, AUX 2': [69, 17], 'Group 2, AUX 3': [69, 18], 'Group 2, AUX 4': [69, 19], 'Group 2, AUX 5': [69, 20], 'Group 2, AUX 6': [69, 21],
            'Group 2, AUX 7': [69, 22], 'Group 2, AUX 8': [69, 23], 'Group 2, AUX 9': [69, 24], 'Group 2, AUX 10': [69, 25], 'Group 3, LR': [64, 50], 'Group 3, AUX 1': [69, 28],
            'Group 3, AUX 2': [69, 29], 'Group 3, AUX 3': [69, 30], 'Group 3, AUX 4': [69, 31], 'Group 3, AUX 5': [69, 32], 'Group 3, AUX 6': [69, 33], 'Group 3, AUX 7': [69, 34],
            'Group 3, AUX 8': [69, 35], 'Group 3, AUX 9': [69, 36], 'Group 4, LR': [64, 51], 'Group 4, AUX 1': [69, 40], 'Group 4, AUX 2': [69, 41], 'Group 4, AUX 3': [69, 42],
            'Group 4, AUX 4': [69, 43], 'Group 4, AUX 5': [69, 44], 'Group 4, AUX 6': [69, 45], 'Group 4, AUX 7': [69, 46], 'Group 4, AUX 8': [69, 47], 'Group 5, LR': [64, 52],
            'Group 5, AUX 1': [69, 52], 'Group 5, AUX 2': [69, 53], 'Group 5, AUX 3': [69, 54], 'Group 5, AUX 4': [69, 55], 'Group 5, AUX 5': [69, 56], 'Group 5, AUX 6': [69, 57],
            'Group 5, AUX 7': [69, 58], 'Group 6, LR': [64, 53], 'Group 6, AUX 1': [69, 64], 'Group 6, AUX 2': [69, 65], 'Group 6, AUX 3': [69, 66], 'Group 6, AUX 4': [69, 67],
            'Group 6, AUX 5': [69, 68], 'Group 6, AUX 6': [69, 69], 'Group 7, LR': [64, 54], 'Group 7, AUX 1': [69, 76], 'Group 7, AUX 2': [69, 77], 'Group 7, AUX 3': [69, 78],
            'Group 7, AUX 4': [69, 79], 'Group 7, AUX 5': [69, 80], 'Group 8, LR': [64, 55], 'Group 8, AUX 1': [69, 88], 'Group 8, AUX 2': [69, 89], 'Group 8, AUX 3': [69, 90],
            'Group 8, AUX 4': [69, 91], 'Group 9, LR': [64, 56], 'Group 9, AUX 1': [69, 100], 'Group 9, AUX 2': [69, 101], 'Group 9, AUX 3': [69, 102], 'Group 10, LR': [64, 57],
            'Group 10, AUX 1': [69, 112], 'Group 10, AUX 2': [69, 113], 'Group 11, LR': [64, 58], 'Group 11, AUX 1': [69, 124], 'Group 12, LR': [64, 59], 'FX 1 Return, LR': [64, 60],
            'FX 1 Return, AUX 1': [70, 20], 'FX 1 Return, AUX 2': [70, 21], 'FX 1 Return, AUX 3': [70, 22], 'FX 1 Return, AUX 4': [70, 23], 'FX 1 Return, AUX 5': [70, 24],
            'FX 1 Return, AUX 6': [70, 25], 'FX 1 Return, AUX 7': [70, 26], 'FX 1 Return, AUX 8': [70, 27], 'FX 1 Return, AUX 9': [70, 28], 'FX 1 Return, AUX 10': [70, 29],
            'FX 1 Return, AUX 11': [70, 30], 'FX 1 Return, AUX 12': [70, 31], 'FX 2 Return, LR': [64, 61], 'FX 2 Return, AUX 1': [70, 32], 'FX 2 Return, AUX 2': [70, 33],
            'FX 2 Return, AUX 3': [70, 34], 'FX 2 Return, AUX 4': [70, 35], 'FX 2 Return, AUX 5': [70, 36], 'FX 2 Return, AUX 6': [70, 37], 'FX 2 Return, AUX 7': [70, 38],
            'FX 2 Return, AUX 8': [70, 39], 'FX 2 Return, AUX 9': [70, 40], 'FX 2 Return, AUX 10': [70, 41], 'FX 2 Return, AUX 11': [70, 42], 'FX 2 Return, AUX 12': [70, 43],
            'FX 3 Return, LR': [64, 62], 'FX 3 Return, AUX 1': [70, 44], 'FX 3 Return, AUX 2': [70, 45], 'FX 3 Return, AUX 3': [70, 46], 'FX 3 Return, AUX 4': [70, 47],
            'FX 3 Return, AUX 5': [70, 48], 'FX 3 Return, AUX 6': [70, 49], 'FX 3 Return, AUX 7': [70, 50], 'FX 3 Return, AUX 8': [70, 51], 'FX 3 Return, AUX 9': [70, 52],
            'FX 3 Return, AUX 10': [70, 53], 'FX 3 Return, AUX 11': [70, 54], 'FX 3 Return, AUX 12': [70, 55], 'FX 4 Return, LR': [64, 63], 'FX 4 Return, AUX 1': [70, 56],
            'FX 4 Return, AUX 2': [70, 57], 'FX 4 Return, AUX 3': [70, 58], 'FX 4 Return, AUX 4': [70, 59], 'FX 4 Return, AUX 5': [70, 60], 'FX 4 Return, AUX 6': [70, 61],
            'FX 4 Return, AUX 7': [70, 62], 'FX 4 Return, AUX 8': [70, 63], 'FX 4 Return, AUX 9': [70, 64], 'FX 4 Return, AUX 10': [70, 65], 'FX 4 Return, AUX 11': [70, 66],
            'FX 4 Return, AUX 12': [70, 67], 'FX 5 Return, LR': [64, 64], 'FX 5 Return, AUX 1': [70, 68], 'FX 5 Return, AUX 2': [70, 69], 'FX 5 Return, AUX 3': [70, 70],
            'FX 5 Return, AUX 4': [70, 71], 'FX 5 Return, AUX 5': [70, 72], 'FX 5 Return, AUX 6': [70, 73], 'FX 5 Return, AUX 7': [70, 74], 'FX 5 Return, AUX 8': [70, 75],
            'FX 5 Return, AUX 9': [70, 76], 'FX 5 Return, AUX 10': [70, 77], 'FX 5 Return, AUX 11': [70, 78], 'FX 5 Return, AUX 12': [70, 79], 'FX 6 Return, LR': [64, 65],
            'FX 6 Return, AUX 1': [70, 80], 'FX 6 Return, AUX 2': [70, 81], 'FX 6 Return, AUX 3': [70, 82], 'FX 6 Return, AUX 4': [70, 83], 'FX 6 Return, AUX 5': [70, 84],
            'FX 6 Return, AUX 6': [70, 85], 'FX 6 Return, AUX 7': [70, 86], 'FX 6 Return, AUX 8': [70, 87], 'FX 6 Return, AUX 9': [70, 88], 'FX 6 Return, AUX 10': [70, 89],
            'FX 6 Return, AUX 11': [70, 90], 'FX 6 Return, AUX 12': [70, 91], 'FX 7 Return, LR': [64, 66], 'FX 7 Return, AUX 1': [70, 92], 'FX 7 Return, AUX 2': [70, 93],
            'FX 7 Return, AUX 3': [70, 94], 'FX 7 Return, AUX 4': [70, 95], 'FX 7 Return, AUX 5': [70, 96], 'FX 7 Return, AUX 6': [70, 97], 'FX 7 Return, AUX 7': [70, 98],
            'FX 7 Return, AUX 8': [70, 99], 'FX 7 Return, AUX 9': [70, 100], 'FX 7 Return, AUX 10': [70, 101], 'FX 7 Return, AUX 11': [70, 102], 'FX 7 Return, AUX 12': [70, 103],
            'FX 8 Return, LR': [64, 67], 'FX 8 Return, AUX 1': [70, 104], 'FX 8 Return, AUX 2': [70, 105], 'FX 8 Return, AUX 3': [70, 106], 'FX 8 Return, AUX 4': [70, 107],
            'FX 8 Return, AUX 5': [70, 108], 'FX 8 Return, AUX 6': [70, 109], 'FX 8 Return, AUX 7': [70, 110], 'FX 8 Return, AUX 8': [70, 111], 'FX 8 Return, AUX 9': [70, 112],
            'FX 8 Return, AUX 10': [70, 113], 'FX 8 Return, AUX 11': [70, 114], 'FX 8 Return, AUX 12': [70, 115], 'FX 1 Return, Group 1': [75, 52], 'FX 1 Return, Group 2': [75, 53],
            'FX 1 Return, Group 3': [75, 54], 'FX 1 Return, Group 4': [75, 55], 'FX 1 Return, Group 5': [75, 56], 'FX 1 Return, Group 6': [75, 57], 'FX 1 Return, Group 7': [75, 58],
            'FX 1 Return, Group 8': [75, 59], 'FX 1 Return, Group 9': [75, 60], 'FX 1 Return, Group 10': [75, 61], 'FX 1 Return, Group 11': [75, 62], 'FX 1 Return, Group 12': [75, 63],
            'FX 2 Return, Group 1': [75, 64], 'FX 2 Return, Group 2': [75, 65], 'FX 2 Return, Group 3': [75, 66], 'FX 2 Return, Group 4': [75, 67], 'FX 2 Return, Group 5': [75, 68],
            'FX 2 Return, Group 6': [75, 69], 'FX 2 Return, Group 7': [75, 70], 'FX 2 Return, Group 8': [75, 71], 'FX 2 Return, Group 9': [75, 72], 'FX 2 Return, Group 10': [75, 73],
            'FX 2 Return, Group 11': [75, 74], 'FX 2 Return, Group 12': [75, 75], 'FX 3 Return, Group 1': [75, 76], 'FX 3 Return, Group 2': [75, 77], 'FX 3 Return, Group 3': [75, 78],
            'FX 3 Return, Group 4': [75, 79], 'FX 3 Return, Group 5': [75, 80], 'FX 3 Return, Group 6': [75, 81], 'FX 3 Return, Group 7': [75, 82], 'FX 3 Return, Group 8': [75, 83],
            'FX 3 Return, Group 9': [75, 84], 'FX 3 Return, Group 10': [75, 85], 'FX 3 Return, Group 11': [75, 86], 'FX 3 Return, Group 12': [75, 87], 'FX 4 Return, Group 1': [75, 88],
            'FX 4 Return, Group 2': [75, 89], 'FX 4 Return, Group 3': [75, 90], 'FX 4 Return, Group 4': [75, 91], 'FX 4 Return, Group 5': [75, 92], 'FX 4 Return, Group 6': [75, 93],
            'FX 4 Return, Group 7': [75, 94], 'FX 4 Return, Group 8': [75, 95], 'FX 4 Return, Group 9': [75, 96], 'FX 4 Return, Group 10': [75, 97], 'FX 4 Return, Group 11': [75, 98],
            'FX 4 Return, Group 12': [75, 99], 'FX 5 Return, Group 1': [75, 100], 'FX 5 Return, Group 2': [75, 101], 'FX 5 Return, Group 3': [75, 102], 'FX 5 Return, Group 4': [75, 103],
            'FX 5 Return, Group 5': [75, 104], 'FX 5 Return, Group 6': [75, 105], 'FX 5 Return, Group 7': [75, 106], 'FX 5 Return, Group 8': [75, 107], 'FX 5 Return, Group 9': [75, 108],
            'FX 5 Return, Group 10': [75, 109], 'FX 5 Return, Group 11': [75, 110], 'FX 5 Return, Group 12': [75, 111], 'FX 6 Return, Group 1': [75, 112], 'FX 6 Return, Group 2': [75, 113],
            'FX 6 Return, Group 3': [75, 114], 'FX 6 Return, Group 4': [75, 115], 'FX 6 Return, Group 5': [75, 116], 'FX 6 Return, Group 6': [75, 117], 'FX 6 Return, Group 7': [75, 118],
            'FX 6 Return, Group 8': [75, 119], 'FX 6 Return, Group 9': [75, 120], 'FX 6 Return, Group 10': [75, 121], 'FX 6 Return, Group 11': [75, 122], 'FX 6 Return, Group 12': [75, 123],
            'FX 7 Return, Group 1': [75, 124], 'FX 7 Return, Group 2': [75, 125], 'FX 7 Return, Group 3': [75, 126], 'FX 7 Return, Group 4': [75, 127], 'FX 7 Return, Group 5': [76, 0],
            'FX 7 Return, Group 6': [76, 1], 'FX 7 Return, Group 7': [76, 2], 'FX 7 Return, Group 8': [76, 3], 'FX 7 Return, Group 9': [76, 4], 'FX 7 Return, Group 10': [76, 5],
            'FX 7 Return, Group 11': [76, 6], 'FX 7 Return, Group 12': [76, 7], 'FX 8 Return, Group 1': [76, 8], 'FX 8 Return, Group 2': [76, 9], 'FX 8 Return, Group 3': [76, 10],
            'FX 8 Return, Group 4': [76, 11], 'FX 8 Return, Group 5': [76, 12], 'FX 8 Return, Group 6': [76, 13], 'FX 8 Return, Group 7': [76, 14], 'FX 8 Return, Group 8': [76, 15],
            'FX 8 Return, Group 9': [76, 16], 'FX 8 Return, Group 10': [76, 17], 'FX 8 Return, Group 11': [76, 18], 'FX 8 Return, Group 12': [76, 19], 'Input 1, FX 1 Send': [76, 20],
            'Input 1, FX 2 Send': [76, 21], 'Input 1, FX 3 Send': [76, 22], 'Input 1, FX 4 Send': [76, 23], 'Input 2, FX 1 Send': [76, 24], 'Input 2, FX 2 Send': [76, 25],
            'Input 2, FX 3 Send': [76, 26], 'Input 2, FX 4 Send': [76, 27], 'Input 3, FX 1 Send': [76, 28], 'Input 3, FX 2 Send': [76, 29], 'Input 3, FX 3 Send': [76, 30],
            'Input 3, FX 4 Send': [76, 31], 'Input 4, FX 1 Send': [76, 32], 'Input 4, FX 2 Send': [76, 33], 'Input 4, FX 3 Send': [76, 34], 'Input 4, FX 4 Send': [76, 35],
            'Input 5, FX 1 Send': [76, 36], 'Input 5, FX 2 Send': [76, 37], 'Input 5, FX 3 Send': [76, 38], 'Input 5, FX 4 Send': [76, 39], 'Input 6, FX 1 Send': [76, 40],
            'Input 6, FX 2 Send': [76, 41], 'Input 6, FX 3 Send': [76, 42], 'Input 6, FX 4 Send': [76, 43], 'Input 7, FX 1 Send': [76, 44], 'Input 7, FX 2 Send': [76, 45],
            'Input 7, FX 3 Send': [76, 46], 'Input 7, FX 4 Send': [76, 47], 'Input 8, FX 1 Send': [76, 48], 'Input 8, FX 2 Send': [76, 49], 'Input 8, FX 3 Send': [76, 50],
            'Input 8, FX 4 Send': [76, 51], 'Input 9, FX 1 Send': [76, 52], 'Input 9, FX 2 Send': [76, 53], 'Input 9, FX 3 Send': [76, 54], 'Input 9, FX 4 Send': [76, 55],
            'Input 10, FX 1 Send': [76, 56], 'Input 10, FX 2 Send': [76, 57], 'Input 10, FX 3 Send': [76, 58], 'Input 10, FX 4 Send': [76, 59], 'Input 11, FX 1 Send': [76, 60],
            'Input 11, FX 2 Send': [76, 61], 'Input 11, FX 3 Send': [76, 62], 'Input 11, FX 4 Send': [76, 63], 'Input 12, FX 1 Send': [76, 64], 'Input 12, FX 2 Send': [76, 65],
            'Input 12, FX 3 Send': [76, 66], 'Input 12, FX 4 Send': [76, 67], 'Input 13, FX 1 Send': [76, 68], 'Input 13, FX 2 Send': [76, 69], 'Input 13, FX 3 Send': [76, 70],
            'Input 13, FX 4 Send': [76, 71], 'Input 14, FX 1 Send': [76, 72], 'Input 14, FX 2 Send': [76, 73], 'Input 14, FX 3 Send': [76, 74], 'Input 14, FX 4 Send': [76, 75],
            'Input 15, FX 1 Send': [76, 76], 'Input 15, FX 2 Send': [76, 77], 'Input 15, FX 3 Send': [76, 78], 'Input 15, FX 4 Send': [76, 79], 'Input 16, FX 1 Send': [76, 80],
            'Input 16, FX 2 Send': [76, 81], 'Input 16, FX 3 Send': [76, 82], 'Input 16, FX 4 Send': [76, 83], 'Input 17, FX 1 Send': [76, 84], 'Input 17, FX 2 Send': [76, 85],
            'Input 17, FX 3 Send': [76, 86], 'Input 17, FX 4 Send': [76, 87], 'Input 18, FX 1 Send': [76, 88], 'Input 18, FX 2 Send': [76, 89], 'Input 18, FX 3 Send': [76, 90],
            'Input 18, FX 4 Send': [76, 91], 'Input 19, FX 1 Send': [76, 92], 'Input 19, FX 2 Send': [76, 93], 'Input 19, FX 3 Send': [76, 94], 'Input 19, FX 4 Send': [76, 95],
            'Input 20, FX 1 Send': [76, 96], 'Input 20, FX 2 Send': [76, 97], 'Input 20, FX 3 Send': [76, 98], 'Input 20, FX 4 Send': [76, 99], 'Input 21, FX 1 Send': [76, 100],
            'Input 21, FX 2 Send': [76, 101], 'Input 21, FX 3 Send': [76, 102], 'Input 21, FX 4 Send': [76, 103], 'Input 22, FX 1 Send': [76, 104], 'Input 22, FX 2 Send': [76, 105],
            'Input 22, FX 3 Send': [76, 106], 'Input 22, FX 4 Send': [76, 107], 'Input 23, FX 1 Send': [76, 108], 'Input 23, FX 2 Send': [76, 109], 'Input 23, FX 3 Send': [76, 110],
            'Input 23, FX 4 Send': [76, 111], 'Input 24, FX 1 Send': [76, 112], 'Input 24, FX 2 Send': [76, 113], 'Input 24, FX 3 Send': [76, 114], 'Input 24, FX 4 Send': [76, 115],
            'Input 25, FX 1 Send': [76, 116], 'Input 25, FX 2 Send': [76, 117], 'Input 25, FX 3 Send': [76, 118], 'Input 25, FX 4 Send': [76, 119], 'Input 26, FX 1 Send': [76, 120],
            'Input 26, FX 2 Send': [76, 121], 'Input 26, FX 3 Send': [76, 122], 'Input 26, FX 4 Send': [76, 123], 'Input 27, FX 1 Send': [76, 124], 'Input 27, FX 2 Send': [76, 125],
            'Input 27, FX 3 Send': [76, 126], 'Input 27, FX 4 Send': [76, 127], 'Input 28, FX 1 Send': [77, 0], 'Input 28, FX 2 Send': [77, 1], 'Input 28, FX 3 Send': [77, 2],
            'Input 28, FX 4 Send': [77, 3], 'Input 29, FX 1 Send': [77, 4], 'Input 29, FX 2 Send': [77, 5], 'Input 29, FX 3 Send': [77, 6], 'Input 29, FX 4 Send': [77, 7],
            'Input 30, FX 1 Send': [77, 8], 'Input 30, FX 2 Send': [77, 9], 'Input 30, FX 3 Send': [77, 10], 'Input 30, FX 4 Send': [77, 11], 'Input 31, FX 1 Send': [77, 12],
            'Input 31, FX 2 Send': [77, 13], 'Input 31, FX 3 Send': [77, 14], 'Input 31, FX 4 Send': [77, 15], 'Input 32, FX 1 Send': [77, 16], 'Input 32, FX 2 Send': [77, 17],
            'Input 32, FX 3 Send': [77, 18], 'Input 32, FX 4 Send': [77, 19], 'Input 33, FX 1 Send': [77, 20], 'Input 33, FX 2 Send': [77, 21], 'Input 33, FX 3 Send': [77, 22],
            'Input 33, FX 4 Send': [77, 23], 'Input 34, FX 1 Send': [77, 24], 'Input 34, FX 2 Send': [77, 25], 'Input 34, FX 3 Send': [77, 26], 'Input 34, FX 4 Send': [77, 27],
            'Input 35, FX 1 Send': [77, 28], 'Input 35, FX 2 Send': [77, 29], 'Input 35, FX 3 Send': [77, 30], 'Input 35, FX 4 Send': [77, 31], 'Input 36, FX 1 Send': [77, 32],
            'Input 36, FX 2 Send': [77, 33], 'Input 36, FX 3 Send': [77, 34], 'Input 36, FX 4 Send': [77, 35], 'Input 37, FX 1 Send': [77, 36], 'Input 37, FX 2 Send': [77, 37],
            'Input 37, FX 3 Send': [77, 38], 'Input 37, FX 4 Send': [77, 39], 'Input 38, FX 1 Send': [77, 40], 'Input 38, FX 2 Send': [77, 41], 'Input 38, FX 3 Send': [77, 42],
            'Input 38, FX 4 Send': [77, 43], 'Input 39, FX 1 Send': [77, 44], 'Input 39, FX 2 Send': [77, 45], 'Input 39, FX 3 Send': [77, 46], 'Input 39, FX 4 Send': [77, 47],
            'Input 40, FX 1 Send': [77, 48], 'Input 40, FX 2 Send': [77, 49], 'Input 40, FX 3 Send': [77, 50], 'Input 40, FX 4 Send': [77, 51], 'Input 41, FX 1 Send': [77, 52],
            'Input 41, FX 2 Send': [77, 53], 'Input 41, FX 3 Send': [77, 54], 'Input 41, FX 4 Send': [77, 55], 'Input 42, FX 1 Send': [77, 56], 'Input 42, FX 2 Send': [77, 57],
            'Input 42, FX 3 Send': [77, 58], 'Input 42, FX 4 Send': [77, 59], 'Input 43, FX 1 Send': [77, 60], 'Input 43, FX 2 Send': [77, 61], 'Input 43, FX 3 Send': [77, 62],
            'Input 43, FX 4 Send': [77, 63], 'Input 44, FX 1 Send': [77, 64], 'Input 44, FX 2 Send': [77, 65], 'Input 44, FX 3 Send': [77, 66], 'Input 44, FX 4 Send': [77, 67],
            'Input 45, FX 1 Send': [77, 68], 'Input 45, FX 2 Send': [77, 69], 'Input 45, FX 3 Send': [77, 70], 'Input 45, FX 4 Send': [77, 71], 'Input 46, FX 1 Send': [77, 72],
            'Input 46, FX 2 Send': [77, 73], 'Input 46, FX 3 Send': [77, 74], 'Input 46, FX 4 Send': [77, 75], 'Input 47, FX 1 Send': [77, 76], 'Input 47, FX 2 Send': [77, 77],
            'Input 47, FX 3 Send': [77, 78], 'Input 47, FX 4 Send': [77, 79], 'Input 48, FX 1 Send': [77, 80], 'Input 48, FX 2 Send': [77, 81], 'Input 48, FX 3 Send': [77, 82],
            'Input 48, FX 4 Send': [77, 83], 'Group 1, FX 1 Send': [77, 84], 'Group 1, FX 2 Send': [77, 85], 'Group 1, FX 3 Send': [77, 86], 'Group 1, FX 4 Send': [77, 87],
            'Group 2, FX 1 Send': [77, 88], 'Group 2, FX 2 Send': [77, 89], 'Group 2, FX 3 Send': [77, 90], 'Group 2, FX 4 Send': [77, 91], 'Group 3, FX 1 Send': [77, 92],
            'Group 3, FX 2 Send': [77, 93], 'Group 3, FX 3 Send': [77, 94], 'Group 3, FX 4 Send': [77, 95], 'Group 4, FX 1 Send': [77, 96], 'Group 4, FX 2 Send': [77, 97],
            'Group 4, FX 3 Send': [77, 98], 'Group 4, FX 4 Send': [77, 99], 'Group 5, FX 1 Send': [77, 100], 'Group 5, FX 2 Send': [77, 101], 'Group 5, FX 3 Send': [77, 102],
            'Group 5, FX 4 Send': [77, 103], 'Group 6, FX 1 Send': [77, 104], 'Group 6, FX 2 Send': [77, 105], 'Group 6, FX 3 Send': [77, 106], 'Group 6, FX 4 Send': [77, 107],
            'Group 7, FX 1 Send': [77, 108], 'Group 7, FX 2 Send': [77, 109], 'Group 7, FX 3 Send': [77, 110], 'Group 7, FX 4 Send': [77, 111], 'Group 8, FX 1 Send': [77, 112],
            'Group 8, FX 2 Send': [77, 113], 'Group 8, FX 3 Send': [77, 114], 'Group 8, FX 4 Send': [77, 115], 'Group 9, FX 1 Send': [77, 116], 'Group 9, FX 2 Send': [77, 117],
            'Group 9, FX 3 Send': [77, 118], 'Group 9, FX 4 Send': [77, 119], 'Group 10, FX 1 Send': [77, 120], 'Group 10, FX 2 Send': [77, 121], 'Group 10, FX 3 Send': [77, 122],
            'Group 10, FX 4 Send': [77, 123], 'Group 11, FX 1 Send': [77, 124], 'Group 11, FX 2 Send': [77, 125], 'Group 11, FX 3 Send': [77, 126], 'Group 11, FX 4 Send': [77, 127],
            'Group 12, FX 1 Send': [78, 0], 'Group 12, FX 2 Send': [78, 1], 'Group 12, FX 3 Send': [78, 2], 'Group 12, FX 4 Send': [78, 3], 'FX 1 Return, FX 1 Send': [78, 4],
            'FX 1 Return, FX 2 Send': [78, 5], 'FX 1 Return, FX 3 Send': [78, 6], 'FX 1 Return, FX 4 Send': [78, 7], 'FX 2 Return, FX 1 Send': [78, 8], 'FX 2 Return, FX 2 Send': [78, 9],
            'FX 2 Return, FX 3 Send': [78, 10], 'FX 2 Return, FX 4 Send': [78, 11], 'FX 3 Return, FX 1 Send': [78, 12], 'FX 3 Return, FX 2 Send': [78, 13], 'FX 3 Return, FX 3 Send': [78, 14],
            'FX 3 Return, FX 4 Send': [78, 15], 'FX 4 Return, FX 1 Send': [78, 16], 'FX 4 Return, FX 2 Send': [78, 17], 'FX 4 Return, FX 3 Send': [78, 18], 'FX 4 Return, FX 4 Send': [78, 19],
            'FX 5 Return, FX 1 Send': [78, 20], 'FX 5 Return, FX 2 Send': [78, 21], 'FX 5 Return, FX 3 Send': [78, 22], 'FX 5 Return, FX 4 Send': [78, 23], 'FX 6 Return, FX 1 Send': [78, 24],
            'FX 6 Return, FX 2 Send': [78, 25], 'FX 6 Return, FX 3 Send': [78, 26], 'FX 6 Return, FX 4 Send': [78, 27], 'FX 7 Return, FX 1 Send': [78, 28], 'FX 7 Return, FX 2 Send': [78, 29],
            'FX 7 Return, FX 3 Send': [78, 30], 'FX 7 Return, FX 4 Send': [78, 31], 'FX 8 Return, FX 1 Send': [78, 32], 'FX 8 Return, FX 2 Send': [78, 33], 'FX 8 Return, FX 3 Send': [78, 34],
            'FX 8 Return, FX 4 Send': [78, 35], 'LR, Matrix 1': [78, 36], 'LR, Matrix 2': [78, 37], 'LR, Matrix 3': [78, 38], 'AUX 1, Matrix 1': [78, 39], 'AUX 1, Matrix 2': [78, 40],
            'AUX 1, Matrix 3': [78, 41], 'AUX 2, Matrix 1': [78, 42], 'AUX 2, Matrix 2': [78, 43], 'AUX 2, Matrix 3': [78, 44], 'AUX 3, Matrix 1': [78, 45], 'AUX 3, Matrix 2': [78, 46],
            'AUX 3, Matrix 3': [78, 47], 'AUX 4, Matrix 1': [78, 48], 'AUX 4, Matrix 2': [78, 49], 'AUX 4, Matrix 3': [78, 50], 'AUX 5, Matrix 1': [78, 51], 'AUX 5, Matrix 2': [78, 52],
            'AUX 5, Matrix 3': [78, 53], 'AUX 6, Matrix 1': [78, 54], 'AUX 6, Matrix 2': [78, 55], 'AUX 6, Matrix 3': [78, 56], 'AUX 7, Matrix 1': [78, 57], 'AUX 7, Matrix 2': [78, 58],
            'AUX 7, Matrix 3': [78, 59], 'AUX 8, Matrix 1': [78, 60], 'AUX 8, Matrix 2': [78, 61], 'AUX 8, Matrix 3': [78, 62], 'AUX 9, Matrix 1': [78, 63], 'AUX 9, Matrix 2': [78, 64],
            'AUX 9, Matrix 3': [78, 65], 'AUX 10, Matrix 1': [78, 66], 'AUX 10, Matrix 2': [78, 67], 'AUX 10, Matrix 3': [78, 68], 'AUX 11, Matrix 1': [78, 69], 'AUX 11, Matrix 2': [78, 70],
            'AUX 11, Matrix 3': [78, 71], 'AUX 12, Matrix 1': [78, 72], 'AUX 12, Matrix 2': [78, 73], 'AUX 12, Matrix 3': [78, 74], 'Group 1, Matrix 1': [78, 75], 'Group 1, Matrix 2': [78, 76],
            'Group 1, Matrix 3': [78, 77], 'Group 2, Matrix 1': [78, 78], 'Group 2, Matrix 2': [78, 79], 'Group 2, Matrix 3': [78, 80], 'Group 3, Matrix 1': [78, 81], 'Group 3, Matrix 2': [78, 82],
            'Group 3, Matrix 3': [78, 83], 'Group 4, Matrix 1': [78, 84], 'Group 4, Matrix 2': [78, 85], 'Group 4, Matrix 3': [78, 86], 'Group 5, Matrix 1': [78, 87], 'Group 5, Matrix 2': [78, 88],
            'Group 5, Matrix 3': [78, 89], 'Group 6, Matrix 1': [78, 90], 'Group 6, Matrix 2': [78, 91], 'Group 6, Matrix 3': [78, 92], 'Group 7, Matrix 1': [78, 93], 'Group 7, Matrix 2': [78, 94],
            'Group 7, Matrix 3': [78, 95], 'Group 8, Matrix 1': [78, 96], 'Group 8, Matrix 2': [78, 97], 'Group 8, Matrix 3': [78, 98], 'Group 9, Matrix 1': [78, 99], 'Group 9, Matrix 2': [78, 100],
            'Group 9, Matrix 3': [78, 101], 'Group 10, Matrix 1': [78, 102], 'Group 10, Matrix 2': [78, 103], 'Group 10, Matrix 3': [78, 104], 'Group 11, Matrix 1': [78, 105],
            'Group 11, Matrix 2': [78, 106], 'Group 11, Matrix 3': [78, 107], 'Group 12, Matrix 1': [78, 108], 'Group 12, Matrix 2': [78, 109], 'Group 12, Matrix 3': [78, 110],
            'LR, Output': [79, 0], 'AUX 1, Output': [79, 1], 'AUX 2, Output': [79, 2], 'AUX 3, Output': [79, 3], 'AUX 4, Output': [79, 4], 'AUX 5, Output': [79, 5], 'AUX 6, Output': [79, 6],
            'AUX 7, Output': [79, 7], 'AUX 8, Output': [79, 8], 'AUX 9, Output': [79, 9], 'AUX 10, Output': [79, 10], 'AUX 11, Output': [79, 11], 'AUX 12, Output': [79, 12],
            'FX 1 Send, Output': [79, 13], 'FX 2 Send, Output': [79, 14], 'FX 3 Send, Output': [79, 15], 'FX 4 Send, Output': [79, 16], 'Matrix 1, Output': [79, 17], 'Matrix 2, Output': [79, 18],
            'Matrix 3, Output': [79, 19], 'DCA 1, Control': [79, 32], 'DCA 2, Control': [79, 33], 'DCA 3, Control': [79, 34], 'DCA 4, Control': [79, 35], 'DCA 5, Control': [79, 36],
            'DCA 6, Control': [79, 37], 'DCA 7, Control': [79, 38], 'DCA 8, Control': [79, 39]
        }
        self.MuteData = {
            'Input 1': 0x00, 'Input 2': 0x01, 'Input 3': 0x02, 'Input 4': 0x03, 'Input 5': 0x04, 'Input 6': 0x05, 'Input 7': 0x06, 'Input 8': 0x07, 'Input 9': 0x08, 'Input 10': 0x09,
            'Input 11': 0x0A, 'Input 12': 0x0B, 'Input 13': 0x0C, 'Input 14': 0x0D, 'Input 15': 0x0E, 'Input 16': 0x0F, 'Input 17': 0x10, 'Input 18': 0x11, 'Input 19': 0x12,
            'Input 20': 0x13, 'Input 21': 0x14, 'Input 22': 0x15, 'Input 23': 0x16, 'Input 24': 0x17, 'Input 25': 0x18, 'Input 26': 0x19, 'Input 27': 0x1A, 'Input 28': 0x1B,
            'Input 29': 0x1C, 'Input 30': 0x1D, 'Input 31': 0x1E, 'Input 32': 0x1F, 'Input 33': 0x20, 'Input 34': 0x21, 'Input 35': 0x22, 'Input 36': 0x23, 'Input 37': 0x24,
            'Input 38': 0x25, 'Input 39': 0x26, 'Input 40': 0x27, 'Input 41': 0x28, 'Input 42': 0x29, 'Input 43': 0x2A, 'Input 44': 0x2B, 'Input 45': 0x2C, 'Input 46': 0x2D,
            'Input 47': 0x2E, 'Input 48': 0x2F, 'Group 1': 0x30, 'Group 2': 0x31, 'Group 3': 0x32, 'Group 4': 0x33, 'Group 5': 0x34, 'Group 6': 0x35, 'Group 7': 0x36, 'Group 8': 0x37,
            'Group 9': 0x38, 'Group 10': 0x39, 'Group 11': 0x3A, 'Group 12': 0x3B, 'FX 1 Return': 0x3C, 'FX 2 Return': 0x3D, 'FX 3 Return': 0x3E, 'FX 4 Return': 0x3F, 'FX 5 Return': 0x40,
            'FX 6 Return': 0x41, 'FX 7 Return': 0x42, 'FX 8 Return': 0x43, 'LR': 0x44, 'AUX 1': 0x45, 'AUX 2': 0x46, 'AUX 3': 0x47, 'AUX 4': 0x48, 'AUX 5': 0x49, 'AUX 6': 0x4A,
            'AUX 7': 0x4B, 'AUX 8': 0x4C, 'AUX 9': 0x4D, 'AUX 10': 0x4E, 'AUX 11': 0x4F, 'AUX 12': 0x50, 'FX 1 Send': 0x51, 'FX 2 Send': 0x52, 'FX 3 Send': 0x53, 'FX 4 Send': 0x54,
            'Matrix 1': 0x55, 'Matrix 2': 0x56, 'Matrix 3': 0x57, 'DCA 1': 0x00, 'DCA 2': 0x01, 'DCA 3': 0x02, 'DCA 4': 0x03, 'DCA 5': 0x04, 'DCA 6': 0x05, 'DCA 7': 0x06, 'DCA 8': 0x07,
            'Master Group 1': 0x00, 'Master Group 2': 0x01, 'Master Group 3': 0x02, 'Master Group 4': 0x03, 'Master Group 5': 0x04, 'Master Group 6': 0x05, 'Master Group 7': 0x06, 'Master Group 8': 0x07
        }

    def SetLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -90,  # represents negative infinity
            'Max': 10
        }

        key = '{0}, {1}'.format(qualifier['Source'], qualifier['Destination'])
        try:
            MSB = self.LevelData[key][0]
            LSB = self.LevelData[key][1]
        except KeyError:
            return self.Discard('Invalid Command for SetLevel')
        if 1 <= int(qualifier['MIDI Channel']) <= 16 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            midiConversion = int('B' + self.MIDIChannelStates[qualifier['MIDI Channel']], 16)
            if value == -90:
                VC = 0  # value coarse
                VF = 0  # value fine
            else:
                LEVEL_MAX = 35328  # (10 * 256) + 0x8000
                LEVEL_MIN = 0
                GainOffB = (value * 256) + 0x8000
                ScaledGain = (GainOffB / (LEVEL_MAX - LEVEL_MIN)) * 0xFFFF
                Gain14Bit = floor(floor(ScaledGain) / 4)
                Gain14BitLSB = Gain14Bit & 0x7F
                Gain14BitMSB = Gain14Bit >> 7
                Gain14BitWord = Gain14BitLSB | (Gain14BitMSB << 8)
                values = divmod(Gain14BitWord, 256)  # splits high byte and low byte into tuple
                VC = values[0]
                VF = values[1]  # confirmed w/ manufacturer the example table in protocol has some incorrect values shown (see 'Calculating VC and VF values.docx')
            LevelCmdString = pack('>12B', midiConversion, 0x63, MSB, midiConversion, 0x62, LSB, midiConversion, 0x06, VC, midiConversion, 0x26, VF)
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')

    def UpdateLevel(self, value, qualifier):

        key = '{0}, {1}'.format(qualifier['Source'], qualifier['Destination'])
        try:
            MSB = self.LevelData[key][0]
            LSB = self.LevelData[key][1]
        except KeyError:
            return self.Discard('Invalid Command for UpdateLevel')
        if 1 <= int(qualifier['MIDI Channel']) <= 16:
            midiConversion = int('B' + self.MIDIChannelStates[qualifier['MIDI Channel']], 16)
            LevelCmdString = pack('>9B', midiConversion, 0x63, MSB, midiConversion, 0x62, LSB, midiConversion, 0x60, 0x7F)
            res = self.__UpdateHelper('Level', LevelCmdString, value, qualifier)
            if res:
                try:
                    VC = res[8]  # value coarse
                    VF = res[11]  # value fine
                    if VC == 0 and VF == 0:
                        value = -90
                    else:
                        LEVEL_MAX = 35328  # (10 * 256) + 0x8000
                        LEVEL_MIN = 0
                        Gain14Bit = (VC << 7) | VF
                        value = round((Gain14Bit * 4 / 0xFFFF * (LEVEL_MAX - LEVEL_MIN) - 0x8000) / 256)
                    self.WriteStatus('Level', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLevel')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        if 1 <= int(qualifier['MIDI Channel']) <= 16 and qualifier['Source'] in self.MuteData and value in ValueStateValues:
            midiConversion = int('B' + self.MIDIChannelStates[qualifier['MIDI Channel']], 16)
            if 'DCA' in qualifier['Source']:
                MSB = 0x02
            elif 'Master Group' in qualifier['Source']:
                MSB = 0x04
            else:
                MSB = 0x00
            LSB = self.MuteData[qualifier['Source']]
            MuteCmdString = pack('>12B', midiConversion, 0x63, MSB, midiConversion, 0x62, LSB, midiConversion, 0x06, 0x00, midiConversion, 0x26, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        if 1 <= int(qualifier['MIDI Channel']) <= 16 and qualifier['Source'] in self.MuteData:
            midiConversion = int('B' + self.MIDIChannelStates[qualifier['MIDI Channel']], 16)
            if 'DCA' in qualifier['Source']:
                MSB = 0x02
            elif 'Master Group' in qualifier['Source']:
                MSB = 0x04
            else:
                MSB = 0x00
            LSB = self.MuteData[qualifier['Source']]
            MuteCmdString = pack('>9B', midiConversion, 0x63, MSB, midiConversion, 0x62, LSB, midiConversion, 0x60, 0x7F)
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[11]]
                    self.WriteStatus('Mute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetSceneRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 300
        }

        if 1 <= int(qualifier['MIDI Channel']) <= 16 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            midiConversion = int('B' + self.MIDIChannelStates[qualifier['MIDI Channel']], 16)
            if 1 <= value <= 128:
                BK = 0  # bank
                PG = value - 1  # program
            elif 129 <= value <= 256:
                BK = 1
                PG = value - 129
            else:
                BK = 2
                PG = value - 257
            SceneRecallCmdString = pack('>5B', midiConversion, 0x00, BK, 0xC0, PG)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=12)
            if not res:
                return ''
            else:
                return res

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)


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
