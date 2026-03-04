# AI Event Planner Chatbot

<div align="center">

<!-- TODO: Add a project logo (e.g., an icon representing AI and events) -->
<!-- ![Logo](assets/logo.png) -->

[![GitHub stars](https://img.shields.io/github/stars/niranjan022/AI_EVENT_PLANNER_CHATBOT?style=for-the-badge)](https://github.com/niranjan022/AI_EVENT_PLANNER_CHATBOT/stargazers)

[![GitHub forks](https://img.shields.io/github/forks/niranjan022/AI_EVENT_PLANNER_CHATBOT?style=for-the-badge)](https://github.com/niranjan022/AI_EVENT_PLANNER_CHATBOT/network)

[![GitHub issues](https://img.shields.io/github/issues/niranjan022/AI_EVENT_PLANNER_CHATBOT?style=for-the-badge)](https://github.com/niranjan022/AI_EVENT_PLANNER_CHATBOT/issues)


**An intelligent, AI-powered chatbot designed to simplify and streamline your event planning process.**

<!-- TODO: Add a live demo link if available -->
<!-- [Live Demo](https://ai-event-planner.vercel.app) -->
<!-- TODO: Add a documentation link if available -->
<!-- [Documentation](https://docs.ai-event-planner.com) -->

</div>

## 📖 Overview

The AI Event Planner Chatbot is an innovative application that leverages artificial intelligence to assist users in organizing various events. From casual gatherings to formal occasions, this chatbot acts as a personalized event assistant, guiding users through the planning stages, suggesting ideas, managing details, and providing helpful recommendations. It aims to reduce the stress and complexity typically associated with event coordination by offering an intuitive, conversational interface.

## ✨ Features

-   🎯 **AI-Powered Conversational Interface:** Interact naturally with the chatbot to discuss event details and requirements.
-   📝 **Event Detail Collection:** Automatically gathers critical information like event type, date, time, location, and guest count.
-   💡 **Intelligent Suggestions:** Receives recommendations for themes, venues, catering, and activities based on user input.
-   📅 **Timeline & Task Management:** Helps users create and manage event timelines and task lists.
-   ✍️ **Event Summary Generation:** Provides a concise summary of the planned event details.
-   🔒 **User Session Management:** Maintains context throughout the conversation for a seamless planning experience.
-   📱 **Responsive Design:** Accessible and user-friendly across various devices and screen sizes.

## 🖥️ Screenshots

<!-- TODO: Add actual screenshots of the chatbot interface and event planning flow -->
<!-- ![Screenshot 1 - Chatbot Conversation](assets/screenshot-conversation.png) -->
<!-- *Chatbot in action, guiding event planning.* -->
<!-- ![Screenshot 2 - Event Summary](assets/screenshot-summary.png) -->
<!-- *Generated event summary.* -->

## 🛠️ Tech Stack

**Frontend:**

![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)

![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

**Backend:**

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white) <!-- Or FastAPI/Django, inferred for Python web backend -->

**AI/ML:**

![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white) <!-- Inferred for chatbot intelligence -->

**Database:**

![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white) <!-- Or PostgreSQL/MongoDB, inferred for data storage -->

## 🚀 Quick Start

Follow these steps to get the AI Event Planner Chatbot up and running on your local machine.

### Prerequisites
-   **Python 3.8+**: Essential for the backend AI logic.
-   **Node.js & npm (or yarn/pnpm)**: Required if there's a separate frontend build process or for managing frontend dependencies.
    -   Node.js (version 16.x or higher recommended)
    -   npm (version 8.x or higher)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/niranjan022/AI_EVENT_PLANNER_CHATBOT.git
    cd AI_EVENT_PLANNER_CHATBOT
    ```

2.  **Navigate to the project directory**
    The core project files are located in the `EVENT_PLANNER_CHATBOT` subdirectory.
    ```bash
    cd EVENT_PLANNER_CHATBOT
    ```

3.  **Install backend dependencies**
    ```bash
    # Create a virtual environment (recommended)
    python -m venv venv
    source venv/bin/activate # On Windows, use `venv\Scripts\activate`

    # Install Python packages
    pip install -r requirements.txt # TODO: Create a requirements.txt based on backend dependencies
    ```
    *(Note: If `requirements.txt` is not present, you'll need to manually install `Flask` and `openai` via `pip install flask openai` or similar.)*

4.  **Install frontend dependencies** (if applicable)
    ```bash
    # If there's a separate frontend directory with its own package.json
    # cd frontend/
    # npm install # or yarn install / pnpm install
    # cd ../
    ```
    *(Note: This step is only necessary if the frontend is a separate buildable project. If it's pure HTML/CSS/JS served by the backend, this step can be skipped.)*

5.  **Environment setup**
    Create a `.env` file in the `EVENT_PLANNER_CHATBOT` directory.
    ```bash
    cp .env.example .env # TODO: Create a .env.example file
    ```
    Open `.env` and configure your environment variables:
    ```
    OPENAI_API_KEY="your_openai_api_key_here" # Required for AI functionality
    # FLASK_APP=app.py                       # Example for Flask applications
    # FLASK_ENV=development
    ```
    *Ensure you have an OpenAI API key for the chatbot to function correctly.*

6.  **Database setup** (if applicable)
   Create a MongoDB Database and create a collection for storing the user data.
(Note: You can use someother database and change the code accordingly)
   

7.  **Start development server**
    ```bash
    # For a Python Flask backend
    python app.py # Or `flask run` if FLASK_APP is set in .env
    ```
    *(Note: If there's a separate frontend, you might need to start it too, e.g., `npm run dev` from the `frontend/` directory.)*

8.  **Open your browser**
    Visit `http://localhost:[detected_port]` (commonly `http://localhost:5000` for Flask).

## 📁 Project Structure

```
AI_EVENT_PLANNER_CHATBOT/
├── EVENT_PLANNER_CHATBOT/
│   ├── static/               # Static assets (CSS, JS for frontend)
│   │   ├── css/
│   │   ├── js/
│   ├── templates/            # HTML templates for the web interface
│   ├── app.py                # Main Flask application file
│   ├── services/             # Backend logic for AI interactions, event parsing, etc.
│   │   └── chatbot_service.py
│   ├── utils/                # Utility functions
│   ├── .env.example          # Example environment variables
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # This README file (or a project-specific one)
├── .github/                  # (Optional) GitHub Actions workflows
├── .gitignore
└── README.md                 # Main repository README (this file)
```

## ⚙️ Configuration

### Environment Variables
Configure these variables in your `.env` file.

| Variable        | Description                            | Default | Required |

|-----------------|----------------------------------------|---------|----------|

| `OPENAI_API_KEY`| Your API key for accessing OpenAI services. |         | Yes      |

| `FLASK_APP`     | The main Flask application entry point. | `app.py`| No       |

| `FLASK_ENV`     | The Flask environment (e.g., `development`, `production`). | `production` | No |

| `DATABASE_URL`  | URL for database connection (e.g., for PostgreSQL). | `sqlite:///site.db` | No |

### Configuration Files
-   `.env`: Stores sensitive environment variables. Not committed to version control.
-   `requirements.txt`: Lists all Python dependencies for the backend.

## 🔧 Development

### Available Scripts
*(Based on common Python Flask project scripts)*

| Command                 | Description                                    |

|-------------------------|------------------------------------------------|

| `python app.py`         | Starts the Flask development server.           |

| `pip install -r requirements.txt` | Installs all Python dependencies.              |

| `source venv/bin/activate`| Activates the Python virtual environment.      |

### Development Workflow
1.  **Activate Virtual Environment**: Always activate your `venv` before running Python commands.
2.  **Modify Code**: Make changes to `app.py`, `services/`, `static/`, or `templates/`.
3.  **Run Server**: Restart the Flask server (`python app.py`) to see changes.

## 🧪 Testing

*(Based on common Python testing practices)*

```bash

# TODO: Add a testing framework (e.g., pytest) and commands.

# Example:

# Install pytest

# pip install pytest

# Run all tests

# pytest

# Run specific test file

# pytest tests/test_chatbot.py
```

## 🚀 Deployment

### Production Build
*(For a Flask application, a "build" often involves ensuring all dependencies are installed and static files are collected if necessary.)*

```bash

# Ensure production dependencies are installed

# pip install -r requirements.txt

# For Gunicorn or a similar WSGI server (recommended for production)

# pip install gunicorn

# gunicorn -w 4 app:app # -w specifies the number of worker processes
```

### Deployment Options
-   **Heroku/Render**: Suitable for Flask applications. Requires a `Procfile` (TODO).
-   **Docker**: Containerization offers isolated environments. A `Dockerfile` (TODO) would be beneficial.
-   **Traditional Hosting (VPS)**: Deploy using a WSGI server like Gunicorn/uWSGI with Nginx/Apache.

## 📚 API Reference

If the backend exposes specific API endpoints for external consumption (e.g., for a decoupled frontend), they would be listed here. For this chatbot, the primary interaction is conversational.

## 🤝 Contributing

We welcome contributions! Please consider the following guidelines:

1.  **Fork the repository.**
2.  **Clone your forked repository.**
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name`.
4.  **Implement your changes.**
5.  **Test your changes** thoroughly.
6.  **Commit your changes** with clear, concise messages.
7.  **Push your branch** to your forked repository.
8.  **Open a Pull Request** to the `main` branch of this repository.

### Development Setup for Contributors
Ensure you follow the [Quick Start](#🚀-quick-start) instructions for setting up the environment.

## 📄 License

This project is licensed under the [MIT LICENSE](LICENSE) - see the LICENSE file for details. <!-- TODO: Add a LICENSE file (e.g., MIT, Apache 2.0) -->

## 🙏 Acknowledgments

-   **OpenAI**: For providing powerful AI models that enable the chatbot's intelligence.
-   **Flask**: For the lightweight web framework simplifying backend development.
-   **The open-source community**: For countless tools and libraries that make development possible.

## 📞 Support & Contact

-   🐛 Issues: Feel free to report bugs or suggest features on [GitHub Issues](https://github.com/niranjan022/AI_EVENT_PLANNER_CHATBOT/issues).
-   📧 Contact: [niranjanrajagopal@outlook].

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by Niranjan Raja

</div>
