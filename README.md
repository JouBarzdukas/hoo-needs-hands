# HooNeedsHands

**HooNeedsHands** is a voice-activated, multi-agent personal assistant designed to perform tasks hands-free. It combines a unintrusive, simple orb interface GUI with a Python-based backend to coordinate specialized agents for browser control, desktop control, data storage, and general knowledge queries, all triggered by simple voice commands.

- ### **Devpost:** [View on Devpost](https://devpost.com/software/hooneedshands)
- ### **Demo Video:** [Watch Demo](#)

## Setup

1. **Backend Setup**  
   - Navigate to the `backend` directory:  
     ```bash
     cd backend
     ```  
   - Install required Python packages:  
     ```bash
     pip install -r requirements.txt
     ```  
   - Create a `.env` file in the `backend` directory and set your OpenAI key, Porcupine key, and OS:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     PORCUPINE_API_KEY=your_porcupine_key
     DEVICE = linux/mac/windows
     ```

2. **Backend Watcher Setup**
    - Navigate to the `backend_watcher` directory:  
      ```bash
      cd backend_watcher
      ```

    - Install required Python packages for the watcher:
        ```bash
        pip install -r requirements.txt
        ```

3. **Electron Setup**  
   - Navigate to the `electron-app` directory:  
     ```bash
     cd electron-app
     ```  
   - Install the required dependencies (using npm):  
     ```bash
     npm install --force
     ```  
   - Follow any additional installation instructions that may appear.
## How to Run

1. **Run the Backend**  
   - In the `backend` directory:  
     ```bash
     python main.py
     ```

2. **Run the Backend Watcher**  
   - In the `backend_watcher` directory:  
     ```bash
     python main.py
     ```

3. **Run the Electron App**  
   - In the `electron-app` directory:  
     ```bash
     npm run dev
     ```  
   - This launches the GUI. You should see a window or overlay that displays audio levels and responds to your configured wake word.

4. **Use the Voice Assistant**  
   - Say the configured wake word (e.g., “Hey Jarvis”) to start voice capture.
   - Issue a command (e.g., “Open YouTube and search for cat videos”) and watch the system delegate tasks to the right agent.
   
## How We Built It

### Frontend

The frontend was built using **Electron**, **React**, and **TypeScript** to deliver a smooth and responsive desktop experience. We designed a **floating orb GUI** that:
- Visualizes real-time audio levels
- Clearly communicates when the system is listening, thinking, or responding
- Remains unintrusive and accessible
- Semi-translucent chat history

---

### Backend

#### Agents

All agents are implemented within the **LangGraph** framework, allowing modular, stateful agent orchestration in a clean and scalable way.

- **Manager Agent**  
  Directs each user command to the appropriate specialized agent (browser, computer, database, or general knowledge) based on intent.

- **Browser Agent**  
  Parses natural language commands and generates a structured plan for DOM-based interactions using an LLM.  
  It maintains a live DOM state and uses **Playwright** to perform real-time browser actions like clicking, typing, or navigating.

- **Computer Agent**  
  Handles OS-level GUI interactions. It captures a **screenshot** of the desktop, uses **visual grounding** to locate UI elements (buttons, menus, etc.), and simulates mouse/keyboard inputs.

- **Database Agent**  
  Provides long-term memory through a retrieval pipeline backed by **ChromaDB**.  
  It can insert and query vectorized data such as preferences, credentials, or past interactions to personalize user experience.

- **General Knowledge Agent**  
  Leverages a powerful **instruction-tuned LLM** to handle open-ended queries and general reasoning tasks that don’t require system interaction.

#### Voice Pipeline

The voice interaction layer connects users to the system using real-time audio:

- **Porcupine** – Detects the wake word from raw audio input
- **PyAudio** – Captures the microphone stream
- **OpenAI** – Transcribes spoken commands into text
- **Kokoro** – Converts text responses back into natural-sounding speech

This pipeline allows for a seamless voice-first experience, enabling users to speak naturally and receive fast, contextual responses.

## Tree
```plaintext
.
├── .gitignore
├── LICENSE
├── README.md
├── backend
│   ├── .env
│   ├── .gitignore
│   ├── __pycache__
│   │   ├── main.cpython-310.pyc
│   │   └── main.cpython-312.pyc
│   ├── agents
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── browser_agent.py
│   │   ├── computer_agent.py
│   │   ├── db_agent.py
│   │   ├── general_knowledge_agent.py
│   │   └── master_agent.py
│   ├── browser_use_example.txt
│   ├── data
│   │   └── chroma
│   ├── general_knowledge_example.txt
│   ├── graph.png
│   ├── main.py
│   ├── output.txt
│   ├── requirements.txt
│   ├── server.py
│   ├── tools
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── browseruse_tool.py
│   │   ├── computeruse_tool.py
│   │   ├── db_tool.py
│   │   └── general_knowledge_tool.py
│   ├── venv
│   │   ├── bin
│   │   ├── include
│   │   ├── lib
│   │   ├── pyvenv.cfg
│   │   └── share
│   └── voice
│       ├── __pycache__
│       ├── test.py
│       ├── text_to_speech.py
│       └── voice_activation.py
├── backend_watcher
│   ├── .gitignore
│   ├── __pycache__
│   │   └── main.cpython-312.pyc
│   ├── main.py
│   ├── requirements.txt
│   └── venv
│       ├── bin
│       ├── include
│       ├── lib
│       └── pyvenv.cfg
├── electron-app
│   ├── .DS_Store
│   ├── .editorconfig
│   ├── .gitignore
│   ├── .npmrc
│   ├── .prettierignore
│   ├── .prettierrc.yaml
│   ├── .vscode
│   │   ├── extensions.json
│   │   ├── launch.json
│   │   └── settings.json
│   ├── README.md
│   ├── dev-app-update.yml
│   ├── electron-builder.yml
│   ├── electron.vite.config.ts
│   ├── eslint.config.mjs
│   ├── out
│   │   ├── .DS_Store
│   │   ├── main
│   │   ├── preload
│   │   └── renderer
│   ├── package-lock.json
│   ├── package.json
│   ├── resources
│   │   ├── icon.png
│   │   ├── icon2.icns
│   │   └── icon2.png
│   ├── src
│   │   ├── .DS_Store
│   │   ├── main
│   │   ├── preload
│   │   └── renderer
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── tsconfig.web.json
├── graph.png

36 directories, 61 files
```

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Author
This project was developed by Matthew Nguyen, Pradeep Ravi, Daniel Son, and Jou Barzdukas