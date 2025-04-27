# PDF to Podcast AI Agent
![pdfpod](https://github.com/user-attachments/assets/ed884e1a-f8e0-4c36-abac-b7f9be16565c)

Welcome to the **PDF to Podcast AI Agent**, a Python-based project that transforms PDF documents into engaging, natural-sounding podcast scripts. Using LangGraph for workflow orchestration and a large language model (LLM) from Together AI, this agent processes PDF content through multiple stages—outline creation, transcript generation, dialogue optimization, and final podcast script production. The result is a polished, production-ready podcast dialogue between two hosts, complete with sound cues and conversational flow.

This project is ideal for educators, content creators, or developers looking to automate the conversion of technical documents (e.g., a DBMS textbook) into accessible audio content.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Example Output](#example-output)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **PDF Processing**: Extracts text from PDFs to serve as the foundation for podcast content.
- **Structured Workflow**: Uses LangGraph to manage a multi-step pipeline, including outline creation, transcript generation, and dialogue optimization.
- **Natural Dialogue**: Generates engaging, two-person podcast scripts with smooth transitions, humor, and professional tone.
- **Deep Insights**: Enhances content with analogies, background information, and examples for richer discussions.
- **Audio Output**: Converts the final script into audio using a text-to-speech utility (via `create_audio`).
- **Environment Safety**: Securely handles API keys using environment variables.

---

## How It Works

The AI agent processes a PDF document through a series of nodes in a LangGraph workflow:

1. **Outline Creation**: Generates a high-level outline from the PDF content.
2. **Structured Outline**: Converts the outline into a conversation plan for a two-person podcast.
3. **Segment Transcript**: Transforms the plan into natural-sounding spoken dialogue.
4. **Deep Dive**: Adds depth with analogies, examples, and background information.
5. **Transcript Optimization**: Refines the dialogue for clarity, coherence, and engagement.
6. **Podcast Dialogue**: Structures the transcript into a lively podcast format.
7. **Outline Fusion**: Re-aligns the dialogue with the original outline for consistency.
8. **Revision**: Polishes the dialogue for natural flow and storytelling.
9. **Final Podcast Script**: Produces a broadcast-ready script with sound cues (e.g., `[music fades in]`).
10. **Audio Generation**: Converts the script into audio output.

The workflow is powered by the Together AI LLM (`meta-llama/Llama-3.3-70B-Instruct-Turbo-Free`) and orchestrated by LangGraph for robust state management.

---

## Installation

Follow these steps to set up the project locally:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/pdf-to-podcast.git
   cd pdf-to-podcast
   ```

2. **Install Python**:
   Ensure you have Python 3.8+ installed. Check with:
   ```bash
   python --version
   ```

3. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Dependencies**:
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**:
   Create a `.env` file in the project root and add your Together AI API key:
   ```env
   TOGETHER_API_KEY=your_together_api_key_here
   ```
   Install `python-dotenv` to load the `.env` file:
   ```bash
   pip install python-dotenv
   ```

6. **Prepare PDF Files**:
   Place your input PDF (e.g., `dbms.pdf`) in the `PDFs/` directory.

---

## Usage

1. **Run the Script**:
   Execute the main script to process a PDF and generate a podcast script:
   ```bash
   python main.py
   ```

2. **Input**:
   The script reads a PDF from `PDFs/dbms.pdf` (modify the path in `main.py` if needed).

3. **Output**:
   - A polished podcast script is printed to the console.
   - An audio file is generated using the `create_audio` utility (ensure the utility is configured).

4. **Example**:
   For a DBMS PDF, the output might look like:
   ```
   **Intro Music Fades In**
   Alex: "Welcome to Deep Dive Talks! Today, we’re exploring the world of Database Management Systems!"
   Sam: "[chuckles] Ever wondered how your favorite apps store all that data? Let’s dive in!"
   ...
   **Outro Music Fades In**
   ```

---

## Example Output

Below is a sample of the podcast audio generated from a DBMS PDF. This audio file, `converted.wav`, was created using the `create_audio` utility after processing the PDF through the AI agent workflow.

**Listen to the Sample Podcast:**

![GeneratedFile](https://github.com/DARK-Shadw/PDF-to-Podcast/blob/main/converted.wav)

---

## Project Structure

```
pdf-to-podcast/
├── PDFs/                 # Directory for input PDF files
├── converted.wav         # Sample podcast audio output
├── util.py               # Utilities for PDF reading and audio generation
├── main.py               # Main script with LangGraph workflow
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (not tracked)
├── README.md             # This file
└── .gitignore            # Git ignore file
```

---

## Dependencies

- `langgraph`: For workflow orchestration
- `langchain-together`: For LLM integration with Together AI
- `python-dotenv`: For environment variable management
- `typing-extensions`: For typed dictionaries
- Custom utilities (`util.py`):
  - `PdfRead`: PDF text extraction
  - `create_audio`: Text-to-speech conversion

Install dependencies with:
```bash
pip install langgraph langchain-together python-dotenv typing-extensions
```

Note: Ensure `util.py` includes working implementations of `PdfRead` and `create_audio`.

---

## Environment Variables

The project uses the following environment variable:

- `TOGETHER_API_KEY`: Your Together AI API key for accessing the LLM.

Store it in a `.env` file:
```env
TOGETHER_API_KEY=your_together_api_key_here
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure your code follows PEP 8 style guidelines and includes tests where applicable.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Together AI**: For providing the LLM backend.
- **LangGraph**: For enabling structured workflows.
---

Happy podcasting! 🎙️
