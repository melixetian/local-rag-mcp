# Information Security and Access Policy

**Policy ID:** SEC-12  
**Owner:** Information Security

Employees must use a company-managed laptop with disk encryption, automatic screen locking, and endpoint protection enabled. Internal applications may only be accessed through ZETA VPN when the employee is outside a Northstar Labs office.

Passwords must be unique and stored in the approved password manager, KeyChest. Sharing a password through email, Slack, a document, or a ticket is prohibited. Multi-factor authentication is mandatory for email, source control, cloud consoles, and production access.

## Credentials and secrets

Application secrets belong in Blackbox Vault. They must not be committed to Git, placed in `config.py`, included in a Docker image, or copied into CI logs. A credential suspected of exposure must be revoked immediately; changing the surrounding code is not sufficient.

ZETA VPN device keys expire every 180 days. To replace a device key before it expires, use:

```bash
vpnctl rotate-key --device <device-id>
```

If a laptop is lost or stolen, call the security hotline within 30 minutes and post no sensitive details in public Slack channels. Information Security will remotely revoke the device certificate and coordinate further action.

## Phishing and suspicious activity

Suspicious emails should be reported with the **Report phishing** button in the mail client. Do not forward the message to colleagues. Suspected credential theft, malware, or unauthorized access must be reported in `#security-redline` and may require a P1 incident under INC-P1.

