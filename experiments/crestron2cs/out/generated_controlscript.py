"""
CrestronDerived (EXPERIMENT-GENERATED, Crestron -> ControlScript translation)

Mechanically translated by crestron2cs.py (experiments/crestron2cs) from the
Crestron LegacyWrappers JSON-engine driver at:
    ../../samples/Samsung QNxxLS03DAFXZA/Crestron/IP/FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg

This is a measurement artifact for project question 1b: "can a Crestron IP
driver be turned into an Extron ControlScript module?" -- NOT a hand-tuned,
production-quality driver. Every command below is derived mechanically from
Crestron's own Commands[]/Transformations[]/Controllers[] naming and value
domains (booleans keyed 'true'/'false', not Extron's 'On'/'Off') -- it does
NOT copy Extron's own shipped ethernet script's naming or value choices.
See experiments/crestron2cs/ for the resolver and the wire-table diff against
that shipped script.

DRIVER STYLE
    Ethernet - HTTP Driver (GC-runtime Extron2.HTTPDriver dialect)
COMMAND STRUCTURE
    JSON-RPC 2.0 over HTTPS, port 1516, createAccessToken handshake.
"""
from Extron2.HTTPDriver import HTTPDriver
import socket
import struct
import urllib.error
import urllib.request
import json


class CrestronDerived(HTTPDriver):

    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'AmbientOff': {'Set': True, 'Update': False, 'Status': {}},
            'AmbientOn': {'Set': True, 'Update': False, 'Status': {}},
            'AnalogAirAntenna': {'Set': True, 'Update': False, 'Status': {}},
            'AnalogCableAntenna': {'Set': True, 'Update': False, 'Status': {}},
            'Artwork': {'Set': True, 'Update': True, 'Status': {}},
            'Back': {'Set': True, 'Update': False, 'Status': {}},
            'Blue': {'Set': True, 'Update': False, 'Status': {}},
            'Channel': {'Set': True, 'Update': True, 'Status': {}},
            'ChannelDown': {'Set': True, 'Update': False, 'Status': {}},
            'ChannelUp': {'Set': True, 'Update': False, 'Status': {}},
            'DigitalAirAntenna': {'Set': True, 'Update': False, 'Status': {}},
            'DigitalCableAntenna': {'Set': True, 'Update': False, 'Status': {}},
            'DisplayRotatorControlLandscape': {'Set': True, 'Update': False, 'Status': {}},
            'DisplayRotatorControlPortrait': {'Set': True, 'Update': False, 'Status': {}},
            'Down': {'Set': True, 'Update': False, 'Status': {}},
            'Exit': {'Set': True, 'Update': False, 'Status': {}},
            'FirstScreenApp': {'Set': True, 'Update': True, 'Status': {}},
            'ForwardScan': {'Set': True, 'Update': False, 'Status': {}},
            'GetAccessToken': {'Set': True, 'Update': False, 'Status': {}},
            'GetMultiViewModes': {'Set': True, 'Update': False, 'Status': {}},
            'Green': {'Set': True, 'Update': False, 'Status': {}},
            'Home': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress0': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress1': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress2': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress3': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress4': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress5': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress6': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress7': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress8': {'Set': True, 'Update': False, 'Status': {}},
            'Keypress9': {'Set': True, 'Update': False, 'Status': {}},
            'KeypressDash': {'Set': True, 'Update': False, 'Status': {}},
            'KeypressEnter': {'Set': True, 'Update': False, 'Status': {}},
            'Left': {'Set': True, 'Update': False, 'Status': {}},
            'MediaService': {'Set': True, 'Update': False, 'Status': {}},
            'Menu': {'Set': True, 'Update': False, 'Status': {}},
            'MultiViewMode1': {'Set': True, 'Update': False, 'Status': {}},
            'MultiViewMode2': {'Set': True, 'Update': False, 'Status': {}},
            'MultiViewMode3': {'Set': True, 'Update': False, 'Status': {}},
            'Mute': {'Set': True, 'Update': True, 'Status': {}},
            'Pause': {'Set': True, 'Update': False, 'Status': {}},
            'PictureModeDynamic': {'Set': True, 'Update': False, 'Status': {}},
            'PictureModeFilmmaker': {'Set': True, 'Update': False, 'Status': {}},
            'PictureModeMovie': {'Set': True, 'Update': False, 'Status': {}},
            'PictureModeStandard': {'Set': True, 'Update': False, 'Status': {}},
            'Play': {'Set': True, 'Update': False, 'Status': {}},
            'Power': {'Set': True, 'Update': True, 'Status': {}},
            'Red': {'Set': True, 'Update': False, 'Status': {}},
            'Return': {'Set': True, 'Update': False, 'Status': {}},
            'ReverseScan': {'Set': True, 'Update': False, 'Status': {}},
            'Right': {'Set': True, 'Update': False, 'Status': {}},
            'Select': {'Set': True, 'Update': False, 'Status': {}},
            'SoundModeAmplify': {'Set': True, 'Update': False, 'Status': {}},
            'SoundModeStandard': {'Set': True, 'Update': False, 'Status': {}},
            'Stop': {'Set': True, 'Update': False, 'Status': {}},
            'TvInput': {'Set': True, 'Update': False, 'Status': {}},
            'TvPlus': {'Set': True, 'Update': False, 'Status': {}},
            'Up': {'Set': True, 'Update': False, 'Status': {}},
            'VideoInput': {'Set': True, 'Update': True, 'Status': {}},
            'Volume': {'Set': True, 'Update': True, 'Status': {}},
            'Yellow': {'Set': True, 'Update': False, 'Status': {}},
        }
        self.AccessToken = None
        self.authenticated = False
        self._commandId = 1
    # Crestron Commands['AmbientOff'] (fire)
    def _cmd_SetAmbientOff(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'firstScreen',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('AmbientOff', value, qualifier, data)


    # Crestron Commands['AmbientOn'] (fire)
    def _cmd_SetAmbientOn(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'ambient',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('AmbientOn', value, qualifier, data)


    # Crestron Commands['SetAnalogAirAntenna'] (fire)
    def _cmd_SetAnalogAirAntenna(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': self.AAChannel,
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('AnalogAirAntenna', value, qualifier, data)


    # Crestron Commands['SetAnalogCableAntenna'] (fire)
    def _cmd_SetAnalogCableAntenna(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': self.ACChannel,
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('AnalogCableAntenna', value, qualifier, data)


    # Crestron Commands['SetArtwork'] (stateful)
    def _cmd_SetArtwork(self, value, qualifier):
        ValueStateValues = {'true': 'artModeOn', 'false': 'artModeOff'}
        data = {
                'method': 'artModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'artMode': ValueStateValues[value],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Artwork', value, qualifier, data)

    def _cmd_UpdateArtwork(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'artModeControl',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('Artwork', value, qualifier, data)
        if res:
            try:
                Artwork = {'artModeOn': 'true', 'artModeOff': 'false'}[str(res['result']['artMode'])]
            except (KeyError, IndexError, AttributeError):
                self.Error(['Artwork: Invalid/unexpected response'])


    # Crestron Commands['Back'] (fire)
    def _cmd_SetBack(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'return',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Back', value, qualifier, data)


    # Crestron Commands['Blue'] (fire)
    def _cmd_SetBlue(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'blue',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Blue', value, qualifier, data)


    # Crestron Commands['SetChannel'] (stateful)
    def _cmd_SetChannel(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': str(value),
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Channel', value, qualifier, data)

    def _cmd_UpdateChannel(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'directChannelControl',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('Channel', value, qualifier, data)
        if res:
            try:
                AntennaName = res['result']['atvDtv']
                AntennaSource = res['result']['airCable']
                Channel = res['result']['channelNum']
            except (KeyError, IndexError, AttributeError):
                self.Error(['Channel: Invalid/unexpected response'])


    # Crestron Commands['ChannelDown'] (fire)
    def _cmd_SetChannelDown(self, value, qualifier):
        data = {
                'method': 'channelUpDnControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'control': 'channelDn',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('ChannelDown', value, qualifier, data)


    # Crestron Commands['ChannelUp'] (fire)
    def _cmd_SetChannelUp(self, value, qualifier):
        data = {
                'method': 'channelUpDnControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'control': 'channelUp',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('ChannelUp', value, qualifier, data)


    # Crestron Commands['SetDigitalAirAntenna'] (fire)
    def _cmd_SetDigitalAirAntenna(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': self.DAChannel,
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('DigitalAirAntenna', value, qualifier, data)


    # Crestron Commands['SetDigitalCableAntenna'] (fire)
    def _cmd_SetDigitalCableAntenna(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': self.DCChannel,
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('DigitalCableAntenna', value, qualifier, data)


    # Crestron Commands['SetDisplayRotatorControlLandscape'] (fire)
    def _cmd_SetDisplayRotatorControlLandscape(self, value, qualifier):
        data = {
                'method': 'displayRotatorControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'orientation': 'Landscape',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('DisplayRotatorControlLandscape', value, qualifier, data)


    # Crestron Commands['SetDisplayRotatorControlPortrait'] (fire)
    def _cmd_SetDisplayRotatorControlPortrait(self, value, qualifier):
        data = {
                'method': 'displayRotatorControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'orientation': 'Portrait',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('DisplayRotatorControlPortrait', value, qualifier, data)


    # Crestron Commands['Down'] (fire)
    def _cmd_SetDown(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'cursorDn',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Down', value, qualifier, data)


    # Crestron Commands['Exit'] (fire)
    def _cmd_SetExit(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'exit',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Exit', value, qualifier, data)


    # Crestron Commands['SetFirstScreenApp'] (stateful)
    def _cmd_SetFirstScreenApp(self, value, qualifier):
        ValueStateValues = {'youtube': 'youTube', 'netflix': 'netflix', 'hulu': 'hulu', 'vudu': 'vudu', 'pandora': 'pandora', 'abcnews': 'ABC News', 'amazon': 'amazon', 'amazonalexa': 'Amazon Alexa', 'amazonmusic': 'Amazon Music', 'amc': 'AMC', 'amc+': 'AMC+', 'applemusic': 'Apple Music', 'appletv': 'Apple TV', 'bixby': 'Bixby', 'britbox': 'BritBox by BBC', 'bloomberg': 'Bloomberg', 'cbsnews': 'CBS News: Live Breaking News', 'cnn': 'CNN', 'crackle': 'Crackle', 'crunchyroll': 'Crunchyroll', 'dazn': 'DAZN', 'espn': 'ESPN', 'foodnetworkgo': 'Food Network GO', 'freevee': 'Freevee', 'deezer': 'Deezer', 'directtvstream': 'DIRECTV STREAM', 'discovery+': 'discovery+ | Stream TV Shows, Originals and More', 'disney+': 'Disney+', 'epix': 'EPIXCast', 'foxsports': 'FOX Sports', 'fubotv': 'Fubo: Watch Live TV & Sports', 'hgtvgo': 'HGTV GO - Stream Live TV', 'iheartradio': 'iHeartRadio', 'max': 'Max', 'mlb': 'MLB', 'nbc': 'NBC', 'nbcsports': 'NBC Sports', 'now': 'الشرق NOW', 'paramount+': 'Paramount+', 'pbsvideo': 'PBS Video', 'peacocktv': 'Peacock TV', 'plex': 'Plex - Free Movies ＆ TV', 'plutotv': 'Pluto TV', 'redbulltv': 'Red Bull TV', 'samsunghealth': 'Samsung Health', 'siriusxm': 'SiriusXM TV: Music, Podcasts, Sports, News', 'slingtv': 'Sling TV: Live TV, Sports, News + Freestream ', 'spotify': 'Spotify - Music and Podcasts', 'starz': 'STARZ', 'tbscast': 'TBS Cast', 'tntcast': 'TNT Cast', 'tiktok': 'TikTok', 'tubi': 'Tubi - Free Movies ＆ TV', 'ufc': 'UFC', 'viki': 'Viki: Asian Drama, Movies and More', 'youtubetv': 'YouTube TV', 'itv': 'iTV', 'internet': 'Internet'}
        data = {
                'method': 'firstScreenAppControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'applicationName': ValueStateValues[self.VideoInput],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('FirstScreenApp', value, qualifier, data)

    def _cmd_UpdateFirstScreenApp(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'firstScreenAppControl',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('FirstScreenApp', value, qualifier, data)


    # Crestron Commands['ForwardScan'] (fire)
    def _cmd_SetForwardScan(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'fastforward',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('ForwardScan', value, qualifier, data)


    # Crestron Commands['GetAccessToken'] (fire)
    def _cmd_SetGetAccessToken(self, value, qualifier):
        data = {
                'method': 'createAccessToken',
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('GetAccessToken', value, qualifier, data)


    # Crestron Commands['GetMultiViewModes'] (fire)
    def _cmd_SetGetMultiViewModes(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'multiviewControl',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        self.__SetHelper('GetMultiViewModes', value, qualifier, data)


    # Crestron Commands['Green'] (fire)
    def _cmd_SetGreen(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'green',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Green', value, qualifier, data)


    # Crestron Commands['Home'] (fire)
    def _cmd_SetHome(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'firstScreen',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Home', value, qualifier, data)


    # Crestron Commands['Keypress0'] (fire)
    def _cmd_SetKeypress0(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number0',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress0', value, qualifier, data)


    # Crestron Commands['Keypress1'] (fire)
    def _cmd_SetKeypress1(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number1',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress1', value, qualifier, data)


    # Crestron Commands['Keypress2'] (fire)
    def _cmd_SetKeypress2(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number2',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress2', value, qualifier, data)


    # Crestron Commands['Keypress3'] (fire)
    def _cmd_SetKeypress3(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number3',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress3', value, qualifier, data)


    # Crestron Commands['Keypress4'] (fire)
    def _cmd_SetKeypress4(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number4',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress4', value, qualifier, data)


    # Crestron Commands['Keypress5'] (fire)
    def _cmd_SetKeypress5(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number5',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress5', value, qualifier, data)


    # Crestron Commands['Keypress6'] (fire)
    def _cmd_SetKeypress6(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number6',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress6', value, qualifier, data)


    # Crestron Commands['Keypress7'] (fire)
    def _cmd_SetKeypress7(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number7',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress7', value, qualifier, data)


    # Crestron Commands['Keypress8'] (fire)
    def _cmd_SetKeypress8(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number8',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress8', value, qualifier, data)


    # Crestron Commands['Keypress9'] (fire)
    def _cmd_SetKeypress9(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'number9',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Keypress9', value, qualifier, data)


    # Crestron Commands['KeypressDash'] (fire)
    def _cmd_SetKeypressDash(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'dash',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('KeypressDash', value, qualifier, data)


    # Crestron Commands['KeypressEnter'] (fire)
    def _cmd_SetKeypressEnter(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'enter',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('KeypressEnter', value, qualifier, data)


    # Crestron Commands['Left'] (fire)
    def _cmd_SetLeft(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'cursorLeft',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Left', value, qualifier, data)


    # Crestron Commands['SetMediaService'] (fire)
    def _cmd_SetMediaService(self, value, qualifier):
        ValueStateValues = {'youtube': 'youTube', 'netflix': 'netflix', 'hulu': 'hulu', 'vudu': 'vudu', 'pandora': 'pandora', 'abcnews': 'ABC News', 'amazon': 'amazon', 'amazonalexa': 'Amazon Alexa', 'amazonmusic': 'Amazon Music', 'amc': 'AMC', 'amc+': 'AMC+', 'applemusic': 'Apple Music', 'appletv': 'Apple TV', 'bixby': 'Bixby', 'britbox': 'BritBox by BBC', 'bloomberg': 'Bloomberg', 'cbsnews': 'CBS News: Live Breaking News', 'cnn': 'CNN', 'crackle': 'Crackle', 'crunchyroll': 'Crunchyroll', 'dazn': 'DAZN', 'espn': 'ESPN', 'foodnetworkgo': 'Food Network GO', 'freevee': 'Freevee', 'deezer': 'Deezer', 'directtvstream': 'DIRECTV STREAM', 'discovery+': 'discovery+ | Stream TV Shows, Originals and More', 'disney+': 'Disney+', 'epix': 'EPIXCast', 'foxsports': 'FOX Sports', 'fubotv': 'Fubo: Watch Live TV & Sports', 'hgtvgo': 'HGTV GO - Stream Live TV', 'iheartradio': 'iHeartRadio', 'max': 'Max', 'mlb': 'MLB', 'nbc': 'NBC', 'nbcsports': 'NBC Sports', 'now': 'الشرق NOW', 'paramount+': 'Paramount+', 'pbsvideo': 'PBS Video', 'peacocktv': 'Peacock TV', 'plex': 'Plex - Free Movies ＆ TV', 'plutotv': 'Pluto TV', 'redbulltv': 'Red Bull TV', 'samsunghealth': 'Samsung Health', 'siriusxm': 'SiriusXM TV: Music, Podcasts, Sports, News', 'slingtv': 'Sling TV: Live TV, Sports, News + Freestream ', 'spotify': 'Spotify - Music and Podcasts', 'starz': 'STARZ', 'tbscast': 'TBS Cast', 'tntcast': 'TNT Cast', 'tiktok': 'TikTok', 'tubi': 'Tubi - Free Movies ＆ TV', 'ufc': 'UFC', 'viki': 'Viki: Asian Drama, Movies and More', 'youtubetv': 'YouTube TV', 'itv': 'iTV', 'internet': 'Internet'}
        data = {
                'method': 'directAccessControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'applicationName': ValueStateValues[self.VideoInput],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('MediaService', value, qualifier, data)


    # Crestron Commands['Menu'] (fire)
    def _cmd_SetMenu(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'menu',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Menu', value, qualifier, data)


    # Crestron Commands['SetMultiViewMode1'] (fire)
    def _cmd_SetMultiViewMode1(self, value, qualifier):
        data = {
                'method': 'multiviewControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'multiviewMode': 'My Multi View 1',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('MultiViewMode1', value, qualifier, data)


    # Crestron Commands['SetMultiViewMode2'] (fire)
    def _cmd_SetMultiViewMode2(self, value, qualifier):
        data = {
                'method': 'multiviewControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'multiviewMode': 'My Multi View 2',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('MultiViewMode2', value, qualifier, data)


    # Crestron Commands['SetMultiViewMode3'] (fire)
    def _cmd_SetMultiViewMode3(self, value, qualifier):
        data = {
                'method': 'multiviewControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'multiviewMode': 'My Multi View 3',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('MultiViewMode3', value, qualifier, data)


    # Crestron Commands['SetMute'] (stateful)
    def _cmd_SetMute(self, value, qualifier):
        ValueStateValues = {'true': 'muteOn', 'false': 'muteOff'}
        data = {
                'method': 'muteControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'mute': ValueStateValues[value],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Mute', value, qualifier, data)

    def _cmd_UpdateMute(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'getTVStates',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('Mute', value, qualifier, data)
        if res:
            try:
                Volume = res['result']['volume']
                Mute = {'muteOn': 'true', 'muteOff': 'false'}[str(res['result']['mute'])]
                VideoConfiguration = {'16:9': 'Sixteen_Nine', '4:3': 'Four_Three'}[str(res['result']['pictureSize'])]
            except (KeyError, IndexError, AttributeError):
                self.Error(['Mute: Invalid/unexpected response'])


    # Crestron Commands['Pause'] (fire)
    def _cmd_SetPause(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'pause',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Pause', value, qualifier, data)


    # Crestron Commands['SetPictureModeDynamic'] (fire)
    def _cmd_SetPictureModeDynamic(self, value, qualifier):
        data = {
                'method': 'pictureModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'pictureMode': 'Dynamic',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('PictureModeDynamic', value, qualifier, data)


    # Crestron Commands['SetPictureModeFilmmaker'] (fire)
    def _cmd_SetPictureModeFilmmaker(self, value, qualifier):
        data = {
                'method': 'pictureModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'pictureMode': 'FilmmakerMode',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('PictureModeFilmmaker', value, qualifier, data)


    # Crestron Commands['SetPictureModeMovie'] (fire)
    def _cmd_SetPictureModeMovie(self, value, qualifier):
        data = {
                'method': 'pictureModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'pictureMode': 'Movie',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('PictureModeMovie', value, qualifier, data)


    # Crestron Commands['SetPictureModeStandard'] (fire)
    def _cmd_SetPictureModeStandard(self, value, qualifier):
        data = {
                'method': 'pictureModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'pictureMode': 'Standard',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('PictureModeStandard', value, qualifier, data)


    # Crestron Commands['Play'] (fire)
    def _cmd_SetPlay(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'play',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Play', value, qualifier, data)


    # Crestron Commands['SetPower'] (stateful)
    def _cmd_SetPower(self, value, qualifier):
        ValueStateValues = {'true': 'powerOn', 'false': 'powerOff'}
        data = {
                'method': 'powerControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'power': ValueStateValues[value],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        if value in ('true', True) and self.AccessToken:
            for _i in range(6):
                self._sendWakeOnLan(self.MacAddress)
        self.__SetHelper('Power', value, qualifier, data)

    def _cmd_UpdatePower(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'powerControl',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('Power', value, qualifier, data)
        if res:
            try:
                Power = {'powerOn': 'true', 'powerOff': 'false'}[str(res['result']['power'])]
            except (KeyError, IndexError, AttributeError):
                self.Error(['Power: Invalid/unexpected response'])


    # Crestron Commands['Red'] (fire)
    def _cmd_SetRed(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'red',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Red', value, qualifier, data)


    # Crestron Commands['Return'] (fire)
    def _cmd_SetReturn(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'return',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Return', value, qualifier, data)


    # Crestron Commands['ReverseScan'] (fire)
    def _cmd_SetReverseScan(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'rewind',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('ReverseScan', value, qualifier, data)


    # Crestron Commands['Right'] (fire)
    def _cmd_SetRight(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'cursorRight',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Right', value, qualifier, data)


    # Crestron Commands['Select'] (fire)
    def _cmd_SetSelect(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'enter',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Select', value, qualifier, data)


    # Crestron Commands['SetSoundModeAmplify'] (fire)
    def _cmd_SetSoundModeAmplify(self, value, qualifier):
        data = {
                'method': 'soundModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'soundMode': 'Amplify',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('SoundModeAmplify', value, qualifier, data)


    # Crestron Commands['SetSoundModeStandard'] (fire)
    def _cmd_SetSoundModeStandard(self, value, qualifier):
        data = {
                'method': 'soundModeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'soundMode': 'Standard',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('SoundModeStandard', value, qualifier, data)


    # Crestron Commands['Stop'] (fire)
    def _cmd_SetStop(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'stop',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Stop', value, qualifier, data)


    # Crestron Commands['SetTvInput'] (fire)
    def _cmd_SetTvInput(self, value, qualifier):
        data = {
                'method': 'inputSourceControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'inputSource': 'TV',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('TvInput', value, qualifier, data)


    # Crestron Commands['SetTvPlus'] (fire)
    def _cmd_SetTvPlus(self, value, qualifier):
        ConvertedAntennaValueStateValues = {'AnalogAntenna': 'atv', 'DigitalAntenna': 'dtv', 'AnalogCable': 'atv', 'DigitalCable': 'dtv', 'TvPlus': 'tvplus'}
        ConvertedSourceValueStateValues = {'AnalogAntenna': 'air', 'DigitalAntenna': 'air', 'AnalogCable': 'cable', 'DigitalCable': 'cable', 'TvPlus': 'air'}
        data = {
                'method': 'directChannelControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'atvDtv': ConvertedAntennaValueStateValues[self.VideoInput],
                    'airCable': ConvertedSourceValueStateValues[self.VideoInput],
                    'channelNum': self.TvPlusChannel,
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('TvPlus', value, qualifier, data)


    # Crestron Commands['Up'] (fire)
    def _cmd_SetUp(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'cursorUp',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Up', value, qualifier, data)


    # Crestron Commands['SetVideoInput'] (stateful)
    def _cmd_SetVideoInput(self, value, qualifier):
        ValueStateValues = {'Hdmi1': 'HDMI1', 'Hdmi2': 'HDMI2', 'Hdmi3': 'HDMI3', 'Hdmi4': 'HDMI4'}
        data = {
                'method': 'inputSourceControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'inputSource': ValueStateValues[value],
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('VideoInput', value, qualifier, data)

    def _cmd_UpdateVideoInput(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'getTVStates',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('VideoInput', value, qualifier, data)
        if res:
            try:
                ReportedVideoInput = {'HDMI1': 'Hdmi1', 'HDMI2': 'Hdmi2', 'HDMI3': 'Hdmi3', 'HDMI4': 'Hdmi4'}[str(res['result']['inputSource'])]
            except (KeyError, IndexError, AttributeError):
                self.Error(['VideoInput: Invalid/unexpected response'])


    # Crestron Commands['SetVolume'] (stateful)
    def _cmd_SetVolume(self, value, qualifier):
        data = {
                'method': 'directVolumeControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'volume': '{0:#0}'.format(value),
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Volume', value, qualifier, data)

    def _cmd_UpdateVolume(self, value, qualifier):
        data = {
                'jsonrpc': '2.0',
                'method': 'getTVStates',
                'id': self._commandId,
                'params': {
                    'AccessToken': self.AccessToken,
                },
            }
        res = self.__UpdateHelper('Volume', value, qualifier, data)
        if res:
            try:
                Volume = res['result']['volume']
                Mute = {'muteOn': 'true', 'muteOff': 'false'}[str(res['result']['mute'])]
                VideoConfiguration = {'16:9': 'Sixteen_Nine', '4:3': 'Four_Three'}[str(res['result']['pictureSize'])]
            except (KeyError, IndexError, AttributeError):
                self.Error(['Volume: Invalid/unexpected response'])


    # Crestron Commands['Yellow'] (fire)
    def _cmd_SetYellow(self, value, qualifier):
        data = {
                'method': 'remoteKeyControl',
                'params': {
                    'AccessToken': self.AccessToken,
                    'remoteKey': 'yellow',
                },
                'id': self._commandId,
                'jsonrpc': '2.0',
            }
        self.__SetHelper('Yellow', value, qualifier, data)

    # ------------------------------------------------------------------
    # Infrastructure (not itself part of the measured wire content)
    # ------------------------------------------------------------------

    def __CheckResponseForErrors(self, sourceCmdName, response):
        try:
            res = json.loads(response.read().decode())
            if 'error' in res:
                self.Error(['{0}: {1}'.format(sourceCmdName, res['error']['message'])])
                return ''
            return res
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])

    def __NextCommandId(self):
        # Crestron's CommandIds[] declares a MonotonicIntegerId, Min=1 Max=127,
        # Rollover=None -- modelled faithfully here. (Extron's own shipped
        # ethernet script hardcodes 'id': 1 for every request instead --
        # see extron_ethernet_source.py; a genuine, if likely inconsequential
        # per JSON-RPC's spec, protocol-detail difference.)
        current = self._commandId
        self._commandId = current + 1 if current < 127 else 1
        return current

    def __SetHelper(self, command, value, qualifier, data=None):
        data['id'] = self.__NextCommandId()
        url = self.RootURL.replace('http', 'https')
        payload = json.dumps(data).encode()
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        my_request = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=8)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:
            res = ''
        else:
            res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, data=None):
        return self.__SetHelper(command, value, qualifier, data)

    def _sendWakeOnLan(self, mac_address):
        """Crestron's WakeOnLan Command (Info.MacAddress = '{_MacAddress_}')
        -- a UDP magic packet, sent 6x by Rule UseWOLForPowerOn before every
        SetPower('true'). Extron's shipped ethernet script has NO equivalent
        anywhere (grep for 'MacAddress'/'WakeOnLan' in
        extron_ethernet_source.py returns nothing): Extron relies solely on
        the IP-remote/createAccessToken handshake to power the display on.
        """
        mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
        packet = b'\xff' * 6 + mac_bytes * 16
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, ('255.255.255.255', 9))
        sock.close()
