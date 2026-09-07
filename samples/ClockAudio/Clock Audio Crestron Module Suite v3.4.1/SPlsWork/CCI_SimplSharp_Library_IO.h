namespace CCI.SimplSharp.Library.IO.Utilities;
        // class declarations
         class PrinterUtil;
         class DebugLevel;
         class StringUtil;
         class CrestronSimplPlusHelper;
    static class PrinterUtil 
    {
        // class delegates

        // class events

        // class functions
        static FUNCTION Print ( DebugLevel level , STRING msg );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

    static class DebugLevel // enum
    {
        static SIGNED_LONG_INTEGER Info;
        static SIGNED_LONG_INTEGER Error;
    };

     class StringUtil 
    {
        // class delegates

        // class events

        // class functions
        static STRING_FUNCTION getBoundString ( STRING msg , STRING startChar , STRING stopChar );
        static STRING_FUNCTION convertEncodingUnicode ( STRING msg );
        static STRING_FUNCTION convertEncodingBigEndian ( STRING msg );
        static STRING_FUNCTION htmlEncoding ( STRING msg );
        static STRING_FUNCTION encode ( STRING msg , INTEGER size );
        static STRING_FUNCTION Base64UrlEncode ( STRING arg );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();
        STRING_FUNCTION ToString ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

     class CrestronSimplPlusHelper 
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

namespace CCI.SimplSharp.Library.IO.Common;
        // class declarations
         class ByteBuffer;
     class ByteBuffer 
    {
        // class delegates

        // class events

        // class functions
        FUNCTION Clear ();
        SIGNED_LONG_INTEGER_FUNCTION Length ();
        SIGNED_LONG_INTEGER_FUNCTION IndexOf ( STRING search );
        STRING_FUNCTION Substring ( SIGNED_LONG_INTEGER startIndex , SIGNED_LONG_INTEGER count );
        STRING_FUNCTION ToString ();
        FUNCTION Delete ( SIGNED_LONG_INTEGER startIndex , SIGNED_LONG_INTEGER count );
        FUNCTION Remove ( SIGNED_LONG_INTEGER startIndex , STRING item );
        SIGNED_LONG_INTEGER_FUNCTION GetHashCode ();

        // class variables
        INTEGER __class_id__;

        // class properties
    };

