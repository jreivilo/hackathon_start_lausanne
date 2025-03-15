# Hackathon Start Lausanne 2025

## Event Details
📅 **Date:** 14-16 March 2025  
📍 **Location:** Lausanne  

## Project Setup

### 1️⃣ Install `uv`
To set up your environment, install `uv` by running:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Install Dependencies
Once `uv` is installed, sync all required libraries:

```bash
uv sync
```

### 3️⃣ Generate Chainlit Secret
To generate the Chainlit secret, run:

```bash
uv run chainlit secret
```

### 4️⃣ Fill the `.env` File
Create a `.env` file in the project root and add the following environment variables:

```env
CHAINLIT_SECRET=<your_generated_secret>
OTHER_ENV_VARIABLE=<your_value>
```

Make sure to replace `<your_generated_secret>` with the actual secret generated in the previous step.

### 5️⃣ Run the Project
To execute the code, use the following command:

```bash
uv run chainlit run main.py -w
```

### 6️⃣ Add New Packages
To install additional dependencies, use:

```bash
uv add <package>
```

---

## 👥 Team Members
- **Jérémy Olivier**
- **Alexandre Mugg**
- **Isabel Tovar**
- **Jérémy Dos Santos**

---

🚀 Happy Hacking! 🎉

