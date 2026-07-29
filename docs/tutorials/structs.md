# Structs

> Group data with structs and methods-as-functions.


## Part 1: Define & construct

### 1.1 Point literal

```flow
struct Point { x: i32, y: i32 }

function main() -> i32 {
    let p: Point = Point { x: 3, y: 4 }
    printf("(%d, %d)\n", p.x, p.y)
    return 0
}
```
### 1.2 Nested structs

```flow
struct Point { x: i32, y: i32 }
struct Segment { a: Point, b: Point }

function main() -> i32 {
    let s: Segment = Segment {
        a: Point { x: 0, y: 0 },
        b: Point { x: 10, y: 5 }
    }
    printf("%d -> %d\n", s.a.x, s.b.x)
    return 0
}
```

## Part 2: Functions

### 2.1 Translate point

```flow
struct Point { x: i32, y: i32 }

function translate(p: Point, dx: i32, dy: i32) -> Point {
    return Point { x: p.x + dx, y: p.y + dy }
}

function main() -> i32 {
    let p: Point = translate(Point { x: 1, y: 2 }, 3, 4)
    printf("(%d, %d)\n", p.x, p.y)
    return 0
}
```
### 2.2 Mutate via ptr

```flow
struct Point { x: i32, y: i32 }

function nudge(p: ptr<Point>) -> void {
    p[0].x = p[0].x + 1
}

function main() -> i32 {
    let mut p: Point = Point { x: 0, y: 0 }
    nudge(&p)
    printf("%d\n", p.x)
    return 0
}
```

## Part 3: Records

### 3.1 RGB colour

```flow
struct Color { r: i32, g: i32, b: i32 }

function luminance(c: Color) -> i32 {
    return (c.r * 3 + c.g * 6 + c.b) / 10
}

function main() -> i32 {
    let c: Color = Color { r: 10, g: 20, b: 30 }
    printf("Y~%d\n", luminance(c))
    return 0
}
```
### 3.2 Rect area

```flow
struct Rect { w: i32, h: i32 }

function area(r: Rect) -> i32 {
    return r.w * r.h
}

function main() -> i32 {
    printf("%d\n", area(Rect { w: 16, h: 9 }))
    return 0
}
```
### 3.3 Player stats

```flow
struct Player { hp: i32, atk: i32 }

function hit(p: ptr<Player>, dmg: i32) -> void {
    p[0].hp = p[0].hp - dmg
}

function main() -> i32 {
    let mut hero: Player = Player { hp: 100, atk: 12 }
    hit(&hero, 25)
    printf("hp=%d\n", hero.hp)
    return 0
}
```
