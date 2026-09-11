# Customer Data Retention Standard

**Standard ID:** DATA-RET-31  
**Owner:** Data Governance

Northstar Labs retains customer data only for a documented business or legal purpose. Product teams must identify the data owner, retention period, and deletion mechanism before collecting a new category of personal data.

## Standard periods

- Application request logs are retained for 30 days.
- Authentication audit logs are retained for 400 days.
- Support tickets are retained for two years after closure.
- Customer invoices and associated accounting records are retained for seven years.
- Temporary analytics exports must be deleted within seven days.

The scheduled deletion workflow is called Janitor. Teams register a dataset in `governance/retention.yaml`, including its owner and deletion schedule. Janitor produces a deletion report after every run.

## Legal holds and backups

A legal hold suspends scheduled deletion for the records named in the hold notice. Only Legal may create or release a legal hold. Engineers must not disable Janitor globally to preserve one dataset.

Encrypted backups may retain deleted production records for up to 35 additional days. Backups are used only for disaster recovery and are not queried for ordinary product or analytics purposes. When a backup expires, its encryption key and stored copy are destroyed.

Questions about DATA-RET-31 or a new retention period should be sent to the Data Governance queue in WorkHub.

