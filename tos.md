# Terms of Service for Discord News Router Bot

**Effective date:** September 19, 2026
**Last updated:** September 19, 2026

These Terms of Service ("Terms") govern your use of the Discord News Router Bot ("the Bot"), operated by Bobby (GitHub: bobbycomet) ("the Operator", "we", "us"). By adding the Bot to a server or using its commands, you agree to these Terms. If you don't agree, don't use the Bot.

If you are using the Bot on behalf of a server, you confirm that you have the authority to accept these Terms for that server.

These Terms apply to the **official hosted instance operated by the Operator**. They do not govern independent copies of the Bot operated by third parties.

---

## 1. What the Bot does

The Bot watches a hub channel set by a server administrator and routes matching posts (for example, posts that arrive through Discord's Follow Channel feature, or that a moderator forwards) into destination channels, forums, or threads according to rules ("mappings") the administrator configures.

The Bot automatically processes and forwards content according to those administrator-configured rules. The Operator does not manually select, review, or approve individual pieces of routed content.

Details about data the Bot handles are provided in our [Privacy Policy](PRIVACY_POLICY.md).

---

## 2. Eligibility

You must meet Discord's minimum age requirement and comply with the [Discord Terms of Service](https://discord.com/terms), [Community Guidelines](https://discord.com/guidelines), and [Developer Policy](https://support-dev.discord.com/hc/en-us/articles/8563934450327-Discord-Developer-Policy).

If Discord bans or restricts you or your server in a way that prevents lawful use of the Bot, you may not use the Bot.

---

## 3. Who can configure the Bot

Configuration commands (`/newsrouter …` and `/test`) require the **Manage Server** permission.

Server administrators are responsible for everything they configure, including:

* The mappings they create or modify.
* The user and origin IDs they enter.
* The channels, forums, and threads used as destinations.
* The content they choose to route.
* Ensuring that people with permission to configure the Bot are trusted to do so.

You are responsible for making sure that only appropriate and trusted people have the permissions necessary to configure the Bot.

---

## 4. Acceptable use

You agree **not** to use the Bot to:

* Break any law, or violate Discord's terms, policies, or guidelines.
* Route, repost, or spam content in a way that harasses others, floods channels, or evades a server's or Discord's moderation.
* Redistribute content you don't have the right to redistribute, or that a source server has asked not to be shared.
* Circumvent access restrictions, for example by moving content from a private or restricted channel into a place where people who weren't meant to see it can read it.
* Collect, scrape, or profile users, or use the Bot's commands to gather personal data about people.
* Attack, overload, reverse-engineer for abusive purposes, or interfere with the Bot or its hosting infrastructure.
* Resell or offer the Operator's hosted instance of the Bot as a paid service without our written permission.

Nothing in these Terms grants permission to access, redistribute, or otherwise use content that you do not have the right to access or use.

---

## 5. Content you route

* **The Bot does not own or manually review routed content.** It automatically copies or forwards content according to administrator-configured rules.
* Server administrators are responsible for the content they choose to route and for complying with applicable laws, Discord's policies, and third-party rights.
* The Operator does not manually select or approve individual routed messages.
* **Following a channel is a Discord feature.** The Bot only routes content that already arrives in the configured hub channel. It does not independently follow other servers' channels for you.
* Content forwarded by the Bot becomes an ordinary Discord message in your server. Deleting, moderating, or otherwise managing that content is the responsibility of the server's moderators and Discord.
* If a copyright owner or other rights holder reports allegedly unauthorized or infringing content, we may investigate the report and may remove, disable, or restrict the relevant mapping or hosted Bot access where we determine that doing so is appropriate.
* Nothing in these Terms transfers ownership of routed content to the Operator.

---

## 6. Permissions and setup

For the Bot to work, you must give it the permissions it needs in the relevant channels, such as permission to read the hub, post in destination channels, create forum posts, or perform other actions required by the configured routing rules.

If you restrict the Bot's permissions, some or all features may stop working.

Mapping rules are matched in order of specificity (origin, then keyword, then author), and multiple matching mappings of the same specificity all receive a copy.

You are responsible for testing your configuration, including with commands such as `/newsrouter scan` and `/test`, and for confirming that routing behaves the way you intend.

The Operator is not responsible for incorrect routing resulting from administrator configuration, insufficient permissions, Discord behavior, or other circumstances outside the Operator's reasonable control.

---

## 7. Discord dependency

The Bot depends on Discord's services, APIs, permissions system, and platform functionality.

The Operator does not control Discord and does not guarantee that:

* Discord will continue to provide any particular feature or API.
* Discord's APIs will remain compatible with the Bot.
* The Bot will remain compatible with future Discord changes.
* Discord will maintain any particular permissions, channel, forum, thread, or Follow Channel functionality.

Changes to Discord's platform, APIs, policies, permissions, or rate limits may cause some or all Bot functionality to stop working.

---

## 8. Availability and changes

The Bot is provided on a best-effort basis.

It may go offline, lose messages, deliver duplicates, fail to route messages, experience delays, or change at any time because of maintenance, bugs, hosting problems, Discord outages, API changes, rate limits, security incidents, or other circumstances.

We do not promise any particular uptime, delivery rate, routing accuracy, or response time.

**Don't rely on the Bot for anything critical or time-sensitive.** If a message or notification is important, maintain an independent backup route, such as manual forwarding by moderators.

We may add, change, limit, or remove features at any time, including commands, supported destinations, mapping behavior, and limits such as the number of IDs allowed per mapping.

---

## 9. Free service

Unless expressly stated otherwise, the official hosted instance of the Bot is provided free of charge.

We may change how the service is provided in the future, including introducing optional paid features, service limits, or other changes. Any paid features may be subject to additional terms.

Nothing in these Terms guarantees that the Bot will remain free indefinitely.

---

## 10. Suspension and termination

We may suspend, restrict, or terminate access to the hosted Bot, with or without notice, when reasonably necessary to address:

* Violations of these Terms.
* Violations of Discord's policies.
* Abuse or misuse of the Bot.
* Security concerns.
* Legal requirements.
* Risks to the Bot, its hosting infrastructure, the Operator, or other users.

You may stop using the Bot at any time by removing it from your server.

To have stored configuration or other data deleted, follow the process described in the [Privacy Policy](PRIVACY_POLICY.md).

---

## 11. Open-source software and self-hosting

The Bot's source code is published on GitHub under the **GNU Affero General Public License, version 3 (AGPL-3.0)**, or another license explicitly identified in the repository.

The applicable software license governs your rights to use, modify, and redistribute the Bot's source code.

These Terms apply to your use of **the Operator's hosted instance** of the Bot.

Nothing in these Terms grants or restricts rights to the Bot's source code beyond those provided by the applicable open-source license.

If you run your own copy of the Bot, you are the operator of that copy and are responsible for:

* Complying with Discord's terms, policies, and developer requirements.
* Complying with applicable law.
* Handling data collected by your installation appropriately.
* Providing any terms, privacy policy, notices, or other documentation required for your installation.
* Maintaining and securing your own infrastructure.

The Operator has no responsibility for third-party copies, installations, modifications, or hosted instances of the Bot.

---

## 12. Disclaimer of warranties

THE BOT IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, ACCURACY, NON-INFRINGEMENT, AND UNINTERRUPTED OR ERROR-FREE OPERATION.

We do not guarantee that the Bot will:

* Route every message correctly, completely, or on time.
* Remain available.
* Remain compatible with Discord.
* Be free of bugs or security vulnerabilities.
* Preserve every routed message.
* Operate without interruption or delay.

---

## 13. Limitation of liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW, THE OPERATOR WILL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR FOR ANY LOSS OF DATA, CONTENT, COMMUNITY, PROFITS, OR GOODWILL, ARISING OUT OF OR RELATED TO YOUR USE OF, OR INABILITY TO USE, THE BOT, EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

BECAUSE THE BOT IS PROVIDED FREE OF CHARGE, OUR TOTAL LIABILITY FOR ANY CLAIM RELATING TO THE BOT WILL NOT EXCEED **USD $50**.

Some jurisdictions do not allow certain limitations of liability, so parts of this section may not apply to you.

---

## 14. Indemnification

To the maximum extent permitted by applicable law, you agree to defend, indemnify, and hold harmless the Operator from claims, damages, liabilities, losses, and reasonable expenses (including reasonable legal fees) arising from:

* Content you route using the Bot.
* Your configuration or use of the Bot.
* Your violation of these Terms.
* Your violation of applicable law.
* Your violation of a third party's rights.

---

## 15. Contact

Questions, reports of abuse, or takedown requests may be submitted through:

* **Email:** [griffin.linux@gmail.com](mailto:griffin.linux@gmail.com)
* **GitHub:** https://github.com/bobbycomet
* **Support server:** [Discord](https://discord.gg/8ZSg375hMS)

For technical issues, you may also use the issue tracker in the Bot's GitHub repository.

---

## 16. Governing law and disputes

These Terms are governed by the **laws of the Commonwealth of Kentucky, United States of America**, without regard to its conflict-of-law rules.

Any dispute that cannot be resolved informally will be brought in the courts located in **Louisville, Kentucky, United States of America**, and you consent to the jurisdiction and venue of those courts.

If a court finds any part of these Terms unenforceable, the remaining provisions will remain in effect to the maximum extent permitted by law.

---

## 17. Changes to these Terms

We may update these Terms from time to time.

When we make changes, we will update the **"Last updated"** date at the beginning of these Terms.

For material changes, we will make a reasonable effort to announce the changes through the Bot's repository, support server, or another appropriate channel.

Continued use of the hosted Bot after the updated Terms become effective means you accept the updated Terms. If you do not agree to the updated Terms, stop using the hosted Bot and remove it from your server.

---

## 18. Entire agreement

These Terms and the [Privacy Policy](PRIVACY_POLICY.md) constitute the entire agreement between you and the Operator regarding the hosted Bot and replace any earlier understandings or agreements regarding the hosted service.

The Bot's open-source license remains a separate agreement governing the software itself.
