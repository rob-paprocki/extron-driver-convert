using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Reflection;

public class Dir {
    const string DIR = @"C:\Program Files (x86)\Extron\GCP";
    static Assembly Resolve(object s, ResolveEventArgs e) {
        string n = e.Name.Split(',')[0];
        string p = Path.Combine(DIR, n + ".dll");
        return File.Exists(p) ? Assembly.LoadFrom(p) : null;
    }
    public static int Main(string[] args) {
        AppDomain.CurrentDomain.AssemblyResolve += Resolve;
        Assembly a = Assembly.LoadFrom(Path.Combine(DIR, "Extron.Configuration.Drivers.dll"));
        Type t = a.GetType("Extron.Configuration.Drivers.DriverAssetValidator");
        object v = Activator.CreateInstance(t, true);
        var fi = t.GetField("a", BindingFlags.NonPublic|BindingFlags.Instance);
        object tbl = fi.GetValue(v);
        Console.WriteLine("fresh ctor guid table: " + (tbl == null ? "NULL" :
            tbl.GetType().Name + " count=" + tbl.GetType().GetProperty("Count").GetValue(tbl, null)));
        var inst = t.GetField("Instance", BindingFlags.Public|BindingFlags.Static).GetValue(null);
        object tbl2 = inst == null ? null : fi.GetValue(inst);
        Console.WriteLine("static Instance: " + (inst == null ? "NULL" : "present") + " table: " +
            (tbl2 == null ? "NULL" : tbl2.GetType().GetProperty("Count").GetValue(tbl2, null).ToString()));
        try {
            t.GetMethod("LoadDefaultFromResource").Invoke(v, null);
            object tbl3 = fi.GetValue(v);
            Console.WriteLine("after LoadDefaultFromResource: " + (tbl3 == null ? "NULL" :
                tbl3.GetType().GetProperty("Count").GetValue(tbl3, null).ToString()));
        } catch (Exception ex) {
            Console.WriteLine("LoadDefaultFromResource threw: " + (ex.InnerException ?? ex).GetType().Name + ": " + (ex.InnerException ?? ex).Message);
        }
        if (args.Length > 0) {
            var mi = t.GetMethod("ProcessDriverDirectory");
            try {
                object res = mi.Invoke(v, new object[] { args[0] });
                Console.WriteLine("ProcessDriverDirectory -> " + (res == null ? "null" : res.GetType().Name));
                if (res is IDictionary) {
                    foreach (DictionaryEntry de in (IDictionary)res)
                        Console.WriteLine("   " + de.Key + " => " + de.Value + " (" + Convert.ToInt64(de.Value) + ")");
                } else if (res is IEnumerable) {
                    foreach (object o in (IEnumerable)res) Console.WriteLine("   " + o);
                }
            } catch (Exception ex) {
                Exception e2 = ex.InnerException ?? ex;
                Console.WriteLine("ProcessDriverDirectory threw: " + e2.GetType().Name + ": " + e2.Message);
            }
        }
        return 0;
    }
}
