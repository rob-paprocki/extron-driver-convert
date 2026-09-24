# Finding 05 — the Samsung cross-vendor result

One device (Samsung QN43LS03DAFXZA), five drivers, two vendors. This is the
sample that turns speculation into measurement — with two independent encodings
you can finally separate *"this is how Extron encodes Samsung"* from
*"this is Samsung's protocol"*.

From a 17-agent analysis with adversarial per-claim verification:
**53 confirmed, 7 overstated, 7 refuted.**

## The headline, stated precisely

For **6 of the 8** capability families the Extron ControlScript module implements
(Power, Volume, AudioMute, Input, Keypad, MenuNavigation — 29 discrete values
plus parameterised Volume), the Crestron Serial driver produces the **identical
7-byte frame, checksum included**.

Verified by two independent re-implementations of both framing paths — Extron's
`build()` (`pack('6B', 0x08, 0x22, ...)` plus `(~sum & 0xFF) + 1`) and Crestron's
`SetVolume → Packet → PacketWithCheckSum` template chain with the Twos-complement
`CheckSum` transform. Both matched on every value:

```
Keypad 6    = 08 22 0d 00 00 0a bf
Volume 50   = 08 22 01 00 00 32 a3
```

Feedback matches too: Extron's four `AddMatchString` regexes and Crestron's four
terminal `BinaryPacket` decoders recognise the same 12-byte response preamble and
the same data-byte alphabets.

> The "50% of the union of families is shared" figure from an earlier pass is a
> methodology artifact. **Quote the like-for-like 6/8, not that.**

## The most telling agreement is a shared bug workaround

Crestron's `SetPower` template would encode "on" as `00 00 00 02`. But Rule
`SendPowerOn` intercepts it and sends a fixed literal `0D 00 00 02` instead.
Extron sends **the same** `0D 00 00 02`, and the Extron script says why:

> `Using Key Gen command as normal Power On command does not work at the time.`
> `Requires IP remote setting enabled.`

Two teams, 17 months apart, hit the same firmware defect and encoded the same
detour. Both also carry two response decoders — one with the echoed `03 0C F1`
preamble and one without — for the same device timing quirk.

**That is evidence that what both drivers encode is the device's actual
behaviour, not merely its documentation.** It is the strongest argument that a
protocol-level intermediate representation is describing something real.

## Correction: the `.pkp` carries TWO scripts, not one

The Samsung `.pkp` contains a serial driver *and* an ethernet driver
(StreamResourceAsset objects 125 and 126). The ethernet one subclasses
`Extron2.HTTPDriver` and speaks **JSON-RPC 2.0 over HTTPS to port 1516**, opening
with `createAccessToken`, then `powerControl`, `directVolumeControl`,
`muteControl`, `inputSourceControl`, `channelUpDnControl`, `remoteKeyControl`,
`multiviewControl`, `pictureSizeControl`.

Crestron's IP driver targets **the same port with the same handshake**, and 8 of
its 16 methods carry exactly Extron's names.

This **refutes** the earlier working assumption that "the wire encoding never
changes across transports". Extron's own package exhibits precisely the
serial-binary vs IP-JSON-RPC split. One device is genuinely N drivers, not one
driver with N transport bindings — and the IR must model that.

## The Crestron DLL is not code in any meaningful sense

Two TypeDefs, **one MethodDef**, zero fields, and a 22-byte constructor whose
entire body is `ldstr <resource name>` plus a base-constructor call into
`LegacyWrappers.DisplayWrapperSerial` / `DisplayWrapperTcp`.

The driver JSON is a CLR ManifestResource (46,164 / 80,889 bytes with BOM).
**No decompiler needed** — read the CLR header's resource RVA, skip the 4-byte
length prefix, parse.

## Ingestion is a partial evaluator, not a field mapper

The Crestron JSON is a rule-engine DSL. Getting this wrong produces drivers that
look right and are wrong:

- Resolve `Template` chains **bottom-up**, running each level's `Transformations`
  before substituting into the parent. The checksum lives on the leaf
  `PacketWithCheckSum`, not on `SetVolume`. Get this backwards and every
  checksum byte is wrong.
- Apply send-rewriting `Rules` **before** recording what reaches the wire, or you
  record the dead `00 00 00 02` power-on branch as live.
- Response routing is keyed on **the outstanding command name**, not payload
  shape — six poll responses differ by a single byte at a fixed offset.
- Honour `Processing: Stop` per node; accept nodes with no `Type` as valid leaves.
- Treat `{:hex}` as a literal-bytes sigil, `{{`/`}}` as escaped braces,
  `{_Name_}` as the CommandIds/UserAttributes namespace.

**Build the interpreter to fail loudly on any unknown `Type`.** The vocabulary is
not even shared between this device's own two files, and will grow with every
sample.

## Where the vendors differ, and why the sorting matters more than the count

- **Protocol choice** — ChannelStep is a genuine wire divergence: Extron uses the
  dedicated `0x03` family, Crestron emulates a remote key `0D 00 00 12/10`. Only
  a live capture says which the panel honours.
- **Coverage** — Crestron Serial adds 8 families Extron lacks (direct channel,
  apps, transport keys, colour keys, Guide, Art Mode `0b 0b 0e`, Ambient
  `0b 0b 10`). Extron alone has AspectRatio "Custom" `0x0B` and, on IP,
  `pictureSizeControl`.
- **Policy** — warm-up 5000 ms / cool-down 3000 ms with send-blocking rules vs
  Extron's power gate and 3-second post-set poll holdoff; 4000 ms vs 3 s polling;
  Crestron hardcodes TLS verification off, Extron exposes an "SSL Verify Mode"
  parameter.

## The limit of this result

One device, one manufacturer, **published protocol**. What it proves is that
*when a protocol is documented, independent vendor encodings converge on it — and
on its bugs.* It says nothing yet about undocumented or reverse-engineered
devices, where the two vendors' guesses would have no reason to agree.

## Status

Three dimensions (`crestron-serial-vs-ip`, `extron-samsung`, `crestron-emission`)
returned stubs or crashed and are being re-run. The synthesist worked around the
first two by doing the analysis directly, which is why the corrections above are
sound; `crestron-emission` remains the real gap.
*(`crestron-emission` closed by finding 06 — "Emitting a Crestron driver:
strategy A works, and was demonstrated," executed end-to-end against the real
Samsung Serial DLL.)*
