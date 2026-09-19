# Privacy Policy Discord News Router Bot

**Effective date:** September 19, 2026
**Last updated:** September 19, 2026

This Privacy Policy explains what information the Discord News Router Bot ("the Bot", "we", "us") collects, processes, stores, and deletes. The Bot is operated by Bobby (GitHub: bobbycomet) ("the Operator").

If you run your own copy of the Bot (self-hosting), **you are the operator of that copy**. This policy describes the software's default behavior, but does not govern how an independent operator stores, processes, or uses data. See [Section 8 — Self-hosted copies](#8-self-hosted-copies).

---

## 1. What the Bot does

The Bot watches a single "hub" channel that a server administrator chooses.

When a post arrives in that channel, typically through Discord's Follow Channel feature or a manual forward by a moderator, the Bot checks it against the server's routing rules ("mappings") and forwards or copies it to the destination channel, forum, or thread configured by the administrator.

The Bot processes this information automatically to perform the routing requested by the server administrator.

---

## 2. Information we store

The Bot stores configuration information entered or created by server administrators.

Configuration is associated with the Discord server that created it and is kept separate from the configuration of other servers.

We may store the following information:

| Data                                         | Why we store it                                            |
| -------------------------------------------- | ---------------------------------------------------------- |
| Server (guild) ID                            | To identify the server whose configuration is being stored |
| Hub channel ID                               | To know which channel to watch                             |
| Mapping name                                 | To identify and manage a routing rule                      |
| Destination channel, forum, or thread ID     | To know where matching posts should be routed              |
| Keywords associated with a mapping           | To determine whether a post matches the mapping            |
| Mapping creation time                        | To provide configuration information and manage mappings   |
| User IDs listed in mappings                  | To match posts by author                                   |
| Origin server/channel IDs listed in mappings | To match posts based on where content originated           |

User IDs are Discord account identifiers and may constitute personal data under some privacy laws.

We store the numeric Discord ID supplied to the Bot. We do not intentionally store the associated username, avatar, profile information, or other account information as part of the mapping itself.

---

## 3. Information we process but do not intentionally store

To perform its functions, the Bot temporarily processes information in memory that is not saved to its configuration database.

This includes:

* **Hub channel messages:** message content, embeds, attachments, author ID, and origin server/channel information. These are examined to determine whether a routing rule applies and, when appropriate, are forwarded or copied to the configured destination. The Bot does not intentionally retain a separate copy of the message in its configuration database.
* **Forwarded or copied attachments:** when an attachment needs to be reposted, the Bot may temporarily download it into memory so it can be uploaded to the destination. The temporary copy is discarded after processing.
* **Messages in other channels:** Discord may deliver message events from channels the Bot can access because the Bot has the required Message Content intent. Messages outside the configured hub channel are not used for routing and are discarded without being intentionally stored by the Bot.
* **Administrator command lookups:** certain administrator commands may read recent hub messages to provide configuration or diagnostic information. For example, `/newsrouter scan` may inspect up to 200 recent messages and `/test` may inspect up to 100. These commands may display author names, IDs, or related information to the administrator in an ephemeral Discord response.
* **User identification lookups:** commands that list or edit configured user IDs may temporarily retrieve a user's public Discord name so that an administrator can recognize which account an ID refers to.

These temporary processing activities are not intentionally written to the Bot's configuration database.

### Discord's own storage

Once a post is forwarded, the resulting message exists as a normal Discord message in the destination channel.

That copy is stored and processed by Discord according to Discord's own systems, policies, and privacy practices. The Operator does not control Discord's storage of those messages.

See [Discord's Privacy Policy](https://discord.com/privacy) for information about Discord's own handling of data.

---

## 4. Logs

The Bot may write operational logs needed to operate and troubleshoot the service.

Examples include:

* Bot startup and shutdown information.
* Command synchronization information.
* Errors and exceptions.
* Information identifying a command or Discord resource involved in an error.

We do **not intentionally log the contents of routed messages** as part of normal operation.

Depending on the hosting environment, logs may be stored by the host system. For example, a systemd installation may place service logs in the system journal.

Logs are retained only as long as reasonably necessary for operation, troubleshooting, security, and maintenance, and may be removed automatically according to the host's log-rotation or retention settings.

---

## 5. How we use information

We use the information described in this policy only as reasonably necessary to:

* Operate the Bot.
* Apply administrator-configured routing rules.
* Display configuration and diagnostic information to authorized server administrators.
* Maintain and troubleshoot the service.
* Protect the Bot, its infrastructure, and users from abuse or security problems.
* Comply with applicable legal obligations.

We do **not** sell or rent the information we store.

We do not use stored Bot configuration or routed message content to advertise to users, build profiles of individuals, or train AI models.

---

## 6. Sharing

We do not sell or otherwise provide stored Bot data to third parties for their own advertising or profiling purposes.

Information may be processed or disclosed in the following circumstances:

### Discord

The Bot necessarily communicates with Discord because it operates through Discord's platform and API.

Information sent through Discord is subject to Discord's own systems and policies.

### Hosting providers

If the official hosted Bot runs on infrastructure operated by a third-party hosting provider, that provider may technically store or process Bot data on our behalf as necessary to provide the infrastructure.

We will use reasonable measures to select and manage hosting services appropriate for the Bot's needs.

### Legal and safety requirements

We may disclose information when reasonably necessary to:

* Comply with applicable law, legal process, or a valid government request.
* Protect the rights, safety, or security of the Operator, users, the Bot, its infrastructure, or the public.
* Investigate abuse, fraud, security incidents, or violations of the Terms of Service.

---

## 7. Retention and deletion

### Configuration data

Configuration data is retained while it is needed to operate the Bot.

Administrators may remove individual mappings and associated configuration through the Bot's commands.

Removing the Bot from a server **does not automatically delete the server's stored configuration**.

If you want the configuration associated with your server deleted, contact us using the information in [Section 11](#11-contact) and provide the server ID.

We will delete the applicable stored configuration within **30 days**, subject to information that we may be required to retain by law or that is reasonably necessary for security, abuse prevention, or the establishment, exercise, or defense of legal claims.

### User IDs in mappings

If your Discord user ID has been added to a mapping, you may request that it be removed.

Contact us with your Discord user ID and, if known, the relevant server ID. We will remove the applicable stored ID within **30 days**, subject to the same legal and security exceptions described above.

Server administrators can also remove configured user IDs themselves using the Bot's available configuration commands.

### Routed messages

We cannot delete copies of messages that have already been forwarded into Discord destination channels.

Those messages are ordinary Discord messages and are controlled by the relevant Discord server, its moderators, and Discord's own systems.

---

## 8. Self-hosted copies

The Bot's source code is available under its applicable open-source license.

If you or another party operates an independent copy of the Bot, the data processed by that copy is controlled by whoever operates that instance.

The Operator of the official hosted Bot does not have access to data stored by independent self-hosted copies and is not responsible for their data handling, security, retention practices, or privacy policies.

If you self-host the Bot for other Discord servers or users, **you are responsible for determining what privacy notices and data-protection obligations apply to your installation**.

You may adapt this policy as a starting point for your own installation, but you are responsible for ensuring that your version accurately describes your own hosting environment and practices.

---

## 9. Security

The official hosted Bot uses reasonable technical and organizational measures appropriate to the type and amount of information it stores.

The Bot's configuration data may be stored in separate SQLite database files for individual servers.

The Bot's Discord authentication token is stored outside the source repository and is not intentionally committed to source control.

Administrator configuration commands require Discord's **Manage Server** permission.

No system can be guaranteed to be completely secure. We cannot guarantee absolute security or that unauthorized access, loss, alteration, or disclosure will never occur.

If we become aware of a security incident affecting stored personal information, we will take reasonable steps to investigate and respond in accordance with applicable law.

---

## 10. Children

The Bot is not directed at children.

Use of the Bot is subject to Discord's minimum age requirements and applicable local law.

We do not knowingly seek to collect personal information from children below the applicable minimum age.

If you believe that the Bot has stored personal information belonging to a child in circumstances where it should not have been collected, contact us using the information in Section 11.

---

## 11. Contact

Questions, privacy requests, data-access requests, deletion requests, or concerns about the Bot's handling of information may be submitted through:

* **Email:** [griffin.linux@gmail.com](mailto:griffin.linux@gmail.com)
* **GitHub:** https://github.com/bobbycomet
* **Support server:** https://discord.gg/8ZSg375hMS

For privacy or deletion requests, please provide enough information for us to identify the relevant server or data without unnecessarily providing additional personal information.

---

## 12. Your privacy rights

Depending on where you live and which privacy laws apply to you, you may have rights regarding personal information we hold about you.

Depending on the applicable law, these may include rights to:

* Request access to personal information.
* Request correction of inaccurate information.
* Request deletion of personal information.
* Request restriction of certain processing.
* Object to certain processing.
* Request a copy of certain information in a portable format.
* Submit a complaint to an applicable data-protection authority.

Because the Bot intentionally stores a limited amount of information, many requests can be handled through the deletion and configuration-management process described in Section 7.

To exercise an applicable privacy right, contact us using Section 11.

We will respond to valid requests within the time required by applicable law. We may need to verify that a request relates to the person or server concerned before disclosing or deleting information.

We will not discriminate against you for exercising privacy rights available to you under applicable law.

---

## 13. Changes to this policy

We may update this Privacy Policy from time to time.

When we make changes, we will update the **"Last updated"** date at the beginning of this policy.

For material changes, we will make a reasonable effort to announce the changes through the Bot's repository, support server, or another appropriate channel.

Continued use of the hosted Bot after an updated policy becomes effective means that the updated policy applies to subsequent use of the Bot.

If you do not agree with the updated policy, you should stop using the hosted Bot and remove it from your server.
