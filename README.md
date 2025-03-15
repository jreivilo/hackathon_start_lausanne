# Hackathon Start Lausanne 2025

## Event Details
📅 **Date:** 14-16 March 2025  
📍 **Location:** Lausanne  

## Documentation
For complete project documentation, please consult the following documents:

- [General Documentation](DOCUMENTATION.md) - Complete project overview
- [Developer Guide](DEVELOPER_GUIDE.md) - Detailed technical guide for developers
- [User Guide](USER_GUIDE.md) - End-user instructions

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
Copy the `.env.template` file and rename it to `.env`. Then, update the necessary environment variables:

```bash
cp .env.template .env
```

Edit `.env` and replace placeholders with actual values.

### 5️⃣ Run the Project
To execute the code, use the following command:

```bash
uv run chainlit run main.py -w
```

---

## 👥 Team Members
- **Jérémy Olivier**
- **Alexandre Mugg**
- **Isabel Tovar**
- **Jérémy Dos Santos**

---

�� Happy Hacking! 🎉
