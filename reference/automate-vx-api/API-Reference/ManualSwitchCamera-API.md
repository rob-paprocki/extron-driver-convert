Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ManualSwitchCamera-API.htm

# ManualSwitchCamera API

The **ManualSwitchCamera** API is used to switch to a particular camera output on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ManualSwitchCamera

## Parameters

**Parameter Content Type**: Application/JSON

POST ManualSwitchCamera Parameters

 

Name

Description

address

**Required.** Integer (body JSON) that sets the camera output that the Automate VX system will change to upon issuing this API call. Valid values are 1 through 255.

Body JSON Formatting

```
{    "address": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"address\":\"[value]\"}" https://[Server URL]:4443/api/ManualSwitchCamera
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"address\":\"4\"}" https://123.456.789.000:4443/api/ManualSwitchCamera
```

Request URL

```
https://[ServerURL]:4443/api/ManualSwitchCamera
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully switched shot to [value]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```
