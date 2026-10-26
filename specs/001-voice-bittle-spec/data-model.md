# VOICE-BITTLE H2 Data Model

This is a logical planning model derived from H1 and the clarified feature specification. It
does not select a storage technology, define source code types, or decide the system-of-interest
boundary. For software-only tests, Bittle is provisionally external behind a simulated
interface.

## Entities

| Entity | Fields supported by H1/spec | Validation and lifecycle |
|---|---|---|
| Voice input | Captured audio; recognized text when available; language; recognition confidence when provided | Capture is enabled/disabled; silence through T_escucha closes capture without motion. Exact audio format, phrase set, language selection, and U remain open. Audio retention is not specified; do not assume persisted audio. |
| Recognized instruction | Text; selected language; confidence; evaluation outcome | Only an approved phrase with confidence at or above U can be considered valid. Phrase set and U remain OPEN-04/06; technology remains OPEN-03. |
| Supported action | Semantic action and corresponding Petoi token | Current scope maps sitting → `ksit`, standing → `kup`. No other Petoi skill is authorized as a voice action by this baseline. |
| Command request | Validated supported action; transmission result | Only validated requests can reach the serial boundary. Tokens are Petoi case-sensitive ASCII. A sent request is not proof of physical execution. |
| System/connection state | Listening state; robot link active/inactive or failed; action active/inactive; user-visible outcome | Motion remains disabled until connection is available; link failure blocks new maneuvers. Exact startup/recovery/close transitions require review of RF-05/RF-08/RF-09 and OPEN-11. |
| Instruction event | Date; time; recognized text; acceptance or rejection status | RM-01 requires these fields for each instruction. Exact time zone, clock source, and retention are not specified. |
| Communication failure event | Date; time; error type | RM-02 requires these fields for communication failures. Additional diagnostics are not specified. |
| User feedback | Outcome (recognized, rejected, sent, or failure); applicable status/message | RF-06/RU-02 and interface requirements require outcome information. Exact wording, channel, and acknowledgment semantics remain unresolved. |
| Physical verification record | Requested instruction; transmitted command; observed movement; conformance result | ESC-08 requires operator observation and discrepancy record before repeat trial. H1 does not prescribe storage format or observer identification. |
| Trial sample | User, utterance/sample, repetition, command class, environmental conditions, recognition result | RR-01 proposes 5 users × 10 utterances × 2 repetitions = 100 samples, 0.5–1 m, and noise below 45 dBA. Distribution by the two actions, protocol, test corpus, and conditions require OPEN-05/06 approval. |

## Relationships

- A voice input may yield a recognized instruction, or no recognized text (including silence).
- A recognized instruction is evaluated as accepted or rejected; rejected input creates no
  movement command.
- An accepted instruction maps to one supported action; an action may create a command request.
- A command request crosses the serial adapter boundary and produces a transmission outcome.
- A physical verification record is separate from a command request and records an operator's
  observation; transmission alone cannot create a confirmed posture.
- Instruction and communication events are recorded under RM-01 and RM-02.
- Trial samples aggregate into the proposed RR-01 recognition result only after the protocol and
  sample distribution are approved.

## State and Outcome Vocabulary

The specification distinguishes listening enabled/disabled, connection available/failed,
action active/inactive, and instruction outcomes recognized/rejected/sent/failed. This vocabulary
supports the H1 use cases but is not a complete state machine. In particular, queueing,
acknowledgment, retry, recovery, end-of-session behavior, and the physical movement state model
must not be inferred; see OPEN-02, OPEN-09–OPEN-12 and the requirement inconsistency register in
[spec.md](./spec.md).
