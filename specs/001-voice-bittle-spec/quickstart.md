# VOICE-BITTLE H2 Validation Quickstart

## Purpose and Status

This guide describes the planned validation flow for the H2 design. No application or test
runner exists in this deliverable, so there are no executable setup or test commands yet. Do not
install dependencies, connect a physical robot, or claim tests passed as part of this H2 document.
Implementation and test execution belong to a later approved phase.

## Prerequisites for Future Software-Only Validation

- A later approved implementation of the logical interfaces in
  [contracts/interfaces.md](./contracts/interfaces.md).
- Deterministic recognition-result fixtures; ASR provider is replaceable.
- A simulated Petoi serial endpoint that captures tokens and injects connection/write failures.
- Test inputs and expected results approved after OPEN-04, OPEN-05, OPEN-06, OPEN-11, and the
  category/REQ crosswalk are reviewed.
- Refer to [data-model.md](./data-model.md) for event fields and state vocabulary.

## Planned Scenarios

1. **Supported sitting action**: Feed an approved sitting recognition result at or above U.
   Expect validated sitting action, `ksit` at the simulated endpoint, and the RM-01 event fields.
2. **Supported standing action**: Feed an approved standing result at or above U. Expect `kup`
   and the same auditable outcome separation.
3. **Safe rejection**: Feed unknown text and below-U confidence. Expect rejection and zero
   movement writes.
4. **Silence (ESC-07)**: Provide no recognized speech through the approved capture interval.
   Expect capture termination, zero movement writes, and user notification. This is a proposed
   test, not yet executed; interval and notification details need approval.
5. **Busy state (ESC-05)**: Set action-active state and provide another valid result. Expect no
   second movement write. Feedback and queue semantics remain subject to OPEN-11.
6. **Connection failure (ESC-06)**: Start without a link and inject a runtime disconnect/write
   error. Expect movement blocked, status/failure notification, and an RM-02 record as applicable.
7. **Microphone failure**: Inject unavailable microphone. Expect listening disabled and user
   notification (RFI-01).
8. **UI/event inspection**: Generate accepted, rejected, and communication failure events.
   Verify required fields and displays without inferring physical posture.

## Proposed RR-01 Recognition Trial

Only after the team approves the sample protocol, collect the proposed 100 utterances:
5 users × 10 utterances × 2 repetitions, at 0.5–1 m with noise below 45 dBA. The ten utterances
are not ten distinct command types; the distribution between sitting and standing remains open
under OPEN-05/06. Calculate recognition percentage against H1's proposed 90% target, and report
the outcome as a proposal-based result until the target is approved. Do not fabricate a
distribution or accepted phrase list.

## Proposed RR-02 Timing Assessment

After OPEN-12 and test conditions are approved, measure each valid recognized utterance from
utterance end to controller transmission. Report the percentage meeting H1's proposed 3-second
limit and 95% target; do not treat it as approved acceptance criteria beforehand.

## Physical Verification Boundary

The simulator cannot verify posture, physical latency, actual Bittle model compatibility, or
independent safety intervention. ESC-08 requires a proposed supervised physical test recording
the requested instruction, transmitted command, and observed movement; mark any discrepancy
nonconforming and record it before repetition. Perform no movement tests until OPEN-02 and
OPEN-09/10 are reviewed and RO-01 conditions are met.
