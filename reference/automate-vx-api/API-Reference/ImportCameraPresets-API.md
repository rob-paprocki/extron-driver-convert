Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/ImportCameraPresets-API.htm

# ImportCameraPresets API

The **ImportCameraPresets** API is used to import all camera presets to configured cameras on the Automate VX system.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/ImportCameraPresets

## Parameters

**Parameter Content Type**: Application/JSON

No parameters are required for this API call.

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "" https://[Server URL]:4443/api/ImportCameraPresets
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "" https://123.456.789.000:4443/api/ImportCameraPresets
```

Request URL

```
https://[ServerURL]:4443/api/ImportCameraPresets
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Camera presets imported successfully",}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```
