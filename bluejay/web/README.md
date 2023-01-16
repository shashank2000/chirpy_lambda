# Bluejay Web Client

This is a [Next.js](https://nextjs.org/) project.

## Getting Started

### VSCode Extensions

- In VSCode, open the extensions menu in the left sidebar
- Search and install “ESLint”
- Search and install “Prettier - Code formatter”

### Project Installation

Go to the `bluejay/web` directory:

```bash
cd bluejay/web
```

If you don't have `yarn` installed, install it:

```bash
npm install -g yarn
```

Then, install the project's dependencies:

```bash
yarn install
```

Finally, run the development server:

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `pages/index.tsx`. The page auto-updates as you edit the file.

## Build and Deploy on Vercel

Go to the `bluejay/web` directory:

```bash
cd bluejay/web
```

Make sure all the dependencies are installed:

```bash
yarn install
```

Then, go back to the root directory of the `chirpycardinal` repository:

```bash
cd ../..
```

Install the Vercel CLI:

```bash
npm install -g vercel
```

Login to Vercel:

```bash
vercel login
```

Deploy the `bluejay/web` directory:

```bash
vercel --prod
```

When prompted, answer the following:

```
? Set up and deploy “chirpycardinal”? [Y/n] y
? Which scope do you want to deploy to? stanfordnlp
? Link to existing project? [y/N] y
? What’s the name of your existing project? chirpycardinal-22-23
```
