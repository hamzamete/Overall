# ⚔️ WARLORD OPTIMIZER — A Gamified Combat Optimization Engine

> *"It should feel like a game first. Only then should you realize it's an optimization problem."*

---

## 🎮 Project Overview

**Warlord Optimizer** is a gamified application built on top of a **multi-variable constrained optimization problem**. Players configure a medieval warrior — choosing physical attributes, armor, weapons, and battlefield terrain — and then engage in combat either against a bot or another player online. Behind every decision lies a mathematical engine that calculates the **globally optimal warrior configuration** and compares it against the player's own build.

The core loop is simple: **make decisions like a player, discover you were solving an optimization problem.**

---

## 🧠 The Optimization Problem

### Problem Class
This is a **Mixed-Integer Nonlinear Programming (MINLP)** problem with:
- **Continuous variables**: BMI, body fat/muscle ratio, age, weapon length/weight, altitude
- **Integer/categorical variables**: armor type (leather / chainmail / iron), weapon type (dagger / spear / sword / mace), map selection
- **Nonlinear constraints**: stamina decay curves, speed-weight trade-offs, carry capacity limits
- **Objective**: Maximize `Warrior Overall Score` subject to physical, equipment, and battlefield constraints

---

### 🔢 Mathematical Model

#### Decision Variables

| Variable | Type | Domain | Description |
|----------|------|--------|-------------|
| `BMI` | Continuous | [15, 45] | Body Mass Index |
| `F` | Continuous | [0.05, 0.60] | Body fat ratio |
| `M` | Continuous | [0.10, 0.70] | Muscle ratio |
| `age` | Integer | [14, 70] | Warrior age |
| `w_type` | Categorical | {dagger, spear, sword, mace} | Weapon type |
| `w_size` | Continuous | [w_min, w_max] | Weapon length or weight |
| `a_head` | Categorical | {none, leather, chainmail, iron} | Head armor |
| `a_body` | Categorical | {none, leather, chainmail, iron} | Body armor |
| `a_legs` | Categorical | {none, leather, chainmail, iron} | Leg armor |
| `map` | Categorical | {plain, forest, mountain} | Battlefield terrain |
| `pos_archer` | Continuous | [0, h_max] | Archer altitude (if bow equipped) |

---

#### Objective Function

$$\text{maximize} \quad \mathcal{O} = \alpha_1 \cdot P_{net} + \alpha_2 \cdot E_{net} + \alpha_3 \cdot S_{net} + \alpha_4 \cdot V_{net} + \alpha_5 \cdot X_{net}$$

Where:
- $P_{net}$ = Net Power (after penalties)
- $E_{net}$ = Net Endurance
- $S_{net}$ = Net Stamina
- $V_{net}$ = Net Speed (Velocity)
- $X_{net}$ = Net Experience

Each is computed from a **base value minus cumulative penalties** from equipment, age, and load.

---

#### Core Attribute Functions

**Base Power:**
$$P_{base} = \beta_1 \cdot M + \beta_2 \cdot (1 - F) + \beta_3 \cdot f_{age}(age)$$

$$f_{age}(age) = \begin{cases} \frac{age}{18} \cdot 0.6 & \text{if } age < 18 \\ 1.0 & \text{if } 18 \leq age \leq 30 \\ 1.0 - \gamma \cdot (age - 30) & \text{if } age > 30 \end{cases}$$

**Max Carry Capacity:**
$$W_{carry}^{max} = \delta_1 \cdot M \cdot BW + \delta_2 \cdot (1 - F) \cdot BW$$

Where $BW$ = body weight derived from BMI and assumed height.

**Stamina:**
$$S_{base} = \phi_1 \cdot M - \phi_2 \cdot F - \phi_3 \cdot f_{age\_decay}(age)$$

$$S_{net} = S_{base} - \sum_{i \in Armor} \lambda_i \cdot w_i - \mu \cdot \frac{W_{load}}{W_{carry}^{max}}$$

**Speed:**
$$V_{base} = \eta_1 \cdot (1 - F) + \eta_2 \cdot M - \eta_3 \cdot BMI_{excess}$$

$$V_{net} = V_{base} - \sum_{i \in Armor} \rho_i \cdot w_i - \sigma \cdot w_{weapon} - \pi_{map}$$

**Experience Modifier:**
$$X_{net} = \min\left(1.0,\ \frac{age}{35}\right) \cdot X_{max}$$

---

#### Constraints

```
1. W_load ≤ W_carry^max                          (carry capacity)
2. W_load > W_carry^max  ⟹  warrior immobilized (hard penalty)
3. w_dagger < w_spear < w_sword < w_mace         (weapon weight order, strictly maintained)
4. P_weapon[dagger] < P_weapon[spear] < ...      (weapon power order, preserved)
5. V_net ≥ V_min                                 (minimum mobility)
6. S_net ≥ 0                                     (stamina cannot be negative)
7. armor_combination ∈ valid_sets                (any combination of head/body/legs allowed)
8. pos_archer ≤ h_map^max                        (altitude bounded by map)
9. stamina_penalty_archer += κ · pos_archer       (oxygen penalty for archers at altitude)
```

---

#### Weapon-Specific Sub-Models

**Spear & Sword (length scaling):**
$$\text{Attack Speed} = AS_{base} - \xi \cdot length$$
$$\text{Damage} = D_{base} + \psi \cdot length$$
$$w_{weapon} = w_{base} + \zeta \cdot length$$

**Mace (weight scaling):**
$$\text{Attack Speed} = AS_{base} - \xi \cdot w_{extra}$$
$$\text{Damage} = D_{base} + \psi \cdot w_{extra}$$

**Bow (altitude scaling):**
$$\text{Range} = R_{base} + \omega \cdot alt$$
$$\text{Stamina Penalty} = \kappa \cdot alt$$

---

#### Map Effects

| Map | Speed Modifier | Stealth | Archer Altitude | Special |
|-----|---------------|---------|-----------------|---------|
| Plain | +10% | None | Low | Fastest movement |
| Forest | −5% | High | None | Concealment bonus |
| Mountain | −15% | None | High | Archer range boost |

Map advantage can **overcome a lower overall score** — a weaker warrior on a favorable map can defeat a stronger one on an unfavorable map.

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        PLAYER INTERFACE                        │
│   Attribute Builder → Equipment Select → Map Select → Battle   │
└────────────────────────┬───────────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │       GAME ENGINE           │
          │  - Attribute Computation    │
          │  - Penalty Resolution       │
          │  - Overall Score Calculator │
          │  - Tip Generator (AI)       │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │    OPTIMIZATION SOLVER      │
          │  - Brute-force bot search   │
          │  - Constraint checking      │
          │  - Optimal config finder    │
          │  - Player vs Optimal diff   │
          └─────────────────────────────┘
```

---

## 🤖 Bot Intelligence — The Brute-Force Optimizer

When a player fights the **Bot**, the bot does not use a random build. It runs a **constrained brute-force search** (or a greedy local search for speed) over the combinatorial space of:

- All armor combinations (4³ = 64 combinations)
- All weapon types × size configurations
- Age & physical attribute calibration to the player's level

The bot finds the configuration that **maximizes the Overall Score** subject to all constraints. This is the benchmark against which the player's score is measured.

$$\text{Efficiency} = \frac{\mathcal{O}_{player}}{\mathcal{O}_{bot}^*} \times 100\%$$

The closer to 100%, the closer the player is to the **optimal solution**.

---

## 💡 Tip System

The Tip System analyzes the player's current attribute selections and outputs **decision-specific recommendations**:

- *"Your muscle ratio is high but your armor is too heavy — you're over your carry limit. Switch to chainmail body armor to recover 12% stamina."*
- *"At age 42, your power decay is significant. Prioritize experience-based multipliers. Equip a heavier mace to compensate for lower raw power."*
- *"On mountain terrain, moving your archer position from altitude 0 to 300m increases range by 40% — stamina penalty is manageable at your current fitness."*

Tips are generated **contextually** based on the player's specific attribute vector, not generic advice.

---

## 🎛️ Warrior Builder — Configurable Attributes

### Physical Profile
| Attribute | Effect |
|-----------|--------|
| BMI | Affects base power, carry capacity, and speed |
| Body Fat % | Penalizes speed, stamina, and power |
| Muscle % | Boosts power, carry capacity, and endurance |
| Age | Low age → low experience, moderate power; Peak 25–30; High age → high experience, lower power & stamina |

### Armor System
Each piece (Head / Body / Legs) can independently be: `None`, `Leather`, `Chainmail`, or `Iron`

| Material | Defense Bonus | Weight | Speed Penalty | Stamina Penalty |
|----------|--------------|--------|---------------|-----------------|
| None | 0 | 0 kg | 0% | 0% |
| Leather | Low | Light | −3% | −2% |
| Chainmail | Medium | Medium | −8% | −6% |
| Iron | High | Heavy | −15% | −12% |

> ⚠️ If total equipment weight exceeds `W_carry^max`, the warrior is **immobilized** and cannot fight.

### Weapon System
| Weapon | Base Weight | Base Power | Customization |
|--------|------------|-----------|---------------|
| Dagger | Lightest | Lowest | Fixed |
| Spear | Light | Low-Med | Length slider |
| Sword | Medium | Medium-High | Length slider |
| Mace | Heaviest | Highest | Weight slider |

Weight and power orderings are **strictly enforced** by constraints — a minimum mace weight is always greater than maximum sword weight.

---

## 🗺️ Map System

Three map archetypes, each with front/back zone configurations:

- **2 Front / 1 Back** — aggressive formation, favors melee
- **1 Front / 2 Back** — defensive formation, favors ranged

| Map | Archer Altitude | Movement | Concealment |
|-----|----------------|----------|-------------|
| Grassland | Low | Fast | None |
| Forest | None | Slow | High |
| Mountain | High | Very Slow | None |

---

## 🌐 Game Modes

- **vs Bot** — Face the optimizer's optimal warrior build
- **Online PvP** — Build your warrior, challenge another player's configuration

---

## 📊 Overall Score Formula (Summary)

$$\mathcal{O} = w_P \cdot P_{net} + w_E \cdot E_{net} + w_S \cdot S_{net} + w_V \cdot V_{net} + w_X \cdot X_{net} + \Delta_{map}$$

| Component | Weight |
|-----------|--------|
| Power | 25% |
| Endurance | 20% |
| Stamina | 20% |
| Speed | 20% |
| Experience | 15% |
| Map Bonus | +/− modifier |

---

## 🧩 Why This Is an Optimization Problem

Most players instinctively **maximize power** — equipping the heaviest armor and the strongest weapon. But this violates carry constraints, collapses stamina, kills speed, and produces a **sub-optimal overall**. The true optimal solution requires **trading off** across all dimensions under hard constraints — exactly what a MINLP solver does.

Players who intuit the trade-offs and approach the optimizer's score have effectively **solved the optimization problem by gameplay**.

---

## 📁 Project Structure

```
warlord-optimizer/
├── README.md
├── src/
│   ├── engine/
│   │   ├── attributes.js        # Physical stat computation
│   │   ├── armor.js             # Armor penalty functions
│   │   ├── weapons.js           # Weapon damage & speed models
│   │   ├── map.js               # Terrain modifiers
│   │   ├── overall.js           # Score aggregator
│   │   └── constraints.js       # Constraint validation
│   ├── optimizer/
│   │   ├── bot.js               # Brute-force optimal finder
│   │   └── tips.js              # Contextual tip generator
│   ├── game/
│   │   ├── battle.js            # Combat resolution
│   │   └── online.js            # PvP matchmaking
│   └── ui/
│       ├── builder.jsx          # Warrior builder interface
│       └── arena.jsx            # Battle visualization
├── math/
│   └── model.md                 # Full mathematical model
└── assets/
    └── sprites/                 # Pixel art warrior assets
```

---

## 🔬 Optimization Technique Summary

| Aspect | Detail |
|--------|--------|
| Problem Type | Mixed-Integer Nonlinear Programming (MINLP) |
| Objective | Maximize Warrior Overall Score |
| Variables | 11 decision variables (continuous + categorical) |
| Constraints | 9 hard constraints |
| Bot Solver | Constrained brute-force / greedy local search |
| Comparison | Player efficiency score vs optimal (0–100%) |
| Insight Delivery | Contextual tip system |

---

## 👥 Team

Built as a gamified optimization project — where the fun comes first, and the math reveals itself through play.

---

*"The best warriors are not the strongest. They are the ones who understand trade-offs."*
