Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,IntPtr e);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c);
  public const uint LD=0x02, LU=0x04;
  public static void Click(int x,int y){ SetCursorPos(x,y); System.Threading.Thread.Sleep(120); mouse_event(LD,0,0,0,IntPtr.Zero); System.Threading.Thread.Sleep(60); mouse_event(LU,0,0,0,IntPtr.Zero); }
  public static void DblClick(int x,int y){ Click(x,y); System.Threading.Thread.Sleep(90); mouse_event(LD,0,0,0,IntPtr.Zero); System.Threading.Thread.Sleep(60); mouse_event(LU,0,0,0,IntPtr.Zero); }
}
"@
