Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/StartZ-API.htm

# StartZ API

The **StartZ** API is used to start a camera zooming in or out.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/StartZ

## Parameters

**Parameter Content Type**: Application/JSON

POST StartZ Parameters

 

Name

Description

cam

**Required.** Integer (body JSON) that sets the camera zoom function. Valid values are 1 through 255.

zDir

**Required.** Integer (body JSON) that sets the camera zoom function. Valid values (0–1) correspond with the following zoom functions:

*   0 - Zoom In
*   1 - Zoom Out

Body JSON Formatting

```
{    "cam": "[value]",    "zDir": "[value]"}
```

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"cam\":\"[value]\", \"zDir\":\"[value]\"}" https://[Server URL]:4443/api/StartZ
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"cam\":\"1\", \"zDir\":\"0\"}" https://123.456.789.000:4443/api/StartZ
```

Request URL

```
https://[ServerURL]:4443/api/StartZ
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "[message]"}
```

Error

```
{    "status": "Error",    "err": "Could not move camera [value]"}
```
