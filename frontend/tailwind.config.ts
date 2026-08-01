import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0c1420",
        ink2: "#121d2e",
        ink3: "#1a2739",
        parchment: "#f2ede1",
        parchmentDim: "#cfc9ba",
        gold: "#c99a4b",
        goldBright: "#e0b563",
        up: "#4f9d69",
        down: "#c25b4a",
        hairline: "#2a3a50",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
