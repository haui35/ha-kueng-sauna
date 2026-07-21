# Küng Sauna for Home Assistant

[![Tests](https://github.com/haui35/ha-kueng-sauna/actions/workflows/tests.yml/badge.svg)](https://github.com/haui35/ha-kueng-sauna/actions/workflows/tests.yml)
[![GitHub release](https://img.shields.io/github/v/release/haui35/ha-kueng-sauna)](https://github.com/haui35/ha-kueng-sauna/releases)

Experimental Home Assistant custom integration for Küng Wellness Smart+ and
KS20 sauna controllers. It communicates directly with the controller's local
web API and does not require a cloud account.

> [!CAUTION]
> A sauna is a high-temperature appliance. Test every control while physically
> present. This integration must never replace or bypass the controller's door
> contact, remote-start approval, temperature limits, or other safety devices.

## Features

- Local polling every 10 seconds
- Current and target temperature
- Current and target humidity
- Küng programs exposed as Home Assistant climate presets
- Start and stop through the climate entity
- Fan control through the climate entity
- Eco-mode switch
- Remaining-time sensor
- Diagnostic sensors for remote access, key lock, operation lock, and events
- German and English translations

## Safety behavior

Before sending a start command, the integration requires the controller to
report all of the following:

- remote access is enabled;
- the keypad is not locked; and
- no controller event has set an operation lock.

The Küng controller remains authoritative and may reject any command. Mutating
commands are not automatically retried.

## Requirements

- Home Assistant with support for config-entry custom integrations
- Küng Smart+ or KS20 controller with its local web interface enabled
- Home Assistant and the sauna controller on the same trusted network
- Local controller address, usually `kueng-wellness.local`

The initial implementation was validated against controller API version
`1.30.2`. Other firmware versions may behave differently.

## Installation

### HACS custom repository

1. Open HACS in Home Assistant.
2. Open the three-dot menu and choose **Custom repositories**.
3. Add `https://github.com/haui35/ha-kueng-sauna` as an **Integration**.
4. Download **Küng Sauna** and restart Home Assistant.

### Manual installation

Copy `custom_components/kueng_sauna` into
`/config/custom_components/kueng_sauna` and restart Home Assistant. See
[INSTALL.md](INSTALL.md) for detailed instructions for Home Assistant OS.

## Configuration

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Küng Sauna**.
4. Enter `kueng-wellness.local` or a reserved local IP address.

No YAML configuration is required.

## Entities

| Entity | Purpose |
| --- | --- |
| Climate | Programs, start/stop, temperature, humidity, and fan |
| Eco-mode switch | Enables eco mode during an active operation |
| Remaining-time sensor | Reports the active program's remaining minutes |
| Remote-access sensor | Shows whether remote start is enabled |
| Key-lock sensor | Shows the controller keypad lock |
| Operation-lock sensor | Shows safety or event-based operation blocking |
| Event sensor | Shows whether the controller reports an event |

## Troubleshooting

- Open `http://kueng-wellness.local` from a device on the same network.
- If mDNS is unreliable, reserve the sauna controller's IP address in the
  router and configure that IP in the integration.
- Keep the controller on a trusted LAN or isolated IoT VLAN. Its local API uses
  HTTP rather than HTTPS.
- Check **Settings → System → Logs** for `kueng_sauna` messages.

## Development

Run the API and safety contract tests with:

```shell
python -m unittest discover -s tests -v
```

The observed API contract is documented in [docs/API.md](docs/API.md).
Contribution guidance is in [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This independent project is not affiliated with, endorsed by, or supported by
Küng Wellness AG. Product and company names belong to their respective owners.

## License

MIT — see [LICENSE](LICENSE).

