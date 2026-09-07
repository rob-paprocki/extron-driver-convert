Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Attribute_Tables/Service_Addresses/Device.htm

Tesira Software Help

Click here to see this page in full context

#### TTP Attribute Table | Generate command strings with: Tesira Command String Calculator

# Device

The DEVICE Instance Tag is case sensitive and must be in capital letters. It is used to send Device Services instructions or Device Attributes and Commands.

## Device Services

The Following table summarizes DEVICE Service Codes. Due to the nature of the service being requested they do not require specific commands (get, set, etc)

Some service commands are specific to the connected device, such as 'reboot'. Other Service commands are design file specific, such as saving or recalling a Preset.

Each element of the command instruction is delimited by one or more spaces. The commands are case sensitive and upper and lower case characters are used.

Instance_Tag Service [Index] [Value] LF

* Instance Tag: Is always required.

* Service: Is always required.

* [Index]: Is shown in [Brackets] and may be required depending on the Attribute being referenced. If not required it should not be defined. Depending on the Attribute, it can be made up of one or more indexes.

* [Value]: Is shown in [Brackets] and may be required depending on the Command or Attribute being referenced. If not be required it should not be defined. The Value would not normally have spaces, if it does it can be defined in "double quotes". It can also be a numerical value.

* LF: A Line feed or Carriage Return is used to define the end of the command.

For additional information on individual elements of a TTP string please review the TTP Syntax page.

The TTP string is structured in the following order:

Instance_Tag Service [Index] [Value] LF

* Instance Tag: Is always required.

* Service: Is always required.

* [Index]: Is shown in [Brackets] as may be required depending on the Attribute being referenced. If not required it should not be defined. Depending on the Attribute, it can be made up of one or more indexes.

* [Value]: Is shown in [Brackets] as may be required depending on the Command or Attribute being referenced. If not be required it should not be defined. The Value would not normally have spaces, if it does it can be defined in "double quotes". It can also be a numerical value.

* LF: A Line feed or Carriage Return is used to define the end of the command.

For additional information on individual elements of a TTP string please review the TTP Syntax page.

| Service Code | Parameters |

| clearEventLogs |  |

| clearLogs |  |

| clearWorkplace |  |

| defaultLogConfig |  |

| deleteConfigData |  |

| getLocalCopyOfFile | blockID, fileID, filePath |

| injectDanteLicenseKey | licenseCertificate, oemCertificate |

| manualFailover | uint32_t unitId |

| reboot |  |

| rebootERD | HostnameList hostnames, HostnameList failedDevices |

| recallPreset | PresetId id |

| recallPresetByName | presetName |

| recallPresetShowFailures | PresetId id, HostnameList failedDevices |

| resetWebServerCredentials | applicationName |

| restoreERDToFactoryDefaults | HostnameList hostnames, HostnameList failedDevices |

| savePreset | PresetId id |

| savePresetByName | presetName |

| sleep |  |

| startAudio |  |

| startMedia |  |

| startPartitionAudio | PartitionID partID |

| startPartitionMedia | PartitionID partID |

| stopAudio |  |

| stopMedia |  |

| stopPartitionAudio | PartitionID partID |

| stopPartitionMedia | PartitionID partID |

| syncERDFirmware | HostnameList hostnames, HostnameList failedDevices |

| verifyDanteLicenseKey | bool valid |

| wake |  |

### Examples

Reboot the connected device. Result: DEVICE reboot

| Instance Tag | Service |

| DEVICE | reboot |

Start audio on a device. Result: DEVICE startAudio

| Instance Tag | Service |

| DEVICE | startAudio |

Reboot multiple expander devices. Result:

* If all expander are discoverable and accept the reboot command: +OK "failedDevices":[ ]

* If all but the EX-IN expander are discoverable and accept the reboot command: +OK "failedDevices":["EX-IN-0001"]

| Instance Tag | Service |

| DEVICE | rebootERD ["EX-OUT-0000", "EX-IN-0001", EX-AEC-0001] |

## Device Attributes and Commands

Additionally there are a number of DEVICE Instance Tag command Attributes. These would reference the device that has the current active Serial, SSH or TELNET session.

Please refer to the TTP section of the Tesira Software System Control Overview page for more details on the controlling Tesira devices using the TTP protocol.

Each element of the command instruction is delimited by one or more spaces. The commands are case sensitive and upper and lower case characters are used.

The TTP string to adjust a DSP object attribute is structured in the following order:

Instance_Tag Command Attribute [Index] [Value] LF

* Instance Tag: Is always required.

* Command: Is always required.

* Attribute: Is always required.

* [Index]: Is shown in [Brackets] and may be required depending on the Attribute being referenced. If not required it should not be defined. Depending on the Attribute, it can be made up of one or more indexes.

* [Value]: Is shown in [Brackets] and may be required depending on the Command or Attribute being referenced. If not be required it should not be defined. The Value would not normally have spaces, if it does it can be defined in "double quotes". It can also be a numerical value.

* LF: A Line feed or Carriage Return is used to define the end of the command.

For additional information on individual elements of a TTP string please review the TTP Syntax page.

| Attribute | Attribute Code | Command | Indexes | Value Range |

| Active Faults | activeFaultList | get |  |  |

| AVB Peer Delay Threshold | avbPDelayThreshold | get / set / increment / decrement |  | 0 - 2147483647 |

| Block Introspection | blockInfo | get |  | The returned information is variable and dependent on the specific block being queried. For example, channelInfo may be absent for special blocks or contain numChannels (0 if unconfigured), numAVChannels (TesiraLUX I/O only), or numInputs / numOutputs. |

| Change client log level | clientLogLevel | get / set | log client name | none, emergency, critical, error, warning, notice, info, debug |

| Retrieve Dante information | danteInfo | get |  |  |

| Retrieve device information | deviceInfo | get |  |  |

| Discovered Servers | discoveredServers | get |  |  |

| DNS Config | dnsConfig | get / set |  |  |

| DNS Status | dnsStatus | get |  |  |

| Disable/Enable duplicate suppression on engineering log | enableDuplicateSuppression | get / set / toggle |  | false, true |

| Remote Device AVB Peer Delay Threshold | ERDavbPDelayThreshold | get / set / increment / decrement | hostname | 0 - 2147483647 |

| Change facility log level | facilityLogLevel | get / set | log facility name | none, emergency, critical, error, warning, notice, info, debug |

| Host Name | hostname | get / set |  |  |

| Resolver Hosts Table | hostTable | get / set |  |  |

| HTTPS should be enabled | httpsEnabled | get / set / toggle |  | false, true |

| IGMP should be enabled | igmpEnabled | get / set / toggle |  | false, true |

| Network Interface Config | ipConfig | get / set | interface name | control |

| Network Interface Status | ipStatus | get | interface name | control |

| Known Redundant Device States | knownRedundantDeviceStates | get / subscribe / unsubscribe |  |  |

| mDNS Enabled | mDNSEnabled | get / set / toggle |  | false, true |

| Retrieve MSRP Information | msrpInfo | get |  |  |

| Retrieve Network Port Information | networkPortInfo | get |  |  |

| Network Port Mode | networkPortMode | get / set |  | PORT_MODE_SEPARATE, PORT_MODE_REDUNDANT, PORT_MODE_DAISY_CHAIN |

| Network Status | networkStatus | get |  |  |

| Disable/Enable POE on a port | poeEnabled | get / set / toggle | port name | false, true |

| Retrieve POE Information | poeInfo | get |  |  |

| Product Revision | productRevision | get |  |  |

| Retrieve gPTP Information | ptpInfo | get |  |  |

| RSTP should be enabled | rstpEnabled | get / set / toggle |  | false, true |

| Serial Number | serialNumber | get |  |  |

| ssh should be disabled | sshDisabled | get / set / toggle |  | false, true |

| telnet should be disabled | telnetDisabled | get / set / toggle |  | false, true |

| Firmware Version | version | get |  |  |

| VoIP2 Network Status | VoIP2NetworkStatus | get | card slot, (unused) |  |

*Note: Attempting to modify the Host Name via this command will result in an error message if the system is currently configured. A reset of the device is required to make changes to the Host Name first (DEVICE deleteConfigData command or a Reset Device via Device Maintenance). In the scenario where a system is configured and is Reset to change the Host Name, the Equipment Table will need to be re-opened and updated to reflect the new details, and the configuration re-sent to the system.

| Instance Tag | Command | Attribute Code |

| DEVICE | get | serialNumber |

#### Example

DEVICE get serialNumber   +OK "value":"01842224"

#### Example

DEVICE get networkStatus   +OK "value":{"schemaVersion":2 "hostname":"TesiraServer91" "defaultGatewayStatus":"0.0.0.0" "networkInterfaceStatusWithName":[{"interfaceId":"control" "networkInterfaceStatus":{"macAddress":"00:90:5e:13:3b:27" "linkStatus":LINK_1_GB "addressSource":STATIC "ip":"10.30.150.62" "netmask":"255.255.0.0" "dhcpLeaseObtainedDate":"" "dhcpLeaseExpiresDate":"" "gateway":"0.0.0.0"}}] "dnsStatus":{"primaryDNSServer":"0.0.0.0" "secondaryDNSServer":"0.0.0.0" "domainName":""} "mDNSEnabled":true" telnetDisabled":false}

## ipConfig Commands

The ipConfig command can set the DHCP state, IP address, Subnet mask and Gateway on a Tesira Server, Server IO and TesiraFORTÉ device. Only values that need to be changed are required to be specified.

To get the IP configuration of a device:

| Instance Tag | Command | Attribute Code | Index |

| DEVICE | get | ipConfig | control |

#### Example

DEVICE get ipConfig control +OK "value":{"autoIPEnabled":true "ip":"" "netmask":"" "gateway":""}

#### Example - Set a device to not use DHCP and with an IP address of 192.168.1.210, a subnet of 255.255.255.0 and no gateway

DEVICE set ipConfig control {"autoIPEnabled":false "ip":"192.168.1.210" "netmask":"255.255.255.0" "gateway":"0.0.0.0"}

#### Example - Set a device that is using a fixed IP address to use DHCP

DEVICE set ipConfig control {"autoIPEnabled":true }

#### Example - Change a device IP address to a new address in the same subnet (this example moves a device from 192.168.1.210 to 192.168.1.110)

DEVICE set ipConfig control { "ip":"192.168.1.110" }

#### Example - Retrieve port status information for all ports

DEVICE get networkPortInfo

+OK "networkPortInfo":[{"name":"P5" "linkUp":true "speed":1000 "statistics":[{"t":RX_PACKETS "v":2129} {"t":TX_PACKETS "v":1922} {"t":RX_MULTICAST_PACKETS "v":18101} {"t":TX_MULTICAST_PACKETS "v":9549} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":1} {"t":PORT_DOWN_COUNTER "v":0}] "info":[{"t":LLDP_HOSTNAME "v":"ICX6450-48P Switch"} {"t":LLDP_PORTNAME "v":"P5"}] "portRole":PORT_ROLE_DANTE_ONLY} {"name":"P4" "linkUp":true "speed":100 "statistics":[{"t":RX_PACKETS "v":524} {"t":TX_PACKETS "v":528} {"t":RX_MULTICAST_PACKETS "v":1029} {"t":TX_MULTICAST_PACKETS "v":25477} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":1} {"t":PORT_DOWN_COUNTER "v":0}] "info":[] "portRole":PORT_ROLE_DANTE_ONLY} {"name":"P3" "linkUp":true "speed":100 "statistics":[{"t":RX_PACKETS "v":473} {"t":TX_PACKETS "v":502} {"t":RX_MULTICAST_PACKETS "v":1020} {"t":TX_MULTICAST_PACKETS "v":25486} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":1} {"t":PORT_DOWN_COUNTER "v":0}] "info":[] "portRole":PORT_ROLE_DANTE_ONLY} {"name":"P2" "linkUp":false "speed":0 "statistics":[{"t":RX_PACKETS "v":0} {"t":TX_PACKETS "v":0} {"t":RX_MULTICAST_PACKETS "v":0} {"t":TX_MULTICAST_PACKETS "v":0} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":0} {"t":PORT_DOWN_COUNTER "v":0}] "info":[] "portRole":PORT_ROLE_DANTE_ONLY} {"name":"P1" "linkUp":true "speed":1000 "statistics":[{"t":RX_PACKETS "v":490} {"t":TX_PACKETS "v":612} {"t":RX_MULTICAST_PACKETS "v":20761} {"t":TX_MULTICAST_PACKETS "v":15708} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":1} {"t":PORT_DOWN_COUNTER "v":0}] "info":[{"t":LLDP_DESCRIPTION "v":"ExtremeXOS (X440-24p) version 16.2.2.4 16.2.2.4-patch1-3 by release-manager on Fri Feb 17 08:00:10 EST 2017"} {"t":LLDP_PORTNAME "v":"P1"}] "portRole":PORT_ROLE_AVB_ONLY} {"name":"control" "linkUp":true "speed":1000 "statistics":[{"t":RX_PACKETS "v":0} {"t":TX_PACKETS "v":13} {"t":RX_MULTICAST_PACKETS "v":3173} {"t":TX_MULTICAST_PACKETS "v":44336} {"t":RX_BAD_PACKETS "v":0} {"t":PORT_UP_COUNTER "v":0} {"t":PORT_DOWN_COUNTER "v":0}] "info":[] "portRole":INVALID PortRoleType}]

#### Example - Get ptp information for all ports

DEVICE get ptpInfo

+OK "gptpInfo":[{"GMID":{"id":[120 69 1 255 254 5 86 102]} "thisSystemIsGM":false "stepsRemoved":4 "priority":{"priority1":246 "priority2":248} "neighborPropDelayThreshholdNs":1200 "portInfo":[{"name":"P5" "asCapable":false "locked":false "role":PTP_PORT_DISABLED "neighborPropDelayNs":0} {"name":"P4" "asCapable":false "locked":false "role":PTP_PORT_DISABLED "neighborPropDelayNs":0} {"name":"P3" "asCapable":false "locked":false "role":PTP_PORT_DISABLED "neighborPropDelayNs":0} {"name":"P2" "asCapable":false "locked":false "role":PTP_PORT_DISABLED "neighborPropDelayNs":0} {"name":"P1" "asCapable":true "locked":true "role":PTP_PORT_SLAVE "neighborPropDelayNs":555} {"name":"control" "asCapable":true "locked":true "role":PTP_PORT_MASTER "neighborPropDelayNs":12}]}]

#### Example - Enable or disable POE on the specified port

DEVICE set poeEnabled "P2" true

+OK

DEVICE set poeEnabled "P2" false

+OK

DEVICE get poeEnabled "P2"

+OK "enabled":true

DEVICE get msrpInfo

+OK "msrpInfo":[{"portNames":["P5" "P4" "P3" "P2" "P1" "control"] "streamInfo":[]}]

#### Example - Get Dante information for all ports

DEVICE get danteInfo

+OK "danteInfo":{"revs":{"danteAPIVersion_major":4 "danteAPIVersion_minor":2 "danteAPIVersion_bugfix":2 "ubootVersion_major":0 "ubootVersion_minor":0 "ubootVersion_bugfix":0 "biampVersion_major":1 "biampVersion_minor":3 "biampVersion_dot":0 "biampVersion_build":1} "netCfg":{"hostname":"TesiraConnect04067397-DAN" "primaryInterface":{"autoConfigure":true "ipAddress":"192.168.1.226" "netMask":"255.255.255.0" "DNSServer":"0.0.0.0" "defaultGateway":"192.168.1.200"} "secondaryInterface":{"autoConfigure":true "ipAddress":"192.168.1.226" "netMask":"255.255.255.0" "DNSServer":"0.0.0.0" "defaultGateway":"192.168.1.200"}} "allNetStatus":{"primaryStatus":{"macAddress":"78:45:01:07:df:7e" "linkSpeedInMbS":1000} "secondaryStatus":{"macAddress":"" "linkSpeedInMbS":0}} "preferredDanteNetworkClockSource":true "networkClockSlaveOnly":false "networkLatencyInMicroseconds":0 "chInfos":[{"name":"" "number":0 "txrx":TX "faultOnInactive":false} {"name":"" "number":1 "txrx":TX "faultOnInactive":false} {"name":"" "number":2 "txrx":TX "faultOnInactive":false} {"name":"" "number":3 "txrx":TX "faultOnInactive":false} {"name":"" "number":4 "txrx":TX "faultOnInactive":false} {"name":"" "number":5 "txrx":TX "faultOnInactive":false} {"name":"" "number":6 "txrx":TX "faultOnInactive":false} {"name":"" "number":7 "txrx":TX "faultOnInactive":false} {"name":"" "number":8 "txrx":TX "faultOnInactive":false} {"name":"" "number":9 "txrx":TX "faultOnInactive":false} {"name":"" "number":10 "txrx":TX "faultOnInactive":false} {"name":"" "number":11 "txrx":TX "faultOnInactive":false} {"name":"" "number":12 "txrx":TX "faultOnInactive":false} {"name":"" "number":13 "txrx":TX "faultOnInactive":false} {"name":"" "number":14 "txrx":TX "faultOnInactive":false} {"name":"" "number":15 "txrx":TX "faultOnInactive":false} {"name":"" "number":16 "txrx":TX "faultOnInactive":false} {"name":"" "number":17 "txrx":TX "faultOnInactive":false} {"name":"" "number":18 "txrx":TX "faultOnInactive":false} {"name":"" "number":19 "txrx":TX "faultOnInactive":false} {"name":"" "number":20 "txrx":TX "faultOnInactive":false} {"name":"" "number":21 "txrx":TX "faultOnInactive":false} {"name":"" "number":22 "txrx":TX "faultOnInactive":false} {"name":"" "number":23 "txrx":TX "faultOnInactive":false} {"name":"" "number":24 "txrx":TX "faultOnInactive":false} {"name":"" "number":25 "txrx":TX "faultOnInactive":false} {"name":"" "number":26 "txrx":TX "faultOnInactive":false} {"name":"" "number":27 "txrx":TX "faultOnInactive":false} {"name":"" "number":28 "txrx":TX "faultOnInactive":false} {"name":"" "number":29 "txrx":TX "faultOnInactive":false} {"name":"" "number":30 "txrx":TX "faultOnInactive":false} {"name":"" "number":31 "txrx":TX "faultOnInactive":false} {"name":"01" "number":0 "txrx":RX "faultOnInactive":false} {"name":"02" "number":1 "txrx":RX "faultOnInactive":false} {"name":"03" "number":2 "txrx":RX "faultOnInactive":false} {"name":"04" "number":3 "txrx":RX "faultOnInactive":false} {"name":"05" "number":4 "txrx":RX "faultOnInactive":false} {"name":"06" "number":5 "txrx":RX "faultOnInactive":false} {"name":"07" "number":6 "txrx":RX "faultOnInactive":false} {"name":"08" "number":7 "txrx":RX "faultOnInactive":false} {"name":"09" "number":8 "txrx":RX "faultOnInactive":false} {"name":"10" "number":9 "txrx":RX "faultOnInactive":false} {"name":"11" "number":10 "txrx":RX "faultOnInactive":false} {"name":"12" "number":11 "txrx":RX "faultOnInactive":false} {"name":"13" "number":12 "txrx":RX "faultOnInactive":false} {"name":"14" "number":13 "txrx":RX "faultOnInactive":false} {"name":"15" "number":14 "txrx":RX "faultOnInactive":false} {"name":"16" "number":15 "txrx":RX "faultOnInactive":false} {"name":"17" "number":16 "txrx":RX "faultOnInactive":false} {"name":"18" "number":17 "txrx":RX "faultOnInactive":false} {"name":"19" "number":18 "txrx":RX "faultOnInactive":false} {"name":"20" "number":19 "txrx":RX "faultOnInactive":false} {"name":"21" "number":20 "txrx":RX "faultOnInactive":false} {"name":"22" "number":21 "txrx":RX "faultOnInactive":false} {"name":"23" "number":22 "txrx":RX "faultOnInactive":false} {"name":"24" "number":23 "txrx":RX "faultOnInactive":false} {"name":"25" "number":24 "txrx":RX "faultOnInactive":false} {"name":"26" "number":25 "txrx":RX "faultOnInactive":false} {"name":"27" "number":26 "txrx":RX "faultOnInactive":false} {"name":"28" "number":27 "txrx":RX "faultOnInactive":false} {"name":"29" "number":28 "txrx":RX "faultOnInactive":false} {"name":"30" "number":29 "txrx":RX "faultOnInactive":false} {"name":"31" "number":30 "txrx":RX "faultOnInactive":false} {"name":"32" "number":31 "txrx":RX "faultOnInactive":false}]}
