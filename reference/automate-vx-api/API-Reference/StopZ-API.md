Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopZ-API.htm

# StopZ API

The **StopZ** API is used to stop a camera zooming in or out.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StopZ

## Parameters

**Parameter Content Type**: Application/JSON

POST StopZ Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera that will have its zooming stopped. Valid values are 1 through 255.

Body JSON Formatting

```
{    "cam": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\"}" https://[Server URL]:4443/api/StopZ
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"1\"}" https://123.456.789.000:4443/api/StopZ
```

Request URL

```
https://[ServerURL]:4443/api/StopZ
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully called stop camera [value]"}
```

Error

```
{    "status": "error",    "message": "Could not stop camera [value]"}OR{    "status": "error",    "message": "Camera address [ip address] is invalid"}
```
