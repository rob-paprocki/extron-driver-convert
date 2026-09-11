using System;
using System.Collections;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization.Formatters.Binary;

public class Reflect2 {
    const string DIR = @"C:\Program Files (x86)\Extron\GCP";
    static Assembly Resolve(object s, ResolveEventArgs e) {
        string n = e.Name.Split(',')[0];
        string p = Path.Combine(DIR, n + ".dll");
        return File.Exists(p) ? Assembly.LoadFrom(p) : null;
    }
    static void Dump(Type t) {
        if (t == null) { Console.WriteLine("(null type)"); return; }
        Console.WriteLine("== " + t.FullName + "  base=" + (t.BaseType==null?"":t.BaseType.FullName));
        Console.WriteLine("   interfaces: " + string.Join(", ", t.GetInterfaces().Select(i=>i.Name)));
        for (Type c = t; c != null && c != typeof(object); c = c.BaseType) {
            foreach (var f in c.GetFields(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly))
                Console.WriteLine("   F[" + c.Name + "] " + f.FieldType.Name + " " + f.Name);
            foreach (var p in c.GetProperties(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly))
                Console.WriteLine("   P[" + c.Name + "] " + p.PropertyType.Name + " " + p.Name);
        }
    }
    public static int Main(string[] args) {
        AppDomain.CurrentDomain.AssemblyResolve += Resolve;
        Assembly a = Assembly.LoadFrom(Path.Combine(DIR, "Extron.Configuration.Drivers.dll"));
        foreach (string n in new[]{"Extron.Configuration.Drivers.DriverFileAsset",
                                   "Extron.Configuration.Drivers.DriverDescriptorAsset"})
            Dump(a.GetType(n));
        Console.WriteLine("--- types in Drivers asm containing 'Resource' or 'Asset' ---");
        foreach (Type t in a.GetTypes().Where(x => x.Name.Contains("Resource") || x.Name.Contains("Asset")))
            Console.WriteLine("   " + t.FullName);
        Console.WriteLine("--- live package ---");
        string path = args.Length>0?args[0]:null;
        if (path != null) {
            byte[] raw = File.ReadAllBytes(path);
            Stream s = new MemoryStream(raw);
            if (raw[0]==0x1f) s = new GZipStream(s, CompressionMode.Decompress);
            object asset = new BinaryFormatter().Deserialize(s);
            Console.WriteLine("root type: " + asset.GetType().FullName);
            Type it = a.GetType("Extron.Configuration.Contracts.Assets.Drivers.IDriverFileAsset");
            foreach (var iface in asset.GetType().GetInterfaces()) Console.WriteLine("  iface " + iface.FullName);
            var pi = asset.GetType().GetProperty("Manifest");
            object man = pi.GetValue(asset, null);
            Console.WriteLine("Manifest: " + (man==null?"null":man.GetType().FullName));
            Dump(man == null ? null : man.GetType());
            int i=0;
            foreach (object r in (IEnumerable)man) {
                Console.WriteLine("  res[" + (i++) + "] " + r.GetType().FullName +
                  " Key=" + r.GetType().GetProperty("Key").GetValue(r,null) +
                  " Guid=" + r.GetType().GetProperty("Guid").GetValue(r,null));
                if (i==1) Dump(r.GetType());
            }
            var hd = asset.GetType().GetProperty("ResourceHashDict").GetValue(asset, null);
            Console.WriteLine("HashDict: " + hd.GetType().FullName + " count=" + hd.GetType().GetProperty("Count").GetValue(hd,null));
            var cmp = hd.GetType().GetProperty("Comparer");
            Console.WriteLine("  comparer: " + (cmp==null?"?":cmp.GetValue(hd,null).GetType().FullName));
            Console.WriteLine("Filename: " + asset.GetType().GetProperty("Filename").GetValue(asset,null));
            var ch = asset.GetType().GetProperty("Children");
            Console.WriteLine("Children prop: " + (ch==null?"none":ch.PropertyType.FullName));
        }
        return 0;
    }
}
