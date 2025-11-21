**10 Zen Rules of Excellent Programming Teaching**.

### 1. Build the Mental Model Before the Syntax

**Do not teach the _How_ until the student sees the _What_.**
_The Instructor’s Way:_ Before typing `try:`, he explains the concept of a "propagation workflow" moving up a stack. Syntax is merely the implementation of a concept; if the student understands the concept, the syntax is easy to learn. If they only learn syntax, they are lost when the context changes.

### 2. Illuminate the Path by Showing the Pits

**To teach the right way, you must first demonstrate the consequences of the wrong way.**
_The Instructor’s Way:_ He does not simply say "Don't use bare exceptions." He writes code using a bare `except:`, runs it, and demonstrates how it swallows a `TypeError` when you were looking for an `IndexError`. Wisdom comes from seeing the crash, not just avoiding it.

### 3. Banish Magic with Mechanics

**There is no magic in code, only hidden machinery. Expose it.**
_The Instructor’s Way:_ He refuses to treat Exceptions as special system events. He runs `type(Exception)` and checks `__mro__` to prove they are just standard objects that follow standard inheritance rules. When a student understands the mechanics, their fear of the unknown vanishes.

### 4. Treat Errors as Data, Not Failure

**A crash is not a dead end; it is a map.**
_The Instructor’s Way:_ He intentionally raises exceptions to generate massive stack traces. Instead of clearing the screen, he parses the traceback line-by-line, teaching the student to read the "red text" as a high-fidelity narrative of exactly what happened and where.

### 5. Scaffold from Toy to Tool

**Start with the trivial to explain the mechanism; end with the architectural to explain the utility.**
_The Instructor’s Way:_ He begins with `1 / 0` (a toy problem) to show how `try/except` works. He ends by building a custom `APIException` class with internal JSON serialization and logging integration (a professional tool). The student must see the bridge between the two.

### 6. Teach the Philosophy, Not Just the Vocabulary

**A language is defined by its idioms, not just its keywords.**
_The Instructor’s Way:_ He doesn't just teach exception handling; he teaches the Pythonic philosophy of **EAFP** (Easier to Ask Forgiveness than Permission). He contrasts it with "Look Before You Leap" to explain _why_ the culture of the language prefers handling errors over checking conditions.

### 7. Show the Journey, Not Just the Destination

**Perfect code on the first try is a lie. Show the refactor.**
_The Instructor’s Way:_ He writes a function with three levels of ugly, nested `try` blocks. He admits it is messy. Then, he refactors it using custom exceptions and `raise from None`. Students must see the evolution of code, not just the polished final product.

### 8. Anchor Abstract Logic in Concrete Reality

**Abstract variables (`foo`, `bar`) breed abstract understanding. Use domain context.**
_The Instructor’s Way:_ He moves quickly away from meaningless variables to building a "Web Scraper" or a "Bank Account" system. When an error changes from `ValueError` to `InsufficientFundsError`, the student intuitively understands the stakes of the code.

### 9. Anticipate the Lazy Shortcut

**Know where the student will try to cheat, and meet them there.**
_The Instructor’s Way:_ He knows beginners want to write `except Exception:` because it is easy. He calls this out explicitly ("You might be tempted to do this..."), validates why they want to do it, and then proves why it is technical debt in disguise.

### 10. Code Does Not Live in a Vacuum

**Teach the feature as part of a living ecosystem.**
_The Instructor’s Way:_ He does not teach exceptions in isolation. He connects them to **Logging** (how to record the error), **APIs** (how to return an HTTP 500 status), and **Data** (how to serialize the error to JSON). Excellent teaching positions the specific skill within the wider engineering system.
