# Production Deployment and Rollback Guide

**Runbook ID:** ENG-DEP-8  
**Owner:** Platform Engineering

Production deployments use the Orchid release pipeline. Changes must be merged into the default branch, pass the required CI checks, and have at least one approval from a code owner. Database migrations that cannot be safely rolled back require a written recovery plan in the pull request.

## Starting a release

Create a production release with:

```bash
deployctl release --service <service-name> --environment production
```

Orchid first sends 5% of traffic to the new version for ten minutes. If the error-rate and latency checks remain within their thresholds, traffic increases to 25%, 50%, and finally 100%. A release owner must watch the Orchid dashboard until the rollout is complete.

The deployment manifest for the Payments API is stored at `services/payments/config.py`. Editing this file requires approval from the Payments code-owner group.

## Reverting a release

If a new version causes customer-visible errors, stop the rollout and return traffic to a known-good release. Use the following emergency rollback command:

```bash
deployctl rollback --service <service-name> --to <release-id>
```

The release ID is shown in the Orchid dashboard and in the deployment message posted to the service's Slack channel. Do not redeploy the previous Git commit as a substitute for `deployctl rollback`; the command also restores the matching runtime configuration.

If rollback does not restore service within five minutes, declare an incident under INC-P1. A rollback is a mitigation action and does not remove the requirement for a post-incident review when the event meets P1 criteria.

Routine production deployments are not allowed on Friday after 15:00 CET. Emergency security patches are exempt when approved by the incident commander and the security duty officer.

