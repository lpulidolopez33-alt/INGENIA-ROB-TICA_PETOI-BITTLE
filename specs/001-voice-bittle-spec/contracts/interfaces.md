# VOICE-BITTLE H2 Interface Contracts

These are logical contracts for design and test planning, not implementation APIs or wire-format
schemas. They preserve H1 boundaries and leave unresolved decisions visible. During software-only
validation, a simulator stands in for external Bittle through the serial adapter contract; this
does not settle the SoI boundary.

## Recognition Provider Boundary

**Purpose**: Separate audio recognition from command interpretation so Vosk can be integrated if
the team approves it, without coupling command, state, or serial behavior to a provider.

**Input**:
- Captured audio from the capture boundary.
- Selected language context when established by the application.

**Result**:
- Recognized text and confidence when recognition yields a candidate.
- Explicit no-result/recognition-failure outcome when no command is recognized or recognition
  cannot be completed.

**Rules**:
- The provider does not decide whether text is an authorized robot action.
- The command validator owns vocabulary and confidence-threshold checks.
- No recognition result by itself triggers movement.
- Vosk with local Spanish and English models remains an RD-02 proposal and is not approved until
  OPEN-03 is resolved.

**Trace**: H1 RF-01, RR-01, RR-03, RD-02; ESC-01–ESC-04, ESC-07; OPEN-03–OPEN-06.

## Command Interpretation and Validation Boundary

**Input**: Recognition result containing text, language context, and confidence, or no-result.

**Output**: One validated semantic action, or a rejected/no-action outcome.

**Rules**:
- Current supported semantic actions are sitting and standing, mapped to `ksit` and `kup`.
- Only phrases approved through OPEN-06 may map to these actions.
- Confidence must be at or above approved U (OPEN-04).
- Unknown, low-confidence, silent, or failed inputs return no action and MUST NOT produce a
  movement request.
- Commands cannot be interpreted as arbitrary serial payloads.

**Trace**: H1 RF-02, RF-04, RS-01; ESC-01–ESC-04, ESC-07; NEC-01–NEC-03.

## State Manager Boundary

**Inputs**: Validated action/rejection; listening control; connection status; action lifecycle;
transmission outcome; capture timeout/fault.

**Outputs**: Permission or denial for a new action; current listening/link/action status; user
feedback and event-record requests.

**Rules**:
- No new action is allowed until the connection is available.
- A detected serial-link failure blocks new maneuvers.
- New instructions received during an active action are not transmitted. Exact rejection
  feedback and any queue policy remain subject to OPEN-11 and RF-05/RF-09 review.
- Silence ends capture without movement and informs the user, as proposed for ESC-07.
- Transmission success is not physical execution confirmation.

**Trace**: H1 RF-05, RF-06, RF-08, RF-09, RO-02, RS-02; ESC-05–ESC-07.

## Petoi Serial Adapter Boundary

**Input**: One allowed command token for an action that passed validation and state gating.

**Output**: Connection status and transmission success/failure; no guarantee of physical result.

**Rules**:
- Only the approved tokens `ksit` and `kup` are in the current voice scope.
- Use case-sensitive ASCII tokens consistent with the Petoi protocol.
- Report connection/write failures; do not accept new maneuver requests after detected link loss.
- The simulator records requested writes and can inject unavailable-link and write-error
  outcomes. It must not claim to emulate firmware posture behavior.
- Actual Bittle model and compatible connection details remain OPEN-02.

**Trace**: H1 RF-02/RF-03, RI-01/RI-02/RI-03, RFI-02, RS-02; ESC-01/02/06; OPEN-02.

## User Interface and Event Recording Boundary

**UI outputs**: Listening state, link state, active language, supported instruction/action pairs,
recognized/rejected/sent/failure outcome, movement state where available, and requested history.

**User inputs**: Manual listening enable/disable and history request. Exact history voice phrase,
display details, language controls, and acknowledgment content need clarification.

**Event fields**:
- Instruction event: date, time, recognized text, acceptance/rejection status (RM-01).
- Communication failure: date, time, error type (RM-02).
- Physical discrepancy record: requested instruction, transmitted command, observed behavior,
  and conformance outcome for ESC-08. This is collected during supervised physical verification.

**Rules**:
- Do not show "executed" or confirmed posture solely because a command was sent.
- Notify the user when microphone or transmission errors occur.
- The history presents accepted and rejected activity as required by RI-06; further event scope
  is not invented here.

**Trace**: H1 RF-06, RI-03–RI-07, RFI-01/RFI-02, RU-01–RU-03, RM-01/RM-02; NEC-04; ESC-03–08.

## Contract Traceability Note

H1's scenario matrix uses historical REQ identifiers and contains no category crosswalk for
ESC-07/ESC-08. Contracts therefore cite the current category IDs from H1 section 5 and scenarios
as source facts, but do not assert unapproved need/requisite links. The team must review and
approve a crosswalk before claiming complete traceability.
