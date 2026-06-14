# Test Plan: JetpackMVVM

## Static Checks
- Open generated project in DevEco Studio.
- Validate `module.json5`, `app.json5`, and resource references.
- Compile ArkTS placeholders.

## UI Migration Checks
- Convert each Android entry screen to ArkUI page/component.
- Map navigation destinations to Harmony router pages.
- Create mock data for repositories and backend calls.

## Behavioral Checks
- Verify cold start and first page rendering.
- Verify list/detail/form flows.
- Verify persistence layer after Room/DataStore replacement.
