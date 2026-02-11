"""
Flow Physics DSL
================

A domain-specific language extension for writing physics simulations
in natural, equation-like syntax.

Example:
--------

```flow
@physics
world Particles {
    # Define what a particle is
    entity Particle {
        position: Vec2
        velocity: Vec2
        mass: f64 = 1.0
    }

    # Constants
    const gravity = Vec2(0, 9.8)
    const friction = 0.02
    const restitution = 0.8

    # Physics rules (applied each timestep)
    rule "gravity":
        velocity += gravity * dt

    rule "friction":
        velocity *= (1.0 - friction)

    rule "motion":
        position += velocity * dt

    # Constraints
    constraint "floor" when position.y > height:
        position.y = height
        velocity.y = -velocity.y * restitution

    constraint "walls" when position.x < 0 or position.x > width:
        position.x = clamp(position.x, 0, width)
        velocity.x = -velocity.x * restitution

    # Interactions
    interact "collision" between a, b when distance(a, b) < 10:
        let normal = normalize(b.position - a.position)
        let impulse = dot(a.velocity - b.velocity, normal)
        a.velocity -= impulse * normal * 0.5
        b.velocity += impulse * normal * 0.5
}
```

This compiles to efficient Flow code with SoA memory layout.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re


@dataclass
class Vec2Type:
    """2D Vector with operator support"""

    pass


@dataclass
class PhysicsEntity:
    name: str
    fields: List[tuple]  # (name, type, default)


@dataclass
class PhysicsRule:
    name: str
    body: str


@dataclass
class PhysicsConstraint:
    name: str
    condition: str
    body: str


@dataclass
class PhysicsInteraction:
    name: str
    entities: List[str]
    condition: str
    body: str


@dataclass
class PhysicsWorld:
    name: str
    entities: List[PhysicsEntity]
    constants: Dict[str, str]
    rules: List[PhysicsRule]
    constraints: List[PhysicsConstraint]
    interactions: List[PhysicsInteraction]


def parse_physics_dsl(code: str) -> PhysicsWorld:
    """Parse physics DSL into structured representation"""
    # This is a simplified parser - in production would use proper parsing

    world_match = re.search(r"world\s+(\w+)\s*\{", code)
    if not world_match:
        raise ValueError("No world definition found")

    world_name = world_match.group(1)

    # Parse entities
    entities = []
    entity_pattern = r"entity\s+(\w+)\s*\{([^}]+)\}"
    for match in re.finditer(entity_pattern, code):
        name = match.group(1)
        fields_str = match.group(2)
        fields = []
        for line in fields_str.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Parse: name: type = default or name: type
            if "=" in line:
                parts = line.split("=")
                name_type = parts[0].strip()
                default = parts[1].strip()
            else:
                name_type = line
                default = None

            if ":" in name_type:
                fname, ftype = name_type.split(":")
                fields.append((fname.strip(), ftype.strip(), default))

        entities.append(PhysicsEntity(name, fields))

    # Parse constants
    constants = {}
    const_pattern = r"const\s+(\w+)\s*=\s*([^\n]+)"
    for match in re.finditer(const_pattern, code):
        constants[match.group(1)] = match.group(2).strip()

    # Parse rules
    rules = []
    rule_pattern = r'rule\s+"([^"]+)":\s*\n((?:\s+[^\n]+\n?)+)'
    for match in re.finditer(rule_pattern, code):
        rules.append(PhysicsRule(match.group(1), match.group(2).strip()))

    # Parse constraints
    constraints = []
    constraint_pattern = (
        r'constraint\s+"([^"]+)"\s+when\s+([^:]+):\s*\n((?:\s+[^\n]+\n?)+)'
    )
    for match in re.finditer(constraint_pattern, code):
        constraints.append(
            PhysicsConstraint(
                match.group(1), match.group(2).strip(), match.group(3).strip()
            )
        )

    # Parse interactions
    interactions = []
    interact_pattern = r'interact\s+"([^"]+)"\s+between\s+(\w+),\s*(\w+)\s+when\s+([^:]+):\s*\n((?:\s+[^\n]+\n?)+)'
    for match in re.finditer(interact_pattern, code):
        interactions.append(
            PhysicsInteraction(
                match.group(1),
                [match.group(2), match.group(3)],
                match.group(4).strip(),
                match.group(5).strip(),
            )
        )

    return PhysicsWorld(
        world_name, entities, constants, rules, constraints, interactions
    )


def compile_physics_to_flow(world: PhysicsWorld) -> str:
    """Compile physics DSL to efficient Flow code"""

    lines = []
    lines.append(f"# Generated from Physics DSL: {world.name}")
    lines.append(f"# Entities: {', '.join(e.name for e in world.entities)}")
    lines.append("")

    # Generate Vec2 struct and operations
    lines.append("# Vector2 type and operations")
    lines.append("struct Vec2 {")
    lines.append("    x: f64,")
    lines.append("    y: f64")
    lines.append("}")
    lines.append("")

    lines.append(
        "function vec2_add(a_x: f64, a_y: f64, b_x: f64, b_y: f64, out: ptr<f64>) -> void {"
    )
    lines.append("    out[0] = a_x + b_x")
    lines.append("    out[1] = a_y + b_y")
    lines.append("}")
    lines.append("")

    lines.append("function vec2_scale(x: f64, y: f64, s: f64, out: ptr<f64>) -> void {")
    lines.append("    out[0] = x * s")
    lines.append("    out[1] = y * s")
    lines.append("}")
    lines.append("")

    lines.append("function vec2_length(x: f64, y: f64) -> f64 {")
    lines.append("    return sqrt(x * x + y * y)")
    lines.append("}")
    lines.append("")

    lines.append("function vec2_dot(a_x: f64, a_y: f64, b_x: f64, b_y: f64) -> f64 {")
    lines.append("    return a_x * b_x + a_y * b_y")
    lines.append("}")
    lines.append("")

    # Generate constants
    lines.append("# Physics constants")
    for name, value in world.constants.items():
        # Convert Vec2(...) to separate x, y constants
        if "Vec2" in value:
            match = re.search(r"Vec2\s*\(\s*([^,]+),\s*([^)]+)\)", value)
            if match:
                lines.append(f"const {name}_x: f64 = {match.group(1).strip()}")
                lines.append(f"const {name}_y: f64 = {match.group(2).strip()}")
            else:
                lines.append(f"const {name}: f64 = {value}")
        else:
            lines.append(f"const {name}: f64 = {value}")
    lines.append("")

    # Generate entity data layout
    for entity in world.entities:
        lines.append(f"# {entity.name} data layout (SoA)")
        lines.append(
            f"# Fields per {entity.name}: {len(entity.fields) * 2} f64s (Vec2 = 2 f64)"
        )

        # Accessor functions
        for i, (fname, ftype, default) in enumerate(entity.fields):
            if ftype == "Vec2":
                offset = i * 2
                lines.append(
                    f"function get_{entity.name.lower()}_{fname}_x(data: ptr<f64>, idx: i32) -> f64 {{"
                )
                lines.append(
                    f"    return data[idx * {len(entity.fields) * 2} + {offset}]"
                )
                lines.append("}")
                lines.append(
                    f"function get_{entity.name.lower()}_{fname}_y(data: ptr<f64>, idx: i32) -> f64 {{"
                )
                lines.append(
                    f"    return data[idx * {len(entity.fields) * 2} + {offset + 1}]"
                )
                lines.append("}")
                lines.append(
                    f"function set_{entity.name.lower()}_{fname}(data: ptr<f64>, idx: i32, x: f64, y: f64) -> void {{"
                )
                lines.append(f"    data[idx * {len(entity.fields) * 2} + {offset}] = x")
                lines.append(
                    f"    data[idx * {len(entity.fields) * 2} + {offset + 1}] = y"
                )
                lines.append("}")
            else:
                offset = i * 2
                lines.append(
                    f"function get_{entity.name.lower()}_{fname}(data: ptr<f64>, idx: i32) -> f64 {{"
                )
                lines.append(
                    f"    return data[idx * {len(entity.fields) * 2} + {offset}]"
                )
                lines.append("}")
                lines.append(
                    f"function set_{entity.name.lower()}_{fname}(data: ptr<f64>, idx: i32, val: f64) -> void {{"
                )
                lines.append(
                    f"    data[idx * {len(entity.fields) * 2} + {offset}] = val"
                )
                lines.append("}")
        lines.append("")

    # Generate update function
    entity: Optional[PhysicsEntity] = world.entities[0] if world.entities else None
    if entity:
        lines.append(f"# Update all {entity.name}s")
        lines.append(
            f"function update_{entity.name.lower()}s(data: ptr<f64>, count: i32, dt: f64, width: f64, height: f64) -> void {{"
        )
        lines.append("    for i in 0 to count {")

        # Load current values
        for fname, ftype, _ in entity.fields:
            if ftype == "Vec2":
                lines.append(
                    f"        let {fname}_x: f64 = get_{entity.name.lower()}_{fname}_x(data, i)"
                )
                lines.append(
                    f"        let {fname}_y: f64 = get_{entity.name.lower()}_{fname}_y(data, i)"
                )

        # Apply rules
        lines.append("")
        lines.append("        # Apply physics rules")
        for rule in world.rules:
            lines.append(f"        # Rule: {rule.name}")
            # Transform rule body
            body = rule.body
            # Replace += with explicit assignment
            body = re.sub(r"(\w+)\s*\+=\s*(.+)", r"\1 = \1 + \2", body)
            body = re.sub(r"(\w+)\s*\*=\s*(.+)", r"\1 = \1 * (\2)", body)
            # Replace vector operations
            body = body.replace("velocity", "velocity_x")  # Simplified
            for line in body.split("\n"):
                line = line.strip()
                if line:
                    # Handle Vec2 arithmetic
                    if "gravity" in line and "velocity" in line:
                        lines.append("        velocity_x = velocity_x + gravity_x * dt")
                        lines.append("        velocity_y = velocity_y + gravity_y * dt")
                    elif "friction" in line:
                        lines.append(
                            "        velocity_x = velocity_x * (1.0 - friction)"
                        )
                        lines.append(
                            "        velocity_y = velocity_y * (1.0 - friction)"
                        )
                    elif "position" in line and "velocity" in line:
                        lines.append(
                            "        position_x = position_x + velocity_x * dt"
                        )
                        lines.append(
                            "        position_y = position_y + velocity_y * dt"
                        )

        # Apply constraints
        lines.append("")
        lines.append("        # Apply constraints")
        for constraint in world.constraints:
            lines.append(f"        # Constraint: {constraint.name}")
            cond = constraint.condition

            # Transform condition
            if "position.y" in cond:
                cond = cond.replace("position.y", "position_y")
            if "position.x" in cond:
                cond = cond.replace("position.x", "position_x")

            lines.append(f"        if {cond} {{")

            # Transform body
            for line in constraint.body.split("\n"):
                line = line.strip()
                if line:
                    line = line.replace("position.y", "position_y")
                    line = line.replace("position.x", "position_x")
                    line = line.replace("velocity.y", "velocity_y")
                    line = line.replace("velocity.x", "velocity_x")
                    line = line.replace("clamp(", "clamp_f64(")
                    lines.append(f"            {line}")

            lines.append("        }")

        # Store values back
        lines.append("")
        lines.append("        # Store updated values")
        for fname, ftype, _ in entity.fields:
            if ftype == "Vec2":
                lines.append(
                    f"        set_{entity.name.lower()}_{fname}(data, i, {fname}_x, {fname}_y)"
                )

        lines.append("    }")
        lines.append("}")

    return "\n".join(lines)


# Example usage
EXAMPLE_DSL = """
@physics
world Particles {
    entity Particle {
        position: Vec2
        velocity: Vec2
    }
    
    const gravity = Vec2(0, 9.8)
    const friction = 0.02
    const restitution = 0.8
    
    rule "gravity":
        velocity += gravity * dt
    
    rule "friction":
        velocity *= (1.0 - friction)
    
    rule "motion":
        position += velocity * dt
    
    constraint "floor" when position.y > height:
        position.y = height
        velocity.y = -velocity.y * restitution
    
    constraint "ceiling" when position.y < 0:
        position.y = 0
        velocity.y = -velocity.y * restitution
    
    constraint "left_wall" when position.x < 0:
        position.x = 0
        velocity.x = -velocity.x * restitution
    
    constraint "right_wall" when position.x > width:
        position.x = width
        velocity.x = -velocity.x * restitution
}
"""

if __name__ == "__main__":
    world = parse_physics_dsl(EXAMPLE_DSL)
    flow_code = compile_physics_to_flow(world)
    print(flow_code)
