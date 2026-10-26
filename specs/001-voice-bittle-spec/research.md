# VOICE-BITTLE H2 Research Notes

**Status**: Design research only. These findings inform the H2 plan but do not approve Vosk,
resolve any H1 OPEN item, amend H1, or authorize implementation.

## Recognition Provider Abstraction

**Decision**: Specify a small, provider-neutral boundary between audio capture/recognition and
command interpretation. The provider returns normalized recognized text and confidence (or an
explicit no-result/failure outcome); command validation remains responsible for deciding whether
the result maps to an approved action.

**Rationale**: A neutral result boundary allows a Vosk adapter to be integrated if the team later
approves Vosk, without exposing provider-specific objects to command mapping, state management,
or the serial boundary. Python PEP 544 describes structural interfaces as a way for independent
implementations to satisfy a contract without inheriting a common base class. This is a design
principle only; H2 does not mandate PEP 544, a Python interface syntax, or a code structure.

**Alternatives considered**:
- Bind command interpretation directly to Vosk-specific recognition results: rejected for this
  plan because it would couple the rest of the system before OPEN-03 is settled.
- Select another recognition provider now: not evaluated or selected; OPEN-03 remains open.

**Sources**: [PEP 544 – Protocols: Structural subtyping](https://peps.python.org/pep-0544/);
H1 sections 2.2, 2.4, and RD-02; feature clarification for OPEN-03.

## Vosk Proposal and Offline Operation

**Decision**: Keep Vosk as the technology proposed by H1 RD-02, not an approved selection.
Retain an adapter boundary and defer provider approval to the team's justified resolution of
OPEN-03.

**Rationale**: Vosk documentation describes offline recognition and lists Spanish support, but
offline runtime depends on a compatible model being present locally. Its model guidance varies
substantially by model size and resource needs. Its basic Python usage page documents a specific
PCM audio format; these facts make the microphone, runtime, model, device, and test conditions
relevant validation inputs, not decisions that can be inferred for this project.

**Alternatives considered**:
- Treat RD-02 as final approval: rejected because H1 section 2.4 explicitly says the technology
  was not investigated or chosen.
- Treat Vosk as disproven: rejected because H1 has not provided evidence against it; it remains
  a proposal pending evaluation.

**Sources**: [Vosk overview](https://alphacephei.com/vosk/);
[Vosk models](https://alphacephei.com/vosk/models);
[Vosk installation and usage](https://alphacephei.com/vosk/install);
[Vosk adaptation](https://alphacephei.com/vosk/adaptation).

## Petoi Serial Command Boundary

**Decision**: Use an explicit allowlist of approved semantic actions and exact Petoi tokens at
the serial boundary. Do not forward raw recognized speech as a serial command. Use a simulator
to validate token selection and failure behavior before physical integration.

**Rationale**: Petoi protocol guidance describes case-sensitive ASCII command tokens and warns
about buffer limits for combined commands. The current H1 scope uses short action tokens rather
than long concatenated sequences. Petoi Serial Monitor instructions include setup-specific
serial parameters; those are not adopted as project settings without confirming the exact board,
firmware, and connection.

**Alternatives considered**:
- Transmit recognized text directly: rejected because user speech is not a validated Petoi
  command and may not correspond to an allowed movement.
- Fix serial parameters from generic Serial Monitor examples: rejected because H1 leaves the
  exact Bittle model and connection configuration open.

**Sources**: [Petoi Serial Protocol](https://docs.petoi.com/apis/serial-protocol.md);
[Petoi Serial Monitor](https://docs.petoi.com/arduino-ide/serial-monitor.md);
[NyBoard communication overview](https://docs.petoi.com/communication-modules/introduction-for-nyboard.md);
H1 sections 2.2–2.4 and CTX-01/CTX-02.

## Firmware-Specific Token Verification

**Decision**: Preserve `ksit` and `kup` as H1's planned semantic mappings, but verify exact token
compatibility against the identified robot model and firmware before physical acceptance.

**Rationale**: The Petoi Python API documents `kup` for standing, while the Serial Protocol
page's displayed skill-list naming rule does not itself enumerate `kup`. H1 already leaves the
exact model open (OPEN-02) and the behavior of `kup` from sitting/lying postures open (OPEN-10).
This source difference does not justify changing H1 or choosing a different token; it motivates
model-specific verification.

**Alternatives considered**:
- Assume all Petoi models and interfaces accept the same token behavior: rejected as unsupported
  until OPEN-02 and OPEN-10 are reviewed.
- Replace the H1 `kup` mapping based on incomplete documentation: rejected; no such change is
  justified by the evidence collected.

**Sources**: [Petoi Python API](https://docs.petoi.com/apis/python-api.md);
[Petoi Serial Protocol](https://docs.petoi.com/apis/serial-protocol.md);
H1 OPEN-02 and OPEN-10.

## Project-Specific Decisions Not Made

- No technology is selected or approved; OPEN-03 remains open.
- No audio sampling format, microphone, operating system, model variant, hardware resource
  target, or runtime version beyond H1's Petoi API prerequisite is selected.
- No baud rate, line ending, retry policy, serial timeout, or movement acknowledgement protocol
  is set.
- No physical safety intervention or test zone dimension is invented; OPEN-09 remains open.
- No recognition or timing target is approved; RR-01/RR-02 and OPEN-04/05/06/12 retain their H1
  status.
- Research does not close the H1 SoI discrepancy, identifier crosswalk, or ESC-07/ESC-08
  traceability gaps.
