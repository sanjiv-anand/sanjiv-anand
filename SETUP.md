# Setup Instructions

## 1. Create the special profile repo
GitHub shows this README on your profile page only if the repo name
**exactly matches your username**.

- Create a new repo named: `sanjus-robotic-studio`
- Make it **public**
- Don't initialize with a README (you already have one)

## 2. Upload these files
Push everything in this folder to that repo, keeping the structure:

```
sanjus-robotic-studio/
├── README.md
├── generate_readme.py
├── svg_render.py
├── requirements.txt
├── assets/
│   ├── avatar.png          <- your pixel-art image
│   ├── dark_mode.svg        <- auto-generated, don't hand-edit
│   └── light_mode.svg       <- auto-generated, don't hand-edit
└── .github/
    └── workflows/
        └── update-readme.yml
```

## 3. Avatar
Your pixel-art avatar is already baked into `assets/dark_mode.svg` and
`assets/light_mode.svg`. If you ever want to swap it for a new image,
replace `assets/avatar.png` and re-run `python generate_readme.py`
locally (or just trigger the Action) to rebake both SVGs.

## 4. Create a Personal Access Token (PAT)
The default `GITHUB_TOKEN` that Actions provides can't always read full
account-wide stats (like `repositoriesContributedTo` across all repos), so
we use a PAT instead:

1. Go to **GitHub Settings → Developer settings → Personal access tokens →
   Tokens (classic)**
2. Click **Generate new token (classic)**
3. Name it something like `readme-stats-token`
4. Set an expiration (or no expiration, your choice)
5. Select scopes: `repo` and `read:user`
6. Generate it and **copy the token** (you won't see it again)

## 5. Add the token as a repo secret
1. In your `sanjus-robotic-studio` repo, go to **Settings → Secrets and
   variables → Actions**
2. Click **New repository secret**
3. Name: `GH_PAT`
4. Value: paste the token from step 4
5. Save

## 6. Run it
- Go to the **Actions** tab in your repo
- Click **Update README Stats** → **Run workflow**
- After ~30–60 seconds, refresh your README — the stats should be filled in

From then on, it re-runs automatically every day at 03:00 UTC and
whenever you push to `main`.

## Notes
- The "Lines of Code" count depends on GitHub's `stats/contributors`
  cache being warm for each repo. The first run may under-count for very
  recently created/updated repos — a second run a few minutes later
  usually fixes it.
- README.md just displays `assets/dark_mode.svg` / `assets/light_mode.svg`
  via a `<picture>` tag, so it automatically matches the viewer's system
  theme. You don't need to touch README.md again unless you want to
  change the caption text below the image.
- Static bio/skills text (Model Name, Chip, Built-In, etc.) lives inside
  `svg_render.py` — edit the strings there if your info changes, then
  either re-run the script locally or just push (the Action will bake a
  fresh SVG with your live stats).
