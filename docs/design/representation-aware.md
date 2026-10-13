# Proposal: what makes Flow distinctive, and where should its semantics go next?

Flow's most compelling thesis is that the model is the program: instead of merely expressing operations on data, the language should express how systems evolve through time and let the compiler derive an executable implementation.

I'd like to open a design conversation about what would make that thesis technically distinctive, testable, and useful beyond the current examples.

### The ideas worth preserving

Evolution as a first-class abstraction. A system's state, parameters and evolution equations should remain visible to compiler analyses rather than being immediately reduced to generic loops and arithmetic.

Self-hosted, deployable systems engineering. The self-hosted `flowc` and portable C backend are important foundations; the deeper research features should not require an enormous toolchain just to execute ordinary programs.

Effects, timing, memory and numerical behaviour as contracts. These are natural candidates for explicit, checkable representations rather than scattered conventions.

One model, multiple valid representations. Differential, discrete, SSA, control-theoretic, numerical and target-specific forms might all be derived from a source-level model, with explicitly recorded assumptions.

### Proposed research direction: representation-aware optimization

Most compilers primarily establish that transformations preserve a chosen notion of observable behaviour. Could Flow also track which information about the original system survives each transformation?

Two transformations could be equivalent under output tests but very different for later stability analysis, diagnostics, symbolic reconstruction, differentiation, timing proof or optimization.

That suggests separating at least three questions:

1. Semantic preservation: what behaviour is preserved, and under which assumptions?
2. Representation loss: what structure, provenance, units, dynamical meaning or proof evidence is discarded?
3. Downstream utility: what analyses and transformations remain possible afterward?

An optimization is selected according to the analyses and deployment guarantees that must remain available. Information loss can be permitted when it is explicit, justified and testable.

### Concrete experiment

Choose a small, reproducible set of systems from the existing repository: a damped oscillator, a discrete controller, a reaction-diffusion model and a real-time DSP kernel.

For each, compare multiple legal lowering and optimization paths while measuring runtime, memory, numerical error, and which source-level properties can still be recovered or checked.

Start with a small contract and a machine-readable transformation report. Establish baseline equivalence first; do not claim formal guarantees without proofs or appropriately scoped validation.

### Questions for maintainers and contributors

What should be Flow's canonical semantic representation: a transition system, a denotational account of SSA, a hybrid dynamical system, or a set of interoperable representations?

Which properties are worth preserving across lowering, and which should intentionally be erased?

Can effects, timing constraints and memory-safety obligations share the same verification framework without making ordinary code impractical?

What is the smallest end-to-end example that would make this direction measurably better than a conventional C/C++ or Python-to-native workflow?

This is a design discussion. It does not claim that all these capabilities are implemented. The stable production compiler and experimental research surfaces remain clearly distinguished.

Relevant context: [Vision](../../VISION.md), [Language design](../language/language_design.md), [Stability policy](../../STABILITY.md).

Interested in concrete counterexamples, simpler formulations, and suggestions for a first falsifiable prototype.