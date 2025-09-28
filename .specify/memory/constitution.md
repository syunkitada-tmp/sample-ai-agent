# Sample AI Agent Constitution

## 3 Core Principles

### 1. Working First (NON-NEGOTIABLE)
**Make it work, then make it better**
- Functionality over perfection
- Iteration speed is the priority

### 2. Small Modules (NON-NEGOTIABLE)  
**Design for future testability**
- One module = One responsibility
- Separate business logic from external dependencies

### 3. Progressive Quality
**Prototype → Stabilization → Production**
- No tests required in prototype phase
- Add tests during stabilization
- Full quality gates for production

## Implementation Guidelines

### Error Handling
- Prototype: Basic error handling only
- Stabilization: Add comprehensive error handling

### Documentation
- Module boundaries explanation required only
- Comments for complex logic

### Architecture
- Domain Logic ← Application ← Infrastructure
- Dependencies point inward only

**Version**: 3.0.0 | **Ratified**: 2025-09-25 | **Last Amended**: 2025-09-25