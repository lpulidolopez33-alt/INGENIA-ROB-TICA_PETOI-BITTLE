<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- Safety Before Motion -> Safety and Fail-Safe Behavior
- Voice-First Reliability -> Voice-First Reliability (expanded)
- Evidence-Driven Validation -> Verifiability
- Traceability and Change Control -> Traceability and Version Control
- Simplicity and Maintainability -> Modular Design and Maintainability
Added principle: Explicit Uncertainty Management
Modified sections: Operational Constraints -> H1 Baseline and Technology Constraints; Development Workflow -> Development Workflow and H1 Inconsistency Register
Added sections: H1 Inconsistency Register; H2 Stage Boundary
Removed sections: none
Deferred items: Reconcile the H1 identifier and scenario-coverage inconsistencies; resolve OPEN-01 through OPEN-12 through the project's planned reviews.
-->

# VOICE-BITTLE Constitution

## Core Principles

### I. Safety and Fail-Safe Behavior
The system MUST send a movement command only after an input has been recognized as an approved
voice instruction, validated, and mapped to an allowed Petoi action. Unrecognized input, low
confidence, silence, a microphone fault, or a serial-link fault MUST NOT cause a new movement
command. Physical tests MUST follow the H1 constraint for a stable, dry, clear surface and
in-person supervision. The independent safety intervention required by RS-03 MUST NOT depend on
voice recognition or the computer link. These rules prioritize prevention of unintended motion;
they do not define an unapproved emergency-stop design.

### II. Voice-First Reliability
The system MUST treat voice recognition, command interpretation, validation, feedback, and
transmission as a reliability chain. Each input MUST result in an observable accepted, rejected,
or failed outcome consistent with the H1 requirements; an issued command MUST NOT be reported as
proof of the correct physical result. Recognition and command rules MUST be tested against the
approved vocabulary and the applicable scenarios. This preserves the project's voice-control
purpose while distinguishing recognition, transmission, and physical execution.

### III. Traceability and Version Control
Project decisions and changes MUST remain traceable to H1, the applicable scenario, stakeholder
need, requirement identifier, verification evidence, and reviewed revision wherever those links
are defined. The baseline comprises all eight scenarios ESC-01 through ESC-08, all five needs
NEC-01 through NEC-05, and requirements in each H1 category: RF, RR, RS, RI, RO, RFI, RU, RM,
and RD. A change to behavior, command mapping, safety, or acceptance criteria MUST identify its
impact on this baseline. The team MUST use version control to preserve reviewable changes and
identify the source revision used for decisions. When identifiers or links conflict, the
inconsistency MUST be recorded and resolved through review; no implicit crosswalk or silent
renumbering is permitted.

### IV. Verifiability
Each requirement taken forward MUST have a defined verification method and observable pass/fail
evidence appropriate to its type. Verification planning MUST cover nominal, alternative, and
exceptional behavior, including all eight H1 scenarios. A command being recognized or transmitted
is not proof that the robot achieved the intended physical result; ESC-08 requires observed
outcome and discrepancy recording. H1's proposed numerical targets remain proposals until
explicitly reviewed and approved; tests MUST NOT be reported as passed when they have only been
planned.

### V. Modular Design and Maintainability
The specification and subsequent design MUST distinguish voice capture and recognition, command
interpretation and validation, user feedback and event records, and the Petoi serial interface
well enough that each responsibility and boundary can be reviewed and verified. This separation
MUST NOT introduce ungrounded implementation requirements or change the scope stated in H1.
Python, pyserial, PetoiRobot, Vosk, and the Petoi protocol are handled according to the baseline
and the uncertainty register below; this principle does not mandate a new architecture or
component beyond what H1 supports.

### VI. Explicit Uncertainty Management
Assumptions, unresolved decisions, proposed thresholds, and risks MUST remain explicitly labeled
with their H1 OPEN identifiers or an approved successor. Planning MUST identify the evidence and
review needed to resolve each item before relying on it as a settled design constraint. Where
sources disagree, the constitution MUST preserve the disagreement until an authorized project
review resolves it. Uncertainty MUST NOT be converted into a factual claim or silently hidden.

## H1 Baseline and Technology Constraints
H1 is the primary source for this constitution. Its scope includes the system's voice-to-command
path and the specified Petoi Bittle actions: sentarse mapped to `ksit` and ponerse de pie
mapped to `kup`. Only these documented voice actions are in the current baseline; other
documented Petoi skills are not thereby authorized as voice commands.

The following technology facts and constraints are recorded in H1 and MUST be preserved without
silently broadening them:
- The Petoi serial protocol uses case-sensitive ASCII tokens; H1 identifies `ksit` and `kup` as
  the commands for the two nominal scenarios.
- H1 records Python 3.6 or later, pyserial 3.5, and the complete OpenCat repository as
  requirements of the Petoi Python API. It also identifies the PetoiRobot library as a Python
  integration option.
- RD-01 specifies Python. RD-02 specifies Vosk with local Spanish and English models, while
  section 2.4 says voice recognition had not yet been investigated or selected. Until H2 reviews
  this conflict, Vosk is a recorded but unvalidated design constraint, not evidence of a completed
  technology evaluation.
- RR-03 specifies offline recognition after installation and model download; this is not a claim
  that setup or model downloads can occur without Internet access.
- RI-01 specifies a compatible Bluetooth module for serial communication. H1 leaves the exact
  Bittle model open; compatibility with legacy Bittle, Bittle X, or Bittle X V2 MUST NOT be
  assumed without checking the actual model and its applicable documentation.
- H1 describes 90% recognition over its proposed 100-command reference trial and processing and
  transmission of 95% of valid recognized commands within 3 seconds as proposed performance
  requirements. These targets are not confirmed results or approved acceptance thresholds.

The baseline covers:
- ESC-01 sitting and ESC-02 standing as nominal scenarios.
- ESC-03 unrecognized input, ESC-04 low-confidence valid input, ESC-05 a new order during
  movement, ESC-06 serial disconnection, ESC-07 silence during capture, and ESC-08 an incorrect
  physical result as alternative or exceptional scenarios.
- NEC-01 expected movement from a valid order, NEC-02 no movement from unrecognized input,
  NEC-03 protection against unexpected movement, NEC-04 status of received/rejected/lost orders,
  and NEC-05 verification without the physical robot.
- Every requirement category present in H1: functional (RF), performance (RR), safety (RS),
  interface (RI), operational (RO), reliability (RFI), usability (RU), maintenance (RM), and
  design constraints (RD), including RF-01 through RF-09, RR-01 through RR-03, RS-01 through
  RS-03, RI-01 through RI-07, RO-01 through RO-02, RFI-01 through RFI-02, RU-01 through RU-03,
  RM-01 through RM-02, and RD-01 through RD-02. H2 MUST review the actual requirements within
  each category rather than treating category names alone as evidence of coverage.

Technology constraints and candidate choices MUST be cited to H1 and their stated status. A
proposal or requirement recorded in one H1 section MUST NOT be represented as a validated
decision when another section leaves it open or contradicts it. Changes to the Python runtime,
voice-recognition approach, Petoi command protocol, or robot model require documented rationale
and impact review before adoption.

## Development Workflow and H1 Inconsistency Register
H2 is limited to specification and planning. H2 work MUST NOT implement application code. It
MUST clarify requirements, scenarios, interfaces, verification plans, and unresolved decisions
before any later implementation stage.

The following discrepancies are part of the H1 baseline and MUST NOT be corrected implicitly:
- The traceability matrix uses legacy identifiers REQ-01 through REQ-12, but the requirements
  section uses category identifiers RF, RR, RS, RI, RO, RFI, RU, RM, and RD. Its stated
  equivalence maps REQ-01 through REQ-08 to RF-01 through RF-08 and REQ-09 through REQ-12 to
  RNF-01 through RNF-04; this does not provide a complete crosswalk to the current category
  requirements, including RF-09 and the other non-functional categories.
- H1 says its coverage review concerns six scenarios and its matrix lists ESC-01 through ESC-06,
  while the same document defines ESC-07 and ESC-08. Their links to needs, requirement IDs, and
  verification cases therefore require explicit review.
- Section 2.4 leaves voice-recognition technology uninvestigated, whereas RD-02 specifies Vosk
  and local Spanish and English models. The status and evidence for this decision require
  reconciliation.
- H1 contains references to REQ identifiers outside the matrix, including in system boundaries,
  technical feasibility, scenario descriptions, and the verification strategy. These references
  must not be treated as a verified mapping to the category-based identifiers.
- Some entries in the category requirement tables have blank linked-element or scenario fields,
  and the verification strategy still refers to legacy REQ identifiers. H2 review must identify
  the actual gaps without inventing links or silently editing H1.

H1 also records OPEN-01 through OPEN-12: missing OpsCon; exact Bittle model; voice technology;
confidence threshold U; acoustic conditions and operating distance; accepted phrases; target
user group; document metadata; physical safety measures; `kup` behavior from relevant postures;
user confirmation and reject-versus-queue behavior; and proposed timing values. Their detailed
statements and ownership remain in H1. H2 planning MUST preserve these uncertainties and document
any resolution or continued deferral in the appropriate project artifact.

## Governance
This Constitution governs project specification, design planning, implementation at the
appropriate later stage, review, and verification. H1 remains the source baseline; this
Constitution does not amend H1 or replace its requirements.

Amendments require a documented rationale, review against H1 and the current project baseline,
and approval by the project team. An amendment that adds or materially changes a principle or
governance section increments the MINOR version; an incompatible removal or redefinition
increments MAJOR; wording-only or non-semantic clarification increments PATCH. Version numbers
follow MAJOR.MINOR.PATCH. The ratification date records the original adoption and MUST remain
unchanged by later amendments; the last-amended date MUST be updated for each amendment.

Every material change MUST be reviewed for safety, traceability, completeness across scenarios,
needs and requirement categories, and verifiability. Reviewers MUST confirm that known H1
inconsistencies and open decisions are either preserved as unresolved or explicitly resolved
with evidence and approval. A review MUST NOT claim compliance or successful verification when
required evidence is absent.

**Version**: 1.1.0 | **Ratified**: 2026-10-26 | **Last Amended**: 2026-10-26
