# Neplink Alpha Repository

Welcome to the alpha repository for Neplink! This project is a learning platform where we explore and implement real-time communication features using WebSockets and WebRTC. The goal is to build a robust chat and call system that can be integrated into larger applications.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [WebSocket Integration](#websocket-integration)
- [WebRTC Integration](#webrtc-integration)
- [Call Logging](#call-logging)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Neplink Alpha is a sandbox project aimed at learning and implementing real-time communication features. This repository focuses on:

- WebSockets for real-time chat functionality.
- WebRTC for peer-to-peer audio and video calls.

## Features

- **Real-time Chat**: Instant messaging using WebSockets.
- **Real-time Calls**: Audio and video calls using WebRTC.
- **Call Logging**: Storing call logs in the database for future reference.

## Technologies Used

- **Django**: Web framework for building the backend.
- **Django Channels**: Extension for handling WebSockets in Django.
- **WebRTC**: Technology for real-time peer-to-peer communication.
- **Redis**: In-memory data structure store used as a message broker.
- **JavaScript**: For client-side scripting and WebRTC integration.

## Setup and Installation

### Prerequisites

- Python 3.x
- Redis server


### Installation Steps
1. **Clone the repository**:
   ```sh
   git clone https://github.com/sajan69/neplink_alpha.git
   cd neplink_alpha


2. **Create a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt

4. **Run Redis server:**
    ```sh
    redis-server

5. **Apply migrations:**
    ```sh
    python manage.py makemigrations
    python manage.py migrate

6. **Run the development server:**
    ```sh
    python manage.py runserver

## Usage

### Accessing the Application

Open your web browser and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the application.

### Real-time Chat

1. Navigate to the chat room.
2. Enter your message and send it to see real-time updates.

### Real-time Calls

1. Navigate to the call room.
2. Allow access to your microphone and camera.
3. Initiate or receive a call to see real-time audio and video communication.

## Code Overview

The codebase is structured to facilitate real-time communication using Django Channels and WebRTC. Below is a brief overview of the key components:

### WebSocket Integration

- **Django Channels**: Used to handle WebSocket connections for real-time chat functionality.
- **Consumers**: WebSocket consumers manage the connection lifecycle and message handling. The `ChatConsumer` handles chat messages, while the `CallConsumer` manages signaling for WebRTC calls.

### WebRTC Integration

- **Peer-to-Peer Communication**: WebRTC is used for establishing peer-to-peer audio and video calls.
- **Signaling**: WebSocket connections are used for signaling between peers to establish and manage WebRTC connections.

### Call Logging

- **CallLog Model**: A Django model to store call logs, including details such as caller, receiver, call type, and timestamp.
- **Database Integration**: Call events are logged in the database to keep track of call history.

## Contributing

We welcome contributions to improve this project. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch to your fork.
4. Create a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.