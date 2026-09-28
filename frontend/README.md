# Aarogya One Frontend

React + Vite frontend for the Aarogya One healthcare platform.

## Run in VS Code

1. Open this folder in VS Code.
2. Open Terminal in this folder.
3. Run:

```bash
npm install
```

Wait until the command finishes successfully.

4. Then run:

```bash
npm run dev
```

5. Open the `Local` URL shown by Vite, normally `http://localhost:5173/`.

## If npm install is stuck

Run:

```bash
npm cache verify
npm ping
npm install
```

Do not run `npm run dev` until `npm install` completes successfully.

## Backend

The UI can open without the backend. Features that call FastAPI need the backend running at `http://127.0.0.1:8000`.
