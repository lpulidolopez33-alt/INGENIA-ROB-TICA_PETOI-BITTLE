# Feature Specification: VOICE-BITTLE Voice-Control System

**Feature Branch**: `001-voice-bittle-spec`

**Created**: 2026-10-26

**Status**: Draft

**Input**: User description: "Genera la especificación funcional del sistema VOICE-BITTLE tomando como fuente principal docs/h1/H1.md y respetando la constitución del proyecto. Incluye ESC-01 a ESC-08, NEC-01 a NEC-05 y las categorías RF, RR, RS, RI, RO, RFI, RU, RM y RD. Conserva trazabilidad y criterios verificables, documenta inconsistencias y OPEN-01 a OPEN-12. No modificar H1 ni implementar código; limitarse a H2."

## Clarifications

### Session 2026-10-26

- Q: ¿Qué elementos deben formar parte del sistema de interés (SoI) de VOICE-BITTLE? → A: Mantener la frontera pendiente de decisión del equipo y documentar ambas definiciones del H1. Para planificar pruebas sin robot físico, tratar provisionalmente al Bittle como sistema externo conectado mediante una interfaz, sin considerar resuelta la discrepancia.
- Q: ¿Cómo debe tratarse Vosk, especificado en RD-02, frente a OPEN-03, que dice que la tecnología de reconocimiento aún no está elegida? → A: Mantener documentada la contradicción entre RD-02 y OPEN-03. Vosk es la tecnología propuesta en H1, pero no está aprobada y OPEN-03 permanece abierto hasta que el equipo justifique la selección. La arquitectura H2 debe permitir integrar Vosk sin acoplar el resto del sistema a una tecnología concreta de reconocimiento, manteniendo la trazabilidad con RD-02.
- Q: ¿Cómo debe interpretarse el ensayo de RR-01, que menciona cinco usuarios, 10 órdenes y dos repeticiones, si el alcance actual solo define dos órdenes válidas? → A: Mantener el ensayo de RR-01 como propuesta de 100 muestras (5 usuarios × 10 locuciones × 2 repeticiones), sin interpretar las 10 locuciones como 10 comandos diferentes. El alcance inicial contempla dos órdenes motrices: sentarse y ponerse de pie. Dejar pendiente la distribución exacta de las muestras entre ambas órdenes hasta que el equipo apruebe el vocabulario y el protocolo de ensayo (OPEN-05 y OPEN-06). No modificar el H1 ni considerar aprobado el criterio de rendimiento.
- Q: ¿Cómo debe tratar la especificación los identificadores `REQ-01`–`REQ-12` de la matriz de H1 y los identificadores por categoría `RF`, `RR`, `RS`, `RI`, `RO`, `RFI`, `RU`, `RM` y `RD`? → A: Mantener ambos conjuntos como referencias distintas. Utilizar los identificadores por categoría para los requisitos actuales de la sección 5 de H1 y conservar `REQ-01`–`REQ-12` como referencias históricas de la matriz. No establecer equivalencias nuevas ni asumir correspondencias numéricas. Registrar como actividad pendiente de H2 la elaboración y revisión por el equipo de una matriz de correspondencia. Hasta aprobarla, señalar explícitamente las relaciones no verificadas y no considerar completa la trazabilidad.
- Q: ¿Cómo debe tratar H2 la cobertura de trazabilidad que falta para ESC-07 y ESC-08? → A: Incorporar propuestas de verificación basadas en sus fichas de H1, manteniendo pendientes los enlaces a necesidades NEC y requisitos por categoría. Para ESC-07, proponer una prueba simulada que compruebe que el silencio finaliza la captura sin generar comandos de movimiento y que se informa al usuario. Para ESC-08, proponer una prueba física supervisada que registre la orden solicitada, el comando transmitido y el movimiento observado, marcando como no conforme cualquier discrepancia. No presentar estas pruebas como ejecutadas ni asignar relaciones de trazabilidad sin revisión y aprobación del equipo.

## User Scenarios & Testing

Priorities below reflect the baseline's primary command and safety goals; they do not alter
the H1's priority proposals for stakeholder needs.

### User Story 1 - Request a supported posture (Priority: P1)

The user speaks one of the two supported instructions: «sentarse» or «ponerse de pie».
When the instruction is valid and the robot is ready, the system recognizes it, associates it
with the corresponding supported action (`ksit` or `kup`), and reports its outcome. The
physical result is assessed separately from recognition and transmission.

**Why this priority**: These are the two nominal voice-control scenarios specified by the
project brief and H1.

**Independent Test**: Run each instruction through the recognition-to-command flow with a
simulated serial endpoint. Verify the associated command and reported result; physical posture
confirmation remains a separate H1/H4 activity.

**Acceptance Scenarios**:

1. **Given** the system is listening and the robot link is ready, **When** the user says the
   accepted instruction for sitting with confidence at or above U, **Then** the system maps it
   to `ksit`, transmits the approved action, and records the outcome. (ESC-01; NEC-01; H1 matrix
   legacy REQ-01, REQ-09, REQ-10; category references RF-01–RF-03, RM-01, and RR-01–RR-02
   require crosswalk review.)
2. **Given** the system is listening and the robot is in a state from which `kup` is valid,
   **When** the user says the accepted instruction for standing with confidence at or above U,
   **Then** the system maps it to `kup`, transmits the approved action, and records the outcome.
   (ESC-02; NEC-01; H1 matrix legacy REQ-02; category references require crosswalk review.)
3. **Given** a supported action was transmitted, **When** the command acknowledgement or
   physical outcome has not been independently verified, **Then** the system does not report the
   physical posture as confirmed solely because transmission occurred. (ESC-08; links to needs
   and category requirements are pending team review and approval; H1 does not assign a matrix
   requirement ID to ESC-08.)

### User Story 2 - Reject unsafe or absent instructions (Priority: P1)

The user or nearby person needs the robot to remain still when speech is not a supported command,
the recognition confidence is insufficient, or no speech is captured. The system provides an
appropriate outcome without issuing a movement action.

**Why this priority**: H1 and the Constitution make non-activation for invalid, ambiguous, or
absent instructions a safety baseline.

**Independent Test**: Feed unrecognized, low-confidence, and silent inputs through the flow with
a simulated serial endpoint. Assert that no movement command is transmitted and inspect the
reported and recorded result.

**Acceptance Scenarios**:

1. **Given** the system is listening, **When** it receives an instruction not in the accepted
   vocabulary, **Then** it rejects the input and transmits no movement command. (ESC-03;
   NEC-02, NEC-03; H1 matrix legacy REQ-03, REQ-04, REQ-08.)
2. **Given** an utterance matches a supported instruction but confidence is below U, **When**
   the system evaluates it, **Then** it treats the input as unrecognized and transmits no
   movement command. (ESC-04; NEC-02, NEC-03; H1 matrix legacy REQ-05, REQ-09.)
3. **Given** audio capture is active, **When** no speech is recognized before the H1-defined
   maximum listening interval T_escucha, **Then** capture ends without a movement command and
   the user is informed that no instruction was received. (ESC-07; H1 provides no matrix
   requirement or need mapping; duration and notification form are open.)
4. **Given** the microphone is unavailable, **When** the system attempts to listen, **Then**
   listening is disabled and the failure is reported. (H1 RFI-01; OP-E02. The scenario-to-need
   link is not explicit in the traceability matrix.)

### User Story 3 - Handle busy or disconnected control (Priority: P2)

The user needs predictable behavior if a new instruction arrives while the robot is moving or
if the serial connection is lost. The system must not silently accept an unsafe or untransmittable
action and must expose the relevant outcome.

**Why this priority**: H1 identifies motion overlap and link loss as exceptional conditions
affecting safety and operational feedback.

**Independent Test**: Use simulated movement and connection states. Verify rejection while busy,
blocking new maneuvers after a link fault, status reporting, and fault recording without a
physical robot.

**Acceptance Scenarios**:

1. **Given** an action is in progress, **When** another movement instruction arrives, **Then**
   the system rejects it and does not enqueue or transmit it. (ESC-05; NEC-03, NEC-04; H1
   matrix legacy REQ-06, REQ-08; the reject-versus-queue decision is OPEN-11.)
2. **Given** the serial link fails, **When** a new maneuver is requested, **Then** the system
   blocks the new maneuver and reports the link state or transmission failure. (ESC-06;
   NEC-03, NEC-04; H1 matrix legacy REQ-07; category references RS-02, RI-03, RFI-02.)
3. **Given** the application starts without a robot link, **When** a movement instruction is
   received, **Then** movement instructions remain disabled until communication is established.
   (H1 RO-02; OP-N01.)

### User Story 4 - Understand and review system status (Priority: P2)

The user or operator needs to know whether listening is active, which instructions are
available, the robot/link status, and whether instructions were accepted or rejected. The
operator also needs a record for reviewing failures and unexpected physical results.

**Why this priority**: H1 includes status and history behaviors to support usability,
traceability, and diagnosis.

**Independent Test**: Use simulated application, movement, and connection states to inspect
status, feedback, and event records. This does not establish the physical robot's posture.

**Acceptance Scenarios**:

1. **Given** the system is available, **When** the user reviews its interface, **Then** it
   displays the supported voice instructions and associated actions, whether listening is
   active, the connection state, and movement state as specified by RI-03–RI-05 and RI-07.
   (RI-04–RI-07 lack complete source links and detailed acceptance definitions.)
2. **Given** instruction and fault events have occurred, **When** the user requests history by
   voice, **Then** the interface displays accepted and rejected activity. (H1 RI-06; command
   phrasing, history content, and event coverage require clarification.)
3. **Given** a voice instruction is rejected or a failure occurs, **When** the event is
   reviewed, **Then** the available record includes the fields required by RM-01 or RM-02.
   (NEC-04; H1 matrix legacy REQ-08.)
4. **Given** a physical test produces a posture different from the requested one, **When** the
   operator observes the discrepancy, **Then** the test is recorded as nonconforming with the
   requested instruction, transmitted command, and observed behavior before any repeat trial.
   (ESC-08; physical observation and intervention details remain open.)

### Edge Cases

- Confidence equals U: H1 says confidence equal to or above U is accepted; the value and its
  measurement semantics remain OPEN-04.
- The recognized text is valid but the robot is already moving: reject the new instruction;
  no queue behavior is assumed until OPEN-11 is decided.
- The link fails during a transmission or execution: report the fault, block new maneuvers, and
  record the failure as applicable; do not claim successful physical execution.
- Silence continues through T_escucha: end capture without movement; the interval remains
  unspecified.
- The microphone is unavailable or serial transmission fails: disable listening or report the
  transmission failure, respectively, as specified by RFI-01/RFI-02.
- The physical result is incomplete, absent, or different from the requested posture: mark
  physical verification as failed and record the discrepancy; do not infer posture from sending
  a command.
- A command phrase, operating language, robot model, or starting posture is not yet approved:
  apply no additional interpretation beyond the documented baseline and keep the affected
  behavior unresolved under the corresponding OPEN item.

## Requirements

This H2 specification uses category identifiers RF, RR, RS, RI, RO, RFI, RU, RM, and RD to
identify the current requirements in H1 section 5. It preserves REQ-01–REQ-12 as historical
references used in the H1 section 6.1 matrix. These are distinct identifier sets: no new
equivalences or numeric correspondences are assumed. Creating and reviewing a crosswalk with the
team is an outstanding H2 activity. Until that crosswalk is approved, relationships between
legacy REQ references and current category requirements are unverified and traceability is not
complete. Source operation labels OP-N/OP-E remain where the category tables provide them; their
mapping to ESC identifiers also requires review.

### Functional Requirements

#### RF - Requisitos funcionales

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RF-01 | The system recognizes the voice commands defined in the selected language. | OP-N02, OP-N04 | With an approved vocabulary and labeled input set, verify recognition outcomes. Vocabulary, selected language, and test corpus need OPEN-03/05/06 resolution. |
| RF-02 | The system converts valid movement instructions into instructions compatible with Bittle firmware. | OP-N02, OP-N03 | With simulated serial output, verify sitting maps to `ksit` and standing to `kup`; exact model/protocol compatibility is OPEN-02. |
| RF-03 | Bittle starts the corresponding validated action when it receives each instruction. | OP-N03 | Simulator verifies the intended command is emitted only for a validated instruction; physical action confirmation requires robot testing. |
| RF-04 | The system rejects unknown instructions without sending movement commands. | OP-E01, OP-E02 | Supply unknown input and assert no movement command is written; verify rejection feedback as applicable. |
| RF-05 | The system rejects instructions received while an action is in progress. | Blank in H1 | Simulate an active action, provide another instruction, and assert it is rejected and not sent. |
| RF-06 | The system informs whether each instruction was recognized, rejected, or sent. | OP-N05 | Exercise each available outcome and verify the corresponding user-visible status. Meaning of “sent” versus “executed” must remain distinct. |
| RF-07 | The application allows the active language to be changed between Spanish and English. | H1 refers to a language scenario not yet added | Verify both language selections are available and the displayed active selection changes. Scenario and vocabulary are unresolved. |
| RF-08 | The application ends the session without leaving an active gait, following the validated closing procedure. | OP-N06 | Verify closure follows the documented procedure; that procedure is not specified and must be resolved before a pass/fail test is finalized. |
| RF-09 | Actions, once started, cannot be interrupted by another instruction. | OP-N07 | Simulate an active action and provide a second instruction; verify it cannot interrupt the first. H1 also says RF-05 rejects new instructions; detailed consistency with the rejection behavior requires review. |

#### RR - Requisitos de rendimiento

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RR-01 | Recognize at least 90% of 100 valid instructions in the reference trial: five users, 10 instructions, two repetitions, 0.5–1 m, and noise below 45 dBA. | OP-N02, OP-E02 | Preserve the proposed sample count as 5 users × 10 utterances × 2 repetitions = 100 samples. The initial scope contains two motor instructions (sitting and standing); the distribution of samples between them remains open until the vocabulary and test protocol are approved (OPEN-05, OPEN-06). Calculate correctly recognized valid instructions out of 100 only after that protocol is set. H1 labels the target proposed; OPEN-12 also requires approval before treating it as binding. |
| RR-02 | Process and transmit 95% of valid recognized instructions to the controller within 3 seconds of the end of the utterance. | OP-N02, OP-N03 | Time the specified valid instructions from utterance end to controller transmission. H1 labels the target proposed; OPEN-12 requires review. |
| RR-03 | Voice recognition continues to work without Internet after installation and model download are complete. | OP-N01 | After setup and model download, disconnect Internet and verify recognition remains available. This does not assert offline setup/download. |

#### RS - Requisitos de seguridad

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RS-01 | The system does not start movement for unknown or unvalidated instructions. | OP-E01, OP-E02 | Inject unknown and unvalidated input; verify no movement command is transmitted. |
| RS-02 | The system blocks acceptance of new maneuvers when a serial-link failure is detected. | OP-E03, OP-E04 | Simulate link failure and provide a new maneuver; verify it is blocked and the failure is reported. |
| RS-03 | The operating procedure provides a safety intervention independent of voice recognition and the computer link. | OP-E04, OP-E05 | Review and demonstrate the approved independent intervention procedure. H1 leaves the specific measure open (OPEN-09); no design is invented here. |

#### RI - Requisitos de interfaz

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RI-01 | The system permits serial communication with Bittle through a compatible Bluetooth module. | OP-N01 | Verify the selected module and robot model establish communication; model and compatibility are OPEN-02. |
| RI-02 | The application transmits movements using the Petoi serial protocol. | OP-N02 | With a simulator, verify the approved command token and case-sensitive transmission format against the applicable Petoi protocol documentation. |
| RI-03 | The application displays whether the link with Bittle is active. | OP-N01, OP-E03 | Simulate connected and disconnected states; verify displayed state follows the link state. |
| RI-04 | The interface displays accepted voice instructions and their associated action. | Blank in H1 | Verify each approved instruction/action pair is displayed after OPEN-06 establishes the vocabulary. |
| RI-05 | The interface displays a signal indicating that listening is active. | Blank in H1 | Toggle listening through the available control and verify the signal matches the state. |
| RI-06 | When “Historial” is spoken, the interface displays the history of accepted and rejected activities. | Blank in H1 | After accepted and rejected events, request history and verify both types appear. Exact voice phrase and record fields need clarification. |
| RI-07 | The interface displays information about the robot's movement state. | Blank in H1 | Verify displayed state corresponds to the defined movement state; states and physical-observation source are not defined in H1. |

#### RO - Requisitos operacionales

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RO-01 | Movement tests are performed on a stable, dry, clear surface with in-person supervision. | OP-N03, OP-E05 | Review the test setup and record confirmation of each stated condition before a physical movement trial. |
| RO-02 | On application start, movement instructions remain disabled until communication with Bittle exists. | OP-N01 | Start with no link and verify movement is disabled; establish link and verify the state changes as specified. |

#### RFI - Requisitos de fiabilidad

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RFI-01 | If the microphone is unavailable, the application disables listening and notifies the user. | OP-E02 | Simulate an unavailable microphone; verify listening is disabled and a notification is presented. |
| RFI-02 | When serial transmission errors are detected, the application notifies the user. | OP-E03 | Simulate a transmission error; verify a user-visible notification and the RM-02 fault record. |

#### RU - Requisitos de usabilidad

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RU-01 | The application visibly indicates whether recognition is configured for Spanish or English. | Language scenario not yet added | Select each available language and verify the active language is visibly identified. |
| RU-02 | For an unrecognized instruction, the system asks the user to repeat it. | OP-E01, OP-E02 | Provide unknown input and verify a repeat request is presented. The exact wording/channel is not specified. |
| RU-03 | The user can enable and disable listening through a manual control. | OP-N01, OP-N06 | Operate the manual control both ways and verify listening state changes accordingly. |

#### RM - Requisitos de mantenimiento

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RM-01 | The system records date, time, recognized text, and acceptance or rejection status for each instruction. | OP-N02, OP-E01 | Provide accepted and rejected inputs and inspect each event for the four required fields. |
| RM-02 | The application records communication failures with date, time, and error type. | OP-E03, OP-E04 | Simulate communication failures and inspect each corresponding record for the three required fields. |

#### RD - Requisitos de diseño y restricciones

| ID (H1) | Requirement preserved from H1 | H1 source link | Acceptance evidence |
|---|---|---|---|
| RD-01 | Recognition, interpretation, and instruction-management logic is implemented using Python. | Proposed architecture | Review the design and later implementation against this constraint; this H2 document does not implement code. H1 also records Python 3.6 or later, pyserial 3.5, and the complete OpenCat repository as Petoi Python API prerequisites, not necessarily project-selected versions. |
| RD-02 | Voice recognition uses Vosk with local models for Spanish and English. | Proposed architecture | Vosk remains the H1 proposal, not an approved selection; OPEN-03 remains open until the team justifies its choice. H2 design must permit Vosk integration without coupling the rest of the system to a specific recognition technology. Preserve traceability to RD-02 and do not claim the H1 conflict is resolved. |

### Traceability and Coverage Register

H1 section 6.1 supplies the following historical trace links. They are reproduced as source
data, not treated as a validated mapping to the category IDs above. An H2 activity is to produce
and review a crosswalk between these historical references and current category requirements;
until approved, the links remain unverified and traceability must not be reported as complete.

| Scenario | H1 need links | H1 legacy requirement links | H1 verification proposal |
|---|---|---|---|
| ESC-01 | NEC-01, NEC-05 | REQ-01, REQ-09, REQ-10 | Simulated serial test; physical latency demonstration in H4 |
| ESC-02 | NEC-01, NEC-05 | REQ-02 | Simulated serial test |
| ESC-03 | NEC-02, NEC-03 | REQ-03, REQ-04, REQ-08 | No serial write; feedback demonstration; record inspection |
| ESC-04 | NEC-02, NEC-03 | REQ-05, REQ-09 | Labeled audio set |
| ESC-05 | NEC-03, NEC-04 | REQ-06, REQ-08 | Simulated movement state |
| ESC-06 | NEC-03, NEC-04 | REQ-07 | Simulated serial disconnection |
| Cross-cutting | NEC-03, NEC-05 | REQ-11, REQ-12 | Code inspection; test-case analysis |
| ESC-07 | Not assigned in matrix; pending team review | Not assigned in matrix; pending team review | Proposed simulated test: verify silence ends capture without movement commands and informs the user. Not executed. |
| ESC-08 | Not assigned in matrix; pending team review | Not assigned in matrix; pending team review | Proposed supervised physical test: record requested instruction, transmitted command, and observed movement; mark any discrepancy nonconforming. Not executed. |

H1 states `REQ-01`–`REQ-08` correspond to `RF-01`–`RF-08`, and `REQ-09`–`REQ-12` correspond
to `RNF-01`–`RNF-04`. This is inconsistent with the present category tables: RF-09 exists,
non-functional requirements use several categories (RR, RS, RI, RO, RFI, RU, RM, RD), and no
complete crosswalk to those IDs is supplied. Do not assume that, for example, a legacy REQ number
equals the same-numbered current category ID.

H1 section 6.2 claims there are no scenarios without needs, although its matrix does not list
ESC-07 or ESC-08. This H2 specification preserves both claims as inconsistent and does not
fabricate need or requirement links for those scenarios. The source tables also leave some
element/scenario references blank, use OP-N/OP-E labels rather than ESC identifiers, and omit a
language scenario referenced by RF-07/RU-01.

H2 proposes a simulated silence test for ESC-07 and a supervised physical outcome test for
ESC-08 based on their H1 scenario descriptions. These tests have not been executed. Their
relationships to NEC and category requirements remain unassigned until team review and approval.

### Verification Without the Physical Robot

H1 section 6.3 proposes software-only verification for legacy REQ-01, REQ-02, REQ-03, REQ-05,
REQ-06, REQ-07, REQ-08, REQ-11, and REQ-12 using a simulated serial endpoint. Because the
REQ-to-category crosswalk is incomplete, those legacy IDs MUST remain the source selectors for
that proposal until reconciled.

The specification's software-only acceptance evidence consists of providing controlled
recognized, unrecognized, low-confidence, silence, busy-state, link-state, and serial-error
inputs; observing decisions, output tokens, displayed states, and event records; and asserting
that invalid inputs do not produce movement writes. A simulator can verify data sent and state
handling, but cannot prove actual posture, physical latency, or the independent physical safety
intervention. H1 identifies integration for REQ-04 and REQ-09 and physical observation for
REQ-10 and final confirmation of REQ-01/REQ-02. These distinctions are retained; no test is
claimed complete. For this test-planning purpose only, Bittle is treated as an external system
connected through a simulated interface; this does not decide the SoI boundary disputed between
H1 sections 2.2 and 5.

### Open Questions and Inconsistencies

The following H1 questions remain open and MUST be resolved, or explicitly retained as deferred,
before affected requirements are baselined. This list preserves the H1 question and its
identified impact without selecting an answer.

| H1 ID | Unresolved question / issue | H1 impact or next step |
|---|---|---|
| OPEN-01 | Project OpsCon is unavailable. | Official usage context is missing; request it from course staff. |
| OPEN-02 | Exact Bittle model (legacy, X, or X V2) is unknown. | Check robot label/package; commands, latency, and applicable documentation depend on model. |
| OPEN-03 | Voice-recognition technology is not selected in section 2.4, while RD-02 proposes Vosk with local Spanish and English models. | Compare options in H2 and justify the team's selection before approving Vosk or closing OPEN-03; affects recognition, RR-01, RR-02, and language behavior. |
| OPEN-04 | Confidence threshold U has no value. | Set only after the selected recognition approach is evaluated; affects RF-01/RF-02, rejection, and recognition behavior. |
| OPEN-05 | Acoustic conditions, distance, and reference audio set are not settled. | Define test inputs and operating distance; affects RR-01, recognition performance, and ESC-01 assumptions. |
| OPEN-06 | Exact accepted phrases for each action are undefined. | Define the supported vocabulary; affects RF-01, RF-02, RI-04, and test inputs. |
| OPEN-07 | Target end-user group is not identified. | Consult course staff; may affect NEC-01 and interface design. |
| OPEN-08 | Formal project metadata (document code, authors/company, repository details, H1 commit hash) is incomplete. | Complete the H1 delivery metadata; does not authorize changing H1 in this task. |
| OPEN-09 | Physical safety measures, including clear-zone and manual intervention, are undefined. | Define with course staff before physical testing; affects RS-03 and RO-01. |
| OPEN-10 | `kup` behavior from sitting or lying posture is unverified. | Check documentation and physical tests in H3; affects ESC-02 and RF-03. |
| OPEN-11 | User confirmation and reject-versus-queue behavior are undecided. | Decide in H2 and align scenarios/requirements; affects feedback and busy-state behavior. |
| OPEN-12 | Proposed 2-second values for notification, connection detection, and latency need validation. | Validate with course staff and physical tests; do not treat as approved thresholds yet. |

## Key Entities

- **Voice instruction**: Captured user input and its recognized text, language, and confidence
  where available. The accepted phrases and confidence threshold remain open.
- **Supported action**: The intended posture action associated with an approved instruction;
  current baseline examples are sitting (`ksit`) and standing (`kup`).
- **Instruction outcome**: Whether an input was recognized, rejected, sent, or failed. These
  states must not be conflated with observed physical execution.
- **Connection state**: Whether communication with Bittle is active or has failed.
- **Event record**: Date, time, recognized text, acceptance/rejection status, or communication
  failure details as required by RM-01 and RM-02.
- **Verification result**: Evidence for a software, integration, or physical test, including
  scenario, requirement source ID, outcome, and any observed discrepancy. The exact record
  format is not specified by H1.

## Success Criteria

### Measurable Outcomes

- **SC-001**: The specification represents all eight H1 scenarios (ESC-01–ESC-08), all five
  stakeholder needs (NEC-01–NEC-05), and all nine requirement categories with their H1
  identifiers. Verify by coverage review against H1.
- **SC-002**: Each of the 33 category requirements in H1 has a source ID, preserved statement,
  source link/status, and acceptance evidence or an explicit unresolved criterion. Verify by
  counting and cross-checking: RF 9, RR 3, RS 3, RI 7, RO 2, RFI 2, RU 3, RM 2, RD 2.
- **SC-003**: In software-only scenarios for which H1 specifies simulated verification, every
  invalid, low-confidence, silent, busy, or disconnected case produces no unauthorized movement
  write; every expected event is observable in the simulated endpoint or event record.
- **SC-004**: The traceability review identifies the legacy REQ-to-category mismatch and
  explicitly labels ESC-07 and ESC-08 as absent from the H1 traceability matrix; neither issue
  is silently treated as closed.
- **SC-005**: Recognition trial planning preserves the proposed RR-01 structure of five users,
  10 utterances, and two repetitions (100 samples); the distribution of utterances between the
  two supported instructions remains unsettled until OPEN-05/OPEN-06 and the test protocol are
  approved. Recognition and timing results are reported against H1's proposed thresholds only
  after OPEN-03, OPEN-05, OPEN-06, and OPEN-12 have been reviewed; no proposed value is described
  as an approved target before that review.
- **SC-006**: Physical posture correctness, physical latency, and independent safety
  intervention are not marked verified by software-only tests.

## Assumptions

- H1 (`docs/h1/H1.md`) is the primary source; this specification does not amend it.
- The current voice-action baseline is limited to sitting (`ksit`) and standing (`kup`), plus
  safe rejection and the additional H1 behaviors. Other Petoi skills are not added as voice
  commands.
- The confidence threshold U, vocabulary, acoustic test conditions, target user, exact model,
  intervention procedure, and unresolved UI details remain open where H1 says so.
- H1's proposed 90%/100-sample recognition trial and 95%/3-second transmission target are
  retained as proposed source criteria, not newly approved commitments. The 100 samples mean
  five users × 10 utterances × two repetitions, not 10 distinct commands; the distribution
  between the two supported instructions remains open under OPEN-05/OPEN-06.
- Python remains an H1 RD constraint. Vosk remains the RD-02 proposal, not an approved
  technology selection, until the project resolves OPEN-03.
- No robot is required for the software-only verification cases. Physical outcome verification
  remains necessary where H1 explicitly requires observing Bittle.
- The SoI boundary remains undecided because H1 sections 2.2 and 5 differ. A simulated external
  Bittle interface is a provisional test-planning convention only and does not resolve that
  system-scope decision.
- Feature development or implementation is outside this H2 specification task.
