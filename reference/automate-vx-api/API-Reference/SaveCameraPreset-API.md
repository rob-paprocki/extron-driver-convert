Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/SaveCameraPreset-API.htm

# SaveCameraPreset API

The **SaveCameraPreset** API is used to save a particular preset on the Automate VX system to a specified camera output.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/SaveCameraPreset

## Parameters

**Parameter Content Type**: Application/JSON

POST SaveCameraPreset Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera output that the camera preset will be saved to. Valid values are 1 through 255.

pre

**Required.** Integer (body JSON) that sets the preset on the Automate VX system. Valid values are 1 through 255.

Body JSON Formatting

```
{    "cam": "[value]",    "pre": [value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\", \"pre\":\"[value]\"}" https://[Server URL]:4443/api/SaveCameraPreset
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"4\", \"pre\":\"47\"}" https://123.456.789.000:4443/api/SaveCameraPreset
```

Request URL

```
https://[ServerURL]:4443/api/SaveCameraPreset
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully saved preset [value] for camera [value]"}
```

Error

```
{    "status": "Error",    "err": "Camera preset [value] is invalid"}
```
