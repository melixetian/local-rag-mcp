# Production Incident Response

**Procedure ID:** INC-P1  
**Owner:** Site Reliability Engineering

This procedure applies to production failures, severe degradation, and customer-impacting security events.

## Severity levels

- **P1 Critical:** The service is unavailable for many customers, data integrity may be at risk, or a security breach is actively occurring.
- **P2 Major:** A major function is degraded but a workaround exists.
- **P3 Minor:** Impact is limited and normal engineering workflow is sufficient.

The on-call engineer must declare a P1 incident with:

```bash
opsctl incident declare --severity p1
```

The incident commander must acknowledge a P1 page within five minutes. The first public status update must be posted within 20 minutes after declaration, followed by updates at least every 30 minutes until recovery.

## Roles

The incident commander coordinates the response and makes priority decisions. The operations lead performs technical mitigation. The communications lead publishes customer-facing updates. One person should not hold more than one of these roles during a P1 incident when enough responders are available.

## Recovery objectives

Checkout and payment processing are classified under recovery target **RTO-17**, which requires restoration of core transaction processing within 45 minutes. RTO-17 is a recovery target, not the identifier used to declare an incident.

After service recovery, the incident commander must create a post-incident review in Sentinel within two working days. A P1 review must include a timeline, root cause, customer impact, contributing factors, and corrective actions with owners and due dates. The review is blameless and focuses on system and process improvements.

Suspected credential theft or unauthorized data access must also be reported immediately in the `#security-redline` Slack channel.

