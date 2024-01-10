# Projects.ai Chatbot Local Setup Guide

This guide will walk you through the steps to set up the projects.ai chatbot on your local machine using Rasa.

## Prerequisites

- Ensure you have Python version 3.8.0 installed. If not, you can download it from the [official Python website](https://www.python.org/downloads/release/python-380/).

## Setup Instructions

### 1. Setting Up the Environment

1. Install Python version 3.8.0.
```bash
# Download and install from https://www.python.org/downloads/release/python-380/
```

2. Create a new virtual environment.
```bash
python -m venv venv_rasa
```

3. Activate the virtual environment.
For Windows:
```bash
.\venv_rasa\Scripts\activate
```
For Linux/Mac:
```bash
source venv_rasa/bin/activate
```

4. Install Rasa.
```bash
pip install rasa
```

### 2. Training and Testing the Model

5. Train the chatbot model.
```bash
rasa train
```

6. Test the trained model.
```bash
rasa shell
```

### 3. Running the Servers

1. To run the website:
```bash
rasa run --enable-api --cors "*"
```

2. To run the actions:
```bash
rasa run actions
```

## Additional Resources

For a deeper dive and more configurations, refer to the official Rasa documentation: [https://rasa.com/docs/rasa/](https://rasa.com/docs/rasa/).