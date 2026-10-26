# Tasks: VOICE-BITTLE Voice-Control System

**Input**: Design documents in `specs/001-voice-bittle-spec/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`,
`contracts/interfaces.md`, and `quickstart.md`

**Scope**: This is a future work plan for H2, H3, and H4. Every task starts unchecked because it
has not yet been performed. H2 tasks are documentation and decisions only. H3 tasks cover future
implementation and software-only verification. H4 tasks cover physical integration and
verification. Do not treat proposed technology or performance values as approved.

**Tests**: Automated and simulated tests are included because the feature specification and user
explicitly request verification without physical hardware.

**Implementation path note**: H3 paths below are proposed task targets, not existing source
directories or an architecture approval. Phase 2 must confirm the implementation layout, runtime,
UI platform, and test runner after prerequisite decisions; if the team chooses different paths,
revise the affected H3 tasks before executing them. Do not create code during H2.

**Task ordering**: Task IDs are stable references, not an execution sequence. Execute tasks
according to their phase and explicit dependencies; tasks may appear out of numerical order.

## Phase 1: Setup and H2 Decision Preparation

**Purpose**: Establish a reviewed record of constraints and execution gates without installing
dependencies, changing H1, or implementing code.

- [ ] T001 [P] Inventory the selected development computer, operating system, installed Python versions, and Petoi Python API prerequisites in `specs/001-voice-bittle-spec/environment-decision.md`; record Python 3.6+ and pyserial 3.5 as H1 API prerequisites, not as an approved project environment (H1 CTX-03, RD-01; OPEN-02/03).
- [ ] T002 Create an H2 decision register in `specs/001-voice-bittle-spec/decision-log.md` listing OPEN-01 through OPEN-12 verbatim or faithfully summarized, owner/status, required evidence, and whether each is resolved or explicitly deferred; do not close any item without team evidence (H1 section 7; Constitution VI).
- [ ] T003 [P] Record the development and validation stages in `specs/001-voice-bittle-spec/stage-gates.md`, separating H2 documentation/approval, H3 implementation and simulated tests, and H4 physical integration; explicitly prohibit treating planned tests as executed (Constitution IV; NEC-05).

---

## Phase 2: Foundational H2 Decisions (Blocks H3)

**Purpose**: Complete or formally defer decisions that affect module boundaries, requirements,
test inputs, and future source layout. No code is created in this phase.

- [ ] T004 [P] Document both SoI descriptions from H1 sections 2.2 and 5 in `specs/001-voice-bittle-spec/system-boundary.md`; record Bittle as external only for simulator planning and keep the formal boundary unresolved until the team decides (spec clarification Q1; OPEN-01/02).
- [ ] T005 Prepare a category-to-legacy identifier crosswalk in `specs/001-voice-bittle-spec/traceability-crosswalk.md` using H1 section 6.1 and section 5; preserve RF/RR/RS/RI/RO/RFI/RU/RM/RD as current IDs and REQ-01–REQ-12 as historical IDs, mark each unsupported link “unverified,” and request team review without assuming numeric equivalence (spec clarification Q4; H1 sections 5–6).
- [ ] T006 Record the approved command vocabulary, language behavior, confidence threshold U, RR-01 sample-distribution protocol, and RR-02 timing protocol or explicit deferrals in `specs/001-voice-bittle-spec/decision-log.md`; do not invent phrases, divide RR-01 samples, set U, or treat proposed performance targets as approved without team evidence (OPEN-03–OPEN-06/12; RF-01/02/07; RR-01/02).
- [ ] T007 Reconcile H1 RF-05 and RF-09 with OPEN-11 in `specs/001-voice-bittle-spec/decision-log.md`, specifying the reviewed behavior for instructions during an active movement and whether any queuing is allowed; until approved, retain “do not transmit a second movement instruction” as the safety rule (ESC-05; RF-05/09; RS-01; OPEN-11).
- [ ] T008 Record approved handling for the language-selection scenario, history request, movement-state display, and close-session procedure in `specs/001-voice-bittle-spec/decision-log.md`, or explicitly defer each missing detail without inventing UI behavior (RF-06–RF-08; RI-04–RI-07; RU-01; OPEN-06/07/11).
- [ ] T009 Confirm the proposed H3 source/test paths, UI platform, Python runtime, test runner, dependency-manifest path/format, and explicitly approved dependencies in `specs/001-voice-bittle-spec/implementation-layout.md`; do not select a runtime incompatible with the approved recognition provider or H1 Petoi API prerequisites, and update this task list if paths differ (OPEN-02/03; plan.md Technical Context).
- [ ] T010 Review the 33 category requirements and H2 verification criteria against `specs/001-voice-bittle-spec/spec.md`; record requirement wording gaps, blank H1 links, and explicit approvals/deferrals in `specs/001-voice-bittle-spec/requirements-review.md` without modifying `docs/h1/H1.md` (RF-01–RF-09; RR-01–RR-03; RS-01–RS-03; RI-01–RI-07; RO-01–RO-02; RFI-01–RFI-02; RU-01–RU-03; RM-01–RM-02; RD-01–RD-02).

**H3 entry gate**: T004–T010 must be reviewed by the team. Any unresolved decision that affects a
specific story remains a blocker for that story; document deferrals and do not silently assume an
answer.

### H3 Environment Preparation (shared prerequisite)

Complete this task after H2 technical decisions and before implementing any H3 story. It does not
approve dependencies on its own.

- [ ] T047 Create the project virtual environment in `.venv/` and prepare the approved Python dependency manifest at the path selected by T009 (for example, root `requirements.txt`); install only dependencies explicitly approved in T009, and leave unapproved providers such as Vosk out (RD-01/02; OPEN-03).

---

## Phase 3: User Story 1 - Request a Supported Posture (Priority: P1, H3)

**Goal**: Recognize an approved instruction for sitting or standing, map it to the corresponding
Petoi action, and distinguish recognition/transmission from physical confirmation.

**Independent Test**: With a deterministic recognition result and simulated serial endpoint,
verify approved sitting maps only to `ksit`, approved standing maps only to `kup`, and each
outcome is recorded after OPEN-04 defines U and T019/T048 authorize transmission. Before then,
verify phrase-to-action mapping only; no motor command may be transmitted. This does not verify
physical posture.

### Implementation and verification

- [ ] T011 [US1] Create the provider-neutral recognition result contract in `src/voice_bittle/recognition/contracts.py`, returning normalized text, language, confidence, and explicit no-result/failure outcomes; keep engine-specific objects out of command interpretation (RD-02; RF-01; OPEN-03).
- [ ] T012 [P] [US1] Implement the recognition provider adapter boundary in `src/voice_bittle/recognition/provider.py` and a deterministic fake provider in `tests/fakes/recognition_provider.py`; leave a Vosk adapter disabled/unselected until T006 records team approval (RD-02; RF-01; RR-03; OPEN-03).
- [ ] T013 [US1] After T006 approves the vocabulary, implement phrase-to-action mapping in `src/voice_bittle/commands/command_mapper.py`: map approved sitting and standing phrases to semantic actions `sit` and `stand`, respectively. This task only maps phrases to semantic actions; it does not map Petoi tokens, validate confidence, or transmit commands (ESC-01/02; NEC-01; RF-02).
- [ ] T014 [US1] Define an explicit action-to-token mapping and allowlist at the Petoi command boundary in `src/voice_bittle/commands/petoi_commands.py`, mapping only `sit` to `ksit` and `stand` to `kup`; prevent recognized text from becoming a raw serial payload (RF-02; RI-02; RS-01).
- [ ] T015 [P] [US1] Add automated tests for the recognition result contract and fake provider in `tests/unit/recognition/test_provider_contract.py`, covering recognized text, confidence, no-result, and provider failure (RF-01; ESC-01–04). The silence test for ESC-07 is specified separately from this contract test and has no assigned need/category link pending team review.
- [ ] T016 [US1] Add automated tests for the approved sitting/standing phrase-to-semantic-action mapping in `tests/unit/commands/test_command_mapper.py`, asserting `sit`/`stand`; also verify the T014 boundary maps only those actions to `ksit`/`kup`. Use the approved vocabulary from T006 and do not substitute invented phrases (ESC-01/02; NEC-01; RF-02).
- [ ] T017 [US1] Connect actions to the serial adapter in `src/voice_bittle/commands/action_dispatcher.py` only after T013 maps the phrase, T014 allowlists the token, and T019 confirms approved-vocabulary membership plus a passing T048 confidence result; while OPEN-04 leaves U unapproved, fail closed and do not transmit any motor command. Record “sent” separately from “physically confirmed” (ESC-01/02; RF-03/06; NEC-01; RS-01).
- [ ] T018 [US1] Create the initial simulated serial endpoint in `tests/fakes/serial_endpoint.py` and add an integration test in `tests/integration/test_supported_postures.py` that, after OPEN-04 is approved and T013/T014/T019/T048 pass, captures writes for sitting and standing and verifies one approved token per accepted action with no physical-success assertion (ESC-01/02; NEC-01/05; RF-02/03; RI-02).

**Checkpoint**: The two approved semantic actions can be verified independently against a
simulated serial endpoint; no physical outcome is claimed.

---

## Phase 4: User Story 2 - Reject Unsafe or Absent Instructions (Priority: P1, H3)

**Goal**: Ensure unknown, insufficient-confidence, silent, or unavailable-microphone input
cannot result in movement.

**Independent Test**: Supply unknown text, confidence below the approved U, no-result/silence,
and microphone failure; assert zero movement writes and verify required feedback/events.

### Implementation and verification

- [ ] T019 [US2] Implement the authorization gate in `src/voice_bittle/commands/command_validator.py`: reject phrases outside the vocabulary approved in T006 and authorize a phrase only when the independent T048 confidence result is passing; if OPEN-04 has not approved U or T048 has no passing result, fail closed and do not authorize motor transmission. This task consumes the recognition result directly and does not depend on T013, avoiding a US1/US2 cycle (ESC-03/04; NEC-02/03; RF-04; RS-01; OPEN-04/06).
- [ ] T020 [US2] Add a standalone authorization-boundary test in `tests/integration/test_unknown_command_rejection.py` for an unknown phrase, using a spy action sink to assert rejection, a request for the user to repeat it, and zero movement requests/writes; run after T019 without depending on T017/T018 or OPEN-04 (ESC-03; NEC-02/03; RF-04; RS-01; RU-02).
- [ ] T048 [US2] Once OPEN-04 defines and approves U, implement independent confidence-threshold validation in `src/voice_bittle/commands/confidence_validator.py` for a recognition result; return an explicit passing/failing result for comparison with the approved threshold and do not perform vocabulary membership validation here. T048 depends on T006 and OPEN-04, not T019 (ESC-04; NEC-02/03; RF-04; RS-01; OPEN-04/06).
- [ ] T021 [US2] Implement silence timeout outcome handling in `src/voice_bittle/audio/capture_session.py`, ending capture after the approved T_escucha interval without producing a movement request (ESC-07; acceptance proposal in spec.md; interval approval required).
- [ ] T022 [P] [US2] Add the proposed automated simulated silence test in `tests/integration/test_silence_rejection.py` based on the ESC-07 scenario description, asserting capture ends, no movement token is written, and the user is notified; keep the test proposed until executed in H3 and leave all NEC/category links pending team review and approval.
- [ ] T023 [US2] Handle unavailable microphone in `src/voice_bittle/audio/capture_session.py` by disabling listening and exposing an explicit failure outcome to the interface (RFI-01; OP-E02).
- [ ] T024 [US2] Add an automated test in `tests/integration/test_low_confidence_rejection.py` using an otherwise approved phrase below the team-defined U; after T048 and OPEN-04 approval, assert rejection and zero movement writes, independently of unknown-vocabulary rejection (ESC-04; NEC-02/03; RF-04; RS-01; OPEN-04/06).
- [ ] T050 [P] [US2] Add an independent automated microphone-failure test in `tests/integration/test_microphone_unavailable.py`; assert listening is disabled and failure feedback is reported, without depending on the confidence threshold U (RFI-01; OP-E02).

**Checkpoint**: Invalid, low-confidence, absent, and microphone-failure cases produce no movement
write in simulation; actual acceptance awaits execution and review.

---

## Phase 5: User Story 3 - Handle Busy or Disconnected Control (Priority: P2, H3)

**Goal**: Gate commands on readiness, active movement, and serial-link state; report failures
without claiming physical execution.

**Independent Test**: Inject not-connected, active-action, disconnect, and write-error states
into a simulated endpoint; verify gating, outcome status, and error records.

### Implementation and verification

- [ ] T025 [US3] Implement robot/listening/action state transitions in `src/voice_bittle/state/state_manager.py`, disabling movement before connection and after detected link failure and denying new movement requests while an action is active (ESC-05/06; NEC-03/04; RF-05/09; RO-02; RS-02; OPEN-11).
- [ ] T026 [US3] Implement the serial adapter interface and production boundary in `src/voice_bittle/robot/serial_adapter.py`, reporting connection and transmission outcomes and accepting motor tokens only from the T017 dispatcher after T019 vocabulary authorization and a passing T048 confidence result; do not expose a dispatch path that bypasses those checks (ESC-01/02/06; RI-01/02/03; RFI-02; RS-02; OPEN-02/04/06).
- [ ] T027 [P] [US3] Extend the simulated serial endpoint in `tests/fakes/serial_endpoint.py` with controllable connected/disconnected and write-success/write-error states and a captured-write list (NEC-05; ESC-06; RI-02/03; RFI-02).
- [ ] T028 [US3] Add automated state-manager tests in `tests/unit/state/test_state_manager.py` for startup without connection, active action, link loss, and denied new action; do not implement queueing or interruption behavior beyond T007's approved decision (ESC-05/06; RF-05/09; RO-02; RS-02; OPEN-11).
- [ ] T029 [US3] Add serial failure integration tests in `tests/integration/test_serial_failures.py`, injecting disconnection and write failure and asserting commands remain blocked, failure outcomes are surfaced, and no success-shaped fallback is emitted (ESC-06; NEC-03/04; RS-02; RFI-02).
- [ ] T030 [US3] Implement session close behavior in `src/voice_bittle/state/session_shutdown.py` only after the closing procedure is defined and approved in T008; verify no active gait is left according to the approved procedure (RF-08; OP-N06).

**Checkpoint**: Simulator proves readiness and link-failure gating; physical robot behavior is not
inferred.

---

## Phase 6: User Story 4 - Understand and Review System Status (Priority: P2, H3)

**Goal**: Present listening, language, connection, instruction, and movement status; provide
history and auditable instruction/failure records.

**Independent Test**: Drive UI and event recording with simulated accepted, rejected, connection,
and movement-state events; verify displayed outcome and the exact H1-required event fields.

### Implementation and verification

- [ ] T031 [US4] Implement instruction and communication event records in `src/voice_bittle/events/event_recorder.py` with required fields “date, time, recognized text, acceptance or rejection status” for each instruction and “date, time, error type” for communication failures (RM-01/02; NEC-04).
- [ ] T032 [US4] Implement user-visible listening, active-language selection between Spanish and English, supported instruction/action pairs, link, movement, recognition, rejection, and transmission status in `src/voice_bittle/ui/status_view.py`, using only behavior approved in T008 and distinguishing sent from physically confirmed (RF-06/07; RI-03–RI-05/RI-07; RU-01/02).
- [ ] T033 [US4] Implement manual listening enable/disable and history request handling in `src/voice_bittle/ui/user_controls.py` according to the behavior approved in T008, without inventing a new voice phrase or confirmation flow (RI-06; RU-03; OPEN-06/11).
- [ ] T034 [P] [US4] Add automated event-record tests in `tests/unit/events/test_event_recorder.py`, verifying the required RM-01/RM-02 fields for accepted/rejected instructions and communication failures (NEC-04; RM-01/02).
- [ ] T035 [US4] Add simulated UI integration tests in `tests/integration/test_status_and_history.py` for listening/link/language/outcome/history states, and verify no command transmission is described as a confirmed posture (RF-06/07; RI-03–RI-07; RU-01–03).
- [ ] T036 [US4] Add the operator-entered physical discrepancy record in `src/voice_bittle/events/physical_verification_record.py` with “requested instruction, transmitted command, and observed movement” and a nonconforming result for any discrepancy; base the proposed check on the ESC-08 scenario description and leave all NEC/category links pending team review and approval.

**Checkpoint**: Simulated events are visible and auditable; ESC-08 physical observations remain
an operator activity and are not simulated as proof.

---

## H3 Preliminary RR-02 Simulation Measurement

This is a software-path measurement only. It precedes H4 hardware integration and cannot
demonstrate physical-controller latency or compliance with RR-02.

- [ ] T049 After T047 and the H3 recognition-to-simulator path (T011–T018 and T026) are complete, collect preliminary utterance-end-to-simulated-controller-write latency samples and record them in `specs/001-voice-bittle-spec/performance-results.md`; report observations only, without claiming physical-controller performance or RR-02 compliance, and keep the RR-02 target and OPEN-12 pending (RR-02; OPEN-12).

---

## Phase 7: H4 Physical Integration and Verification

**Purpose**: Perform hardware-dependent tasks only after H2 gates and H3 simulated validation.

- [ ] T037 Verify the actual Bittle model, board/firmware documentation, compatible serial/Bluetooth connection, and `ksit`/`kup` token behavior; record evidence in `specs/001-voice-bittle-spec/hardware-verification.md` before enabling physical commands (OPEN-02/10; RI-01/02; ESC-01/02).
- [ ] T038 Review and approve the independent intervention procedure, test-zone criteria, and in-person supervision record in `specs/001-voice-bittle-spec/physical-safety-approval.md` before moving Bittle (OPEN-09; RS-03; RO-01).
- [ ] T039 Conduct supervised ESC-01/02 physical trials only after T037–T038 and only through the T017 dispatch path after T019/T048 authorize the instruction; record requested phrase, transmitted token, observed posture, and outcome in `specs/001-voice-bittle-spec/physical-test-results.md`; mark each trial result only after execution (ESC-01/02; NEC-01; RF-03; OPEN-04/10).
- [ ] T040 Conduct the proposed supervised test based on the ESC-08 scenario description after T037–T038 and using the T017 dispatch path only after T019/T048 authorize the instruction; record requested instruction, transmitted command, observed movement, and conformance result in `specs/001-voice-bittle-spec/physical-test-results.md`, marking any discrepancy nonconforming before a repeat (ESC-08; physical acceptance evidence only; no NEC/category link until team approval).
- [ ] T041 After T037, T038, and the H3 checkpoint T049, measure utterance-end-to-transmission latency during integration with the physical Bittle controller through the T017 validated dispatch path; record observations in `specs/001-voice-bittle-spec/performance-results.md`. This H4 evidence is distinct from the simulator measurement and does not establish physical posture. Keep results descriptive unless the RR-02 objective and OPEN-12 are approved; do not present the proposed 95%/3-second target as accepted (RR-02; OPEN-02/04/09/10/12; H1 section 6.3).

---

## Phase 8: Polish, Performance, and Traceability Closure

**Purpose**: Reconcile evidence, preserve open decisions, and review cross-cutting acceptance
before any release decision.

- [ ] T042 Run the approved RR-01 trial only after T006 approves the vocabulary, sample allocation, audio set, and conditions; record the proposed 100 samples as “5 users × 10 utterances × 2 repetitions,” with distribution between `ksit` and `kup` explicitly approved, in `specs/001-voice-bittle-spec/performance-results.md` (RR-01; OPEN-03/04/05/06/12).
- [ ] T043 Verify offline recognition after installation/model download under the approved provider/model selection and record observed conditions in `specs/001-voice-bittle-spec/offline-validation.md`; do not claim offline setup or model download unless separately tested (RR-03; RD-02; OPEN-03).
- [ ] T044 Review each scenario ESC-01–ESC-08 against NEC-01–NEC-05, current category IDs, and the approved historical REQ crosswalk; update `specs/001-voice-bittle-spec/traceability-crosswalk.md` only with team-approved links and retain gaps as unverified (H1 sections 6.1–6.2; all categories; NEC-05).
- [ ] T045 Review all OPEN-01–OPEN-12 against `specs/001-voice-bittle-spec/decision-log.md`, preserving unresolved entries and attaching evidence/approval references before declaring affected requirements baselined (Constitution III/VI; all scenarios and requirements).
- [ ] T046 Review release evidence and the test results in `specs/001-voice-bittle-spec/validation-summary.md`, separating planned, simulated, integration, and physical tests; do not mark a criterion passed without recorded evidence or describe proposed RR targets as approved without team approval (Constitution IV; SC-001–SC-006).

## Dependencies and Execution Order

### Phase dependencies

- **Phase 1 (H2 preparation)**: Independent documentation tasks; no code or installation.
- **Phase 2 (H2 foundational decisions)**: Depends on Phase 1. T004–T010 gate the affected H3
  stories. OPEN items may remain deferred only if their impacts are isolated and documented.
- **H3 environment preparation (T047)**: Depends on T009; complete before H3 implementation tasks.
- **Phase 3 (US1, H3)**: Mapping tasks depend on T006/T009/T047 and approved phrase/technology
  boundaries. The dispatcher task T017 additionally depends on T013, T014, T019, and T048; no
  command is transmitted until vocabulary and confidence validation pass.
- **Phase 4 (US2, H3)**: Depends on T006/T009/T047 and the recognition result contract from US1
  (T011/T012), but not on completion of US1 or T013. T048 depends on T006 and approval of OPEN-04;
  T019 consumes its result and therefore cannot authorize a phrase without T048's passing result.
  The unknown-phrase check can reject without U, but no motor command is authorized while U is
  unapproved. Microphone failure testing (T023/T050) does not depend on U.
- **Phase 5 (US3, H3)**: Depends on T007/T009 and the fake serial endpoint contract.
- **Phase 6 (US4, H3)**: Depends on T008/T009 plus status/outcome events from the applicable
  stories.
- **H3 preliminary RR-02 checkpoint (T049)**: Depends on T047 and H3 simulator-path tasks
  T011–T018/T026, and must precede Phase 7 physical integration.
- **Phase 7 (H4)**: Depends on H3 integration and simulated validation, including T049 where
  applicable, plus T037/T038 safety gates.
- **Phase 8 (polish)**: Depends on the relevant H3/H4 evidence and team decisions.

### User story dependencies

- **US1 (P1)**: Recognition-to-action mapping increment; mapping can be checked independently
  after T006, but dispatch through the serial simulator waits for the US2 authorization gate
  (T019/T048) and cannot transmit while U remains unapproved.
- **US2 (P1)**: Uses the provider result contract (T011/T012), not completion of US1. Vocabulary
  rejection can be tested without U; confidence validation and the below-U test wait for
  OPEN-04/T048. Silence and microphone-failure cases have separate simulated acceptance checks.
- **US3 (P2)**: Uses action/state and serial interfaces; independent acceptance is no new
  movement write while unready, busy, or disconnected.
- **US4 (P2)**: Uses outcome/state events from US1–US3; independent acceptance is verified
  status and event fields driven by fixtures.

### Parallel opportunities

- **Phase 1**: T001 and T003 can proceed in parallel; T002 is the shared OPEN register and should
  be established before decisions are recorded.
- **Phase 2**: T004 and T005 can be drafted in parallel after T002. T006–T008 all update
  `decision-log.md`, so coordinate those edits through one writer; T009 layout selection gates
  affected implementation.
- **US1/US2 shared command path**: T013 follows T006; T019 depends on T006 and the provider
  result (T011/T012) and consumes T048's passing result, but not T013. T048 depends on T006 and
  OPEN-04, not T019. T017 follows T013, T014, T019, and T048; T018 follows T017. This is a one-way
  validation-to-dispatch dependency, not a US1/US2 cycle.
- **US1**: T015 can proceed in parallel with mapping work after the provider contract is stable;
  T016 follows T013/T014; T018 follows T017 and creates the serial simulator used by later tests.
- **US2**: T020 follows T019 and uses a spy action sink, so unknown-phrase rejection does not
  depend on T017/T018 or U. T024 follows T048 and OPEN-04. T050 follows T023 and is independent
  of U/T048. T022 is a separate scenario-derived test proposal without NEC/category links.
- **US3**: T027 can proceed in parallel with state-manager design; T028/T029 require T025–T027.
- **US4**: T034 can proceed alongside UI design; T035 requires T031–T033.
- **Between stories**: Story coding can be split after Phase 2, but US2/US3/US4 depend on shared
  contracts from US1 and Phase 2; do not treat them as fully independent until those contracts
  are stable.

## Parallel Example: User Story 1

```text
After the Phase 2 contract and path decisions are approved:
1. Implement the provider boundary and deterministic fake (T011–T012).
2. In parallel, draft the provider-contract tests (T015) against the agreed result shape.
3. Implement approved-phrase mapping (T013) and the command allowlist (T014); neither task
   authorizes transmission.
4. Implement confidence validation (T048) and then the US2 vocabulary/confidence authorization
   gate (T019), with U approved before any valid motor command can be authorized.
5. Add the mapping tests (T016), then dispatch through the serial boundary (T017) only after
   the authorization gate passes.
6. Verify the full vertical slice with the simulator (T018) after OPEN-04 is approved.
```

## Parallel Example: User Story 2

```text
After T006/T009/T047 and the required vocabulary decisions:
1. Implement the independent confidence result (T048) once OPEN-04 defines U.
2. Implement the fail-closed authorization gate (T019) using the approved vocabulary and the
   passing result from T048; its unknown-phrase rejection case can be tested without OPEN-04, but
   it must not authorize motor transmission until U is approved.
3. Implement silence and microphone-failure outcomes (T021, T023), and prepare the separate
   ESC-07 scenario-derived silence test proposal (T022) without assigning its unapproved trace links.
4. Add the below-U test (T024) and the independent microphone-failure test (T050); only T024
   depends on OPEN-04.
5. Verify the applicable rejection paths produce zero movement writes through the simulator.
```

## Implementation Strategy

1. Complete H2 decision-preparation and review tasks first. Keep OPEN-01–OPEN-12 visible; record
   approvals or deferrals rather than filling gaps by assumption.
2. Establish the environment with T047 only after the project Python version, provider decision,
   UI platform, and test runner are compatible and approved. Install only approved dependencies;
   do not treat Vosk, PyPI dependencies, or performance targets as approved prematurely.
3. Treat the US1 recognition and mapping work (T011–T016) as the first functional increment.
   Serial dispatch and its simulator check (T017/T018) are gated by the US2 authorization checks;
   no motor command may be sent until U is approved and the confidence gate passes.
4. Define the complete challenge MVP as the two approved actions plus US2's essential
   unknown-input rejection path (T019/T020): unknown phrases yield an explicit rejection/repeat
   outcome and zero simulated movement writes. A valid motor command remains blocked until
   OPEN-04 defines U and the confidence gate passes. Silence, microphone-failure handling
   (T021–T024/T050), US3, US4, and physical movement remain outside this MVP and are required
   for the broader scope.
5. Add the remaining US2 safety cases, then US3 state/link handling and US4 user feedback and
   event records, each with its independent simulated acceptance evidence.
6. Proceed to H4 only after the physical model, protocol compatibility, intervention procedure,
   and test setup are confirmed.
7. Finish with approved RR-01/RR-02/RR-03 validation and a reviewed traceability crosswalk.
   Planned activities remain unchecked until actually completed and evidenced.
