# Installation on Home Assistant OS

## HACS custom repository

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/haui35/ha-kueng-sauna` with category
   **Integration**.
4. Open the new **Küng Sauna** entry and select **Download**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration**.
7. Search for **Küng Sauna** and use `kueng-wellness.local` as the host.

## Manual installation

Copy the complete folder `custom_components/kueng_sauna` to:

```text
/config/custom_components/kueng_sauna
```

Restart Home Assistant, then add **Küng Sauna** from **Settings → Devices &
services → Add integration**.

## First safe test

After setup, verify only the reported temperature, humidity, remote-access
approval, and program list. Perform the first start test while physically
present and confirm the Küng display and door-contact behavior.
