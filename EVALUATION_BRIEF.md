# Evaluation brief

You are evaluating a set of *putative morphisms* between Erdős problems and
physical systems. Your job is not to admire the connections; it is to find out
whether they hold up.

## Task, in order

**1. Verify your copy.** Run `python3 tools/validate.py`. It re-hashes every
snapshot payload against `snapshot/manifest.json`. If it fails, stop — you are
not looking at a pinned target and nothing you conclude will be reproducible.

**2. Read the manifest.** Note `reconciliation` and `known_gaps`. Write down the
capture date and the morphism count before you look at any claim. This is your
denominator, and quoting a fraction against the wrong denominator is the easiest
error to make here.

**3. Evaluate every claim in `claims/CLAIMS_REGISTER.json`** using
`rubric/MORPHISM_RUBRIC.md`. Work claim by claim. Do not aggregate early: the
interesting failures are individual, and averages hide them.

**4. Check anchors against the world.** For each claim that survives step 3, use
`anchors/GROUND_TRUTH.md` to reach the original Erdős problem statement and the
cited literature. The question is not whether the atlas is internally consistent
— it usually is — but whether the invariant it names is the invariant the
mathematics actually has.

**5. Attack the strongest claims hardest.** A morphism marked
`strength: proved` is the atlas asserting it has earned confidence. Those are the
highest-value targets. A wrong `proved` damages the whole set more than ten loose
`conjectured` entries, because it is a claim about evidence rather than about
resemblance.

**6. Produce `EVALUATION_LOG.md`**, separating defects from weaknesses from gaps.

## What makes a morphism genuinely good

A correspondence earns its keep when the *transfer operator does work* — when it
lets you carry a result, a bound, or a proof technique from the physics side to
the math side, or conversely. It does not earn its keep by both sides being
vaguely similar, or by sharing a word such as "density" or "entropy".

Ask of each one: **if I deleted the physics column, would any mathematical
statement become harder to prove or any bound tighter?** If the answer is no, the
morphism is decorative, and saying so is a real finding.

## Known traps in this corpus

These are the failure modes the atlas is most likely to exhibit. Check for them
deliberately rather than hoping to notice them.

- **Shared-word overlap.** Two invariants described with the same English word
  ("density", "capacity", "entropy", "gap") that are not the same mathematical
  object. A morphism built on a pun is the most common defect in this genre.
- **Classical result dressed as a morphism.** The `mr-001` Sidon/radar record is
  the pattern to watch: Sidon 1938 and Singer 1938 are genuine classical
  theorems, but "`strength: proved`" there may be crediting the underlying
  classical fact rather than establishing a transfer between the two fields.
  Distinguish *the result is true* from *the morphism is established*.
- **Breakdown boundaries that are too generous.** A `breakdown_boundary` that
  names a limit so narrow the correspondence looks safe is doing rhetorical work.
  Check whether the boundary is where the analogy actually dies, or earlier.
- **Confidence inflation under citation.** Four citations make a record look
  rigorous. Check whether any of them is *about* the claimed correspondence, or
  merely adjacent to it.
- **The question-begging term.** Physics-side descriptions written to echo the
  math-side ones. Compare `physics_desc` with what a physicist would actually say
  about that system in its own terms.

## Output format

For every claim, record: claim id, verdict from the rubric, one sentence of
justification, and a finding type (defect / weakness / gap). Then a short
summary: how many survive, and the two or three findings a maintainer should
address first.

Do not soften. A substrate that only receives praise has told its author nothing.
