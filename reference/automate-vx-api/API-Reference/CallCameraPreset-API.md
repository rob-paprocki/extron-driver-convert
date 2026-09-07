Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CallCameraPreset-API.htm

# CallCameraPreset API

The **CallCameraPreset** API is used to switch to a particular preset for a camera output on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/CallCameraPreset

## Parameters

**Parameter Content Type**: Application/JSON

POST CallCameraPreset Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera output that contains the desired camera preset. Valid values are 1 through 255.

pre

**Required.** Integer (body JSON) that sets the preset on the selected camera output. Valid values are 1 through 255.

Body JSON Formatting

```
{    "cam": "[value]",    "pre": [value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\",\"pre\":\"[value]\"}" https://[Server URL]:4443/api/CallCameraPreset
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"4\",\"pre\":\"47\"}" https://123.456.789.000:4443/api/CallCameraPreset
```

Request URL

```
https://[ServerURL]:4443/api/CallCameraPreset
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully called preset [value] for camera [value]"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```
