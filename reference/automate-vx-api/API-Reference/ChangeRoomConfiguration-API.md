Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ChangeRoomConfig-API.htm

# ChangeRoomConfiguration API

The **ChangeRoomConfiguration** API is used to change the active room configuration on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ChangeRoomConfiguration

## Parameters

**Parameter Content Type**: Application/JSON

POST ChangeRoomConfiguration Parameters

 

Name

Description

id

**Required.** Integer (body JSON) that sets the room configuration ID that the Automate VX system will change to upon issuing this API call. Valid values are 1 through 99.

[Copy](javascript:void\(0\);)

Body JSON Formatting

```
{    "id": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

[Copy](javascript:void\(0\);)

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"id\":\"[value]\"}" https://[Server URL]:4443/api/ChangeRoomConfiguration
```

[Copy](javascript:void\(0\);)

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"id\":\"16\"}" https://123.456.789.000:4443/api/ChangeRoomConfiguration
```

[Copy](javascript:void\(0\);)

Request URL

```
https://[ServerURL]:4443/api/ChangeRoomConfiguration
```

Response Messages

 

Result

Message

Success

[Copy](javascript:void\(0\);)

```
{    "status": "OK",    "message": "Changed to Room Configuration [1-99]"}OR{    "status": "OK",    "message": "Already on Room Configuration [1-99]"}
```

Error

[Copy](javascript:void\(0\);)

```
{    "status": "Error",    "err": "[Reason for error]"}
```

©2026 Crestron Electronics, Inc.
