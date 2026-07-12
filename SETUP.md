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
├── requirements.txt
├── assets/
│   └── avatar.png       <- add your pixel-art image here
└── .github/
    └── workflows/
        └── update-readme.yml
```

## 3. Add your avatar
Drop your pixel-art image into `assets/avatar.png` (any size, ~220px wide
looks best). The README already points to this path.

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
- You can freely edit any of the static text in `README.md` (bio, contact,
  skills) — only the block between `<!--START_SECTION:stats-->` and
  `<!--END_SECTION:stats-->` gets overwritten automatically.
