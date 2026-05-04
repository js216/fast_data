# Legal review of toolchain

Selache is an open-source toolchain for SHARC+ DSP processors, developed
from scratch to avoid reliance on source and binary codes encumbered by
complicated legal agreements that make open code sharing difficult or
impossible.

### Agent: Check derivative violation

During agentic coding it can happen that a misguided agent includes in
its output code that is obviously (or not so obviously) *derived* from a
source whose license explicitly or implicitly prohibits inclusion in an
open-source final result.

Task: review the entire codebase, including all git history, to check if
there is any evidence that an agent inappropriately included encumbered
source material in this toolchain. Flag such material for removal.

### Agent: Check intellectual property violations

Even if the code is independently created, an agent could have violated
IP laws by reimplementing patented mechanisms. This would undermine the
goals of this toolchain, preventing any open sharing.

Task: review entire codebase, including all git history, to check if
there is any violation of patented material, or any other knowledge or
information that was not intended for public release.

### Agent: Trade secrets or NDA material

If any opcode table, memory map, errata, or register description was
transcribed from a document marked confidential, or obtained under NDA
(datasheets, other toolchain internals, support-portal material),
publishing it is a trade-secret exposure even without any copyright or
patent claim.

Task: scan code, comments, commit messages, and documentation chunks for
paraphrased text that looks derived from such sources; flag any
constants, tables, or encodings whose only plausible source is a
non-public document. Verify that citations point only to publicly
available references.

### Agent: Clean-room provenance

The development of an independent toolchain must occur with total
separation from access to any legally encumbered materials. Reverse
engineering is a violation of agreements and serious ethical misconduct
that could entirely jeopardize all the work invested in an open source
toolchain.

Task: audit code and its git history for evidence that implementation
commits reference any specifications or implementation that do not allow
derivation into an open source code. Flag any commit whose message or
content suggests the author had simultaneous access to proprietary
sources and implementation code. Flag any code that is not obviously
public knowledge and that does not document where the information was
obtained from.

### Agent: Trademark usage

Nominative use or trademarks is fine; implying endorsement, using logos,
or naming the project in a way that suggests affiliation is not.

Task: grep for trademark terms across the entire codebase and its git
history, crate metadata (Cargo.toml name/description), doc comments, and
generated output banners. Flag any use that goes beyond factual
description of the target hardware.

### Agent: Inbound license compatibility

Test vectors, golden files, example programs, and fixture binaries can
carry incompatible licenses (MPL, proprietary, CC-NC). Mixed in a
GPL-3.0 tree, these create distribution blockers.

Task: enumerate every non-source asset (binary blobs, .elf, .hex, .ldr,
hex dumps, reference outputs, fonts, images) and document the provenance
and license of each. Flag anything without a clear origin.

### Agent: Export control (EAR)

DSP development tools can fall under EAR categories (typically EAR99 or
5D002 if crypto is involved), especially if any crypto primitives,
secure-boot support, or military-adjacent example code is added later.

Task: scan for cryptographic primitives, secure-boot/signing code,
and anything that would pull the toolchain into 5D002. Flag anything
that might trigger export control violations.

### Agent: Appearance of guilt

Even if no legal violation took place, the mere appearance, probability,
or suggestion of it could have the same consequences, making the
toolchain unusable for the duration of lengthy, possibly decades-long,
legal proceedings.

Task: review entire codebase, including all git history, with a very
fine comb to flag *any* potential issues that an adversarially-minded
opponent could see as evidence or probably cause to claim IP, patent,
and related laws were violated. There should be no appearance or
suggestion that this product has been *derived* in any way from existing
products---it's a clean, independent implementation. Extend this beyond
mere legal claims to include any violations of professional ethics, and
prevent any cause for offense to other people and organizations
developing and marketing toolchains and firmware for the SHARC+ series
of processors.
