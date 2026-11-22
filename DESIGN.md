# Design

<!-- impeccable:design-schema 1 -->

## Visual World

The site extends PLAYTREE's existing near-black forest identity as a chapter dossier. Near-black green is the field, vivid green carries action and progress, and gold marks chapter and round information.

## Palette

- `--ink`: #07110b
- `--ink-2`: #0b1910
- `--ink-3`: #11231a
- `--green`: #55ef78
- `--green-2`: #35c85a
- `--green-soft`: #9beaaa
- `--gold`: #e0c66a
- `--text`: #ecf6ed
- `--muted`: #9aafa0

## Typography

Use the system sans stack for interface and display copy. Headings use a compact, heavy scale with negative letter spacing. Keep body copy readable and avoid decorative monospace treatment.

## Surface Structure

The primary experience is a campaign dossier:

- Fixed translucent navigation over the page
- Large split first viewport with title/action on the left and a framed chapter artifact on the right
- Campaign trail directly under the chapter artwork
- A compact proof strip
- Four alternating campaign entries
- A systems index built as ruled rows
- A platform-focused download section

## Components

- Plain bordered buttons with a primary vivid-green action
- Ruled navigation and data divisions instead of repeated card shells
- Campaign nodes shown as in-world waypoints
- Modal panels for existing account and trailer interactions

## Responsive Rules

- Above 980px: two-column hero and alternating campaign layout
- 980px and below: stacked hero, single-column navigation menu
- 640px and below: 2-column proof strip, 1-column campaign entries, full-width actions

## Motion

Use only short transform and color transitions for actions. Preserve reduced-motion behavior and avoid nonessential particle effects for users who opt out.
