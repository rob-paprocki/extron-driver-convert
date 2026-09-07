Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StopPT-API.htm

# StopPT API

The **StopPT** API is used to stop a camera panning in a specified direction.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StopPT

## Parameters

**Parameter Content Type**: Application/JSON

POST StopPT Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera that will have its panning stopped. Valid values are 1 through 255.

Body JSON Formatting

```
{    "cam": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\"}" https://[Server URL]:4443/api/StopPT
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"1\"}" https://123.456.789.000:4443/api/StopPT
```

Request URL

```
https://[ServerURL]:4443/api/StopPT
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
{    "status": "error",    "message": "Could not stop camera [value]"}OR{    "status": "error",    "message": "Camera address [value] is invalid"}
```
