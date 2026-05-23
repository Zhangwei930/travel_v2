# Repository Guidelines

## Project Structure & Module Organization

This is a UniApp + Vue 3 frontend for “周密出游”, targeting H5 and WeChat Mini Program. Source lives under `src/`. Page routes are defined in `src/pages.json`, platform settings in `src/manifest.json`, and global Sass tokens in `src/uni.scss`. App shell and shared global styles are in `src/App.vue`.

Key modules:
- `src/pages/`: route pages such as `index`, `scenes`, `generate`, `result`, `poi/detail`, `assistant/chat`, and `profile`.
- `src/components/`: shared UI components including `ZTabBar`, `ZSectionHeader`, and `ZTag`.
- `src/api/mock.js`: mock data and the `api.*` boundary for future backend integration.
- `design_handoff_zhoumi/`: design references and prototype files.

Treat `dist/` as generated output unless a task explicitly targets build artifacts.

## Build, Test, and Development Commands

Install dependencies with:

```bash
npm install --legacy-peer-deps
```

Use `npm run dev:h5` for local H5 preview, normally at `http://localhost:3000`. Use `npm run dev:mp-weixin` to generate WeChat Mini Program development output in `dist/dev/mp-weixin/`. Use `npm run build:h5` and `npm run build:mp-weixin` for production builds.

## Coding Style & Naming Conventions

Use Vue 3 Composition API patterns already present in the pages. Keep changes small and page-local unless shared behavior is clearly needed. Prefer descriptive names for refs, computed values, and handlers.

Use Sass variables from `src/uni.scss` for colors, spacing, font sizes, radii, and font families. Avoid hard-coded component colors except scene colors defined in `src/api/mock.js`. Name shared components with the existing `Z` prefix and PascalCase, for example `ZSectionHeader.vue`.

## Testing Guidelines

No automated test script is currently configured in `package.json`. For behavior changes, add the smallest practical test setup before production changes when feasible, then document the command in this file. Until then, verify with `npm run build:h5` and, for Mini Program work, `npm run build:mp-weixin`.

## Commit & Pull Request Guidelines

This checkout has no local commit history for this project. Use Conventional Commits such as `fix(result): correct source labels` or `feat(generate): add loading state`. Keep PRs focused, describe user-visible changes, include verification commands, and attach screenshots for UI changes.

## Agent-Specific Instructions

Preserve product compliance details from `CLAUDE.md`: keep result-page source labels and disclaimers, do not invent real-time data, and route future backend work through `src/api/mock.js`.
