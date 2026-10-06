# Type identity, member tables, and layout certificates

Ordinary Flow types have a compiler-defined description that libraries can
embed in generated metadata (audio endpoints, versioned patch state) without
hand-assigned `type_key` values and without runtime string reflection on an
RT path.

This page is the user-facing contract for issue #775. The first slice shipped
family/schema IDs, `alignof`, and `TransportSafe`. This page also covers the
remaining surface: member description tables, `@schema_revision`, and
native64-versus-wasm32 layout certificates.

Identity is target-independent: the same public type yields the same family,
schema, and member-table IDs whether the program is lowered to C, MLIR, or
Wasm. Size, alignment, and field offsets are the ABI and may differ across
native64 (8-byte pointers) and wasm32 (4-byte pointers), so they are not
folded into the identity.

## Three levels

One scalar cannot be both semantic identity and an ABI certificate. A
pointer-bearing struct is the same Flow type on native64 and wasm32, but the
size, alignment, and field offsets change.

| Level | Builtin | Meaning |
|-------|---------|---------|
| Family | `type_family_id<T>() -> u64` | Nominal family (public name / constructor). Stable across schema revisions of the same named type. |
| Schema | `type_schema_id<T>() -> u64` | FNV-1a 64 of the v1 canonical public schema: field names and order, semantic field types, extents, enum variants, generic args, and `@schema_revision(N)` when set. No C/MLIR/Wasm layout. |
| Members | `type_member_count<T>() -> i32` | Public field count (0 for scalars). |
| Members | `type_member_table<T>() -> u64` | FNV-1a 64 of the ordered member description table: each field's name and field `schema_id`. Target-independent. |
| Revision | `type_schema_revision<T>() -> i32` | `@schema_revision(N)` on the type, or `0` if unset. |
| Layout | `sizeof<T>()` / `alignof<T>() -> i64` | Host ABI size and alignment. |
| Layout | `type_sizeof_native64<T>()` / `type_sizeof_wasm32<T>() -> i64` | Size for pointer width 8 and 4. |
| Layout | `type_alignof_native64<T>()` / `type_alignof_wasm32<T>() -> i64` | Alignment for those ABIs. |
| Layout | `type_layout_native64<T>()` / `type_layout_wasm32<T>() -> u64` | Layout certificate: FNV-1a 64 of size, alignment, and field offsets. Equal when the two ABIs agree. |
| Predicate | `type_transport_safe<T>() -> bool` | Conservative `TransportSafe(T)`: fixed-width scalars, fixed arrays, and structs of those. Pointers, spans, strings, and extern/fn types are rejected. |

IDs and certificates are compile-time integer constants. The C backend emits
`((uint64_t)0x…ULL)` / `((int64_t)N)`; the MLIR backend emits the same values.

## Schema revision

`@schema_revision(N)` may sit on a `struct`, `enum`, or `type` alias (including
`export` forms). `N` is a non-negative integer.

- Family identity does not include the revision: the same public name stays
  the same migration family.
- Schema identity includes `;rev;N` only when `N != 0`, so unversioned types
  keep the v1 keys from the first #775 slice.
- The member table does not include the revision; it describes the public
  fields. Two revisions with the same fields share a member table and differ
  in `type_schema_id` / `type_schema_revision`.

```flow
struct EndpointSample {
    left: f32
    right: f32
}

@schema_revision(2)
struct EndpointSampleV2 {
    left: f32
    right: f32
}

function revision_ids() -> i32 {
    if type_schema_revision<EndpointSample>() != 0 {
        return 1
    }
    if type_schema_revision<EndpointSampleV2>() != 2 {
        return 2
    }
    if type_member_table<EndpointSample>() != type_member_table<EndpointSampleV2>() {
        return 3
    }
    if type_schema_id<EndpointSample>() == type_schema_id<EndpointSampleV2>() {
        return 4
    }
    return 0
}
```

## Member description table

`type_member_table<T>()` is the structured public-field description as a
digest: field names in source order and the schema of each field type. Field
order and field-type changes move the table; a field rename does too. The
count is `type_member_count<T>()`.

That is the table exporters and state migration can store next to
`type_schema_id<T>()` without a second hand-maintained schema. Offsets stay
out of it; they belong to the layout certificate.

## Native64 versus wasm32 layout certificates

`type_layout_native64<T>()` and `type_layout_wasm32<T>()` hash the same
canonical ABI string (`v1;lay;size;align;off0;off1;…`) under pointer width 8
and 4. When the layouts match, the certificates are equal.

```flow
struct HasPtr {
    p: ptr<i32>
    n: i32
}

function layout_certs() -> i32 {
    if type_layout_native64<EndpointSample>() != type_layout_wasm32<EndpointSample>() {
        return 1
    }
    if type_sizeof_native64<HasPtr>() != 16 {
        return 2
    }
    if type_sizeof_wasm32<HasPtr>() != 8 {
        return 3
    }
    if type_layout_native64<HasPtr>() == type_layout_wasm32<HasPtr>() {
        return 4
    }
    return 0
}
```

## Compatibility lattice

- family equal → same migration family
- schema equal → same exact semantic schema revision
- schema equal and `TransportSafe` → cross-target schema payload compatibility
- schema equal and layout certificates equal → same ABI representation
  (address-space ownership is still checked separately)

Scheme v1 prefixes canonical strings with `v1;` so a later digest can change
without silently reusing old keys.

## See also

[Types](types.md), the [language specification](../LANGUAGE_SPEC.md), and
GitHub issue #775.
