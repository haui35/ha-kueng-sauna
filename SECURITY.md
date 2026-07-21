# Security policy

## Reporting a vulnerability

Please report potential vulnerabilities privately through GitHub's security
advisory feature for this repository. Do not open a public issue containing
credentials, local addresses, serial numbers, HAR files, or controller traffic.

## Deployment guidance

- Keep the sauna controller and Home Assistant on a trusted local network or an
  isolated IoT VLAN.
- Do not expose the controller's HTTP interface directly to the internet.
- Do not disable or bypass the door contact, remote-start approval, thermal
  protection, or other hardware safety mechanisms.
- Perform initial and post-update control tests while physically present.

This integration treats the controller as the final authority and adds its own
preflight checks before remote starts. These checks are defense in depth, not a
replacement for certified safety equipment.
