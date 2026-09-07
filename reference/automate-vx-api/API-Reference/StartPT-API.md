Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartPT-API.htm

# StartPT API

The **StartPT** API is used to start a camera panning in a specified direction.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StartPT

## Parameters

**Parameter Content Type**: Application/JSON

POST StartPT Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera that will be panned. Valid values are 1 through 255.

ptDir

**Required.** Integer (body JSON) that sets the direction that the camera will be panned. Valid values (0–7) correspond with the following panning directions:

*   0 - Up
*   1 - Up Right
*   2 - Right
*   3 - Down Right
*   4 - Down
*   5 - Down Left
*   6 - Left
*   7 - Up Left

Body JSON Formatting

```
{    "cam": "[value]",    "ptDir": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\", \"ptDir\":\"[value]\"}" https://[Server URL]:4443/api/StartPT
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"1\", \"ptDir\":\"5\"}" https://123.456.789.000:4443/api/StartPT
```

Request URL

```
https://[ServerURL]:4443/api/StartPT
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully called started movement for camera [value]"}
```

Error

```
{    "status": "Error",    "err": "Could not move camera [value]"}
```
