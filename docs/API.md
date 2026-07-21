# Observed local API contract

This document records the API behavior observed from a Küng controller running
API version `1.30.2`. It is not an official Küng specification.

## Base URL

```text
http://<controller>/api/1.30.2/sauna/
```

The integration sends and accepts JSON. The controller is polled every ten
seconds. No credentials, cookies, serial numbers, network settings, or captured
traffic are stored in this repository.

## Read operations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `status` | Live operation, temperature, humidity, locks, and timing |
| `GET` | `program` | Available program summaries |
| `GET` | `program/<id>` | Complete program used for start and stop |
| `GET` | `program/default` | Editable default program |
| `GET` | `information/system` | Controller and software metadata |

## Write operations

| Method | Path | Payload shape |
| --- | --- | --- |
| `PUT` | `operation` | `{"program": {...}, "enable": true}` |
| `PUT` | `temperature` | `{"targetTemp": 85}` |
| `PUT` | `humidity` | `{"targetHumidity": 40}` |
| `PUT` | `fan` | `{"power": true}` |
| `PUT` | `ecomode` | `{"enable": true}` |

## Safety invariants

The integration refuses a remote start when any of these conditions applies:

- `remoteAccessEnabled` is absent or false;
- `keyLock` is true; or
- `event.operationLock` is true.

The controller remains the final authority and must enforce its own physical
safety chain. Write calls are not automatically retried.
