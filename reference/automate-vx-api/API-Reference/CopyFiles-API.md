Source: https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/CopyFiles-API.htm

# CopyFiles API

The **CopyFiles** API is used to copy recorded files on the Automate VX system from **D:\\Recordings** to an external location.

## Syntax

*   **HTTP Method**: POST
*   **Base URI**: /api/CopyFiles

## Parameters

**Parameter Content Type**: Application/JSON

POST CopyFiles Parameters

 

Name

Description

destination

**Required.** String (body JSON) that sets the external destination folder where the recorded files will be copied.

logDestination

**Required.** String (body JSON) that turns on logging by setting an external logging destination. Leave this parameter blank to turn off logging.

deleteSource

**Required.** Boolean (body JSON) that sets whether the source files will be deleted from the Automate VX system after being copied (**true**) or not (**false**)

Body JSON Formatting

```
{    "destination": "[destination folder address]",    "logDestination": [logging destination folder address]",    "deleteSource": [true/false]}
```

NOTE: To ensure correct JSON syntax, use "\\\\" for each "\\" used (for example, "D:\\\\Copy-Destination" for local destinations and "\\\\\\\\Network-Location\\Copy-Destination" for network destinations).

## Responses

**Response Content Type**: Application/JSON

cURL Base Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: [Token]" -X POST --data "{\"[destination folder address]\",\"[logging destination folder address]\",\"deleteSource\":\[true|false]\"}" https://[Server URL]:4443/api/CopyFiles
```

Example cURL Command

```
curl -v -H "Content-Type: application/json" -H "Authorization: 1234567890" -X POST --data "{\"destination\":\"C:\Intel\",\"logDestination\":\"C:\Program Files\1 Beyond\Automate VX\Log\", \"deleteSource\":\true\"}" https://123.456.789.000:4443/api/CopyFiles
```

Request URL

```
https://[ServerURL]:4443/api/CopyFiles
```

Response Messages

 

Result

Message

Success

```
{    "status": "OK",    "message": "Successfully backed up information"}
```

Error

```
{    "status": "Error",    "err": "[Reason for error]"}
```
