# FLOW Tutorial: Training Game AIs

Three ways to train an agent on the repo's games. Everything runs in Flow on
the CPU and finishes in seconds. The trainers live in
[`lib/stdlib/ai.flow`](../../lib/stdlib/ai.flow); the demos re-simulate the
game rules headlessly (same constants, same LCG, no graphics) so training runs
at millions of frames per minute.

Prerequisites: [arrays.md](arrays.md), [pointers.md](pointers.md). The library
leans on module statics (top-level `let mut`, spec section 3.3.1) for its
tables and weights.

Every demo prints a real learning curve, evaluates against a random-policy
baseline on the same environment seeds, and exits 0 only if the trained agent
wins by a wide margin. They double as regression tests.

```bash
./flow run examples/ai/q_snake.flow       # tabular Q-learning
./flow run examples/ai/ga_flappy.flow     # neuroevolution
./flow run examples/ai/policy_pong.flow   # policy gradients
```

All randomness comes from one deterministic LCG (`ai_seed`), so two runs of a
demo print byte-identical output.

## Part 1: Tabular Q-learning on Snake

Snake has a small trick to it: the head only ever needs local information.
Compress the board into 7 bits, and a lookup table can hold the whole policy.

```flow-pseudocode
# 3 danger bits + 4 food-direction bits, all relative to the heading
let mut s: i32 = 0
if cell_deadly(sxp, syp, len, hx + lx, hy + ly) { s = s + 1 }   # left
if cell_deadly(sxp, syp, len, hx + dx, hy + dy) { s = s + 2 }   # ahead
if cell_deadly(sxp, syp, len, hx + rx, hy + ry) { s = s + 4 }   # right
if dot > 0 { s = s + 8 }      # food ahead
if dot < 0 { s = s + 16 }     # food behind
if cross < 0 { s = s + 32 }   # food left
if cross > 0 { s = s + 64 }   # food right
```

128 states, 3 actions (turn left, straight, turn right). The training loop is
four calls:

```flow-pseudocode
q_init(1234 as u32)
let eps: f32 = q_epsilon(ep, 3000, 1.0, 0.05)   # linear decay
let a: i32 = q_select(s, 3, eps)                 # epsilon-greedy
q_update(s, a, r, s_next, 3, alpha, gamma)       # Q(s,a) += alpha*(target - Q)
q_update_terminal(s, a, -10.0, alpha)            # on death: no bootstrap
```

Rewards: +10 food, -10 death, +0.2 for a step toward the food, -0.25 away,
-2 for starving out. The shaping terms are optional; they roughly halve the
episodes needed.

Output from `examples/ai/q_snake.flow` (4000 episodes, under a second):

```
random baseline: avg score 0.06 over 100 episodes
  episode 250   avg_score 0.13  epsilon 0.92
  episode 1000  avg_score 0.78  epsilon 0.68
  episode 2000  avg_score 1.96  epsilon 0.37
  episode 3000  avg_score 10.54 epsilon 0.05
  episode 4000  avg_score 15.03 epsilon 0.05
trained (greedy): avg score 19.71 over 100 episodes
```

The Q-table is a module static in `ai.flow`, sized by two consts:
`AI_Q_BUCKETS` (1024) x `AI_Q_MAX_ACTIONS` (4). States are caller-hashed
i32s. Values in `[0, AI_Q_BUCKETS)` map to buckets 1:1 with no collisions;
anything larger goes through `ai_hash_mix` and can collide, which degrades
learning quietly. Keep your encoding compact when you can.

## Part 2: Neuroevolution on Flappy

Flappy's controller is one decision (flap or not) from three numbers. That is
a 4-gene linear threshold:

```flow-pseudocode
# flap when w0*(gap_center - bird_y) + w1*vel + w2*dist + w3 > 0
if w0 * x0 + w1 * x1 + w2 * x2 + w3 > 0.0 { flap = true }
```

No gradients exist for "frames survived", so evolve the weights instead. The
GA keeps a population of genomes in module statics; you supply the fitness:

```flow-pseudocode
ga_init(32, 4, 4321 as u32)          # pop 32, 4 genes each
for each generation {
    for each genome i {
        ga_fitness_set(i, simulate(ga_get(i,0), ..., seed))
    }
    ga_evolve(0.25, 0.15)            # elite 25%, mutation sigma 0.15
}
```

`ga_evolve` ranks by fitness, copies the elites unchanged, and fills the rest
from tournament-of-3 parents with uniform crossover plus gaussian mutation.
Fitness here is `frames + 200 * pipes`, averaged over two seeds so champions
generalize.

Output from `examples/ai/ga_flappy.flow`:

```
random-flap baseline: avg pipes 0.00 over 20 runs
  gen 1   best_fitness 191   mean_fitness 71    pipes 0
  gen 2   best_fitness 199   mean_fitness 133   pipes 0
  gen 3   best_fitness 8800  mean_fitness 458   pipes 29
  gen 8   best_fitness 8800  mean_fitness 7595  pipes 29
champion policy : avg pipes 41.55 over 20 fresh-seed runs
```

Generation 3 finds a genome that survives the whole fitness window; the mean
then climbs as the population converges on it. The champion is evaluated on
seeds never used during evolution.

## Part 3: Policy Gradients on Pong

Pong needs a policy that maps continuous inputs to actions, and the reward
(hitting the ball) is delayed by dozens of frames. This is the gradient
regime: a tiny MLP trained with REINFORCE.

The MLP in `ai.flow` is one hidden tanh layer with linear output logits,
sized at init (within static budgets of 8 inputs, 16 hidden, 4 outputs):

```flow-pseudocode
mlp_init(3, 8, 3, 1337 as u32)   # ball dx, dy, relative y -> up/stay/down
mlp_forward(xp)
let a: i32 = mlp_sample()        # softmax sample while training
let a: i32 = mlp_argmax()        # greedy at evaluation time
```

After each episode, compute reward-to-go returns, whiten them, and take one
gradient-ascent step on `advantage * log pi(action | x)` per decision:

```flow-pseudocode
let mut g: f32 = 0.0
let mut t: i32 = ep_len - 1
while t >= 0 {
    g = ep_r[t] + GAMMA * g
    ep_g[t] = g
    t = t - 1
}
# ... subtract the mean, divide by the std ...
mlp_reinforce(xp, ep_a[k], (ep_g[k] - mean) * scale, LR)
```

The whitening step earns its keep. Raw returns worked for the first hundred
episodes, then the growing update magnitudes collapsed the policy; normalized
advantages train stably to the rally cap:

```
random baseline: avg rally 0.37 hits over 100 episodes
  episode 50   avg_rally 0.38  hit_rate 0.28
  episode 150  avg_rally 1.94  hit_rate 0.72
  episode 300  avg_rally 3.88  hit_rate 0.99
  episode 500  avg_rally 3.92  hit_rate 0.99
trained (greedy): avg rally 4.00 hits over 100 episodes (cap 4)
```

Rewards: +1 per paddle hit, -1 for a miss, +1.5 when the scripted opponent
misses, plus a small shaping bonus for closing the gap to the ball.
`mlp_train_mse` is the supervised sibling: same network, squared-error loss
against a target vector, for when you have labels instead of rewards.

## Choosing a trainer

| Situation | Reach for |
|-----------|-----------|
| State compresses to a few hundred discrete cases | Q-table |
| Reward is a black box (survival time, score), few parameters | GA |
| Continuous inputs, delayed credit, need a real policy | Policy MLP |
| You have labeled targets | `mlp_train_mse` |

Tables are the fastest to converge and trivially inspectable, and they stop
working the moment the state space grows past the bucket count. The GA needs
nothing differentiable and parallelizes naturally, and it spends simulation
frames very inefficiently. REINFORCE handles continuous inputs with delayed
reward and is the most sensitive to tuning; whiten your advantages.

## Honest notes on scale

- These budgets are deliberately small: 1024 Q-buckets, 64 genomes of 16
  genes, an 8-16-4 MLP. Atari-scale problems need function approximation,
  replay buffers and orders of magnitude more compute; this module is for
  game-sized problems and for teaching the mechanics.
- Everything here is a module static, so one Q-table, one population and one
  MLP exist per process. Two agents cannot train side by side yet.
- Q-state collisions above `AI_Q_BUCKETS` fail silently. If learning stalls,
  count your distinct states first.
- REINFORCE variance is real. The pong demo converges because the episode is
  short, returns are whitened and the learning rate is small. Change one and
  watch it wobble.

## Interactive sketches

### Q-update toy (browser)

One tabular Q-learning step — state/action tables as flat arrays:

```flow
function main() -> i32 {
    let mut q: array<f64, 6> = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    let s: i32 = 0
    let a: i32 = 1
    let r: f64 = 1.0
    let s2: i32 = 2
    let alpha: f64 = 0.5
    let gamma: f64 = 0.9
    let mut max_next: f64 = q[s2 * 2]
    if q[s2 * 2 + 1] > max_next {
        max_next = q[s2 * 2 + 1]
    }
    let target: f64 = r + gamma * max_next
    let idx: i32 = s * 2 + a
    q[idx] = q[idx] + alpha * (target - q[idx])
    printf("Q[s,a]=%f\n", q[idx])
    return 0
}
```

### Fitness ranking toy (browser)

```flow
function main() -> i32 {
    let mut fit: array<f64, 4> = [0.2, 0.9, 0.4, 0.7]
    let mut best_i: i32 = 0
    for i in 1 to 4 {
        if fit[i] > fit[best_i] {
            best_i = i
        }
    }
    printf("best_genome=%d fitness=%f\n", best_i, fit[best_i])
    return 0
}
```

### Epsilon-greedy pick (browser)

```flow
function main() -> i32 {
    let q: array<f64, 3> = [0.1, 0.8, 0.3]
    let eps: f64 = 0.0
    let mut best: i32 = 0
    for a in 1 to 3 {
        if q[a] > q[best] {
            best = a
        }
    }
    # eps=0 → always greedy
    let action: i32 = best
    printf("action=%d q=%f\n", action, q[action])
    return 0
}
```

### Reward shaping toward food (browser)

```flow
function main() -> i32 {
    let dist_before: i32 = 5
    let dist_after: i32 = 3
    let mut r: f64 = 0.0
    if dist_after < dist_before {
        r = r + 0.2
    } else {
        r = r - 0.25
    }
    printf("shaped=%f\n", r)
    return 0
}
```

### Mutation step (browser)

```flow
function main() -> i32 {
    let mut gene: f64 = 0.5
    let delta: f64 = 0.1
    gene = gene + delta
    if gene > 1.0 { gene = 1.0 }
    if gene < 0.0 { gene = 0.0 }
    printf("gene=%f\n", gene)
    return 0
}
```

### Policy logit (browser)

```flow
function main() -> i32 {
    let logit_up: f64 = 0.2
    let logit_down: f64 = -0.1
    let mut action: i32 = 0
    if logit_down > logit_up {
        action = 1
    }
    printf("action=%d\n", action)
    return 0
}
```

## Where the pieces live

| File | Contents |
|------|----------|
| [`lib/stdlib/ai.flow`](../../lib/stdlib/ai.flow) | RNG, hash, Q-learning, GA, policy MLP |
| [`examples/ai/q_snake.flow`](../../examples/ai/q_snake.flow) | Headless snake + Q-learning |
| [`examples/ai/ga_flappy.flow`](../../examples/ai/ga_flappy.flow) | Headless flappy + GA |
| [`examples/ai/policy_pong.flow`](../../examples/ai/policy_pong.flow) | Headless pong + REINFORCE |
| [`examples/games/`](../../examples/games/) | The original graphical games |
