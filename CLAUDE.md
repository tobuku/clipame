# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clipame.com is a static HTML/CSS/JS directory site for the social media clipping industry. It is deployed via GitHub Pages to clipame.com. The site indexes clippers, agencies, tools, communities, and jobs in the short-form video editing ecosystem.

## Deployment

GitHub Pages, main branch. Push to main = live in 1-3 minutes. No build step.

## Tech Stack

- Pure HTML/CSS/JS -- no frameworks, no bundler, no dependencies
- Font: Inter via Google Fonts
- Forms: Formspree endpoint `https://formspree.io/f/mkoldeja` (all forms use this single endpoint)
- No images yet (see `images/IMAGES-NEEDED.txt`)

## Architecture

### Pages

All pages are flat HTML files at the repo root. Every page includes:
- Shared header with nav (copy-pasted, not templated)
- Shared footer (copy-pasted)
- `css/style.css` (single stylesheet)
- `js/main.js` (single script)

The nav active state is set per-page via `nav__link--active` class. When adding or modifying nav items, update ALL pages.

### CSS Conventions

- CSS custom properties defined in `:root` -- navy color palette (`--navy`, `--navy-light`, `--navy-dark`) is the brand identity
- BEM-style naming: `.block__element` and `.block--modifier`
- Card types: `.listing-card` (clippers/agencies), `.tool-card`, `.job-card`, `.community-card`
- Sections: `.section`, `.section--gray` (light bg), `.section--navy` (dark bg)
- Responsive breakpoints: 1024px, 768px, 480px

### JS Features (main.js)

- Header scroll shadow toggle
- Mobile hamburger menu
- Filter buttons: use `data-filter` on `.filter-btn` and `data-category` on cards. Filter bar must be the immediate previous sibling of the card grid
- Search: hero search redirects to clippers.html with `?q=` param; sub-page search filters cards by text content
- Modal system: `data-modal="#modalId"` triggers on any element; `.modal-overlay.active` shows the modal
- Smooth scroll for anchor links

### Data Pattern

All directory listings are hardcoded HTML. There is no database or JSON data source. Each card contains its own data inline. To add a listing, duplicate an existing card in the appropriate page and update the content.

### Modal/Form Pattern

- `index.html` and `clippers.html` share a general "Get Listed" modal (`#submitModal`)
- `agencies.html` has its own agency-specific submit modal (`#submitModal`)
- `jobs.html` has a "Post a Job" modal (`#postJobModal`)
- `about.html` has an inline contact form (no modal)

## Gotchas

- Header and footer are duplicated across all 8 HTML files. Any nav/footer change must be applied to every page.
- The 404.html has no footer -- this is intentional for the minimal error page design.
- Filter buttons rely on DOM order: the `.filter-bar` must be the immediate previous sibling of the grid container for `bar.nextElementSibling` to work.
- The `data-modal` click handler on CTA buttons uses `index.html#submit` hrefs on sub-pages that don't have their own modal. These navigate to index.html rather than opening a modal.
