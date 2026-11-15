using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization.Formatters.Binary;

public class Mutate {
    const string DIR = @"C:\Program Files (x86)\Extron\GCP";
    static Assembly Resolve(object s, ResolveEventArgs e) {
        string n = e.Name.Split(',')[0];
        string p = Path.Combine(DIR, n + ".dll");
        return File.Exists(p) ? Assembly.LoadFrom(p) : null;
    }
    static FieldInfo Fld(object o, string name) {
        for (Type t = o.GetType(); t != null; t = t.BaseType) {
            var f = t.GetField(name, BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly);
            if (f != null) return f;
        }
        throw new Exception("no field " + name + " on " + o.GetType().FullName);
    }
    static object Get(object o, string n) { return Fld(o, n).GetValue(o); }
    static void Set(object o, string n, object v) { Fld(o, n).SetValue(o, v); }
    static object Prop(object o, string n) { return o.GetType().GetProperty(n).GetValue(o, null); }

    static object Load(string path) {
        byte[] raw = File.ReadAllBytes(path);
        Stream s = new MemoryStream(raw);
        if (raw.Length>1 && raw[0]==0x1f && raw[1]==0x8b) s = new GZipStream(s, CompressionMode.Decompress);
        return new BinaryFormatter().Deserialize(s);
    }
    static void Save(object asset, string path) {
        using (var fs = File.Create(path))
        using (var gz = new GZipStream(fs, CompressionMode.Compress))
            new BinaryFormatter().Serialize(gz, asset);
    }
    static object CloneDetached(object o) {
        object parent = Get(o, "_parentAsset");
        Set(o, "_parentAsset", null);
        object copy;
        using (var ms = new MemoryStream()) {
            var bf = new BinaryFormatter();
            bf.Serialize(ms, o);
            ms.Position = 0;
            copy = bf.Deserialize(ms);
        }
        Set(o, "_parentAsset", parent);
        return copy;
    }
    static List<object> Res(object asset) {
        var l = new List<object>();
        foreach (object r in (IEnumerable)Prop(asset, "Manifest")) l.Add(r);
        return l;
    }
    static object ByExt(object asset, string ext) {
        foreach (object r in Res(asset)) {
            string k = (string)Prop(r, "Key");
            if (k != null && k.EndsWith(ext)) return r;
        }
        throw new Exception("no resource ending " + ext);
    }
    static IDictionary Dict(object asset) { return (IDictionary)Prop(asset, "ResourceHashDict"); }

    static FieldInfo CollField(object a, bool wantBase) {
        for (Type t = a.GetType(); t != null; t = t.BaseType) {
            var fi = t.GetField("_internalChildCollection", BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly);
            if (fi == null) continue;
            bool isBase = (t.Name == "AssetBase" && !t.IsGenericType);
            if (isBase == wantBase) return fi;
        }
        return null;
    }
    // the collection that actually holds this asset's children
    static IList Coll(object a) {
        var g = CollField(a, false);
        if (g != null) { object v = g.GetValue(a); if (v != null) return (IList)v; }
        var b = CollField(a, true);
        if (b != null) { object v = b.GetValue(a); if (v != null) return (IList)v; }
        throw new Exception("no non-null child collection on " + a.GetType().Name);
    }
    static object NewResource(object proto, string key, byte[] content, string name) {
        object r = CloneDetached(proto);
        Set(r, "_key", key);
        Set(r, "_content", content);
        Set(r, "_name", name);
        Set(r, "_defaultName", name);
        Set(r, "_guid", Guid.NewGuid());
        return r;
    }
    static byte[] Flip(byte[] c) { byte[] n = (byte[])c.Clone(); n[n.Length-1] ^= 0x20; return n; }

    public static int Main(string[] args) {
        AppDomain.CurrentDomain.AssemblyResolve += Resolve;
        string src = args[0], mut = args[1], dst = args[2];
        object a = Load(src);
        object py = ByExt(a, ".py"), pdf = ByExt(a, ".pdf");
        IDictionary d = Dict(a);
        object man = Prop(a, "Manifest");
        switch (mut) {
        case "control": break;
        case "py_bytes": Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "pdf_bytes": Set(pdf, "_content", Flip((byte[])Get(pdf, "_content"))); break;
        case "drop_pdf_hash": d.Remove((string)Prop(pdf, "Key")); break;
        case "drop_py_hash": d.Remove((string)Prop(py, "Key")); break;
        case "null_hash_value": d[(string)Prop(py,"Key")] = null; break;
        case "null_key": Set(py, "_key", null); break;
        case "content_not_bytes": Set(py, "_content", "I am a string, not a byte array"); break;
        case "content_null": Set(py, "_content", null); break;
        case "case_key": {
            string k = (string)Prop(py, "Key"); object v = d[k]; d.Remove(k); d[k.ToUpperInvariant()] = v; break; }
        case "dict_null": Set(a, "_resourceHashDict", null); break;
        case "filename_eir":
            Set(a, "_filename", "totally_bogus.eir");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "filename_eir_only": Set(a, "_filename", "totally_bogus.eir"); break;
        case "filename_seir":
            Set(a, "_filename", "weirdname_seir");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "filename_pkp_badpy":
            Set(a, "_filename", "totally_bogus.pkp");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "filename_null":
            Set(a, "_filename", null);
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "filename_eir_zwj":
            Set(a, "_filename", "totally_bogus.eir\u200d");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "extra_resource":
            Coll(man).Add(NewResource(py, "intruder.py", new byte[]{1,2,3}, "intruder.py")); break;
        case "nested_resource": {
            // a sub-asset under Manifest, planted in the shadowed base-class
            // collection (the generic one is typed OC<IResourceAsset> and will
            // not accept a folder asset).
            object sub = CloneDetached(man);
            Set(sub, "_name", "SubFolder"); Set(sub, "_defaultName", "SubFolder"); Set(sub, "_guid", Guid.NewGuid());
            Coll(sub).Clear();
            Coll(sub).Add(NewResource(py, "nested.py", new byte[]{9,9,9}, "nested.py"));
            var bfn = CollField(man, true);
            IList holder = (IList)Activator.CreateInstance(bfn.FieldType);
            holder.Add(sub);
            bfn.SetValue(man, holder);
            break; }
        case "no_manifest": Coll(a).Remove(man); break;
        case "two_manifests": {
            object m2 = CloneDetached(man);
            Set(m2, "_name", "Manifest"); Set(m2, "_defaultName", "Manifest"); Set(m2, "_guid", Guid.NewGuid());
            Coll(m2).Clear();
            Coll(m2).Add(NewResource(py, "second.py", new byte[]{7,7,7}, "second.py"));
            Coll(a).Add(m2); break; }
        case "empty_manifest": Coll(man).Clear(); break;
        case "orphan_key": d["ghost.py"] = new byte[32]; break;
        case "null_resource": Coll(man).Add(null); break;
        case "base_only": {
            var bfo = CollField(man, true);
            var gfo = CollField(man, false);
            IList gen = (IList)gfo.GetValue(man);
            IList good = (IList)Activator.CreateInstance(bfo.FieldType);
            foreach (object r in gen) good.Add(r);
            bfo.SetValue(man, good);
            gfo.SetValue(man, null);
            break; }
        case "py_bad_pdf_missing":
            Set(py, "_content", Flip((byte[])Get(py, "_content")));
            d.Remove((string)Prop(pdf, "Key")); break;
        case "pdf_bad_py_missing":
            Set(pdf, "_content", Flip((byte[])Get(pdf, "_content")));
            d.Remove((string)Prop(py, "Key")); break;
        case "manifest_name_null":
            Set(man, "_name", null);
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "manifest_renamed":
            Set(man, "_name", "NotManifest");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "manifest_case":
            Set(man, "_name", "manifest");
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "manifest_names_both_gone":
            Set(man, "_name", null); Set(man, "_defaultName", null);
            Set(py, "_content", Flip((byte[])Get(py, "_content"))); break;
        case "show":
            Console.WriteLine("manifest _name=" + (Get(man,"_name") ?? "<null>") +
                              " _defaultName=" + (Get(man,"_defaultName") ?? "<null>"));
            return 0;
        case "split_colls": {
            // good resources stay in the generic collection; a bogus resource is
            // planted in the SHADOWED base-class AssetBase._internalChildCollection,
            // which is null in every shipping file.
            var bf = CollField(man, true);
            IList shadow = (IList)Activator.CreateInstance(bf.FieldType);
            shadow.Add(NewResource(py, "shadow.py", new byte[]{4,4,4}, "shadow.py"));
            bf.SetValue(man, shadow);
            break; }
        case "swap_colls": {
            // mirror image: the good resources move to the base-class field and a
            // single bogus resource is left in the generic one.
            var bf2 = CollField(man, true);
            var gf2 = CollField(man, false);
            IList gen2 = (IList)gf2.GetValue(man);
            IList good = (IList)Activator.CreateInstance(bf2.FieldType);
            foreach (object r in gen2) good.Add(r);
            bf2.SetValue(man, good);
            IList bogus = (IList)Activator.CreateInstance(gf2.FieldType);
            bogus.Add(NewResource(py, "swapped.py", new byte[]{5,5,5}, "swapped.py"));
            gf2.SetValue(man, bogus);
            break; }
        default: throw new Exception("unknown mutation " + mut);
        }
        Save(a, dst);
        Console.WriteLine("wrote " + mut);
        return 0;
    }
}
