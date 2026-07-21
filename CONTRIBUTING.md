# Contributing

Contributions are welcome, especially reports covering additional Küng
controller and firmware versions.

## Before opening an issue

- Confirm that `http://kueng-wellness.local` is reachable from the same network.
- Include the Home Assistant version, controller model, and firmware/API version.
- Remove credentials, cookies, local addresses, serial numbers, and personal
  program names from logs or traffic captures.

## Development workflow

1. Create a focused branch.
2. Keep controller I/O asynchronous.
3. Preserve the remote-start safety checks.
4. Add or update contract tests for API changes.
5. Run:

   ```shell
   python -m unittest discover -s tests -v
   ```

6. Explain any controller write behavior in the pull request.

Never add captured HAR files or unredacted diagnostics to the repository.
