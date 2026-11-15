using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization.Formatters.Binary;

public class Harness {
    const string DIR = @"C:\Program Files (x86)\Extron\GCP";
    static HashSet<string> busy = new HashSet<string>();

    static Assembly Resolve(object s, ResolveEventArgs e) {
        string n = e.Name.Split(',')[0];
        if (!busy.Add(n)) return null;
        try {
            string p = Path.Combine(DIR, n + ".dll");
            if (File.Exists(p)) return Assembly.LoadFrom(p);
            return null;
        } finally { busy.Remove(n); }
    }

    static object Load(string path) {
        byte[] raw = File.ReadAllBytes(path);
        Stream s = new MemoryStream(raw);
        if (raw.Length > 1 && raw[0] == 0x1f && raw[1] == 0x8b)
            s = new GZipStream(s, CompressionMode.Decompress);
        var bf = new BinaryFormatter();
        return bf.Deserialize(s);
    }

    public static int Main(string[] args) {
        AppDomain.CurrentDomain.AssemblyResolve += Resolve;
        Assembly a = Assembly.LoadFrom(Path.Combine(DIR, "Extron.Configuration.Drivers.dll"));
        Type t = a.GetType("Extron.Configuration.Drivers.DriverAssetValidator");
        MethodInfo mi = t.GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static)
                         .FirstOrDefault(m => m.Name == "Validate");
        object inst = mi.IsStatic ? null : Activator.CreateInstance(t, true);
        var files = new List<string>();
        bool loadTable = false, dumpTable = false;
        foreach (string s in args) {
            if (s == "--loadtable") loadTable = true;
            else if (s == "--dumptable") { loadTable = true; dumpTable = true; }
            else files.Add(s);
        }
        if (loadTable) t.GetMethod("LoadDefaultFromResource").Invoke(inst, null);
        if (dumpTable) {
            var fi = t.GetField("a", BindingFlags.NonPublic|BindingFlags.Instance);
            IDictionary tbl = (IDictionary)fi.GetValue(inst);
            Console.WriteLine("# guid table entries: " + tbl.Count);
            foreach (DictionaryEntry de in tbl)
                Console.WriteLine(de.Key + "\t" + BitConverter.ToString((byte[])de.Value).Replace("-", "").ToLowerInvariant());
            return 0;
        }
        foreach (string f in files) {
            string res;
            try {
                object asset = Load(f);
                try {
                    object code = mi.Invoke(inst, new object[] { asset });
                    res = Convert.ToInt64(code) + " " + code;
                } catch (TargetInvocationException tie) {
                    Exception ex = tie.InnerException;
                    res = "THROW " + ex.GetType().Name + ": " + ex.Message.Replace("\r"," ").Replace("\n"," ");
                }
            } catch (Exception ex) {
                res = "LOADFAIL " + ex.GetType().Name + ": " + ex.Message.Replace("\r"," ").Replace("\n"," ");
            }
            Console.WriteLine(res + "\t" + Path.GetFileName(f));
        }
        return 0;
    }
}
