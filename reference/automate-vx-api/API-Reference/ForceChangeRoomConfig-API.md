Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ForceChangeRoomConfig-API.htm

# ForceChangeRoomConfig API

The **ForceChangeRoomConfig** API is used to change the active room configuration on the Automate VX system even if the AutoSwitching functionality is currently active. AutoSwitching is stopped and then resumed before the API call was issued.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ForceChangeRoomConfig

## Parameters

**Parameter Content Type**: Application/JSON

POST ForceChangeRoomConfig Parameters

 

Name

Description

id

**Required.** Integer (body JSON) that sets the room configuration ID that the Automate VX system will change to upon issuing this API call. Valid values are 1 through 99.

Body JSON Formatting

```
{    "id": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"id\":\"[value]\"}" https://[Server URL]:4443/api/ForceChangeRoomConfig
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"id\":\"16\"}" https://123.456.789.000:4443/api/ForceChangeRoomConfig
```

Request URL

```
https://[ServerURL]:4443/api/ForceChangeRoomConfig
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Changed to Room Configuration [1-99]"}OR{    "status": "OK",    "message": "Already on Room Configuration [1-99]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```
