Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopAutoSwitch.htm

# StopAutoSwitch API

The **StopAutoSwitch** API is used to stop the AutoSwitching functionality on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StopAutoSwitch

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

[Copy](javascript:void\(0\);)

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/StopAutoSwitch
```

[Copy](javascript:void\(0\);)

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/StopAutoSwitch
```

[Copy](javascript:void\(0\);)

Request URL

```
https://[ServerURL]:4443/api/StopAutoSwitch
```

Response Messages

 

Result

Message

Success

[Copy](javascript:void\(0\);)

```
{    "status": "OK",    "message": "AutoSwitching Stopped Successfully"}
```

Error

[Copy](javascript:void\(0\);)

```
{    "status": "Error",    "err": "AutoSwitching Failed to Stop"}
```

©2026 Crestron Electronics, Inc.
