namespace Clock_Audio;
        // class declarations
         class LedColorState;
         class Response;
         class ResponsePhantom;
         class ResponseHeartbeat;
         class ResponseSwitchState;
         class ResponsePresetLoad;
         class NoiseSupState;
         class ResponseLedState;
         class ResponseNoiseSup;
         class EQState;
         class AptState;
         class ArmState;
         class DeviceMap;
         class BrightnessMap;
         class DeviceBase;
         class C303D;
         class SwitchesState;
         class ResponsePhantomList;
         class EQMap;
         class ResponseLedAndSwitchState;
         class ResponseLedColorState;
         class ResponseLedColorBrightnessGroupList;
         class Constants;
         class SwitchPinState;
         class ButtonState;
         class ResponsePresetSave;
         class ResponseApt;
         class IntegerEventArgs;
         class ButtonStateEventArgs;
         class SwitchState;
         class ResponseLedBrightness;
         class ArmStateEventArgs;
         class CUT4;
         class PhantomState;
         class ResponseLedBrightnessList;
         class ResponseDefaults;
         class Command;
         class ResponseAddress;
         class ResponseLedColorBrightnessList;
         class PortUtil;
         class CDT100MkII;
         class ResponseLedColorBrightness;
         class LedStateEventArgs;
         class AddressStateEventArgs;
         class ClockAudioDevice;
         class PhantomsState;
         class LedState;
         class LedsState;
         class StateMap;
         class AptMap;
         class EQStateEventArgs;
         class UDPTransportComm;
         class ModeMap;
         class CDT100MkIII;
         class ResponseLedAndSwitchStateList;
         class LevelConverter;
         class AptStateEventArgs;
         class AddressState;
         class ResponseParser;
         class CommandBuilder;
         class ChannelMapper;
         class ResponseArm;
         class ResponseEQ;
         class ColorMap;
         class StringEventArgs;
         class CDT100MkI;
         class ResponseLedColorBrightnessGroup;
         class ResponseTracking;
         class PhantomStateEventArgs;
         class TrackingState;
         class ResponseButtonState;
         class ResponseLedColorStateList;
         class SwitchStateEventArgs;
         class TIM1000;
     class LedColorState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        INTEGER_FUNCTION GetBrightness ();
        FUNCTION ToggleState ();
        FUNCTION SetBrightness ( INTEGER value );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class Response 
    {
        // class delegates

        // class events

        // class functions
        STRING_FUNCTION ToString ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class NoiseSupState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION ToggleState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class EQState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetEQCount ();
        INTEGER_FUNCTION GetLevel ( INTEGER index );
        FUNCTION SetLevel ( INTEGER index , INTEGER value );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class AptState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION SetState ( INTEGER state );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ArmState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION ToggleState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class DeviceMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static DeviceMap CDT100_MKI;
        static DeviceMap CDT100_MKII;
        static DeviceMap CDT100_MKIII;
        static DeviceMap C303D;
        static DeviceMap TIM_1000;
        static DeviceMap CUT4;
        static DeviceMap UNKNOWN;

        // class properties
        INTEGER value;
    };

     class BrightnessMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static BrightnessMap STANDARD;
        static BrightnessMap DUTY_CYCLE;
        static BrightnessMap UNKNOWN;

        // class properties
        SIGNED_LONG_INTEGER index;
    };

     class SwitchesState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetSwitchCount ();
        INTEGER_FUNCTION GetState ( INTEGER sw , INTEGER pin );
        FUNCTION ToggleState ( INTEGER sw , INTEGER pin );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class EQMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static EQMap LOW;
        static EQMap MEDIUM;
        static EQMap HIGH;
        static EQMap UNKNOWN;

        // class properties
        SIGNED_LONG_INTEGER index;
        SIGNED_LONG_INTEGER value;
    };

     class Constants 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static SIGNED_LONG_INTEGER HEARTBEAT_TIME;
        static SIGNED_LONG_INTEGER RESPONSE_TIME;
        static SIGNED_LONG_INTEGER POLL_TIME;
        static SIGNED_LONG_INTEGER REFRESH_TIME;
        static SIGNED_LONG_INTEGER REINIT_TIME;
        static SIGNED_LONG_INTEGER MAX_BUFFER;
        static INTEGER PRIORITY_LEVELS;
        static INTEGER PRIORITY_COMMAND;
        static INTEGER PRIORITY_QUERY;
        static INTEGER MAX_FAILED_RESPONSES;
        static STRING DEV_CMD_DELIM[];
        static STRING DEV_CMD_VERSION[];
        static STRING DEV_CMD_SET_MODE[];
        static STRING DEV_CMD_GET_MODE[];
        static STRING DEV_CMD_ASYNC[];
        static STRING DEV_CMD_ADDRESS[];
        static STRING DEV_CMD_GET_ARM_C[];
        static STRING DEV_CMD_SET_ARM_C[];
        static STRING DEV_CMD_GET_PHANTOM[];
        static STRING DEV_CMD_SET_PHANTOM[];
        static STRING DEV_CMD_GET_CH32[];
        static STRING DEV_CMD_GET_TS[];
        static STRING DEV_CMD_SET_CH32[];
        static STRING DEV_CMD_SET_TS[];
        static STRING DEV_CMD_GET_CH32_B[];
        static STRING DEV_CMD_GET_RGB[];
        static STRING DEV_CMD_SET_CH32_B[];
        static STRING DEV_CMD_SET_TSB[];
        static STRING DEV_CMD_SET_RGB[];
        static STRING DEV_CMD_BUTTON_STATUS[];
        static STRING DEV_CMD_PRESET_SAVE[];
        static STRING DEV_CMD_PRESET_LOAD[];
        static STRING DEV_CMD_IDENTIFY[];
        static STRING DEV_CMD_FIND[];
        static STRING DEV_CMD_DEFAULTS[];
        static STRING DEV_CMD_APT[];
        static STRING DEV_CMD_TRACKING[];
        static STRING DEV_CMD_EQ[];
        static STRING DEV_CMD_NOISESUP[];
        static STRING DEV_CMD_ID[];
        static STRING DEV_CMD_GET_TSB[];
        static STRING DEV_RSP_ACK[];
        static STRING DEV_RSP_NACK[];

        // class properties
    };

     class SwitchPinState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION ToggleState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ButtonState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetIndex ();
        INTEGER_FUNCTION GetState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class IntegerEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        INTEGER payload;
    };

     class ButtonStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        ButtonState payload;
    };

     class SwitchState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetCount ();
        INTEGER_FUNCTION GetState ( INTEGER pin );
        FUNCTION ToggleState ( INTEGER pin );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ArmStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        ArmState payload;
    };

     class PhantomState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION ToggleState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class PortUtil 
    {
        // class delegates

        // class events

        // class functions
        static SIGNED_LONG_INTEGER_FUNCTION GetNextLocalPort ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class LedStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        LedsState payload;
    };

     class AddressStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        AddressState payload;
    };

     class ClockAudioDevice 
    {
        // class delegates

        // class events
        EventHandler OnDebugChange ( ClockAudioDevice sender, StringEventArgs args );
        EventHandler OnCommunicatingChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnInitializedChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnDebugEnableChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnPassbackEnableChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnAddressChange ( ClockAudioDevice sender, AddressStateEventArgs args );
        EventHandler OnArmCChange ( ClockAudioDevice sender, ArmStateEventArgs args );
        EventHandler OnPhantomChange ( ClockAudioDevice sender, PhantomStateEventArgs args );
        EventHandler OnLedChange ( ClockAudioDevice sender, LedStateEventArgs args );
        EventHandler OnSwitchChange ( ClockAudioDevice sender, SwitchStateEventArgs args );
        EventHandler OnPresetChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnPassbackChange ( ClockAudioDevice sender, StringEventArgs args );
        EventHandler OnTrackingChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnAptChange ( ClockAudioDevice sender, AptStateEventArgs args );
        EventHandler OnEQChange ( ClockAudioDevice sender, EQStateEventArgs args );
        EventHandler OnNoiseSupChange ( ClockAudioDevice sender, IntegerEventArgs args );
        EventHandler OnButtonChange ( ClockAudioDevice sender, ButtonStateEventArgs args );

        // class functions
        FUNCTION SendTrace ( STRING msg );
        FUNCTION Strikeout ();
        FUNCTION ProcessResponse ( Response response );
        FUNCTION Debug ( STRING message );
        FUNCTION ForwardMessage ( Command message , INTEGER priority );
        STRING_FUNCTION GetIP ();
        FUNCTION Configure ( INTEGER deviceType , STRING remoteIP , INTEGER remotePort , INTEGER adapterType , INTEGER brightnessType , STRING adapterIPOverride );
        FUNCTION Reinitialize ();
        FUNCTION SetDebug ( INTEGER state );
        FUNCTION Poll ();
        FUNCTION SetPassback ( INTEGER state );
        FUNCTION SetArmC ( INTEGER state );
        FUNCTION ToggleArmC ();
        FUNCTION SetPhantomAll ( INTEGER state );
        FUNCTION SetPhantom ( INTEGER index , INTEGER state );
        FUNCTION TogglePhantom ( INTEGER index );
        FUNCTION SetLedStateAll ( INTEGER color , INTEGER state );
        FUNCTION SetLedState ( INTEGER index , INTEGER color , INTEGER state );
        FUNCTION ToggleLedState ( INTEGER index , INTEGER color );
        FUNCTION SetLedBrightAll ( INTEGER color , INTEGER value );
        FUNCTION SetLedBright ( INTEGER index , INTEGER color , INTEGER value );
        FUNCTION SavePreset ();
        FUNCTION LoadPreset ();
        FUNCTION Passthrough ( STRING text );
        FUNCTION SetIdentify ( INTEGER state );
        FUNCTION SetFind ();
        FUNCTION SetDefaults ();
        FUNCTION SetTracking ( INTEGER state );
        FUNCTION ToggleTracking ();
        FUNCTION SetNoiseSup ( INTEGER state );
        FUNCTION ToggleNoiseSup ();
        FUNCTION SetApt ( INTEGER value );
        FUNCTION SetEQ ( INTEGER index , INTEGER value );
        FUNCTION SendMessage ( Command msg );
        FUNCTION FailedResponse ();
        SIGNED_LONG_INTEGER_FUNCTION GetHeartbeatTime ();
        FUNCTION GetInitialized ();
        SIGNED_LONG_INTEGER_FUNCTION GetResponseTime ();
        FUNCTION Reconnect ();
        FUNCTION SendHeartbeat ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class PhantomsState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetPhantomCount ();
        INTEGER_FUNCTION GetState ( INTEGER index );
        FUNCTION ToggleState ( INTEGER sw );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class LedState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetColorCount ();
        INTEGER_FUNCTION GetState ( ColorMap color );
        INTEGER_FUNCTION GetBrightness ( ColorMap color );
        FUNCTION ToggleState ( ColorMap color );
        FUNCTION SetBrightness ( ColorMap color , INTEGER value );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class LedsState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetLedCount ();
        INTEGER_FUNCTION GetState ( INTEGER index , INTEGER color );
        INTEGER_FUNCTION GetBrightness ( INTEGER index , INTEGER color );
        FUNCTION ToggleState ( INTEGER index , ColorMap color );
        FUNCTION SetBrightness ( INTEGER index , ColorMap color , INTEGER value );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class StateMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static StateMap OFF;
        static StateMap ON;

        // class properties
        INTEGER index;
        STRING name[];
    };

     class AptMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static AptMap OFF;
        static AptMap SLOW;
        static AptMap MEDIUM;
        static AptMap NORMAL;
        static AptMap UNKNOWN;

        // class properties
        SIGNED_LONG_INTEGER index;
        SIGNED_LONG_INTEGER value;
    };

     class EQStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        EQState payload;
    };

     class ModeMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static ModeMap CDT100_MKI;
        static ModeMap CDT100_MKII;

        // class properties
        INTEGER value;
    };

     class LevelConverter 
    {
        // class delegates

        // class events

        // class functions
        static INTEGER_FUNCTION ScaleToCrestronRGB ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleFromCrestronRGB ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleToCrestronCH32 ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleFromCrestronCH32 ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleToCrestronTSB ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleFromCrestronTSB ( INTEGER levelIn );
        static INTEGER_FUNCTION ScaleToCrestronEQ ( SIGNED_INTEGER levelIn );
        static SIGNED_INTEGER_FUNCTION ScaleFromCrestronEQ ( INTEGER levelIn );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class AptStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        AptState payload;
    };

     class AddressState 
    {
        // class delegates

        // class events

        // class functions
        STRING_FUNCTION GetSwitchAddress ();
        STRING_FUNCTION GetIpAddress ();
        FUNCTION SetSwitchAddress ( STRING value );
        FUNCTION SetIpAddress ( STRING value );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ResponseParser 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class CommandBuilder 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ChannelMapper 
    {
        // class delegates

        // class events

        // class functions
        static INTEGER_FUNCTION MapChannel ( DeviceMap device , INTEGER index );
        static INTEGER_FUNCTION MapSwitch ( DeviceMap device , INTEGER index );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class ColorMap 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        static ColorMap RED;
        static ColorMap GREEN;
        static ColorMap BLUE;

        // class properties
        SIGNED_LONG_INTEGER index;
        STRING value[];
        STRING name[];
    };

     class StringEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        STRING payload[];
    };

     class PhantomStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        PhantomsState payload;
    };

     class TrackingState 
    {
        // class delegates

        // class events

        // class functions
        INTEGER_FUNCTION GetState ();
        FUNCTION ToggleState ();
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class SwitchStateEventArgs 
    {
        // class delegates

        // class events

        // class functions
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
        SwitchesState payload;
    };

